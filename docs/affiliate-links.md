# アフィリエイトリンク格納・運用ルール

執筆対象記事の **本文** に登録済み案件キーワードが含まれている場合、
このファイルの HTML スニペットを使って **1〜2箇所だけ** 戦略的に置き換える。

---

## 運用ルール

### 配置箇所の選定（1記事につき最大2箇所）

SEO スパム判定の回避と UI/UX 配慮のため、 **同じ案件は 1記事につき 1〜2箇所だけ** に絞る。

#### ✅ 高CTR・配置推奨

- **まとめ・結論セクション** の推奨文
- **「結局どっちを使うべきか」「おすすめは○○」型** の文脈
- 商品・サービスを **初めて本文で紹介する** 箇所（読者が最初に好奇心を持つタイミング）
- **比較表の "おすすめ" 列** の決定的セル（複数ある場合は1つだけ）

#### ❌ 配置NG

- **見出し**（h1〜h6）
- **冒頭の導入文**（読者が記事を理解する前に踏ませない）
- **disclaimer ブロック内**（注意書きの中にリンクを混ぜない）
- **「関連情報・参考リンク」セクション**（プレーンリンク扱い）
- **比較表のすべてのセル**（強調文脈の1箇所のみに絞る）

### 必須属性

すべてのアフィリエイトリンクに以下を含める:

- `rel="nofollow sponsored noopener"` — Google ガイドライン & セキュリティ
- `target="_blank"` — 外部サイトは新規タブで開く

### 開示（ステマ規制対応）

案件のアフィリエイトリンクを含む記事には、**disclaimer 内に必ず明記**:

```
※ 本記事には広告・アフィリエイトリンクが含まれます。
```

消費者庁ステマ規制（2023年10月施行）への対応。漏れると景品表示法違反リスク。

### 提供リンクは一字一句改変禁止（最重要）

各案件の HTML スニペットは **byte-for-byte そのまま** 使う。改変は成果非認証リスク:

- ❌ URL パラメータの追加・削除・順序変更
- ❌ `rel` / `target` / `style` 属性の改変・削除
- ❌ 登録スニペットのアンカー内テキストを**手で書き換える**こと（例: 登録の「楽天トラベル」を勝手に「楽天トラベルで予約」に直す／矢印や語を足す）
- ❌ JavaScript 等での挙動上書き

> ⚠ ただし楽天の **自由テキストリンク** は、文言違いを**別スニペットとして公式生成・登録済み**（下記「CTAボタン用」4種）。
> その中から文脈に合うものを**そのまま選ぶ**のは改変ではなくOK。登録にない文言を使いたい場合は、運営者が楽天ツールで生成して登録してから使う。

### 外側の装飾ラッパーは OK（運用方針 2026-05-22 確定）

`<a>` タグ自体に手を加えない限り、外側を以下のような通常 HTML 要素で囲むのは **許容**:

- `<strong>` / `<em>` / `<span>` 等のインライン装飾
- `<p>` / `<li>` / `<td>` 等のブロック要素
- `<u>`（下線）等のシンプルな装飾

例（OK）:
```html
<strong><a href="..." target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベル</a></strong>
```

例（NG・改変扱い）:
```html
<!-- 登録テキストに勝手に矢印や語を足している -->
<a href="..." ...>楽天トラベルで宿を探す →</a>

<!-- rel / style 属性を削除している -->
<a href="...">楽天トラベル</a>
```

検証推奨: 配置後に `<a>` タグ部分だけ抜き出して、提供原文と SHA-256 一致を確認すると安全。

---

## 案件一覧

### 楽天トラベル

- **提供元**: 楽天アフィリエイト
- **リンク種別**: テキストリンク
- **置換対象テキスト**: 「楽天トラベル」
- **HTML スニペット**:

```html
<a href="https://hb.afl.rakuten.co.jp/hgc/183a3f07.8ee0da3f.183a3f08.48a96798/?pc=https%3A%2F%2Ftravel.rakuten.co.jp&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベル</a>
```

### 楽天トラベル（CTAボタン用）
<a href="https://hb.afl.rakuten.co.jp/hgc/183a3f07.8ee0da3f.183a3f08.48a96798/?pc=https%3A%2F%2Ftravel.rakuten.co.jp&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベルで宿を探す</a>

<a href="https://hb.afl.rakuten.co.jp/hgc/183a3f07.8ee0da3f.183a3f08.48a96798/?pc=https%3A%2F%2Ftravel.rakuten.co.jp&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベルで宿・パックを探す</a>

<a href="https://hb.afl.rakuten.co.jp/hgc/183a3f07.8ee0da3f.183a3f08.48a96798/?pc=https%3A%2F%2Ftravel.rakuten.co.jp&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベルで予約する</a>

<a href="https://hb.afl.rakuten.co.jp/hgc/183a3f07.8ee0da3f.183a3f08.48a96798/?pc=https%3A%2F%2Ftravel.rakuten.co.jp&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベルで料金・空室をチェック</a>

> ※ 上記4本は **URLが全て同一**（楽天の自由テキストリンク）で、アンカー文言だけが異なる正規リンク。文脈で選ぶ。


### じゃらんnet（A8.net）

- **提供元**: A8.net（提携済み）
- **リンク種別**: テキストリンク ＋ **インプレッション計測 img（1×1）必須**
- **アンカーテキスト**: 「じゃらんnet」（A8では**自由文言を選べない**。長い候補もあるが実用は実質これ1択）
- **HTML スニペット**（`<a>` と直後の計測 img を**セットで** byte 一致で貼る）:

```html
<a href="https://px.a8.net/svt/ejp?a8mat=4B5Y0I+5XQQT6+14CS+64JTE" rel="nofollow">じゃらんnet</a><img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4B5Y0I+5XQQT6+14CS+64JTE" alt="">
```

- **重要・A8の仕様**: A8の素材は `rel="nofollow"` のみで、`sponsored` / `noopener` / `target="_blank"` は**付かない**。
  これは楽天（自由テキストリンク）と違い**改変するとA8規約違反＝成果非認証リスク**なので、**付け足さずそのまま**使う。
  `nofollow` がある時点でGoogleの有料リンク開示要件は満たす（`sponsored` は推奨止まり）。同一タブで開く点は許容する。
- **計測 img は必須**: リンク直後に併置しないと成果計測されない。1×1で不可視。
- **アンカーが「じゃらんnet」で短いのは、むしろ2ボタンCTAのボタン文言として最適**（後述）。
- **afiB（サイト審査中）**: 承認後は「ホテル・宿予約サイト「じゃらんnet」」等の**長め文言**が取れる見込み。
  長文言は**ボタンには不向き／本文インラインテキストリンク向き**。承認されたらここに別スニペットとして追記する。
  ボタン用途は短い「じゃらんnet」で完結するため、afiB待ちでCTA導入を止める必要はない。
- **SHA-256**（`<a>` 部分のみ）: `b58a09d169e3dd6acc31e27e7a37f14e93ad654fed0795e4e061215d9bd065ae`

---

#### 楽天CTAボタンの使い方（2026-06-17 追加）

記事下部に「行動喚起ブロック」を1つ置ける。本文インラインのテキストリンクとは別枠で、
**1記事の合計を 本文テキスト1 ＋ CTA1 = 最大2** に収める（3つ目は作らない）。

- **配置**: まとめ直前、または予約・パック・宿に言及したセクションの直後。**ファーストビューには置かない**。
- **テーマ条件**: 旅行・宿泊・移動手段比較・観光地アクセスなど「宿予約と自然につながる」記事のみ。
  路線スペック解説のみ／宿予約と無関係な考察コラム（例: リニア延伸論）には**入れない**（唐突さ＝離脱・無効判定リスク）。
- **文言の選び方**（上の登録4種から1つ。改変せずそのまま使う）:
  - 汎用 → 「楽天トラベルで宿を探す」
  - パック文脈（交通＋宿）→ 「楽天トラベルで宿・パックを探す」
  - 決断地点（まとめ直後）→ 「楽天トラベルで予約する」
  - ハードル低め → 「楽天トラベルで料金・空室をチェック」
- **マークアップ**（`.affiliate-cta` は Thread A 実装の CSS。`<a>` は登録スニペットを byte 一致で）:

```html
<div class="affiliate-cta">
  <p class="affiliate-cta__label">{文脈に合う誘導コピー（例: 新幹線＋宿のセットプランを探すなら）}</p>
  {登録CTAリンクの <a> をそのまま貼る}
  <p class="affiliate-cta__note">※ 広告（アフィリエイトリンク）です</p>
</div>
```

- `disclaimer` 内に開示文「※ 本記事には広告・アフィリエイトリンクが含まれます。」を必ず入れる。
- 設置後は `<a>` 部分を抜き出して登録スニペットと **SHA-256 一致**を確認すると安全。

実例: [columns/shinkansen-vs-airplane-tokyo-osaka.html](../columns/shinkansen-vs-airplane-tokyo-osaka.html)（パック節直後にCTA・本文に1リンクの計2構成）

---

## 2ボタンCTA（楽天＋じゃらん）（2026-06-17 追加）

宿予約の意思決定が濃い記事では、**楽天とじゃらんを横並び**にして「自分の使う方を選んでもらう」動線で取りこぼしを防ぐ。

### 設計の肝（アンカー文言の制約をそのまま活かす）

- **動詞（CTA）は共通ラベルに持たせ、ボタンはブランド名のみにする**。
  - 楽天 → 登録済みの **「楽天トラベル」**（ブランド文言）スニペットを使う（`…で宿を探す` のような動詞版ではなく短いブランド版で揃える）
  - じゃらん → A8の **「じゃらんnet」**（短いのでボタンに最適）
- 文言形が「動詞句 vs ブランド名」でちぐはぐにならず、**短いブランド名2つが綺麗に並ぶ**。
- A8の長文言や afiB の長文言を**ボタンに使わない**（ボタンは短さが正義。長文言はインラインテキストリンク向き）。

### マークアップ（`<a>` は各案件の登録スニペットを byte 一致で）

```html
<div class="affiliate-cta affiliate-cta--duo">
  <p class="affiliate-cta__label">{動詞を含む共通コピー（例: 両方の料金・ポイントを見比べてみる）}</p>
  <a href="…楽天…" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">楽天トラベル</a>
  <a href="…A8じゃらん…" rel="nofollow">じゃらんnet</a><img border="0" width="1" height="1" src="…A8gif…" alt="">
  <p class="affiliate-cta__note">※ 広告（アフィリエイトリンク）です</p>
</div>
```

- **CSS**: 既存の `.affiliate-cta a`（PCは inline-block＝横並び／モバイルは block＝縦積み）で**追加CSSなしでも機能する**。
  ブランド別の色分け（楽天=赤／じゃらん=別色）は `.affiliate-cta--duo` 向けの**任意ポリッシュ＝Thread A 管轄**。色は白文字コントラスト比 4.5:1 以上を満たす濃さで（淡いオレンジは不可）。
- **計数**: 2ボタンで **CTA「1枠」** と数える。本文インラインテキスト1 ＋ CTA枠1 ＝ 最大2 の原則は維持。
- **開示**: 既存の汎用開示「※ 本記事には広告・アフィリエイトリンクが含まれます。」で両案件まとめてカバー。
- **検証**: 設置後、楽天「楽天トラベル」`<a>`＝SHA-256 `7138d6f0ff8b3df01b7d804bd694537cb073f7ebf1441c6aa3e2aa36bb499ab5` ／ じゃらん`<a>`＝`b58a09d1…`（上記）と一致を確認。

実例: [columns/jalan-vs-rakuten-travel.html](../columns/jalan-vs-rakuten-travel.html)（タイプ別ガイドの結論直後に2ボタン）

---

## 配置の意図ティア（記事の検索意図でアフィリ濃度を出し分ける）

アフィリは全記事一律ではなく、**検索意図の濃さに比例**させる。これがアクセス（トピック整合）と収益（意図一致）の両立点。

| 記事の検索意図 | アフィリ配置 |
|---|---|
| 趣味・車両スペック解説（route記事の大半） | 楽天 **1ボタン**（または無し）。唐突な勧誘はしない |
| 旅行計画・アクセス比較・「○○のおすすめ宿」系 | **楽天＋じゃらん 2ボタン**（決断地点 or まとめ直前） |
| 宿予約サイト比較コラム | フル（2ボタン＋本文インライン1の計2） |

---

## YMYL・クレカ系の方針（2026-06-17 確定）

- **クレジットカード等のYMYL案件は新規追加しない**。理由: (1) 金融はページ単位で高E-E-A-Tを要求され鉄道趣味サイトは上位化しない、
  (2) サイトの「鉄道×旅行」トピックを希薄化し本丸記事の順位を巻き添えにしうる（＝唯一の実害経路）、(3) カード発行はCVRが低く文脈ミスマッチ。
- **T&E（旅行予約）に集中**: トピック整合でSEOに安全・意図一致でCVR高・件数で稼ぐ。EV最大。
- **既存の旅行文脈コラムが上限**: [recruit-card-travel](../columns/recruit-card-travel.html) のように「旅行レンズで包んだ」カード記事は許容するが、
  カードレビュー特集への拡張・route記事本文へのカードCTA注入は**しない**。

---

## 案件を追加するときの手順

1. このファイルに新しい `### {案件名}` セクションを追加
2. 提供元・リンク種別・置換対象テキスト・HTML スニペットを記載
3. （あれば）案件固有の配置ノート（例: ニュース記事では使わない、特定カテゴリ専用 等）

---

最終更新: 2026-06-17（じゃらんnet[A8]・楽天＋じゃらん2ボタンCTA・意図ティア・YMYL方針を追加）
