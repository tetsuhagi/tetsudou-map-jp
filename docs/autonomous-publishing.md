# 自動記事公開ルーチン仕様（Autonomous Publishing）

スケジュール実行される自動執筆エージェント（Routine）の **実行手順書**。
Routine は毎回まっさらな状態で起動し、過去セッションの記憶を持たない。
**このファイルが唯一の指示書** なので、ここに書かれていないことは勝手に判断せず、
迷ったら「公開せずレポートだけ残して終了」を選ぶこと。

---

## 0. 自分の立場

- あなたは `docs/THREAD-RESPONSIBILITIES.md` における **Thread B（Content）** である
- 担当は記事 prose・記事の SEO 個別情報・sitemap への URL 追加・articles-index 更新のみ
- `assets/` `src/` `scripts/` `_redirects` `_headers` `data/` および
  HTML の構造要素（タグ・class・script）は **触らない**（Thread A 領域）
- CSS / tts.js のバージョン番号（`?v=N`）は既存記事の値をそのまま踏襲し、**変更しない**

## 1. フェーズ定義（現在: Phase 1）

| | Phase 1（現在） | Phase 2（未解禁） |
|---|---|---|
| 頻度 | **1本/日** | 2〜3本/日（Search Console 健全確認後） |
| ジャンル | 路線ガイド＋コラムのみ | ＋ニュース（情報源ルール策定後） |
| サムネ | 白背景テキストサムネ（§3.5 — `scripts/gen_thumbnail.py` が**存在する場合のみ**生成。未完成のうちは完全スキップ） | 同左 |
| バルーン | 自動生成で埋める | 同左 |

Phase 2 への切替は運営者がこのファイルを書き換えて指示する。
**このファイルに書かれていない機能（ニュース執筆・サムネ生成・複数本公開）を勝手に始めないこと。**

## 2. 実行手順（1サイクル）

1. `git pull` で最新化
2. 必読ドキュメントを読む:
   - `docs/THREAD-RESPONSIBILITIES.md`（担当範囲）
   - `docs/voice-guide.md`（声・トーン・バルーン語感 — 最優先）
   - `docs/article-workflow.md`（執筆チェックリスト・時刻ポリシー・アフィリエイト）
   - `docs/articles-index.md`（既存記事・スラッグ重複チェック）
   - `docs/affiliate-links.md`（登録済みアフィリエイト案件）
3. `docs/article-backlog.md` の **未チェック（`- [ ]`）最上位の1件** を選ぶ
4. 既存記事とテーマ・スラッグが重複しないか確認（重複したらその行を `[skip: 重複]` にして次の行へ）
5. 語感の参考として、既存公開記事のうち2本（路線なら `routes/sunrise-seto.html`、コラムなら `columns/` の最新）を読む
6. `docs/article-template.html` を元に執筆
   - 【路線】→ `routes/{slug}.html`、【コラム】→ `columns/{slug}.html`（breadcrumb・canonical をカテゴリに合わせる）
   - タイトルは SEO/SNS 最適化して生成（`docs/article-request-template.md` の生成ルール参照）
   - **導入文の直後・最初のh2の前に『要点3つ』(`div.keypoints`)を必ず置く**。各1行・結論を早く知りたい/長文が苦手な読者向け。鉄道記事なら区間・所要の目安・特徴などの要点を簡潔に。
     ⚠ 具体時刻(XX:XX形式)は入れない（Phase 1の禁止事項を厳守）。誇大語('最強'等)も使わない。
7. **バルーンを自動生成して埋める**（§3）。続けて **サムネイルを生成する**（§3.5 — `scripts/gen_thumbnail.py` が存在する場合のみ。なければスキップし、og:image 系も入れない）
7.5 **アフィリエイトCTA（該当テーマ記事のみ）**: 記事が旅行・宿泊・移動手段比較・観光地アクセス等
   「宿予約と自然につながる」内容のときだけ、`docs/affiliate-links.md` のCTA運用ルールに従い、
   まとめ直前 or 予約・パック・宿に言及したセクション直後に CTAボタン(`div.affiliate-cta`)を1つ設置。
   本文インラインのテキストリンクと合わせて **合計2まで**。`<a>` は登録スニペットを byte 一致で使い、
   disclaimer に開示文を入れる。テーマ非該当（路線スペック解説のみ・考察コラム等）には設置しない。
8. 関連ファイル更新:
   - `routes/index.html` または `columns/index.html` の該当カテゴリにエントリ追加
   - `index.html`（TOP）の該当グリッドにテキストカード追加（最新を先頭）
   - `sitemap.xml` に URL 追加（lastmod = 公開日 / monthly / 0.8）
   - `docs/articles-index.md` にエントリ追加・関連記事との相互リンク
   - ⚠ `_redirects` は Thread A 領域なので**触らない**（クリーンURL運用は Cloudflare 側の既存ルールでカバーされない場合があるが、追記はしない。コミットメッセージに「Note for Thread A: /xxx/{slug}.html の 301 追加をお願いします」と書く）
9. バックログの該当行を `- [x]` にし、`→ 2026-MM-DD / {slug}` を追記
10. `docs/balloon-review-queue.md` に記事タイトル・URL・バルーン全文を追記（§4）
11. セルフチェック（§5）を全部通す
12. コミット＆プッシュ:
    - メッセージ: `feat(content): add {記事名} (auto)`
    - push 失敗時は `git pull --rebase` して再 push。それでも失敗したら **push せず**、状況をレポートに残して終了

## 3. バルーン自動生成ルール

- `voice-guide.md` §3（キャラクター像）・§4（ゴールデンサンプル）・§5（DO/DON'T）に厳密に従う
- 既存記事の `.speech__bubble` 全文を **語感コーパス** として参照する（30本以上の実例がある）
- 個数は **4〜6個**、各1〜2文、語尾をばらす、❌リスト（ですます調・絵文字・営業誘導等）厳守
- `class="speech"` で最初から本文入りで配置（`speech--draft` は使わない）
- 「運営者が言いそうな一言」= アラフォー・旅行好き・ライトな鉄道好き・コスパや年齢の自虐を混ぜる

## 3.5 サムネイル（テキストサムネ）生成ルール

- **前提**: `scripts/gen_thumbnail.py`（Thread A 実装）が存在する場合のみ実行。
  存在しない間はこの節を丸ごとスキップし、og:image / twitter:image / article-hero も記事に入れない
- **キャッチコピーを2行・合計20字以内**で生成する。記事タイトルの転記ではなく、
  記事内容の超要約＋フック（疑問形・対比・意外性）のコピーとして作る
  - 良い例: 「リニアは／博多まで来る？」「じゃらんか／楽天か」「寝てる間に／出雲大社へ」
  - 「最強」「日本一」等の断定 NG 語は使わない（voice-guide §6 準拠）
- 実行: `python3 scripts/gen_thumbnail.py --line1 "{1行目}" --line2 "{2行目}" --out assets/og/{slug}.png`
  （`assets/og/` への生成物の出力は Thread B の運用として許可されている）
- 記事 HTML 側: テンプレのプレースホルダどおり og:image / twitter:image（summary_large_image）/
  JSON-LD image / 記事冒頭 article-hero / TOP カード画像を設定
- `balloon-review-queue.md` のエントリに `サムネ文言: {1行目}／{2行目}` の行を追加（運営者レビュー対象）

## 4. レビューキュー運用

公開のたびに `docs/balloon-review-queue.md` の末尾に以下の形式で追記:

```markdown
## 2026-MM-DD: {記事タイトル}
URL: https://tetsudou-map.com/{section}/{slug}
1. 「{バルーン1全文}」
2. 「{バルーン2全文}」
...
```

運営者は2〜3日ごとにこのファイルだけ確認し、修正が済んだエントリを削除する。
Routine は **既存エントリを編集・削除しない**（追記のみ）。

## 5. セルフチェックリスト（push 前必須）

- [ ] 本文に具体時刻（`XX:XX` 形式）がない — `grep -E '[0-9]{1,2}:[0-9]{2}' {記事}` で本文域を確認
- [ ] 導入直後に要点3つ（`div.keypoints`）がある（各1行・具体時刻/誇大語なし）
- [ ] `speech--draft` が残っていない／バルーンが4〜6個
- [ ] canonical / og:url / breadcrumb / JSON-LD mainEntityOfPage の URL がすべて一致
- [ ] サムネがある場合、og:image / twitter:image / JSON-LD image / 記事冒頭 article-hero / TOPカード画像が揃っている（gen_thumbnail.py 実行時。未実行なら一式なしで統一）
- [ ] アフィリエイト使用時: `<a>` が `docs/affiliate-links.md` の登録スニペットと完全一致（SHA-256推奨）・本文テキスト1＋CTA1の計2まで・disclaimer に開示文
- [ ] CTAボタン(`div.affiliate-cta`)は該当テーマ記事のみ・まとめ前/予約文脈の直後・ファーストビュー外
- [ ] related の内部リンク先が実在するパス
- [ ] sitemap.xml / articles-index.md / カテゴリ index / TOP カードの4点更新済み
- [ ] CSS・tts.js の `?v=` は既存記事と同じ値

## 6. 禁止事項（Phase 1）

- YMYL（クレジットカード・金融・保険・医療・法律）記事の自動執筆
- ニュース記事の自動執筆（情報源ルール未策定のため）
- 1サイクルで2本以上の公開
- 具体時刻の記載・時刻表テーブルの作成
- Thread A 領域（assets/ src/ scripts/ data/ _redirects 等）の変更
- アフィリエイトリンクの改変（byte 単位で原文一致が必須）
- アフィリの過剰設置（1記事3つ以上）・テーマ非該当記事へのCTA設置
- バックログにない記事の執筆（思いつきで書かない）

## 7. バックログ枯渇時

未チェックが残り5件以下になったら、`data/routes.csv`（読み取りのみ可）の未執筆路線と、
既存記事から自然に派生するコラム案を **末尾に10件追記**（未チェック状態・路線:コラム≒2:1）し、
コミットメッセージに `Note for operator: バックログを補充しました。並びを確認してください` と書く。

## 8. 運営者向けメモ

- 記事の取り消しは `git revert {commit}` 一発（Cloudflare Pages が自動で旧状態を再デプロイ）
- 頻度変更・Phase 切替はこのファイルの §1 を書き換え、Routine のスケジュール設定も合わせて変更
- バックログ（`docs/article-backlog.md`）は自由に並び替え・追加・削除してよい

---

最終更新: 2026-05-22（初版 / Phase 1）
