# RapasAI Lab site update

## 内容

- 親サイト一式
- `/ask/` フォームページ
- `ask/assets/ask.css`

## 今回の状態

- 親サイトの概要PDF導線を削除し、R-DR関連記事4本へのリンクに変更しています。
- `assets/pdf/R-DR_overview.pdf` は同梱していません。
- 親サイト Contact セクションの表示メールアドレスを `contact@rapasai.jp` に変更しています。
- 親サイト Contact セクションから `/ask/` への問い合わせフォーム導線は維持しています。
- `/ask/` ページは、Formspree無料運用を前提とした問い合わせフォームのまま維持しています。
- `/ask/index.html` の Formspree送信先URLは変更していません。

## note記事リンク

- 文書サービスに「完成文書の整合確認機能」を追加する――R-DRでできること  
  https://note.com/rapasai_lab/n/necffb69677c8
- その文書、本当に全体として整っていますか？――R-DR｜RapasAI Document Reviewer  
  https://note.com/rapasai_lab/n/nc42816ea4f03
- 生成AIに判断を任せない理由――R-DRの設計思想  
  https://note.com/rapasai_lab/n/ncdd6c177af86
- 生成AIに判断を任せない文書解析エンジン――R-DR｜RapasAI Document Reviewer  
  https://note.com/rapasai_lab/n/nfb0725b73fef

## Formspree送信先

`ask/index.html` 内のフォーム送信先は変更していません。

```html
<form class="contact-form" action="https://formspree.io/f/mkjgrzpr" method="POST">
```

Formspreeの受信先メールアドレスは、Formspree管理画面側で `contact@rapasai.jp` に変更してください。

## フォーム項目

- お問い合わせの種類：必須
- お名前：任意
- 会社名・屋号：任意
- メールアドレス：必須
- お問い合わせ内容：必須

## 注意

本番アップロード後、`https://rapasai.jp/ask/` から送信テストしてください。

## v2補足
- `/ask/` ページを維持しています。
- `/ask/assets/ask.css` を同梱しています。
- `/ask/index.html` のCSS参照は `./assets/ask.css` のままです。
- `CNAME` は `rapasai.jp` として同梱しています。
- `assets/pdf/R-DR_overview.pdf` は同梱していません。
