RapasAI Lab｜記事の追加・おすすめ・並び順

【通常の記事追加】
1. assets/covers/ に新記事の表紙WebP画像を追加します。
2. articles.json の配列に1件追加します。
   必須：id（重複しない番号）、title、category、cover、url、published_at（YYYY-MM-DD）。
   recommendation は最新記事用POPとして使われます。
3. GitHubへ articles.json と表紙画像だけアップロードしてCommitします。
   index.html、ask/、CNAMEなどの再アップロードは不要です。

【自動表示】
・本棚：各カテゴリで published_at の新しい記事が左上（目次表示では最上段）。
・おすすめ第1枠：全記事中で published_at が最新の1本。
・おすすめ第2枠：recommendation_slot が editor_pick の記事。
・おすすめ第3枠：recommendation_slot が nanohana の記事。
・1記事を2枠に同時表示しない。最新記事が第2／第3枠と同一なら、その枠は重複させません。
・第2／第3枠の変更は articles.json の recommendation_slot の付け替えだけで行います。各枠1本ずつ指定します。

【現在のおすすめ】
第1枠：Maia 300（最新記事）
第2枠：AIの計算処理能力は、どこで増やせるのか？（手動選択）
第3枠：名前を持つということ（当面固定）

【注意】
・公開日が同日の記事はidの大きい方が先になります。1日に複数投稿する場合は公開時刻で厳密に比較しない仕様です。
・HTMLを file:// で直開きするとfetch制限で記事が表示されない場合があります。GitHub PagesまたはHTTPサーバーで確認してください。
・既存記事の公開日はnoteから照合。article_07（データセンター記事）はnote記事一覧の新着順から2026-10-12として登録しているため、日付が違う場合はarticles.json内の日付を訂正してください。
