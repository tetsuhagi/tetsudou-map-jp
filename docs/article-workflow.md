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
