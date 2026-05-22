# 記事追加ワークフロー

新規記事（路線詳細／旅行記／雑記）を追加するときの **手順チェックリスト**。
このまま上から順にやればOK。

---

## 1. データの扱い（最重要）

### 時刻・ダイヤ情報

**記事に具体的な発着時刻（21:26 / 翌 0:37 など）を書かない**。
ダイヤ改正・季節臨時で変わるため、最新性が担保できず誤情報のリスクがある。
読者に対して誠実であるために、最新の時刻は公式時刻表へリンクで誘導する。

代わりに記事に書くもの:

- **運行頻度**: 「毎日1往復」「1時間に1〜2本」「平日19本／休日15本」など
- **大まかな時間帯**: 「夜21時台発・翌朝10時前後着」「朝発の昼着」など
- **片道所要時間の目安**: 「約12時間半」「約2時間」など
- **公式時刻表へのリンク**: 「最新の時刻は ... でご確認ください」を必ず添える

#### 公式リンク先の選び方

| 系統 | 第一選択リンク |
|---|---|
| JR共同運行（在来線・寝台特急） | [JR西日本「JRおでかけネット」](https://www.jr-odekake.net/) |
| JR東日本（特急・新幹線） | [えきねっと](https://www.eki-net.com/) または JR東日本公式 |
| JR東海（東海道新幹線・特急） | [JR東海公式](https://railway.jr-central.co.jp/) |
| 私鉄 | 各社の列車紹介ページ |

`data/timetables/{ROUTE_ID}/` の CSV は **マップ表示の概略データ** で、記事に転記してはいけない。

### 停車駅リスト

- 時刻なしの **矢印チェーン** で記載: 「東京 → 横浜 → ... → 出雲市」
- 「主な停車駅」と書いて、全駅ではないことを明示
- 上下で停車駅が異なる列車は、下り／上りを分けて書く
- 切り離し・併結・伯備線進入など特徴的な区間は 1〜2文の補足を添える

### 料金情報

- 具体的金額は明記せず、「乗車券＋特急券＋B寝台個室料金」のような構成で書く
- 「時期により変動」「購入時にご確認ください」と必ず添える

### 観光・所要時間

- 「徒歩約25分」「バスで約30分」など、根拠のある目安に留める
- バス・接続交通は廃止・改変が多いので「2026年X月時点」を必ず明示

### 1.5 参照 URL の扱い（ニュース系で特に重要）

執筆依頼プロンプトに **参照URL** が含まれていたら、WebFetch でページを取得して記事素材にする。
ただし以下を厳守:

- **コピペ厳禁**: 元記事の文章をそのまま転載しない。要約・解釈・自分の言葉での再構成のみ
- **出典明示**: 本文中に「{社名/サイト名} の発表によると」「{ポータルサイト} の報道によると」と明記する
- **元リンク掲載**: 「出典・関連情報」セクションに元 URL を必ず置く
- **PR単独はバイアス注意**: 鉄道会社 PR は前向きな話に偏るので、PR 1本だけで書く場合は
  「{社名} の発表によると」と限定的に書き、断定表現を避ける
- **複数情報源があれば中立に**: 主張のズレを把握し、片方だけを採用しない
- **公開日明示**: ニュースは公開日（YYYY-MM-DD）を `page-meta` と `disclaimer` に必ず記載

### 1.8 アフィリエイトリンクの扱い

執筆対象記事の **本文** に、`docs/affiliate-links.md` 登録済みの案件キーワード
（例:「楽天トラベル」「リクルートカード」等）が含まれる場合、戦略的に **1〜2箇所だけ**
アフィリエイトリンクで置き換える。**3箇所以上はスパム判定リスクのため絶対NG**。

詳細ルールは `docs/affiliate-links.md` 参照。要点だけ抜粋:

- ✅ 配置推奨: まとめ・結論文・最初の主要言及・比較表「おすすめ」セルの決定的1箇所
- ❌ 配置NG: 見出し・導入文・disclaimer内・関連情報セクション・比較表の全セル
- 必須属性: `rel="nofollow sponsored noopener"` + `target="_blank"`
- **必須開示**: 案件リンクを含む記事は disclaimer 内に
  「※ 本記事には広告・アフィリエイトリンクが含まれます」を必ず明記
  （消費者庁ステマ規制 2023年10月施行への対応）

---

### 1.7 TTS（音声読み上げ）ウィジェット

記事ページ右下に折りたたみ式の音声読み上げボタンが自動表示される（`assets/tts.js`）。
新規記事執筆時に **特別な作業は不要**：テンプレ（`article-template.html` / `article-template-news.html`）に
script タグが組み込み済みのため、テンプレからコピーすれば自動的にウィジェットが表示される。

ウィジェット仕様:
- 本文 → 日本語女性声 / `.speech` バルーン → 日本語男性声 を可能な限り自動選択
- 再生 / 一時停止 / 停止 / 次のセクションへスキップ
- 速度 0.5〜2x（`localStorage` 永続化）
- 読み上げ中の段落／バルーンをハイライト＋スクロール追従
- 除外: `.page-meta` / `.map-cta` / `.related` / 「関連情報・参考リンク」h2以降

OS依存の制約:
- iOS Safari: バックグラウンド・画面ロックで再生停止（iOS 仕様）
- 男女声の区別は voice 一覧の有無依存（該当声がない環境では fallback で同じ声）

### 1.6 サムネイル画像の扱い（2026年5月 現在: 非表示方針）

> **現行方針（2026-05-21〜）**: AI生成サムネ画像が「AI製感」で逆にユーザーを遠ざける懸念があるため、
> サムネイル表示はサイト全体で **オフ** にしている。記事はテキスト中心で勝負する。
> CSSクラス（`.article-hero` / `.article-card__image`）と `assets/og/*.jpg` のファイルは
> 将来の再有効化に備えて保持しているが、HTML 上では参照しない。

**現在のルール（サムネを記事に表示しない）:**

新規記事執筆時、執筆依頼の `サムネイル画像:` 欄に何が書かれていても **以下を含めない**:

- `<meta property="og:image">` / `<meta name="twitter:image">` の OGP 画像 meta タグ
- JSON-LD の `"image"` フィールド
- 記事本文冒頭の `<figure class="article-hero">...</figure>` ブロック
- TOP（`index.html`）の `.article-card` 内の `<div class="article-card__image">` 部分

代わりに:
- `twitter:card` は `summary` を使用（large_image でなく）
- TOP の `.article-card` はテキストのみ（カテゴリバッジ＋タイトル＋説明文）で構成

**将来サムネ表示を再開する場合の手順（参考・現在は休眠）:**

サムネが指定されたら以下を自動実行する想定だった処理:

1. リポジトリルートから当該ファイルを探す
2. `sips` で 1200px 幅・JPEG q75 に圧縮:
   ```bash
   sips --resampleWidth 1200 {input} --out assets/og/{slug}.jpg \
     -s format jpeg -s formatOptions 75
   ```
3. `og:image` / `twitter:image` / JSON-LD `image` に `https://tetsudou-map.com/assets/og/{slug}.jpg` を設定
4. `twitter:card` を `summary_large_image` に変更
5. 記事本文冒頭に `<figure class="article-hero">` を追加（`height` は実画像比率で CLS 対策）
6. TOP の該当 `.article-card` に `<div class="article-card__image">` を再追加

再開する際は、本セクションを「現行方針」として書き換える。

---

## 0. 事前準備

- [ ] `docs/voice-guide.md` を通読した
- [ ] `docs/articles-index.md` で既存記事のスラッグ・カテゴリを確認した（クロスリンクの判断材料）
- [ ] 書く列車のスラッグ（URL用の英語）を決めた
  - 例: `sunrise-izumo` / `nozomi` / `romance-car-gse` など
  - 命名規則: 小文字・ハイフン区切り・実列車名ベース
- [ ] 現在の `content.css` のバージョンを確認した
  - `grep "content.css?v=" routes/sunrise-seto.html` などで確認

---

## 1. 記事ファイルを作成

### カテゴリ別の配置先

| 記事タイプ | コピー元 | 配置先 |
|---|---|---|
| 路線詳細（列車別ガイド） | `docs/article-template.html` | `routes/{slug}.html` |
| コラム・雑記・旅行記 | `docs/article-template.html` | `columns/{slug}.html` |
| ニュース | `docs/article-template-news.html` | `news/{slug}.html` |

```bash
# 路線詳細の場合
cp docs/article-template.html routes/{SLUG}.html
# コラム・雑記・旅行記の場合（テンプレは routes と共通。breadcrumb・canonical を /columns/ に修正）
cp docs/article-template.html columns/{SLUG}.html
# ニュースの場合
cp docs/article-template-news.html news/{SLUG}.html
```

**コラム・雑記・旅行記の特記**:
- ファイルパスは `columns/{slug}.html`、URL は `/columns/{slug}`
- breadcrumb のパンくず 2 階層目は「コラム」（`/columns/`）に変更する（路線詳細用テンプレは「路線一覧」になっているので修正必須）
- JSON-LD `BreadcrumbList` の position 2 も同様に修正

開いて以下を順に処理:

- [ ] 冒頭コメントの **プレースホルダ一覧** を見ながら `{{...}}` を全置換
- [ ] `{{CSS_VERSION}}` は **現時点で他HTMLが参照している最新値** に合わせる
  - 例: 他が `?v=97` なら新規記事も `?v=97`
  - 新コンポーネントのために CSS を変更する場合のみ、後でまとめて全ファイルバンプ
- [ ] `<!-- TODO: ... -->` コメントを順に潰しながら本文を執筆
- [ ] **不要な h2 ブロックは丸ごと削除**してOK
  - 例: 寝台特急でない列車では「個室タイプ一覧」セクション削除
  - 例: 併結相手がいない列車では「関連列車との違い」セクション削除
  - 例: ニュース記事で背景・経緯が不要なら h2 ごと削除
- [ ] **speech--draft クラスのバルーンは触らない**
  - 運営者があとで実コメントを入れる工程（後述）
  - 路線詳細は標準 6個、ニュースは標準 3〜4個
  - 多すぎる場合は減らしてOK（その場合は前後の文脈に合う位置を残す）

### 執筆時のチェック

- [ ] 記事本体は **ですます調**
- [ ] 数値・時刻は「**頃**」「**おおよそ**」「**目安**」「**{年}{月}時点**」付き
- [ ] 「公式情報をご確認ください」リンクが本文中に最低1つある
- [ ] 商標は事実の参照として登場（公式・official など誤認を誘う語を使わない）

---

## 2. 関連ファイルを更新

### 2-A. インデックスページ（カテゴリ別）

**路線詳細記事の場合**: `routes/index.html` の該当カテゴリ（寝台特急 / 新幹線 / 特急 / 私鉄特急 etc.）の `<ul>` に追加:

```html
<li>
  <a href="/routes/{SLUG}">{記事タイトル}</a>
  <div class="related__desc">{1行説明}</div>
</li>
```

**コラム・雑記・旅行記の場合**: `columns/index.html` の該当カテゴリ（コラム・考察 / 旅行記）に追加。

**ニュース記事の場合**: `news/index.html` の該当カテゴリ（鉄道ニュース / 旅行・観光ニュース）に追加。
ニュースは **公開日が新しいものを上** に並べる（時系列降順）。

**新TOP（/）の最新記事グリッドも更新**: `index.html` の該当カテゴリの `.article-grid` 内に
新しい `<article class="article-card">` を追加（thumbnail 必須・最新を先頭に）。

カテゴリが存在しない場合は新しい `<h2>` ブロックを追加。

### 2-B. `sitemap.xml`

新しい URL を追加（記事タイプで loc と priority が変わる）:

```xml
<!-- 路線詳細 -->
<url>
  <loc>https://tetsudou-map.com/routes/{SLUG}</loc>
  <lastmod>{YYYY-MM-DD}</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>

<!-- コラム・雑記・旅行記 -->
<url>
  <loc>https://tetsudou-map.com/columns/{SLUG}</loc>
  <lastmod>{YYYY-MM-DD}</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>

<!-- ニュース -->
<url>
  <loc>https://tetsudou-map.com/news/{SLUG}</loc>
  <lastmod>{YYYY-MM-DD}</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.7</priority>
</url>
```

現行の priority / changefreq 値:
- トップ `/`: 1.0 / weekly
- 走行マップ `/map`: 0.9 / weekly（※ sitemap 未登録なら追加検討）
- `/routes/`: 0.9 / weekly
- `/columns/`: 0.9 / weekly
- `/news/`: 0.9 / weekly
- 路線詳細個別記事: 0.8 / monthly
- コラム個別記事: 0.8 / monthly
- ニュース個別記事: 0.7 / monthly

`<lastmod>` は **公開日**。後で本文を更新したらここも更新する。

### 2-C. `_redirects`

`.html` 付き URL → クリーン URL の 301 を追加（記事タイプで配置先が変わる）:

```
# 路線詳細
/routes/{SLUG}.html  /routes/{SLUG}  301
# コラム・雑記・旅行記
/columns/{SLUG}.html /columns/{SLUG} 301
# ニュース
/news/{SLUG}.html    /news/{SLUG}    301
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

`file://` で直接 HTML を開くと `/assets/content.css` のパスが解決できず、装飾が消えて見づらい。
**必ず HTTP サーバー経由で確認すること**。

```bash
# リポジトリのルートで:
python3 -m http.server 8765
# → http://localhost:8765/routes/{SLUG} で確認
```

（`.claude/launch.json` に同じ設定が入っているので、Claude Code 内では `preview_start` で起動可。
 Claude Code 外でも上記コマンドで OK。）

確認項目:

- [ ] レイアウト崩れがない（CSS が当たっている）
- [ ] パンくず・関連リンクが正しい
- [ ] 表が表示されている（時刻データの流し込みミスがないか）
- [ ] map-cta ボタンから `/` に戻れる
- [ ] バルーンが speech--draft の派手な黄色で表示されている（= プレースホルダのまま）
- [ ] バルーン本文が `← ここに一言（不要なら削除）` のままになっている（= 執筆AIが誤って埋めていない）

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
| 新規路線詳細HTMLを追加 | routes/index.html, sitemap.xml, _redirects, articles-index.md, index.html (TOP grid) | ❌ 不要 |
| 新規コラムHTMLを追加 | columns/index.html, sitemap.xml, _redirects, articles-index.md, index.html (TOP grid) | ❌ 不要 |
| 新規ニュースHTMLを追加 | news/index.html, sitemap.xml, _redirects, articles-index.md, index.html (TOP grid) | ❌ 不要 |
| サムネ画像の追加 | assets/og/{slug}.jpg, 該当HTML の og:image系 + article-hero + TOPの article-card | ❌ 不要 |
| 既存記事の本文修正 | （その記事のみ） | ❌ 不要 |
| バルーン公開（draft→本番） | （その記事のみ） | ❌ 不要 |
| content.css の修正 | content.css 自身 + 全 HTML の ?v= | ✅ 必要 |
| 新コンポーネント追加（speech 等） | content.css + 全 HTML の ?v= | ✅ 必要 |

---

## 命名規則メモ

| 種類 | 命名 | 例 |
|---|---|---|
| スラッグ（路線） | 小文字・ハイフン区切り・実列車名ベース | `sunrise-izumo`, `mu-sky`, `romance-car-gse` |
| スラッグ（コラム） | 小文字・ハイフン区切り・内容を簡潔に表す | `linear-to-hakata`, `sunrise-vs-airline` |
| スラッグ（ニュース） | 小文字・ハイフン区切り・内容を簡潔に表す | `jr-east-2026-summer-campaign`, `mu-sky-renewal-2026` |
| ファイル名（路線） | `routes/{slug}.html` | `routes/sunrise-izumo.html` |
| ファイル名（コラム） | `columns/{slug}.html` | `columns/linear-to-hakata.html` |
| ファイル名（ニュース） | `news/{slug}.html` | `news/jr-east-2026-summer-campaign.html` |
| URL（路線） | `/routes/{slug}` (拡張子なし) | `/routes/sunrise-izumo` |
| URL（コラム） | `/columns/{slug}` (拡張子なし) | `/columns/linear-to-hakata` |
| URL（ニュース） | `/news/{slug}` (拡張子なし) | `/news/jr-east-2026-summer-campaign` |
| 路線カテゴリ | 寝台特急 / 新幹線 / 特急 / 私鉄特急 | （routes/index.html 内の h2） |
| コラムカテゴリ | コラム・考察 / 旅行記 | （columns/index.html 内の h2） |
| ニュースカテゴリ | 鉄道ニュース / 旅行・観光ニュース | （news/index.html 内の h2） |
| サムネ画像 | `assets/og/{slug}.jpg`（1200px幅・JPEG q75） | `assets/og/sunrise-izumo.jpg` |

---

最終更新: 2026-05-19
