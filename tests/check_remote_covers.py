import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sync_note_rss import valid_cover_url
items=json.loads(Path('articles.json').read_text(encoding='utf-8'))
assert len(items)==21,len(items)
assert sorted(x['series_order'] for x in items if x['category']=='series')==list(range(10))
assert all(valid_cover_url(x['cover']) for x in items)
assert not Path('assets/covers').exists()
assert len({x['url'] for x in items})==len(items)
print('PASS: 21記事、連載0〜9回、全表紙note URL、covers無し')
