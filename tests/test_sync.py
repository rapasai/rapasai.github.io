import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sync_note_rss import canonical, extract, sync

RSS='''<?xml version="1.0" encoding="UTF-8"?><rss xmlns:media="http://search.yahoo.com/mrss/" version="2.0"><channel><item><title>第9回：新しい正式タイトル</title><link>https://note.com/rapasai_lab/n/n3531a5020a48</link><pubDate>Sun, 18 Oct 2026 20:25:00 +0900</pubDate><media:thumbnail>https://assets.st-note.com/test.jpg</media:thumbnail></item><item><title>次の記事</title><link>https://note.com/rapasai_lab/n/nnew001</link><pubDate>Mon, 19 Oct 2026 12:00:00 +0900</pubDate></item></channel></rss>'''.encode('utf-8')
class TestSync(unittest.TestCase):
 def test_feed(self):
  feed=extract(RSS)
  self.assertEqual(feed['https://note.com/rapasai_lab/n/n3531a5020a48']['date'],'2026-10-18')
  self.assertEqual(feed['https://note.com/rapasai_lab/n/n3531a5020a48']['cover'],'https://assets.st-note.com/test.jpg')
 def test_existing_and_pending(self):
  existing=[{'url':'https://note.com/rapasai_lab/n/n3531a5020a48','title':'old','published_at':'2026-01-01','cover':'local.webp','category':'infra','recommendation':'keep'}, {'url':'https://note.com/rapasai_lab/n/nother','title':'preserve','published_at':'2026-01-02','cover':'local2.webp','category':'daily'}]
  output,changed,pending=sync(existing,extract(RSS))
  self.assertEqual(output[0]['title'],'第9回：新しい正式タイトル')
  self.assertEqual(output[0]['category'],'infra')
  self.assertEqual(output[0]['recommendation'],'keep')
  self.assertEqual(output[1],existing[1])
  self.assertEqual(len(changed),1)
  self.assertEqual(len(pending),1)
 def test_reject_no_feed(self):
  with self.assertRaises(ValueError): extract(b'<rss><channel></channel></rss>')
 def test_reject_bad_date(self):
  with self.assertRaises(Exception): extract(RSS.replace(b'Sun, 18 Oct 2026 20:25:00 +0900',b'invalid'))
 def test_reject_unsafe_url(self):
  self.assertEqual(canonical('https://evil.example/rapasai_lab/n/abc'),'')
if __name__=='__main__':unittest.main()
