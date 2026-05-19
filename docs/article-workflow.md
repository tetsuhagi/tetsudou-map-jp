# 記事追加ワークフロー

新規記事（路線詳細）を追加するときの **手順チェックリスト**。
このまま上から順にやればOK。

---

## 0. 事前準備

- [ ] `docs/voice-guide.md` を通読した
- [ ] 書く列車のスラッグ（URL用の英語）を決めた
  - 例: `sunrise-izumo` / `nozomi` / `romance-car-gse` など
  - 命名規則: 小文字・ハイフン区切り・実列車名ベース
- [ ] 現在の `content.css` のバージョンを確認した
  - `grep "content.css?v=" routes/sunrise-seto.html` などで確認

---

## 1. 記事ファイルを作成

```bash
cp docs/article-template.html routes/{SLUG}.html
```

開いて以下を順に処理:

- [ ] 冒頭コメントの **プレースホルダ一覧** を見ながら `{{...}}` を全置換
- [ ] `{{CSS_VERSION}}` は **現時点で他HTMLが参照している最新値** に合わせる
  - 例: 他が `?v=97` なら新規記事も `?v=97`
  - 新コンポーネントのために CSS を変更する場合のみ、後でまとめて全ファイルバンプ
- [ ] `<!-- TODO: ... -->` コメントを順に潰しながら本文を執筆
- [ ] **不要な h2 ブロックは丸ごと削除**してOK
  - 例: 寝台特急でない列車では「個室タイプ一覧」セクション削除
  - 例: 併結相手がいない列車では「関連列車との違い」セクション削除
- [ ] **speech--draft クラスの 6 バルーンは触らない**
  - 運営者があとで実コメントを入れる工程（後述）
  - 6個多すぎる場合は 3〜4個に減らしてOK（その場合は前後の文脈に合う位置を残す）

### 執筆時のチェック

- [ ] 記事本体は **ですます調**
- [ ] 数値・時刻は「**頃**」「**おおよそ**」「**目安**」「**{年}{月}時点**」付き
- [ ] 「公式情報をご確認ください」リンクが本文中に最低1つある
- [ ] 商標は事実の参照として登場（公式・official など誤認を誘う語を使わない）

---

## 2. 関連ファイルを更新

### 2-A. `routes/index.html`（路線一覧）

該当カテゴリ（寝台特急 / 新幹線 / 特急 / 私鉄特急 etc.）の `<ul>` に追加:

```html
<li>
  <a href="/routes/{SLUG}">{記事タイトル}</a>
  <div class="related__desc">{1行説明}</div>
</li>
```

カテゴリが存在しない場合は新しい `<h2>` ブロックを追加。

### 2-B. `sitemap.xml`

新しい URL を追加:

```xml
<url>
  <loc>https://tetsudou-map.com/routes/{SLUG}</loc>
  <lastmod>{YYYY-MM-DD}</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

（路線詳細は 0.8 / monthly。トップは 1.0 / weekly、routes/ は 0.9 / weekly が現行値。）

`<lastmod>` は **公開日**。後で本文を更新したらここも更新する。

### 2-C. `_redirects`

`.html` 付き URL → クリーン URL の 301 を追加:

```
/routes/{SLUG}.html /routes/{SLUG} 301
```

### 2-D. `assets/content.css` のバンプ（CSS自体を変更した場合のみ）

content.css のスタイルを修正した場合は:

1. `content.css` の `* v97 → v98` のような **コメント更新は不要**（変更点はGitログでOK）
2. **全コンテンツHTMLの `?v=N` を一斉バンプ**:

```bash
# 例: v97 → v98
cd routes && sed -i '' 's|content.css?v=97|content.css?v=98|g' *.html
cd ..      && sed -i '' 's|content.css?v=97|content.css?v=98|g' \
    about.html contact.html faq.html privacy.html terms.html
```

`grep -r "content.css?v=" --include="*.html"` で取りこぼし確認。

**バンプ不要なケース**:
- 新規記事HTML 追加のみ（CSS未変更）
- 既存記事の本文修正のみ
- speech バルーンの実コメント差し込みのみ

---

## 3. ローカル確認

ブラウザで `routes/{SLUG}.html` を直接開いて:

- [ ] レイアウト崩れがない
- [ ] パンくず・関連リンクが正しい
- [ ] 表が表示されている（CSV 等から流し込みミスがないか）
- [ ] map-cta ボタンから `/` に戻れる
- [ ] バルーンが speech--draft の派手な黄色で表示されている（= プレースホルダのまま）

---

## 4. コミット & プッシュ

```bash
git add routes/{SLUG}.html routes/index.html sitemap.xml _redirects
git commit -m "feat(routes): add {列車名} route detail page

- {主要見どころの要約}
- routes/index.html, sitemap.xml, _redirects 更新

Co-Authored-By: ..."
git push
```

Cloudflare Pages が自動デプロイ → 数分後に `https://tetsudou-map.com/routes/{SLUG}` で確認。

---

## 5. 公開後: スピーチバルーン差し込み（運営者作業）

執筆AIが残した 6 個の `speech speech--draft` バルーンを、運営者が実際に読んでコメントを入れる工程。

1. ブラウザで公開された記事を読む
2. 各バルーンに入れたい一言を考える（voice-guide.md の語感を意識）
3. 各バルーンを以下のように書き換え:

```html
<!-- Before (テンプレ) -->
<div class="speech speech--draft">
  <span class="speech__avatar">🙋‍♂️</span>
  <div class="speech__bubble">← ここに一言（不要なら削除）</div>
</div>

<!-- After (本番) -->
<div class="speech">
  <span class="speech__avatar">🙋‍♂️</span>
  <div class="speech__bubble">実際のコメント本文</div>
</div>
```

ポイント:
- `speech--draft` クラスを削除（黄色の派手スタイルが消えて本番表示に）
- 不要なバルーンは `<div class="speech speech--draft">...</div>` を丸ごと削除

4. コミット & プッシュ:

```bash
git add routes/{SLUG}.html
git commit -m "publish speech bubbles on {列車名}"
git push
```

---

## 6. SEO メンテナンス

- [ ] Google Search Console で **URL 検査 → インデックス登録をリクエスト**（任意・効果は限定的）
- [ ] sitemap.xml を GSC が再取得するのを待つ（数日）
- [ ] 内容を大幅に更新したら `sitemap.xml` の `<lastmod>` を更新

---

## チートシート: ファイル変更の依存関係

| やったこと | 何を更新する？ | content.css バンプ |
|---|---|---|
| 新規記事HTMLを追加 | routes/index.html, sitemap.xml, _redirects | ❌ 不要 |
| 既存記事の本文修正 | （その記事のみ） | ❌ 不要 |
| バルーン公開（draft→本番） | （その記事のみ） | ❌ 不要 |
| content.css の修正 | content.css 自身 + 全 HTML の ?v= | ✅ 必要 |
| 新コンポーネント追加（speech 等） | content.css + 全 HTML の ?v= | ✅ 必要 |

---

## 命名規則メモ

| 種類 | 命名 | 例 |
|---|---|---|
| スラッグ | 小文字・ハイフン区切り | `sunrise-izumo`, `mu-sky`, `romance-car-gse` |
| ファイル名 | `routes/{slug}.html` | `routes/sunrise-izumo.html` |
| URL | `/routes/{slug}` (拡張子なし) | `/routes/sunrise-izumo` |
| カテゴリ | 寝台特急 / 新幹線 / 特急 / 私鉄特急 | （routes/index.html 内の h2） |

---

最終更新: 2026-05-19
