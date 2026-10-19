#!/usr/bin/env python3
"""RapasAI Lab: note metadata synchronizer.

New article workflow:
1. Add a record to articles.json with at least id/url/category and optional series_order/recommendation fields.
2. GitHub Actions runs this script automatically.
3. note RSS supplies title, published_at and cover for articles currently in the feed.
4. Existing curated metadata is preserved for older articles no longer present in the feed.

Only note-controlled metadata is updated:
  - title
  - published_at
  - cover
Editorial fields (category, series_order, recommendation, recommendation_slot, etc.) are preserved.
"""
import argparse
import json
import re
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
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def canonical(url):
    u = urlsplit((url or '').strip())
    if u.scheme != 'https' or u.netloc != 'note.com' or not u.path.startswith('/rapasai_lab/n/'):
        return ''
    return urlunsplit((u.scheme, u.netloc, u.path.rstrip('/'), '', ''))


def valid_cover_url(url):
    try:
        u = urlparse(url or '')
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
        if not title or not raw_date:
            continue
        dt = parsedate_to_datetime(raw_date)
        if dt.tzinfo is None:
            continue
        found[url] = {
            'title': title,
            'published_at': dt.astimezone(JST).date().isoformat(),
            'cover': cover,
        }
    return found


def load_articles(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, list) or not data:
        raise ValueError('articles.json が記事配列ではありません')
    ids, urls = set(), set()
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


def complete_existing(e):
    return bool((e.get('title') or '').strip()) and bool(DATE_RE.match((e.get('published_at') or '').strip())) and valid_cover_url(e.get('cover'))


def build_sync(original, feed, live_images=True):
    output, report, failures = [], [], []
    for src in original:
        entry = dict(src)
        url = canonical(src['url'])
        incoming = feed.get(url)
        row = {'id': src['id'], 'url': url}

        if incoming is None:
            if complete_existing(src):
                row['status'] = 'PRESERVED_NOT_IN_RSS'
                output.append(entry)
                report.append(row)
                continue
            row['status'] = 'FAIL'
            row['error'] = 'RSSに未同期の記事で、既存メタデータも未完成です'
            failures.append(row['error'] + ': ' + url)
            output.append(entry)
            report.append(row)
            continue

        cover = (incoming.get('cover') or '').strip()
        if not valid_cover_url(cover):
            try:
                cover = fetch_page_og(url) if live_images else cover
            except Exception as exc:
                row['og_error'] = str(exc)

        title = (incoming.get('title') or '').strip()
        published_at = (incoming.get('published_at') or '').strip()
        if not title or not DATE_RE.match(published_at):
            row['status'] = 'FAIL'
            row['error'] = 'RSSのタイトルまたは公開日が不正です'
            failures.append(row['error'] + ': ' + url)
            output.append(entry)
            report.append(row)
            continue
        if not valid_cover_url(cover):
            row['status'] = 'FAIL'
            row['error'] = '表紙URLを取得できません'
            failures.append(row['error'] + ': ' + url)
            output.append(entry)
            report.append(row)
            continue

        changed_cover = cover != (src.get('cover') or '')
        if live_images and changed_cover:
            try:
                check_image(cover)
            except Exception as exc:
                row['status'] = 'FAIL'
                row['error'] = str(exc)
                failures.append(row['error'])
                output.append(entry)
                report.append(row)
                continue

        entry['title'] = title
        entry['published_at'] = published_at
        entry['cover'] = cover
        entry['note_metadata_source'] = 'note_rss_ogp'
        row.update({'status': 'UPDATED' if (entry != src) else 'UNCHANGED', 'title': title, 'published_at': published_at, 'cover': cover})
        output.append(entry)
        report.append(row)

    return output, report, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--articles', default='articles.json')
    ap.add_argument('--rss-file', help='オフライン検査用RSS XML')
    ap.add_argument('--report', default='note_fetch_report.json')
    ap.add_argument('--no-image-request', action='store_true', help='テスト用: 画像HTTP検査を省略')
    ap.add_argument('--write', action='store_true', help='同期可能な全記事が正常な場合だけarticles.jsonを更新')
    args = ap.parse_args()

    original = load_articles(args.articles)
    if args.rss_file:
        xml = Path(args.rss_file).read_bytes()
    else:
        xml, ct = fetch_bytes(FEED, 'application/rss+xml,application/xml,text/xml')
        if 'xml' not in ct and 'rss' not in ct:
            raise SystemExit(f'FAIL: RSSではありません: {ct}')

    feed = extract(xml)
    updated, report, failures = build_sync(original, feed, live_images=not args.no_image_request)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    counts = {}
    for r in report:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print(f'RSS記事数={len(feed)} 対象={len(original)} ' + ' '.join(f'{k}={v}' for k,v in sorted(counts.items())) + f' FAIL={len(failures)}')

    if failures:
        print('FAIL: articles.json は変更しません')
        for msg in failures:
            print('-', msg)
        raise SystemExit(1)

    if args.write:
        tmp = Path(args.articles + '.tmp')
        tmp.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(args.articles)
        print(f'PASS: {len(original)}記事をnote取得情報で同期しました')
    else:
        print(f'PASS: {len(original)}記事を検証しました（未書き込み）')


if __name__ == '__main__':
    main()
