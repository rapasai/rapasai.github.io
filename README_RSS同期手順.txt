RapasAI Lab｜note記事情報・表紙画像の同期手順

本版は、記事21件と連載第0～9回を維持します。デザインは変更していません。
画像21枚は初回表示用・通信失敗時用として同梱しています。

GitHubで .github/workflows/sync-note-rss.yml を含む全ファイルを反映してください。
GitHub の Settings → Pages は「Deploy from a branch」「main」「/(root)」のままです。
Actions → note記事タイトルと表紙の同期 → Run workflow で同期を実行します。

処理はnote公式RSSを取得し、記事URLが一致するものについて正式タイトルと公開日を更新します。
表紙画像URLはRSSから取得し、足りなければ記事のOGPから取得します。
画像データの取得に成功したURLだけ採用します。失敗時には同梱の表紙を使用します。
RSSに表示されない古い記事は変更しません。
新記事は自動で棚に追加せず、候補データに記録します。
GitHub Actionsの実通信成功はGitHubで実行して確認してください。

重要：CNAME（rapasai.jp）を同梱しています。削除しないでください。
