RapasAI Lab｜note記事情報の自動同期

このZIPは、GitHubリポジトリの中身を全削除した後、そのまま全アップロードできる完全版です。
ZIP自体ではなく、解凍後の中身をリポジトリ直下へアップロードしてください。

■ この版に含まれるもの
・index.html
・articles.json（第0回〜第10回を含む全22記事）
・CNAME（rapasai.jp）
・.nojekyll
・assets/（ロゴのみ。記事coverフォルダはありません）
・ask/（お問い合わせページ）
・scripts/sync_note_rss.py
・.github/workflows/sync-note-rss.yml

■ 新しい記事を追加するとき
以後は articles.json に1件追加してGitHubへアップロードするだけです。
GitHub Actionsがnote RSSを参照し、次を自動取得してarticles.jsonへ反映します。
・正式タイトル
・公開日
・表紙画像URL

例：連載の第11回を追加する場合
{
  "id": 23,
  "title": "",
  "category": "series",
  "cover": "",
  "url": "https://note.com/rapasai_lab/n/xxxxxxxxxxxx",
  "recommendation": "",
  "published_at": "",
  "series_order": 11
}

category、series_order、recommendation、recommendation_slotなど、HP側の編集情報は自動同期で変更しません。

■ RSS反映が遅れた場合
新記事がまだnote RSSに出ていない場合、その回の同期はFAILになり、articles.jsonを壊しません。
ワークフローは1時間ごとにも再実行されます。
既存記事はそのまま表示されます。

■ GitHub上で確認する場所
Actions に「note記事情報を自動同期」が表示されます。
新記事追加後、このActionが成功すると、articles.jsonのtitle / published_at / coverがnote取得値へ更新されます。
