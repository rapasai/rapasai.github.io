#!/usr/bin/env python3
"""Sync official note RSS metadata into the existing curated article catalogue.

The website still controls categories, recommendations, and manual article inclusion.
Existing article titles, dates, and image URLs follow the live feed when available.
RSS outages never overwrite articles.json.
"""
import argparse
import json
import os
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

FEED = 'https://note.com/rapasai_lab/rss'
NS_MEDIA = '{http://search.yahoo.com/mrss/}thumbnail'

def canonical(url):
    u = urlsplit((url or '').strip())
    if u.scheme != 'https' or u.netloc != 'note.com' or not u.path.startswith('/rapasai_lab/n/'):
        return ''
    return urlunsplit((u.scheme, u.netloc, u.path.rstrip('/'), '', ''))

def extract(xmlbytes):
    root = ET.fromstring(xmlbytes)
    items = root.findall('./channel/item')
    if not items:
        raise ValueError('RSSに記事がありません。更新しません')
    found = {}
    for item in items:
        url = canonical(item.findtext('link'))
        if not url:
            continue
        title = (item.findtext('title') or '').strip()
        raw_date = (item.findtext('pubDate') or '').strip()
        # media:thumbnail generally stores the URL in its url attribute, not text.
        media = item.find(NS_MEDIA)
        thumb = ((media.get('url') or media.text or '') if media is not None else '').strip()
        if not thumb:
            for elt in item:
                if elt.tag.rsplit('}', 1)[-1] in ('enclosure','content'):
                    candidate = (elt.get('url') or '').strip()
                    if candidate.startswith('https://') and any(ext in candidate.lower() for ext in ('.jpg','.jpeg','.png','.webp','image')):
                        thumb=candidate
                        break
        if not title or not raw_date:
            raise ValueError(f'RSS記事のタイトルまたは日付がありません: {url}')
        dt = parsedate_to_datetime(raw_date)
        if dt.tzinfo is None:
            raise ValueError(f'RSS記事の日付にタイムゾーンがありません: {url}')
        date = dt.astimezone(__import__('datetime').timezone(__import__('datetime').timedelta(hours=9))).date().isoformat()
        if thumb and not thumb.startswith('https://'):
            raise ValueError(f'画像URLが不正です: {url}')
        if url in found:
            raise ValueError(f'RSSの同一URLが重複: {url}')
        found[url] = {'title': title, 'date': date, 'cover': thumb}
    if not found:
        raise ValueError('RSSのURLを解釈できませんでした')
    return found

def sync(data, feed):
    if not isinstance(data, list) or not data:
        raise ValueError('記事データ形式が不正です')
    updated = []
    out = []
    for original in data:
        entry = dict(original)
        url = canonical(entry.get('url'))
        if not url:
            raise ValueError(f'記事URLが不正です: {entry.get("url")}')
        incoming = feed.get(url)
        if incoming:
            old = (entry.get('title'), entry.get('published_at'), entry.get('cover'))
            entry['title'] = incoming['title']
            entry['published_at'] = incoming['date']
            if incoming['cover']:
                entry['cover'] = incoming['cover']
            if old != (entry['title'], entry['published_at'], entry['cover']):
                updated.append(url)
        out.append(entry)
    # A new note article needs editorial category/POP approval before appearing in shelves.
    existing = {canonical(x['url']) for x in out}
    pending = [{'url': url, **info} for url, info in feed.items() if url not in existing]
    pending.sort(key=lambda x:(x['date'],x['url']),reverse=True)
    return out, updated, pending


class OGParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.images=[]; self.titles=[]
    def handle_starttag(self, tag, attrs):
        if tag != 'meta': return
        a=dict(attrs)
        if a.get('property') in ('og:image','twitter:image') or a.get('name') == 'twitter:image':
            self.images.append(a.get('content',''))
        if a.get('property') == 'og:title': self.titles.append(a.get('content',''))

def fetch_page_og(url):
    req=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html'})
    with urlopen(req,timeout=25) as res:
        ct=res.headers.get('Content-Type','')
        if 'html' not in ct: raise ValueError(f'記事HTMLを取得できません: {url}')
        content=res.read(3_000_001)
    if len(content)>3_000_000: raise ValueError('記事HTMLのサイズ制限超過')
    parser=OGParser();parser.feed(content.decode('utf-8',errors='replace'))
    for img in parser.images:
        if valid_cover_url(img): return img
    return ''

def valid_cover_url(url):
    try:
        u=urlparse(url)
        return u.scheme=='https' and u.hostname in ('assets.st-note.com','d2l930y2yx77uc.cloudfront.net','note.com','cdn.note.com','image.st-note.com') and bool(u.path.strip('/'))
    except (ValueError,TypeError): return False

def check_image(url):
    if not valid_cover_url(url):raise ValueError(f'note画像CDN以外のURLです: {url}')
    req=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/avif,image/webp,image/png,image/jpeg,*/*'})
    with urlopen(req,timeout=25) as res:
        ct=res.headers.get('Content-Type','').split(';')[0].lower()
        blob=res.read(64)
        if not ct.startswith('image/') or not blob:
            raise ValueError(f'表紙画像ではありません: {url}: {ct}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--rss-file',help='XMLテストファイル')
    ap.add_argument('--articles',default='articles.json')
    ap.add_argument('--pending',default='note_pending_articles.json')
    ap.add_argument('--test-offline',action='store_true',help='テスト専用。画像の通信検証は行わない')
    args=ap.parse_args()
    if args.rss_file:
        xml=Path(args.rss_file).read_bytes()
    else:
        req=Request(FEED,headers={'User-Agent':'Mozilla/5.0','Accept':'application/rss+xml,application/xml,text/xml'})
        with urlopen(req,timeout=25) as res:
            ct=res.headers.get('Content-Type','')
            if 'xml' not in ct and 'rss' not in ct:raise ValueError(f'RSSではありません: {ct}')
            xml=res.read(3_000_001)
            if len(xml)>3_000_000:raise ValueError('RSSのサイズ制限超過')
    feed=extract(xml)
    articles_path=Path(args.articles)
    original=json.loads(articles_path.read_text(encoding='utf-8'))
    # RSSに存在しない記事がある場合、過去の手入力タイトルを正式タイトルとして公開しない。
    # RSSの配信対象外の記事は既存データを保持し、取得できた記事だけ同期。
    missing_titles=[e['url'] for e in original if canonical(e['url']) not in feed]
    updated,changed,pending=sync(original,feed)
    # note RSS/OGPで実際に取得できた画像を個別に検証し、参照する。
    # 同期できない記事は同梱の表紙を残す。表示を壊さない。
    remote_count=0
    for entry in updated:
        cover=entry.get('cover','')
        if not valid_cover_url(cover) and canonical(entry['url']) in feed:
            try:
                cover=fetch_page_og(canonical(entry['url'])) if not args.test_offline else ''
            except Exception:
                cover=''
        if valid_cover_url(cover) and not args.test_offline:
            try:
                check_image(cover)
                entry['cover']=cover
                remote_count+=1
            except Exception as e:
                print('画像確認失敗・ローカル表紙を保持:',entry['url'],e)
                entry['cover']=f"assets/covers/article_{entry['id']:02d}.webp"
        elif not args.test_offline:
            entry['cover']=f"assets/covers/article_{entry['id']:02d}.webp"
    if not args.test_offline:
        body=json.dumps(updated,ensure_ascii=False,indent=2)+'\n'
        tmp=articles_path.with_name(articles_path.name+'.tmp')
        tmp.write_text(body,encoding='utf-8');tmp.replace(articles_path)
    print('noteで画像を確認した件数=',remote_count,'RSS対象外=',len(missing_titles))
    Path(args.pending).write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'RSS={len(feed)} 記事={len(updated)} 未検証画像={len(missing)}')

if __name__=='__main__':main()
