# 記事 TTS ウィジェット 仕様

記事ページ（`<main class="article">` 配下）に音声読み上げ機能を提供する
共通ウィジェット。**Thread A（エンジニアリング）が管理**する。

> 出自: 2026-05-21 までに Thread B（記事スレッド）で実装されたものを
> Thread A 側に「責任移管」した。今後の修正・拡張は本ドキュメントを
> 起点に Thread A で行う。

---

## 1. ファイル構成

| ファイル | 役割 | 行数 |
|---|---|---|
| `assets/tts.js` | ウィジェット本体（IIFE、自己完結）| 約 609 行 |
| `assets/content.css` (322行目〜) | TTS UI のスタイル | 約 100 行 |
| 各記事 HTML の末尾 `<script>` | tts.js の読み込み | 1 行 |

---

## 2. HTML への組み込み

各記事ファイルの `</body>` 直前に以下を入れる：

```html
<script src="/assets/tts.js?v={CSS_VERSION}" defer></script>
```

- `?v={CSS_VERSION}` はキャッシュバスタ。`assets/content.css` のバージョン
  と同じ番号を使うのが慣習（記事系ファイルでまとめてバンプする）
- `defer` 属性必須。DOM がパースされた後に実行される
- script は `<body>` 内末尾でも `<head>` でも動作する（defer なので）

### 組み込み済みファイル（2026-05-21時点）

- `routes/sunrise-seto.html`
- `routes/sunrise-izumo.html`
- `columns/recruit-card-travel.html`
- `columns/jalan-vs-rakuten-travel.html`
- `columns/linear-to-hakata.html`
- `columns/kitakyushu-airport-access.html`
- `docs/article-template.html`（テンプレ）
- `docs/article-template-news.html`（テンプレ）

新しい記事は **テンプレを使えば自動的に組み込まれる**。

---

## 3. 動作モデル

### 3-1. 起動条件

- `main.article` 要素が DOM に存在する場合のみウィジェットを生成
- `speechSynthesis` API 非対応ブラウザでは何もしない（無害にスキップ）

### 3-2. UI 構造

```
┌─────────────────────────────────────────┐
│  右下に固定配置 (position: fixed)        │
│                                          │
│  [折りたたみ時]                          │
│  ┌──────────┐                           │
│  │ 🔊 読み上げ │  ← .tts-widget__fab     │
│  └──────────┘                           │
│                                          │
│  [展開時]                                │
│  ┌──────────────────┐                  │
│  │ ▶ ⏸ ⏹ ⏮ ⏭  [1x ▼] │ ← __panel       │
│  └──────────────────┘                  │
└─────────────────────────────────────────┘
```

### 3-3. 読み上げ範囲（ビルドキューの仕組み）

`buildQueue()` (tts.js 212行) が記事を解析し、読み上げ対象のリストを構築：

- **包含**: `main.article` 配下の `<p>`, `<li>`, `<h2>`, `<h3>`, `.speech__bubble`
- **除外**: 以下の要素は読み飛ばす
  - `.page-meta`（最終更新日とカテゴリ）
  - `.map-cta`（マップ誘導ブロック）
  - `.related`（関連記事リンク）
  - `<h2>関連情報</h2>` 以降の全要素
  - `.disclaimer` 内（注意書きは読まなくてよい設計）

### 3-4. センテンス分割 & ハイライト

- `splitSentences()` (106行): 日本語句点「。」で文を分割
- `wrapTextNodesIntoSentences()` (129行): テキストノードを `<span>` で囲む
- **カラオケスタイル**: 読み上げ中のセンテンスにハイライトクラスを付与、
  完了したら次へ進む
- スクロール追従: `smartScroll()` で読み上げ中のセンテンスを視野中央へ

### 3-5. 声選択

`selectVoices()` (335行) で最適な日本語声を自動選択：

- **本文用**: 女性声優先（Kyoko / O-ren / Haruka / Nanami 等）
- **バルーン (.speech__bubble) 用**: 男性声優先（Otoya / Keita / Ichiro 等）
- 高品質バリアント検出キーワード（22-36行）:
  - `enhanced`（Apple Enhanced）
  - `premium`、`natural`、`neural`、`online`（Microsoft）
  - `wavenet`、`studio`（Google）
- 該当声がない環境では同じ声に fallback

### 3-6. 速度設定

- 0.5x 〜 2.0x の選択肢
- `setRate()` (508行) で `localStorage` に保存
- 次回訪問時にも反映

---

## 4. 主要関数一覧（tts.js）

| 行 | 関数 | 役割 |
|---|---|---|
| 50 | `scoreVoiceQuality(v)` | 高品質キーワードで voice をスコアリング |
| 75 | `hardCancel()` | `speechSynthesis.cancel()` 周辺の安全策 |
| 90 | `waitUntilIdle(cb, maxMs)` | TTS エンジンが idle になるまで待機 |
| 106 | `splitSentences(text)` | 句点で文分割 |
| 129 | `wrapTextNodesIntoSentences(container)` | テキストを `<span>` 化 |
| 212 | `buildQueue()` | 読み上げ対象のキュー構築 |
| 274 | `clearAllHighlights()` | 全ハイライト消去 |
| 282 | `smartScroll(el)` | ビューポート中央へスクロール |
| 320 | `highlightItem(item)` | 現在読み上げ中の要素を強調 |
| 335 | `selectVoices()` | 男女声を選定 |
| 363 | `ensureVoicesLoaded()` | voice 一覧読み込み完了を待つ |
| 385 | `playFromCurrent()` | 現在位置から読み上げ開始 |
| 424 | `play()` | 再生（初回 or 再開）|
| 443 | `pause()` | 一時停止 |
| 450 | `stop()` | 停止して先頭に戻す |
| 461 | `isHeading(el)` | h2/h3 判定 |
| 465 | `jumpTo(pos)` | キュー上の任意位置にジャンプ |
| 480 | `skipNextHeading()` | 次の見出しまでスキップ |
| 492 | `skipPrevHeading()` | 前の見出しまで戻る |
| 508 | `setRate(rate)` | 速度変更 + 保存 |
| 525 | `createUI()` | DOM 構築 + イベントリスナー |
| 590 | `updateUI()` | 再生中/停止中の見た目切り替え |

---

## 5. CSS クラス一覧（content.css 322行〜）

| クラス | 役割 |
|---|---|
| `.tts-widget` | コンテナ（fixed positioning）|
| `.tts-widget__fab` | 折りたたみ時の丸ボタン |
| `.tts-widget__panel` | 展開時のコントロールパネル |
| `.tts-widget__header` | パネル上部 |
| `.tts-widget__title` | パネル見出し |
| `.tts-widget__close` | × ボタン |
| `.tts-widget__controls` | ボタン群コンテナ |
| `.tts-widget__play`、`__pause` | 再生・停止 |
| `.tts-widget__skip` | スキップ系（prev/next）|
| `.tts-widget[data-state="expanded/collapsed"]` | 状態切り替え |

ハイライト用クラス（tts.js 内で動的に付与）:
- `.tts-current` 等（要確認、CSS 側で透明度や背景色変化）

---

## 6. 既知の制約・OS依存問題

| 環境 | 制約 |
|---|---|
| **iOS Safari** | バックグラウンド／画面ロックで再生停止（iOS 仕様、回避不可）|
| **Android Chrome** | Google TTS の有無で音声品質に差 |
| **男女声分け** | voice 一覧に該当声がない環境では fallback で同じ声に統一 |
| **Microsoft Edge (Windows)** | Natural voice は実質 neural で高品質、自動選択される |
| **Firefox** | 一部の neural voice が認識されない場合あり |

---

## 7. キャッシュバスタの運用

- 現在のバージョン: `?v=105`（2026-05-21 時点）
- `assets/content.css` と同じバージョンで揃えるのが原則
- バージョンアップが必要なケース:
  - tts.js の挙動変更
  - content.css の TTS 関連スタイル変更
  - 上記のいずれかと連動して新機能追加
- バージョンアップ手順:
  1. 全記事ファイルの `<script src="/assets/tts.js?v=NEW">` を更新
  2. テンプレ（`docs/article-template*.html`）も更新
  3. 旧バージョンを参照する箇所が残っていないか `grep -n "tts.js?v="` で確認

`bump-version.sh` は現状マップ用（`map.html` / `src/app.js` / `src/data.js`）
のみ対象。**記事系のバンプは別運用**（手動 or 別スクリプト）。
将来 `bump-content-version.sh` のような分離スクリプトを作るのも候補。

---

## 8. 修正・拡張するときの注意

### 8-1. 影響範囲が広い変更

- 全記事 HTML を一括で書き換える必要がある変更は、テンプレートに含まれる
  なら **テンプレ側を直し、既存記事は順次同期**する
- 既存記事を直接いじる場合は `grep -l "tts.js" routes/ columns/` で対象を
  把握してから一括 `sed`

### 8-2. localStorage キーの命名

現在使われているキー（`setRate` 周辺）を把握してからキーを増やすこと。
名前空間衝突を避ける（例: `ttsmap:rate` のようなプレフィックス）。

### 8-3. 除外要素の追加

`buildQueue()` の除外ロジックを修正する場合、影響を受ける記事を確認:
- `.disclaimer`、`.page-meta`、`.map-cta`、`.related` を読まない設計
- 新しい除外クラスを追加するなら、 `assets/content.css` で該当クラスを
  使う記事が複数あるかチェック

---

## 9. 将来の改修候補

- **再生位置の URL ハッシュ同期**: `#tts=p12` のような位置記憶
- **読み上げ完了の analytics 送信**（プライバシー配慮要）
- **ハイライト色のテーマ追従**（ダークモード考慮）
- **テキストブロックのスキップ機能**（読みたくない段落の手動除外）
- **音声品質メーター**: 選択された voice の品質スコアを UI 表示
- **オフラインモード**: Web Speech API なしで音声合成（複雑、未検討）

---

## 10. このドキュメント自身の更新ルール

- tts.js / content.css の TTS セクション / テンプレート HTML に変更を
  入れたら、本ドキュメントの該当箇所を同時更新
- 新しい既知問題が見つかったらセクション 6 に追加
- 改修候補が実装されたらセクション 9 から削除、5/6/7 に反映

---

最終更新: 2026-05-21（初版、Thread A への責任移管時に作成）
