# Mayfly Studios

Mayfly Coffee Lab is a small pilot comparing two ways to prepare a code diagnosis: a structured technical discussion and a conversational one. Both use the same historical source and three model calls per condition. The pilot records what each approach produces and how much it costs in time and tokens.

Run the offline checks with `python3 -m unittest -v test_coffee.py`. To run a live trial, use the repository's manually started **Mayfly Coffee Lab** workflow. Each matched pair uses six model calls.

Download the workflow's results. Open `review.md` and grade each answer on its diagnosis, proposed fix, and regression test before opening `review-key.json`. Use `manifest.json` to see the model, source revision, trial status and token/time measurements. The automatic source indicators describe what an answer mentions. A blind grade still needs a human reviewing the pinned source, and one historical task is a pilot.
