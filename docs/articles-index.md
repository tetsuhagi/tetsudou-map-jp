# 既存記事インデックス

クロスリンク（兄弟列車・併結列車・関連記事）を書くときに参照する、
公開済み記事の **スラッグ・カテゴリ・1行説明** の一覧。

新規記事を追加したら、ここにも一行追加すること。

---

## 路線詳細（routes/）

### 寝台特急

| スラッグ | パス | タイトル | 1行説明 | 兄弟列車 |
|---|---|---|---|---|
| `sunrise-seto` | `/routes/sunrise-seto` | サンライズ瀬戸（東京〜高松） | JR西日本・JR東海運行の寝台特急。瀬戸大橋を渡って高松まで | sunrise-izumo |
| `sunrise-izumo` | `/routes/sunrise-izumo` | サンライズ出雲（東京〜出雲市） | JR西日本・JR東海運行の寝台特急。伯備線・宍道湖を抜けて出雲大社のお膝元まで | sunrise-seto |

### 新幹線

（準備中）

### 特急

（準備中）

### 私鉄特急

（準備中）

---

## コラム・雑記・旅行記（columns/）

### コラム・考察

| スラッグ | パス | タイトル | 1行説明 | 関連記事 |
|---|---|---|---|---|
| `linear-to-hakata` | `/columns/linear-to-hakata` | リニアは博多まで来るのか？ | リニア中央新幹線の博多延伸の可能性を、歴史と現実の壁から考察 | — |

### 旅行記

（準備中）

---

## ニュース（news/）

### 鉄道ニュース

（準備中）

### 旅行・観光ニュース

（準備中）

---

## クロスリンクの書き方

`<div class="related">` の `<ul>` 先頭に、**共通リンク（路線一覧・About 等）より上** に置く。

```html
<li>
  <a href="/{section}/{related-slug}">{表示名}</a>
  <div class="related__desc">{1行説明}</div>
</li>
```

「兄弟列車」列に挙がっているスラッグ同士は、**両方の記事で相互リンク** を貼る。
片方だけ貼り忘れがちなので、新規記事追加時にもう片方の記事も併せて更新すること。

ニュース記事と関連する路線記事がある場合（例: 新型車両のニュース → その車両の路線詳細）は、
両方向にリンクを張ると読者の回遊性が上がる。

---

## 命名規則の再掲

| 種類 | 命名 | 例 |
|---|---|---|
| 路線スラッグ | 小文字・ハイフン区切り・実列車名ベース | `sunrise-izumo`, `mu-sky`, `romance-car-gse` |
| コラムスラッグ | 小文字・ハイフン区切り・内容を簡潔に表す | `linear-to-hakata`, `sunrise-vs-airline` |
| ニューススラッグ | 小文字・ハイフン区切り・内容を簡潔に表す | `jr-east-2026-summer-campaign`, `mu-sky-renewal-2026` |
| 路線ファイル | `routes/{slug}.html` | `routes/sunrise-izumo.html` |
| コラムファイル | `columns/{slug}.html` | `columns/linear-to-hakata.html` |
| ニュースファイル | `news/{slug}.html` | `news/jr-east-2026-summer-campaign.html` |
| 路線URL | `/routes/{slug}`（拡張子なし） | `/routes/sunrise-izumo` |
| コラムURL | `/columns/{slug}`（拡張子なし） | `/columns/linear-to-hakata` |
| ニュースURL | `/news/{slug}`（拡張子なし） | `/news/jr-east-2026-summer-campaign` |
| サムネ画像 | `assets/og/{slug}.jpg` | `assets/og/sunrise-izumo.jpg` |

---

## 新規記事を依頼するときのプロンプトテンプレ

依頼プロンプトの標準フォーマットは [docs/article-request-template.md](article-request-template.md) を参照。
スレッドが長くなっても抜け漏れなくルールが適用されるよう設計されている。

---

最終更新: 2026-05-21
