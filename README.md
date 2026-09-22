# RapasAI Lab site with Formspree ask page

## 内容

- 親サイト一式
- `/ask/` フォームページ
- `ask/assets/ask.css`
- `assets/pdf/R-DR_overview.pdf`

## 今回の状態

- 親サイトの Contact セクションに `/ask/` への問い合わせフォーム導線を戻しています。
- `/ask/` ページは、Tawk.toチャットではなく Formspree無料運用を前提とした問い合わせフォームに差し替えています。
- Tawk.to Widget Code は削除済みです。
- フォーム送信先は `https://formspree.io/f/mkjgrzpr` に設定済みです。

## Formspree送信先

`ask/index.html` 内のフォーム送信先は設定済みです。

```html
<form class="contact-form" action="https://formspree.io/f/mkjgrzpr" method="POST">
```

## フォーム項目

- お問い合わせの種類：必須
- お名前：任意
- 会社名・屋号：任意
- メールアドレス：必須
- お問い合わせ内容：必須

## 注意

本番アップロード後、`https://rapasai.github.io/ask/` から送信テストしてください。


## v15 update

- `/ask/` ページの見出しを「自社の文書確認フローに、R-DRを組み込めるか確認したい方へ」に修正しました。
- Tawk.toコードは引き続き削除済みです。
- Formspree送信先URLは仮のままです。
- 親サイトContactから `/ask/` へのリンクは外したままです。


## v16 update

- `/ask/` の見出しを「R-DRについて、知りたいことや確認したいことがある方へ」に変更。
- フォーム冒頭説明を、R-DRの理解確認・自社文書確認での活用・既存ツールへの組み込み・R-DR単体利用を拾える内容に変更。
- お問い合わせ種類に「R-DRについて、もう少し詳しく知りたい」を追加。
- お問い合わせ内容の例文を、組み込み相談限定ではない内容に変更。
- Tawk.toコードは削除済みのまま。Formspree送信先は仮URLのまま。親サイトContactから `/ask/` へのリンクは外したまま。


## v17
- /ask/index.html の Formspree送信先URLを `https://formspree.io/f/mkjgrzpr` に設定。
- Tawk.toコードは入っていません。
- 親サイトContactから /ask/ へのリンクは外したままです。


## v18

- 親サイト Contact セクションに `/ask/` への問い合わせフォーム導線を追加。
- `/ask/` は Formspree送信先設定済みのフォームページです。
- Tawk.toコードは入っていません。
