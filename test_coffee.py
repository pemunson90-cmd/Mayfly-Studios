import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import run_coffee as m
class CoffeeLabTests(unittest.TestCase):
 def test_grounded_functions(self):
  source="func _threats(dt):\n pass\nfunc path(a,b):\n pass\n"
  v=m.source_checks("In _threats() path() returns [] on blocked goal >35; assert regression",source)
  self.assertTrue(v["correct_root_functions"])
  self.assertEqual(v["cited_unknown_functions"],[])
 def test_flags_unknown_method(self):
  source="func path(a,b):\n pass\n"
  v=m.source_checks("Call _tick() and path() for regression",source)
  self.assertIn("_tick",v["cited_unknown_functions"])
 def test_three_calls_both_conditions(self):
  source="func _threats(dt):\n pass\nfunc path(a,b):\n pass\n"
  task="diagnose"
  with patch.object(m,"call",return_value=("In _threats() path() returns empty route when blocked and distance 35. test assert",{"totalTokenCount":10})) as mocked:
   for condition in ("control","coffee"):
    result=m.trial(condition,task,"dummy",source,1)
    self.assertEqual(len(result["transcript"]),3)
    self.assertEqual(result["total_tokens"],30)
   self.assertEqual(mocked.call_count,6)
 def test_bounded_pairs(self):
  self.assertTrue(1<=m.PAIRS<=5)
 def test_review_keeps_trial_labels_out_of_the_grading_sheet(self):
  results = [
   {"pair": 1, "condition": "control", "final": "First diagnosis"},
   {"pair": 1, "condition": "coffee", "final": "Second diagnosis"},
  ]
  with tempfile.TemporaryDirectory() as tmp, patch.object(m, "OUT", Path(tmp)):
   m.write_review(results)
   review = (Path(tmp) / "review.md").read_text(encoding="utf-8")
   key = json.loads((Path(tmp) / "review-key.json").read_text(encoding="utf-8"))
  self.assertNotIn("control", review)
  self.assertNotIn("coffee", review)
  self.assertEqual(set(key), {"1A", "1B"})
  self.assertEqual(set(key.values()), {"control", "coffee"})
  for answer_id, condition in key.items():
   answer = next(r["final"] for r in results if r["condition"] == condition)
   self.assertIn(f"## Answer {answer_id}\n\n> {answer}", review)
if __name__=="__main__": unittest.main()
