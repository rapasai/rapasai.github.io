import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
class SiteTest(unittest.TestCase):
 def test_series(self):
  a=json.loads((ROOT/'articles.json').read_text()); s=[x for x in a if x['category']=='series'];self.assertEqual(len(a),21);self.assertEqual(len(s),10);self.assertEqual(sorted(x['series_order'] for x in s),list(range(10))); self.assertEqual([x for x in s if x['series_order']==9][0]['id'],21)
 def test_images(self):
  for a in json.loads((ROOT/'articles.json').read_text()):self.assertTrue(a['cover'].startswith('assets/covers/') or a['cover'].startswith('https://'),a['cover'])
 def test_index(self):
  h=(ROOT/'index.html').read_text();self.assertIn("['series','連載｜AI産業の資金と利益']",h);self.assertIn("id==='series'?a.series_order-b.series_order",h)
