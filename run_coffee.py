#!/usr/bin/env python3
"""Mayfly Coffee Lab: randomized matched calls, source-grounded blind scoring.
Read-only historical source, no production writes, manual GitHub Actions trigger.
"""
import os, json, random, hashlib, time, urllib.request, urllib.error, pathlib, re, sys
SOURCE="https://raw.githubusercontent.com/pemunson90-cmd/Siren-s-Song/f1ea536/game/src/simulation/simulation.gd"
EXPECTED="48940b8dbebece0b3aab7c425bee154fdb447700"
MODEL=os.getenv("GEMINI_MODEL","gemini-3.8-flash")
PAIRS=max(1,min(5,int(os.getenv("MAYFLY_PAIRS","3"))))
OUT=pathlib.Path("results")
MAX_OUTPUT=900
def fetch_source():
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"Mayfly-Studio/0.8"})
    with urllib.request.urlopen(req,timeout=30) as r: raw=r.read()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=EXPECTED: raise ValueError("Historical source SHA mismatch")
    return raw.decode(),sha
def call(prompt,key):
    url="https://generativelanguage.googleapis.com/v1beta/models/"+MODEL+":generateContent"
    payload={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":MAX_OUTPUT}}
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json","x-goog-api-key":key},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=120) as r: response=json.load(r)
    except urllib.error.HTTPError as e:
        body=e.read(500).decode(errors="replace")
        raise RuntimeError("Gemini HTTP "+str(e.code)+": "+body) from None
    answer="".join(p.get("text","") for c in response.get("candidates",[]) for p in c.get("content",{}).get("parts",[]))
    if not answer.strip(): raise RuntimeError("Empty model response")
    return answer,response.get("usageMetadata",{})
def tokens(u):
    return int(u.get("totalTokenCount",0))
def source_checks(answer,source):
    """Source-grounded indicators, not a semantic or executable test verdict."""
    fn=set(re.findall(r"^func\s+([A-Za-z_][\w]*)\s*\(",source,re.M))
    citations=re.findall(r"(?<![\w])(?:_threats|_move|path|blocked|_tick|advance)\s*\(",answer)
    valid=[x[:-1].strip() for x in citations if x[:-1].strip() in fn]
    invented=[x[:-1].strip() for x in citations if x[:-1].strip() not in fn]
    paths=re.findall(r"res://[\w/.-]+",answer)
    return {"correct_root_functions":all(x in answer for x in ["_threats","path"]),
            "mentions_blocked_goal":bool(re.search(r"block|unreach|invalid",answer,re.I)),
            "mentions_empty_route":bool(re.search(r"empty|\[\]",answer,re.I)),
            "mentions_arrival_gate":bool(re.search(r"35|arriv|distance",answer,re.I)),
            "mentions_liveness_test":bool(re.search(r"test|assert|regression",answer,re.I)),
            "cited_existing_functions":sorted(set(valid)),
            "cited_unknown_functions":sorted(set(invented)),
            "proposed_source_paths":paths,
            "warning":"Indicators only: tests are not executed and no blind semantic judge is implemented."}
def trial(kind,task,key,source,pair):
    start=time.monotonic(); transcript=[]; usages=[]
    def ask(role,question):
        answer,usage=call(question,key)
        transcript.append({"role":role,"text":answer})
        usages.append(usage)
        return answer
    # Both conditions have exactly three model calls, same source, per-call output cap.
    if kind=="control":
        a=ask("analyst-1",task+"\nMake preliminary technical observations under 120 words; do not finalize.")
        b=ask("analyst-2",task+"\nPrevious observations:\n"+a+"\nIndependently check assumptions and risks in a structured technical note under 120 words.")
    else:
        a=ask("colleague-1",task+"\nCasually tell a colleague what seems odd or interesting. Under 120 words; do not finalize.")
        b=ask("colleague-2",task+"\nColleague says:\n"+a+"\nRespond conversationally, ask questions, and challenge assumptions. Under 120 words; do not finalize.")
    final=ask("final-analyst",task+"\nPreparation:\n"+a+"\nSecond perspective:\n"+b+"\nGive diagnosis, minimal correction, and a regression test. Cite exact source functions. Under 350 words.")
    return {"pair":pair,"condition":kind,"transcript":transcript,"final":final,
            "usage":usages,"total_tokens":sum(tokens(u) for u in usages),
            "elapsed_seconds":round(time.monotonic()-start,2),
            "source_checks":source_checks(final,source)}
def write(name,obj):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
def main():
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise SystemExit("GEMINI_API_KEY missing")
    source,sha=fetch_source()
    task=("Diagnose the historical Siren patrol-stalling defect, smallest safe fix, "
          "and a liveness regression test. Cite exact source functions. "
          "Do not consult later fixes or audits.\nSOURCE:\n"+source)
    order=[(p,c) for p in range(1,PAIRS+1) for c in ("control","coffee")]
    random.Random("mayfly-0.8-balanced").shuffle(order)
    manifest={"schema":2,"status":"running","model":MODEL,"source_blob":sha,
              "source_url":SOURCE,"pairs":PAIRS,"conditions":order,
              "design":"Matched three calls per condition, same source and per-call output cap; token use is measured, not forced equal.",
              "limitations":["Single historical bug; repeated trials are not independent tasks",
                             "Prompt content differs by treatment","Token counts and reasoning budgets may differ",
                             "Static indicators are not executed regression tests or blinded expert grading"],
              "trials":[]}
    write("manifest.json",manifest)
    try:
        for i,(pair,condition) in enumerate(order,1):
            result=trial(condition,task,key,source,pair)
            filename=f"trial-{i:02d}.json"
            write(filename,result)
            manifest["trials"].append({"pair":pair,"condition":condition,"file":filename,
                                       "tokens":result["total_tokens"],"seconds":result["elapsed_seconds"],
                                       "checks":result["source_checks"]})
            write("manifest.json",manifest)
        manifest["status"]="completed"
    except Exception as exc:
        manifest["status"]="failed";manifest["error_type"]=type(exc).__name__
        manifest["error"]=str(exc)[:500]
        raise
    finally:
        write("manifest.json",manifest)
if __name__=="__main__":main()
