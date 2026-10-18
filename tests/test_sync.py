import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sync_note_rss import canonical, extract, build_sync

RSS = '''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:media="http://search.yahoo.com/mrss/" version="2.0"><channel>
<item><title>第9回：新しい正式タイトル</title><link>https://note.com/rapasai_lab/n/n3531a5020a48</link><pubDate>Sun, 18 Oct 2026 20:25:00 +0900</pubDate><media:thumbnail url="https://assets.st-note.com/test.jpg" /></item>
</channel></rss>'''.encode('utf-8')

class TestSync(unittest.TestCase):
    def test_feed(self):
        feed = extract(RSS)
        e = feed['https://note.com/rapasai_lab/n/n3531a5020a48']
        self.assertEqual(e['published_at'], '2026-10-18')
        self.assertEqual(e['cover'], 'https://assets.st-note.com/test.jpg')
        self.assertEqual(e['title'], '第9回：新しい正式タイトル')

    def test_build_sync_offline(self):
        existing = [{
            'id': 21,
            'url': 'https://note.com/rapasai_lab/n/n3531a5020a48',
            'title': 'old',
            'published_at': '2026-01-01',
            'cover': '',
            'category': 'series',
            'series_order': 9,
            'recommendation': 'keep',
        }]
        output, report, failures = build_sync(existing, extract(RSS), live_images=False)
        self.assertEqual(failures, [])
        self.assertEqual(report[0]['status'], 'PASS_OFFLINE')
        self.assertEqual(output[0]['title'], '第9回：新しい正式タイトル')
        self.assertEqual(output[0]['published_at'], '2026-10-18')
        self.assertEqual(output[0]['cover'], 'https://assets.st-note.com/test.jpg')
        self.assertEqual(output[0]['category'], 'series')
        self.assertEqual(output[0]['series_order'], 9)
        self.assertEqual(output[0]['recommendation'], 'keep')

    def test_reject_no_feed(self):
        with self.assertRaises(ValueError):
            extract(b'<rss><channel></channel></rss>')

    def test_reject_bad_date(self):
        with self.assertRaises(Exception):
            extract(RSS.replace(b'Sun, 18 Oct 2026 20:25:00 +0900', b'invalid'))

    def test_reject_unsafe_url(self):
        self.assertEqual(canonical('https://evil.example/rapasai_lab/n/abc'), '')

if __name__ == '__main__':
    unittest.main()
