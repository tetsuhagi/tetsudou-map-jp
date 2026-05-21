# 記事執筆依頼プロンプトテンプレ

新規記事を依頼するときに使う、コピペ用の **標準プロンプト** 。
スレッドが長くなってコンテキストが圧縮されても、必要な情報を毎回 fresh に取得できるよう
docs 再読を強制し、重要ルールを inline で再掲する設計。

---

## 標準版（コピペ用）

```text
【鉄道マップ全国版 記事執筆依頼】

# 入力（空欄は適切に判断してOK）
記事タイプ:           ※ ニュース / 路線詳細 / 旅行記 / 雑記
タイトル案:
slug:
カテゴリ:             ※ 寝台特急 / 新幹線 / 特急 / 私鉄特急 / 鉄道ニュース / 旅行・観光ニュース など
公開日:               ※ ニュースは必須（未指定なら今日の日付）
運行区間:             ※ 路線詳細時のみ
サムネイル画像:        ※ リポジトリルートのファイル名（例: samune-foo.png）。指定があれば自動圧縮して assets/og/{slug}.jpg に配置
備考:                  ※ 兄弟記事・記事の角度・特記事項など

# 参照URL（ニュース系は必須・他カテゴリでも参考資料があれば）
主情報源（PR/公式発表）:
  -
追加情報源（中立報道・関連解説）:
  -
  -

# 着手前プロセス（スレッドが長くても毎回守ること）
1. 以下5ファイルを必ず再読:
   - docs/voice-guide.md
   - docs/article-workflow.md
   - docs/article-template.html      ※ 路線詳細・旅行記・雑記
   - docs/article-template-news.html ※ ニュース
   - docs/articles-index.md
2. 参照URLがあれば WebFetch で内容を取得し、要約・整理してから執筆
3. 既存の本番記事を語感サンプルとして確認:
   routes/sunrise-seto.html / routes/sunrise-izumo.html

# 違反NGの重要ルール
- speech--draft の本文は絶対に埋めない（運営者作業）
- 具体時刻（XX:XX）は書かない。頻度＋公式時刻表リンクで誘導
- data/timetables の CSV は参考扱い、記事に転記しない
- 参照URLの文章はコピペ禁止、要約・解釈のみ。出典は本文中に明示し、本文末に元リンクを置く
- ニュースは公開日を冒頭 page-meta と disclaimer に明記
- 既存記事との相互リンクは docs/articles-index.md を見て両方向に張る

# 完了時の更新セット
- 路線詳細: routes/{slug}.html / routes/index.html / sitemap.xml / _redirects / docs/articles-index.md
- ニュース: news/{slug}.html / news/index.html / sitemap.xml / _redirects / docs/articles-index.md
- サムネ: assets/og/{slug}.jpg（指定があれば）+ HTML の og:image系設定
```

---

## 簡略版（短いスレッド・継続作業向け）

```text
鉄道マップ: 「{タイトル/列車名}」を {slug} で記事化（{記事タイプ}）。
docs/voice-guide.md / article-workflow.md / article-template{-news}.html / articles-index.md を必ず再読してから着手。
speech--draft の本文は触らない。時刻は具体値NG・頻度＋公式リンクで。
参照URL: {URLがあれば}
サムネ: {ファイル名があれば}
```

---

## 入力欄が空欄だったときの判断ルール

| 欄 | 空欄時の判断 |
|---|---|
| 記事タイプ | タイトル・URL・備考から推測（ニュース性なら ニュース、列車名主体なら 路線詳細） |
| タイトル案 | 主題から「{主題} | {ニュース要点 or 完全ガイド}」型で生成 |
| slug | タイトルから kebab-case で生成。articles-index.md と重複しないこと |
| カテゴリ | 記事タイプから自動マッピング（路線詳細 → 寝台特急/新幹線/etc、ニュース → 鉄道/旅行・観光） |
| 公開日 | 今日の日付（YYYY-MM-DD） |
| 運行区間 | 路線詳細時に空欄なら、参照URL or 一般知識から記載 |
| サムネイル画像 | 指定なし → og:image 系タグを記事から削除して書く（あとで追加可能） |
| 備考 | 特記なしとして進める |
| 参照URL | ニュース系で空欄 → 「参照URLが必要」と確認を求める／路線詳細では空欄でOK |

---

## サムネイル画像の処理（指定があった場合）

`サムネイル画像:` 欄に `samune-foo.png` のようなファイル名が指定された場合、執筆と同時に以下を自動実行:

```bash
sips --resampleWidth 1200 {ROOT}/{指定ファイル名} \
  --out {ROOT}/assets/og/{slug}.jpg \
  -s format jpeg -s formatOptions 75
```

- 出力: `assets/og/{slug}.jpg`（記事の slug と一致させる）
- HTML 側:
  - `og:image` / `twitter:image` を `https://tetsudou-map.com/assets/og/{slug}.jpg` に設定
  - `twitter:card` は `summary_large_image`
  - JSON-LD `image` フィールドにも同パス

元のファイル（リポジトリルートの `samune-foo.png` 等）は削除せず残す（運営者判断で後で除去）。

---

最終更新: 2026-05-21
