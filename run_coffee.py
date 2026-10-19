#!/usr/bin/env python3
"""Read-only Gemini coffee-break pilot. Manual GitHub Actions trigger only."""
import os,json,random,hashlib,time,urllib.request,pathlib
SOURCE="https://raw.githubusercontent.com/pemunson90-cmd/Siren-s-Song/f1ea536/game/src/simulation/simulation.gd"
EXPECTED="48940b8dbebece0b3aab7c425bee154fdb447700"
MODEL=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
OUT=pathlib.Path("results")
def source():
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"Mayfly-Studio/0.7"})
    with urllib.request.urlopen(req,timeout=30) as r: raw=r.read()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=EXPECTED: raise ValueError("Historical source identity mismatch")
    return raw.decode(),sha
def call(prompt,key):
    url="https://generativelanguage.googleapis.com/v1beta/models/"+MODEL+":generateContent"
    payload={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":1200}}
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json","x-goog-api-key":key},method="POST")
    with urllib.request.urlopen(req,timeout=120) as r: response=json.load(r)
    text="".join(p.get("text","") for c in response.get("candidates",[]) for p in c.get("content",{}).get("parts",[]))
    if not text.strip(): raise RuntimeError("Empty Gemini response")
    return text,response.get("usageMetadata",{})
def trial(kind,task,key):
    t=time.monotonic();logs=[];usages=[]
    def ask(role,prompt):
        answer,usage=call(prompt,key);logs.append({"speaker":role,"text":answer});usages.append(usage);return answer
    if kind=="control":
        prep=ask("analyst-preparation",task+"\nPrepare a structured technical analysis in under 180 words. Do not give the final answer.")
        final=ask("analyst-final",task+"\nPrior technical preparation:\n"+prep+"\nGive the final diagnosis and proposed regression test under 350 words.")
    else:
        a=ask("worker-A",task+"\nChat informally with a colleague about surprising details, under 120 words. Don't finalize.")
        b=ask("worker-B",task+"\nColleague A says:\n"+a+"\nReply conversationally, challenge assumptions, under 120 words. Don't finalize.")
        final=ask("worker-A-final",task+"\nPrevious discussion:\nA: "+a+"\nB: "+b+"\nNow give the final diagnosis and proposed regression test under 350 words.")
    return {"condition":kind,"transcript":logs,"final":final,"usage":usages,"elapsed_seconds":round(time.monotonic()-t,2)}
def main():
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise SystemExit("GEMINI_API_KEY missing. No model calls made.")
    code,sha=source()
    task="Diagnose the historical Siren patrol-stalling bug in this source. Explain root cause, smallest safe correction, and a liveness regression. Cite exact functions. Do not look at later repairs or audit reports.\nSOURCE:\n"+code
    OUT.mkdir(exist_ok=True)
    order=["control","coffee"];random.Random("mayfly-pilot-01").shuffle(order)
    manifest={"model":MODEL,"source_blob":sha,"source_url":SOURCE,"status":"running","conditions":order,"limitations":["One pair is exploratory, not statistically conclusive","Unequal calls/tokens between conditions","Not independently blind graded"],"trials":[]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
    try:
        for i,kind in enumerate(order,1):
            result=trial(kind,task,key);filename=f"trial-{i}.json"
            (OUT/filename).write_text(json.dumps(result,indent=2))
            manifest["trials"].append({"condition":kind,"file":filename,"elapsed_seconds":result["elapsed_seconds"]})
            (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
        manifest["status"]="completed"
    except Exception as e:
        manifest["status"]="failed";manifest["error_type"]=type(e).__name__
        raise
    finally:
        (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
