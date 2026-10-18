RapasAI Lab｜note記事情報 21件取得テスト手順

目的
noteの公開情報から、HPに登録済みの21記事すべてについて次の3項目を取得・検証します。
・正式タイトル
・公開日
・表紙画像URL

このテストは、連載の分類、連載順、おすすめ指定、POP、デザインを変更しません。

【テスト1：取得・検証のみ（articles.jsonは変更しない）】
このフォルダをローカルHTTPサーバーで開く必要はありません。
ターミナルでHPフォルダへ移動して、次を実行します。

python3 scripts/sync_note_rss.py

成功条件
最後に次の形式で表示されます。
RSS記事数=... 対象=21 PASS=21 PASS_OFFLINE=0 FAIL=0
PASS: 21記事すべて取得・検証済み。--write 指定時のみ articles.json を更新します

また、note_fetch_report.json が作られます。
21件すべての status が PASS なら取得検証合格です。

失敗条件
1件でも取得できなければ終了コード1で停止し、articles.json は変更しません。
note_fetch_report.json の status=FAIL と error で原因を確認できます。

【テスト2：21件すべてPASSした後だけ反映】

python3 scripts/sync_note_rss.py --write

21件すべてPASSした場合だけ、articles.json の次の項目をnote取得値へ更新します。
・title
・published_at
・cover

category、series_order、recommendation、recommendation_slot などの編集情報は変更しません。

【HP表示テスト】
更新後は、HPフォルダでローカルHTTPサーバーを起動します。

python3 -m http.server 8765

ブラウザで次を開きます。
http://127.0.0.1:8765/

確認事項
・記事21本
・連載の本棚は第0回〜第9回の10本
・第9回が連載の本棚に存在する
・各記事のタイトルがnoteと一致する
・各記事の表紙が表示される
・おすすめ3枠、POP、レイアウトが変わっていない

注意
fetch実通信テストはハナのテスト環境で行います。
本番GitHubへ反映する前に、必ず上記の21件PASSとHP表示を確認してください。
