# スレッド分担ガイド (Thread Responsibilities)

複数の Claude / Gemini スレッドで本リポジトリを運用するための **分担ルール**
と **情報同期メカニズム** を定義する。新しいスレッドで作業を始める AI は
**必ず冒頭でこのドキュメントを読むこと**。

---

## 0. なぜ分担が必要か

- **コンテキストスイッチコスト**: 記事執筆（文章クラフト）と JS/CSS デバッグ
  （構造思考）は頭の使い方が違う。同じスレッドで混ぜると両方のキャッシュが
  薄まり、品質が落ちる。
- **規約のドリフト防止**: 命名・キャッシュバスタ・コミット規約などが、片方
  で一貫していると変な分岐が起きにくい。
- **デバッグ時の責任所在**: 「TTS が動かない」「列車が消えた」となったとき、
  該当 commit history が1スレッドにまとまっていると追跡しやすい。

---

## 1. スレッド構成（2スレッド体制）

### Thread A: Engineering（このリポジトリでのデフォルト）

**愛称**: 「コードスレッド」「Engineering」

**担当範囲**:
- マップ機能全般（`map.html`, `src/`）
- 路線データ全般（`data/routes.csv`, `stations.csv`, `geometry/`, `timetables/`）
- Python ビルドスクリプト（`scripts/`）
- 共通 CSS（`assets/content.css`）
- 共通 JS ウィジェット（`assets/tts.js` 等）
- 共通画像アセット（`assets/icons/`, `assets/og/`）
- 記事テンプレートの **構造**（`docs/article-template*.html` のタグ・属性）
- サイト共通要素（header / footer / nav）
- インフラ設定（`_redirects`, `_headers`, `sitemap.xml` の構造）
- 駅命名規則（`docs/station-naming.md`）
- スレッド分担（このドキュメント）

### Thread B: Content（記事執筆スレッド）

**愛称**: 「記事スレッド」「Content」

**担当範囲**:
- 記事本文の文章執筆（`routes/*.html`, `columns/*.html`, `news/*.html`
  の `<p>...prose...</p>` 内テキスト）
- 記事の SEO 個別情報（title, description, keywords を **per-article**
  で埋める作業）
- 新規記事の追加（`sitemap.xml` への URL 追加、`docs/articles-index.md`
  更新）
- スピーチバルーンの **位置・個数の判断**（バルーン本文は運営者が後で
  挿入なので執筆AIは触らない）
- 声・トーン規約（`docs/voice-guide.md`）
- 記事追加ワークフロー（`docs/article-workflow.md`）

---

## 2. 担当範囲マトリクス

| ファイル / 領域 | Thread A | Thread B |
|---|:-:|:-:|
| `map.html` | ✅ | ❌ |
| `index.html`（サイトトップ）| 🟡 構造 | 🟡 hero copy・記事リスト |
| `routes/*.html`（記事ファイル全体）| 🟡 テンプレ部分 | 🟡 prose 部分 |
| `columns/*.html`、`news/*.html` | 🟡 テンプレ部分 | 🟡 prose 部分 |
| `src/app.js`、`src/data.js`、`src/train.js` | ✅ | ❌ |
| `assets/content.css` | ✅ | ❌ |
| `assets/tts.js`、他共通ウィジェット | ✅ | ❌ |
| `assets/icons/` | ✅ | ❌ |
| `assets/og/`（サムネ生成物 PNG）| 🟡 スクリプト・既存分 | 🟡 新記事分の生成・出力は許可 |
| `data/routes.csv`、`stations.csv` | ✅ | ❌ |
| `data/geometry/*.json`、`data/timetables/*` | ✅ | ❌ |
| `scripts/*.py`、`scripts/*.sh` | ✅ | ❌ |
| `_redirects`、`_headers` | ✅ | ❌ |
| `sitemap.xml`（構造変更）| ✅ | ❌ |
| `sitemap.xml`（新記事URL追加）| ❌ | ✅ |
| `docs/station-naming.md` | ✅ | ❌ |
| `docs/THREAD-RESPONSIBILITIES.md` | ✅ | ❌ |
| `docs/widgets-*.md`（ウィジェット仕様）| ✅ | ❌ |
| `docs/voice-guide.md` | ❌ | ✅ |
| `docs/article-workflow.md` | ❌ | ✅ |
| `docs/article-template*.html`（テンプレ構造）| ✅ | ❌ |
| `docs/articles-index.md` | ❌ | ✅ |

凡例:
- ✅: 完全担当
- ❌: 触らない
- 🟡: ファイル内で領域分け（後述）

`assets/og/` の補足（2026-06 サムネ方針転換）:
`scripts/gen_thumbnail.py`（Thread A 実装・保守）によるテキストサムネ PNG の
**生成・出力は Thread B（Routine）の運用として許可**する。Thread B は新記事の
公開フローで `python3 scripts/gen_thumbnail.py --line1 .. --line2 .. --out
assets/og/{slug}.png` を実行し、生成された PNG をコミットしてよい
（ルール: docs/autonomous-publishing.md §3.5）。スクリプト本体・フォント
（`assets/fonts/`）・既存画像の整理は引き続き Thread A 担当。

---

## 3. 境界ルール（覚えやすい一行）

迷ったときの判断基準：

1. **触ったファイルが `src/` / `scripts/` / `assets/` 配下 / 拡張子 `.css`
   / `.py`** → **Thread A**
2. **触った内容が、HTML の `<p>`, `<li>`, `<h2>`〜`<h3>` の "見える日本語
   文章" だけ** → **Thread B**
3. **HTML の構造要素**（タグ・属性・id・class・script・link）を触ったら
   → **Thread A**
4. **記事の prose を生成・修正する** → **Thread B**
5. **どこにも当てはまらない、または両方にまたがる** → **Thread A**（コード
   集約原則）

### 同じファイル内での領域分け（🟡 ケース）

例: `routes/sunrise-seto.html` を編集する場合

| 編集対象 | 担当 |
|---|---|
| `<title>`, `<meta>` タグの値 | Thread B（記事の SEO 情報） |
| `<head>` 内 `<script>` の追加・URL バンプ | Thread A |
| `<h2>...</h2>` の見出しテキスト | Thread B |
| `<h2>` を `<h3>` に変える等のタグ変更 | Thread A |
| `<p>記事本文...</p>` の中身 | Thread B |
| `<div class="speech speech--draft">` ブロックの位置・個数 | Thread B |
| `<div class="speech">` 内の `__bubble` 本文（draft 解除後）| **運営者**（人間） |
| `class="speech"` の class 名変更や CSS 構造 | Thread A |

---

## 4. コミットメッセージ規約

担当スレッドが一目でわかるプレフィックスを使う。

### Thread A の使うプレフィックス

| プレフィックス | 用途 | 例 |
|---|---|---|
| `feat(map):` | マップ機能の追加 | `feat(map): add ミュースカイ route` |
| `fix(map):` | マップ機能の修正 | `fix(map): correct station coords` |
| `feat(widget):` | 共通ウィジェット追加 | `feat(widget): add TTS playback rate slider` |
| `fix(widget):` | 共通ウィジェット修正 | `fix(widget): tts overlap on mobile` |
| `feat(infra):` | ビルド・CI・スクリプト | `feat(infra): add bump-version.sh` |
| `chore(infra):` | インフラ雑務 | `chore(infra): adapt bump to new layout` |
| `chore(deps):` | ライブラリ更新 | — |
| `docs(infra):` | エンジニアリング系ドキュメント | `docs(infra): add THREAD-RESPONSIBILITIES.md` |

### Thread B の使うプレフィックス

| プレフィックス | 用途 | 例 |
|---|---|---|
| `feat(content):` | 新規記事追加 | `feat(content): add サンライズ出雲 article` |
| `fix(content):` | 記事の修正 | `fix(content): typo in 4-bubble` |
| `chore(content):` | sitemap / articles-index 等の更新 | `chore(content): add new article to sitemap` |
| `docs(content):` | 記事系ドキュメント更新 | `docs(content): update voice-guide` |

`git log --oneline -20` でスキャンするだけで、各スレッドが何をしたか
わかる状態を維持する。

---

## 5. 情報同期メカニズム（3点セット）

### 5-1. Git が単一の真実 (Single Source of Truth)

- 両スレッドとも **作業開始時に `git pull`**
- **1単位の作業が終わったら即 `git push`**（プッシュせず長く保留しない）
- 「あちらで何が起きたか」は `git log --oneline -20` で常に把握可能

### 5-2. `docs/` フォルダが共有知識ベース

| ドキュメント | 目的 | 担当 |
|---|---|---|
| `THREAD-RESPONSIBILITIES.md`（本文書）| 分担定義 | A |
| `voice-guide.md` | 記事の声・トーン | B |
| `article-template.html`、`article-template-news.html` | 記事スケルトン | A 構造 / B 内容 |
| `article-workflow.md` | 記事追加チェックリスト | B |
| `station-naming.md` | 駅命名規則 | A |
| `articles-index.md` | 既存記事一覧 | B |
| `widgets-tts.md` | TTSウィジェット仕様 | A |

新しいスレッドを開いた AI は、自分の担当に関する `docs/` をまず読む。

### 5-3. クロススレッド通知プロトコル

片方の変更がもう片方に影響する場合、**コミットメッセージに明示**:

```
feat(widget): add prev-section button to TTS

Note for Thread B (content):
  記事HTMLに既存の <button class="tts-widget__skip"> が増えました。
  新規記事もテンプレートに従えば自動で対応されます。特別な対応不要。
```

```
chore(content): add 北海道新幹線 article

Note for Thread A (engineering):
  /routes/hokkaido-shinkansen.html 新規追加。
  sitemap.xml も更新済み。content.css のバージョン操作は不要。
```

---

## 6. AI Agent 向け Cold Start ガイド

新しいスレッドで作業を始める AI は、以下の順で読む：

### Thread A（コードスレッド）として起動した場合

1. **本ドキュメント（THREAD-RESPONSIBILITIES.md）** — 担当範囲確認
2. **`docs/station-naming.md`** — 駅命名規則
3. **必要に応じて `docs/widgets-*.md`** — 該当ウィジェットを触る場合
4. **`scripts/build_geometry.py` の docstring** — ジオメトリ生成パイプライン
5. **`src/data.js`** — マップのデータロードの仕組み

### Thread B（記事スレッド）として起動した場合

1. **本ドキュメント** — 担当範囲確認
2. **`docs/voice-guide.md`** — 声・トーン規約（必読）
3. **`docs/article-workflow.md`** — 記事追加チェックリスト
4. **`docs/article-template.html`** — テンプレ構造の把握
5. **`docs/articles-index.md`** — 既存記事のスラッグ一覧（クロスリンク用）

---

## 7. グレーゾーンと例外

### 7-1. 「コード触らないと記事が完成しない」場合

例: 新しい記事カテゴリ（`/trips/` とか）を作りたい

→ **Thread A に依頼**してインフラ整備（テンプレ、CSS、ナビゲーション、
sitemap 構造）を済ませてから、**Thread B が prose を埋める** 流れにする。

### 7-2. 「記事固有のウィジェット」が欲しくなった場合

例: 「この記事だけ FAQ アコーディオンが欲しい」

→ **Thread A に依頼**してアコーディオン共通ウィジェットを実装し、CSS と
JS を `assets/` に置く。`docs/widgets-accordion.md` を作って仕様化。
→ その後 **Thread B が記事に組み込む**（HTML タグだけ追加、JS は読み込み済み）

### 7-3. URGENT な記事修正（typo 等）

→ **Thread B が直接 prose を直す**。Thread A の介入不要。

### 7-4. URGENT なバグ修正（マップ動かない等）

→ **Thread A が直接 src/ を直す**。Thread B の介入不要。

---

## 8. 過去の事例（学び）

### 2026-05-21: TTS ウィジェットが Thread B で実装された

- 経緯: 記事執筆スレッド（B）で TTS ウィジェットを実装してしまった
- 影響: assets/tts.js（609行）と content.css に TTS スタイルが追加。
  各記事 HTML に `<script src="/assets/tts.js?v=105" defer>` が追加された
- 整理: Thread A が `docs/widgets-tts.md` で仕様を吸収。今後の修正・拡張
  は Thread A が担当
- 教訓: 「記事執筆 = 文章だけ」 に絞らないと、結局 Thread A の負債になる

### 2026-05-21: index.html のサイト構成変更

- 経緯: マップトップ（旧 `index.html`）を記事 hub にリネーム、マップは
  `map.html` に分離
- 副作用: `bump-version.sh` が `index.html` を見ていたので動作しなくなった
- 対応: Thread A が `bump-version.sh` を `map.html` 参照に修正
- 教訓: HTML ファイル構成を変えるときは `scripts/` も合わせて更新する。
  影響範囲が広い場合は本ドキュメントの **担当マトリクス** を再確認

---

## 9. このドキュメント自身の更新ルール

- 担当範囲が増減したら表を更新（コミット: `docs(infra):` プレフィックス）
- 新しいスレッドが追加されたら（例: 「画像生成スレッド」など）、セクション
  1 / 2 / 4 を拡張
- グレーゾーン事例が増えたらセクション 7 / 8 に追記

---

最終更新: 2026-05-21（初版作成）
