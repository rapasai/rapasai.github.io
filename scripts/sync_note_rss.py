#!/usr/bin/env python3
"""RapasAI Lab: note metadata synchronizer.

Fetch the official note RSS, then verify all curated articles against note.
Only note-controlled metadata is updated:
  - title
  - published_at
  - cover
Editorial fields (category, series_order, recommendation, etc.) are preserved.

A live run is strict by default: every curated article must be present in the feed,
must have a title/date/cover, and every cover URL must return an image.
On any failure articles.json is left untouched.
"""
import argparse
import json
from datetime import timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urlparse
from urllib.request import Request, urlopen
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

FEED = 'https://note.com/rapasai_lab/rss'
JST = timezone(timedelta(hours=9))
NS_MEDIA = '{http://search.yahoo.com/mrss/}thumbnail'


def canonical(url):
    u = urlsplit((url or '').strip())
    if u.scheme != 'https' or u.netloc != 'note.com' or not u.path.startswith('/rapasai_lab/n/'):
        return ''
    return urlunsplit((u.scheme, u.netloc, u.path.rstrip('/'), '', ''))


def valid_cover_url(url):
    try:
        u = urlparse(url)
        return (
            u.scheme == 'https'
            and u.hostname in (
                'assets.st-note.com',
                'd2l930y2yx77uc.cloudfront.net',
                'note.com',
                'cdn.note.com',
                'image.st-note.com',
            )
            and bool(u.path.strip('/'))
        )
    except (ValueError, TypeError):
        return False


class OGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag != 'meta':
            return
        a = dict(attrs)
        prop = a.get('property') or a.get('name')
        if prop in ('og:image', 'twitter:image'):
            value = (a.get('content') or '').strip()
            if value:
                self.images.append(value)


def fetch_bytes(url, accept, limit=3_000_000):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': accept})
    with urlopen(req, timeout=25) as res:
        content_type = (res.headers.get('Content-Type') or '').lower()
        blob = res.read(limit + 1)
    if len(blob) > limit:
        raise ValueError(f'サイズ制限超過: {url}')
    return blob, content_type


def fetch_page_og(url):
    blob, ct = fetch_bytes(url, 'text/html,application/xhtml+xml')
    if 'html' not in ct:
        raise ValueError(f'記事HTMLではありません: {url}: {ct}')
    parser = OGParser()
    parser.feed(blob.decode('utf-8', errors='replace'))
    for img in parser.images:
        if valid_cover_url(img):
            return img
    return ''


def check_image(url):
    if not valid_cover_url(url):
        raise ValueError(f'note画像URLとして認められません: {url}')
    # 表紙画像の存在確認ではファイル全体をダウンロードしない。
    # Content-Type が image/* であり、先頭バイトを取得できればよい。
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'image/avif,image/webp,image/png,image/jpeg,*/*',
    })
    with urlopen(req, timeout=25) as res:
        ct = (res.headers.get('Content-Type') or '').lower()
        head = res.read(64)
    if not ct.startswith('image/') or not head:
        raise ValueError(f'画像として取得できません: {url}: {ct}')


def extract(xmlbytes):
    root = ET.fromstring(xmlbytes)
    items = root.findall('./channel/item')
    if not items:
        raise ValueError('RSSにitemがありません')

    found = {}
    for item in items:
        url = canonical(item.findtext('link'))
        if not url:
            continue
        title = (item.findtext('title') or '').strip()
        raw_date = (item.findtext('pubDate') or '').strip()
        media = item.find(NS_MEDIA)
        cover = ((media.get('url') or media.text or '') if media is not None else '').strip()
        if not cover:
            for elt in item:
                local = elt.tag.rsplit('}', 1)[-1]
                if local in ('enclosure', 'content'):
                    candidate = (elt.get('url') or '').strip()
                    if valid_cover_url(candidate):
                        cover = candidate
                        break
        if not title:
            raise ValueError(f'タイトルがありません: {url}')
        if not raw_date:
            raise ValueError(f'投稿日がありません: {url}')
        dt = parsedate_to_datetime(raw_date)
        if dt.tzinfo is None:
            raise ValueError(f'投稿日にタイムゾーンがありません: {url}')
        published_at = dt.astimezone(JST).date().isoformat()
        if url in found:
            raise ValueError(f'RSS URL重複: {url}')
        found[url] = {'title': title, 'published_at': published_at, 'cover': cover}
    if not found:
        raise ValueError('RSSから記事URLを取得できませんでした')
    return found


def load_articles(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, list) or not data:
        raise ValueError('articles.json が記事配列ではありません')
    ids = set()
    urls = set()
    for e in data:
        if e.get('id') in ids:
            raise ValueError(f'id重複: {e.get("id")}')
        ids.add(e.get('id'))
        u = canonical(e.get('url'))
        if not u:
            raise ValueError(f'note URL不正: {e.get("url")}')
        if u in urls:
            raise ValueError(f'URL重複: {u}')
        urls.add(u)
    return data


def build_sync(original, feed, live_images=True):
    output = []
    report = []
    failures = []

    for src in original:
        entry = dict(src)
        url = canonical(src['url'])
        incoming = feed.get(url)
        row = {'id': src['id'], 'url': url}
        if incoming is None:
            row['status'] = 'FAIL'
            row['error'] = 'RSSに記事がありません'
            failures.append(row['error'] + ': ' + url)
            report.append(row)
            output.append(entry)
            continue

        cover = incoming.get('cover') or ''
        if not valid_cover_url(cover):
            try:
                cover = fetch_page_og(url) if live_images else cover
            except Exception as exc:
                row['og_error'] = str(exc)

        row.update({
            'title': incoming['title'],
            'published_at': incoming['published_at'],
            'cover': cover,
        })

        if not valid_cover_url(cover):
            row['status'] = 'FAIL'
            row['error'] = '表紙URLを取得できません'
            failures.append(row['error'] + ': ' + url)
        elif live_images:
            try:
                check_image(cover)
                row['status'] = 'PASS'
            except Exception as exc:
                row['status'] = 'FAIL'
                row['error'] = str(exc)
                failures.append(row['error'])
        else:
            row['status'] = 'PASS_OFFLINE'

        if row['status'].startswith('PASS'):
            entry['title'] = incoming['title']
            entry['published_at'] = incoming['published_at']
            entry['cover'] = cover
            entry['note_metadata_source'] = 'note_rss_ogp'
        output.append(entry)
        report.append(row)

    return output, report, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--articles', default='articles.json')
    ap.add_argument('--rss-file', help='オフライン検査用RSS XML')
    ap.add_argument('--report', default='note_fetch_report.json')
    ap.add_argument('--no-image-request', action='store_true', help='テスト用: 画像HTTP検査を省略')
    ap.add_argument('--write', action='store_true', help='21件すべてPASS時だけarticles.jsonを更新')
    args = ap.parse_args()

    original = load_articles(args.articles)
    if len(original) != 21:
        raise SystemExit(f'FAIL: 記事数が21ではありません: {len(original)}')

    if args.rss_file:
        xml = Path(args.rss_file).read_bytes()
    else:
        xml, ct = fetch_bytes(FEED, 'application/rss+xml,application/xml,text/xml')
        if 'xml' not in ct and 'rss' not in ct:
            raise SystemExit(f'FAIL: RSSではありません: {ct}')

    feed = extract(xml)
    updated, report, failures = build_sync(original, feed, live_images=not args.no_image_request)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    passed = sum(1 for r in report if r.get('status') == 'PASS')
    offline_passed = sum(1 for r in report if r.get('status') == 'PASS_OFFLINE')
    print(f'RSS記事数={len(feed)} 対象=21 PASS={passed} PASS_OFFLINE={offline_passed} FAIL={len(failures)}')

    if failures:
        print('FAIL: articles.json は変更しません')
        for msg in failures:
            print('-', msg)
        raise SystemExit(1)

    if args.write:
        tmp = Path(args.articles + '.tmp')
        tmp.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(args.articles)
        print('PASS: 21記事すべてをnote取得情報で更新しました')
    else:
        print('PASS: 21記事すべて取得・検証済み。--write 指定時のみ articles.json を更新します')


if __name__ == '__main__':
    main()
