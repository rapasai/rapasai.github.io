RapasAI Lab｜記事追加手順

今後、新しいnote記事をHPへ追加するときは、原則として次の2点だけ更新します。

1. articles.json に新しい記事データを1件追加する
2. assets/covers/ に新しい表紙画像を追加する

【articles.json の項目】
- id: 重複しない連番
- title: noteの正式タイトル
- category: infra / safety / daily
- cover: 表紙画像のパス
- url: note記事の正式URL
- featured: おすすめ記事に出す場合 true、それ以外 false
- recommendation: おすすめ記事のPOP。featured=false の場合は空文字で可

index.html は articles.json を読み込んで自動表示します。記事追加のたびに index.html を編集する必要はありません。

【注意】
Macで index.html を file:// で直接開くと、Chromeのセキュリティ制限で articles.json を読み込めない場合があります。公開後の https://rapasai.jp/ では通常どおり読み込まれます。
