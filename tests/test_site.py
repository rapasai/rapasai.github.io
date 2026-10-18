import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
class SiteTest(unittest.TestCase):
 def test_series(self):
  a=json.loads((ROOT/"articles.json").read_text(encoding="utf-8")); s=[x for x in a if x["category"]=="series"]; self.assertEqual(len(a),21); self.assertEqual(len(s),10); self.assertEqual(sorted(x["series_order"] for x in s),list(range(10))); self.assertEqual([x for x in s if x["series_order"]==9][0]["id"],21)
 def test_no_local_covers(self):
  self.assertFalse((ROOT/"assets/covers").exists()); a=json.loads((ROOT/"articles.json").read_text(encoding="utf-8")); self.assertTrue(all(not x.get("cover") or x["cover"].startswith("https://") for x in a)); h=(ROOT/"index.html").read_text(encoding="utf-8"); self.assertNotIn("assets/covers/",h)
 def test_index(self):
  h=(ROOT/"index.html").read_text(encoding="utf-8"); self.assertIn("['series','連載｜AI産業の資金と利益']",h); self.assertIn("id==='series'?a.series_order-b.series_order",h)
if __name__=="__main__": unittest.main()
