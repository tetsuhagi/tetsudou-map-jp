# 既存記事インデックス

クロスリンク（兄弟列車・併結列車・関連記事）を書くときに参照する、
公開済み記事の **スラッグ・カテゴリ・1行説明** の一覧。

新規記事を追加したら、ここにも一行追加すること。

---

## 記事の標準構成 早見表（2026-06 現在 / 詳細は各docを参照）

新規・既存いずれも、記事は以下の要素で構成する。詳細ルールはリンク先が正。

| 要素 | 概要 | 正となるdoc |
|---|---|---|
| 要素順（FV最適化） | `h1 → page-meta → hero(CSSで非表示) → 要点3つ → バルーン1 → 導入文 → disclaimer → 本文` | `article-template.html`（構造はThread A管轄） |
| 要点3つ `div.keypoints` | 導入の直後。各1行・具体時刻/誇大語NG | `autonomous-publishing.md` §2-6 |
| 導入文 | 約100字に短縮（FVに収めるため） | 同上 |
| バルーン `div.speech` | 4〜6個・自動生成で本文入り→`balloon-review-queue.md`で事後レビュー | `voice-guide.md` §5.5 |
| 読ませる工夫（エンタメ） | 物語アーク・意外性フック・物語的見出し・締めのリワード。本体ですます維持／笑いはバルーン。タイプ別濃度（歴史高・ガイド/比較中・ニュース低） | `voice-guide.md` §6.5（基準=西鉄記事） |
| サムネ（テキスト） | `assets/og/{slug}.png`（`gen_thumbnail.py`生成）＋ og:image/twitter:image(summary_large_image)/JSON-LD image/`article-hero`/TOPカード画像 | `autonomous-publishing.md` §3.5 |
| 時刻表記 | 具体時刻(XX:XX)は書かない・頻度＋公式リンク | `article-workflow.md` §1 |
| アフィリ | 宿予約と自然につながる記事のみ。本文テキスト1＋CTA `div.affiliate-cta` 1＝計2まで。`<a>`は登録スニペットとbyte一致・disclaimerに開示 | `affiliate-links.md` |
| TTS | 全記事に `<script src="/assets/tts.js?v=…">`（Thread A管轄・触らない） | `widgets-tts.md` |

- CSS/JSの現行版: **content.css?v=106**（既存記事に合わせる。変更はThread A）
- 自動公開はRoutine（毎朝1本・Phase 1）。手順の正は `autonomous-publishing.md`
- 分担: 構造/CSS/JS/assets = **Thread A** ／ prose・SEO個別値・台帳 = **Thread B**（`THREAD-RESPONSIBILITIES.md`）

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

| スラッグ | パス | タイトル | 1行説明 | 兄弟列車 |
|---|---|---|---|---|
| `odoriko` | `/routes/odoriko` | 踊り子・サフィール踊り子完全ガイド｜東京〜伊豆急下田・修善寺の停車駅・E261系・伊豆観光特急の乗り方 | JR東日本が運行する伊豆方面の特急。踊り子はE257系の一般特急（東京〜伊豆急下田／修善寺）、サフィール踊り子はE261系の全車グリーン車・個室・カフェテリアを備えた観光特急（東京〜伊豆急下田）。停車駅・相模湾沿いの車窓・全席指定の乗り方・予約のコツ・下田/伊豆高原/熱海/修善寺観光を解説 | romancecar-hakone, shimakaze, kanko-tokkyu-ninki |
| `hitachi-tokiwa` | `/routes/hitachi-tokiwa` | ひたち・ときわ完全ガイド｜品川・上野〜いわき・仙台の停車駅・E657系・常磐線特急の乗り方 | JR東日本が運行する常磐線の特急。ひたちは品川・上野〜いわき・仙台の速達タイプ、ときわは水戸・勝田中心の中距離タイプ。E657系・全車指定席・座席未指定券・太平洋沿いの車窓・偕楽園/ひたち海浜公園/いわき/仙台観光を解説 | azusa-kaiji, narita-express |
| `azusa-kaiji` | `/routes/azusa-kaiji` | あずさ・かいじ完全ガイド｜新宿〜松本・甲府の停車駅・E353系・全車指定席の乗り方 | JR東日本が運行する中央本線の特急。あずさは新宿〜松本（一部白馬・南小谷）、かいじは新宿〜甲府・竜王。E353系・全車指定席・座席未指定券・諏訪湖の車窓・松本/諏訪/甲府観光を解説 | hitachi-tokiwa, narita-express, romancecar-hakone, thunderbird |
| `narita-express` | `/routes/narita-express` | 成田エクスプレス（NEX）完全ガイド｜停車駅・運行区間・予約のコツ | JR東日本が運行する成田空港アクセス特急。東京・新宿・横浜から全席指定で直通 | skyliner |
| `thunderbird` | `/routes/thunderbird` | サンダーバード完全ガイド｜大阪・京都〜敦賀の停車駅・運行区間・北陸への旅 | JR西日本が運行する北陸アクセス特急。大阪・京都〜敦賀を湖西線経由で結び、北陸新幹線への乗継拠点 | — |
| `haruka` | `/routes/haruka` | はるか完全ガイド｜京都・新大阪〜関西空港の停車駅・ハローキティ車両・関空アクセス | JR西日本が運行する関西空港アクセス特急（281系・271系）。京都・新大阪・天王寺から乗り換えなしで関空へ。ハローキティはるかでも人気 | rapit, narita-express, skyliner |
| `kuroshio` | `/routes/kuroshio` | くろしお完全ガイド｜新大阪・京都〜白浜・新宮の停車駅・287系／283系オーシャンアロー・南紀への旅 | JR西日本が運行する南紀アクセス特急。新大阪・京都から和歌山を経て白浜・新宮へ。287系・289系・283系オーシャンアローの違い、太平洋を望むきのくに線の車窓、全車指定席化の動き、停車駅・予約のコツと白浜温泉/アドベンチャーワールド/熊野三山/那智の滝観光を解説。楽天CTA＋本文楽天テキストリンク1の計2 | haruka, thunderbird, shaso-zekkei-tokkyu, kanko-tokkyu-ninki |

### 私鉄特急

| スラッグ | パス | タイトル | 1行説明 | 兄弟列車 |
|---|---|---|---|---|
| `laview` | `/routes/laview` | ラビュー完全ガイド｜池袋〜西武秩父の停車駅・001系・大きな窓と黄色い座席の乗り方 | 西武鉄道が運行する秩父アクセス特急（001系）。建築家・妹島和世デザインの床近くまで届く大きな窓と黄色い座席が人気。池袋から西武秩父へ乗り換えなしで直通。特急ちちぶ／むさしの違い・飯能での進行方向転換・停車駅・座席・Smoozチケットレス予約のコツと秩父神社/三峯神社/羊山公園の芝桜観光まで。楽天CTA＋本文楽天テキストリンク1の計2 | romancecar-hakone, spacia, kanko-tokkyu-ninki |
| `hinotori` | `/routes/hinotori` | ひのとり完全ガイド｜大阪難波〜近鉄名古屋の停車駅・プレミアムシート・名阪特急の旅 | 近鉄が運行する名阪特急のフラッグシップ（80000系）。全席バックシェルのシートと本革のプレミアム車両が人気。大阪難波〜近鉄名古屋を乗り換えなしで直結 | — |
| `romancecar-hakone` | `/routes/romancecar-hakone` | ロマンスカー・はこね完全ガイド｜新宿〜箱根湯本の停車駅・展望席・箱根への旅 | 小田急電鉄が運行する箱根アクセス特急。GSE（70000形）の前面展望席が人気。新宿から乗り換えなしで箱根湯本へ | — |
| `skyliner` | `/routes/skyliner` | スカイライナー完全ガイド｜成田空港へ最速アクセスの停車駅・料金・予約 | 京成電鉄が運行する成田空港アクセス特急。日暮里〜成田空港を最短36分前後で結ぶ在来線最速クラス | narita-express |
| `rapit` | `/routes/rapit` | ラピート完全ガイド｜難波〜関西空港の停車駅・スーパーシート・関空アクセス | 南海電気鉄道が運行する関西空港アクセス特急（50000系）。丸窓とラピートブルーのレトロフューチャーなデザインが特徴。難波から乗り換えなしで関空へ | haruka, skyliner, mu-sky |
| `mu-sky` | `/routes/mu-sky` | ミュースカイ完全ガイド｜名鉄名古屋〜中部国際空港の停車駅・全車特別車・セントレアアクセス | 名古屋鉄道が運行する中部国際空港（セントレア）アクセス特急（2000系）。名鉄では数少ない全車特別車で、名鉄名古屋から乗り換えなしで空港へ。乗車にはミューチケットが必要 | rapit, skyliner, narita-express |
| `spacia` | `/routes/spacia` | スペーシア／スペーシアX完全ガイド｜浅草〜東武日光・鬼怒川温泉の停車駅・個室・日光観光 | 東武鉄道が運行する日光・鬼怒川アクセス特急。100系スペーシアと2023年デビューの新型スペーシアX（N100系）を解説。停車駅・個室やコックピットスイートなどの座席・予約のコツ・日光東照宮/華厳の滝/鬼怒川温泉観光まで。楽天CTA＋本文楽天テキストリンク1の計2 | liberty, romancecar-hakone, kanko-tokkyu-ninki |
| `liberty` | `/routes/liberty` | リバティ完全ガイド｜浅草〜会津田島・鬼怒川温泉・東武日光の停車駅・分割併合・500系の乗り方 | 東武鉄道の特急リバティ（500系）。3両編成の分割併合で浅草から会津・鬼怒川・日光の3方向へ直通。リバティ会津/きぬ/けごんの違い・下今市の切り離し・停車駅・座席・予約のコツと会津/大内宿/鬼怒川温泉/日光観光まで。楽天CTA＋本文楽天テキストリンク1の計2 | spacia, romancecar-hakone, kanko-tokkyu-ninki |

### 観光列車

| スラッグ | パス | タイトル | 1行説明 | 兄弟列車 |
|---|---|---|---|---|
| `shimakaze` | `/routes/shimakaze` | しまかぜ完全ガイド｜大阪・京都・名古屋〜賢島の停車駅・展望車・伊勢志摩の旅 | 近鉄が運行する伊勢志摩への観光特急（50000系）。ハイデッカー展望車・2階建てカフェ車両・個室を備え、大阪難波・京都・近鉄名古屋の3方面から賢島へ向かう | hinotori（同じ近鉄）, rail-kitchen-chikugo |
| `rail-kitchen-chikugo` | `/routes/rail-kitchen-chikugo` | THE RAIL KITCHEN CHIKUGO 完全ガイド｜西鉄の"走るレストラン"で筑後の食を味わう | 西日本鉄道の観光レストラン列車。車内の石窯と筑後の食材を楽しむ完全予約制。太宰府・柳川観光とも好相性 | shimakaze |

---

## コラム・雑記・旅行記（columns/）

### コラム・考察

| スラッグ | パス | タイトル | 1行説明 | 関連記事 |
|---|---|---|---|---|
| `nikko-kinugawa-train-trip` | `/columns/nikko-kinugawa-train-trip` | 日光・鬼怒川は電車旅が正解？アクセス比較と観光の組み立て方｜スペーシアX・リバティ・JR直通で巡るモデルコース | いろは坂の渋滞・駐車場を避けられる日光・鬼怒川は電車旅向き。東武（浅草発）とJR（新宿直通）の2系統の選び方、スペーシアX/スペーシア/リバティ/JR日光きぬがわの使い分け、東照宮・鬼怒川温泉・奥日光の3コースを紹介。楽天＋じゃらん2ボタンCTA＋本文楽天テキストリンク1の計2 | spacia, liberty, izu-train-trip, kanko-tokkyu-ninki |
| `izu-train-trip` | `/columns/izu-train-trip` | 伊豆を電車だけで巡るモデルコース｜熱海・伊豆高原・下田・修善寺の乗り継ぎと観光プラン | 踊り子・伊豆急行・駿豆線を乗り継ぎ、伊豆を電車だけで回る3コース（東伊豆=熱海→伊豆高原→下田／中伊豆=三島→修善寺／観光列車）を乗り継ぎのコツ・観光スポットつきで紹介。楽天＋じゃらん2ボタンCTA＋本文楽天テキストリンク1の計2 | odoriko, kanko-tokkyu-ninki, shaso-zekkei-tokkyu |
| `shaso-zekkei-tokkyu` | `/columns/shaso-zekkei-tokkyu` | 車窓が絶景の在来線特急5選｜移動時間そのものが旅になる路線（個人的セレクション） | 琵琶湖（サンダーバード）・八ヶ岳/諏訪湖（あずさ・かいじ）・瀬戸内海（しおかぜ）・飛騨の渓谷（ひだ）・日本海の夕景（いなほ）の絶景車窓を持つ在来線特急5本を個人的セレクションで紹介するコラム | thunderbird, azusa-kaiji, kanko-tokkyu-ninki |
| `kanko-tokkyu-ninki` | `/columns/kanko-tokkyu-ninki` | 観光特急はなぜ人気？プレミアムシート時代の鉄道旅を考える | 乗ること自体が目的になる観光特急・プレミアムシートの人気の背景を体験消費・移動時間の再定義から考察するコラム | shimakaze, rail-kitchen-chikugo, hinotori |
| `nishitetsu-history` | `/columns/nishitetsu-history` | 西鉄って結局なに者？路面電車から日本一の野球チーム、バス王国まで（西日本鉄道の歴史） | 西日本鉄道の歴史をエンタメ風に解説。九州電気軌道→1942年合併→西鉄ライオンズ→バス王国・街づくり・沿線観光まで | rail-kitchen-chikugo, kitakyushu-airport-access |
| `shinkansen-vs-airplane-tokyo-osaka` | `/columns/shinkansen-vs-airplane-tokyo-osaka` | 東京〜大阪は新幹線と飛行機どっちが楽？費用・所要時間・快適性で比較 | 費用・所要時間・快適性・本数の4軸で新幹線「のぞみ」と飛行機を比較するコラム | narita-airport-access, jalan-vs-rakuten-travel |
| `narita-airport-access` | `/columns/narita-airport-access` | 成田空港アクセスはNEXかスカイライナーか？出発地・所要時間・料金で比較 | 出発地・所要時間・料金・荷物スペースの4軸でNEXとスカイライナーを比較するコラム | narita-express, skyliner, kansai-airport-access |
| `kansai-airport-access` | `/columns/kansai-airport-access` | 関空アクセスはどれが正解？はるか・ラピート・バスを所要時間・料金・出発地で比較 | 出発地・所要時間・料金・乗り換えの4軸で特急はるか・ラピート・リムジンバスを比較するコラム | haruka, rapit, narita-airport-access |
| `jalan-vs-rakuten-travel` | `/columns/jalan-vs-rakuten-travel` | じゃらん vs 楽天トラベル、宿予約はどっちがお得？ | ポイント還元・対応宿数・キャンペーン傾向で二大宿予約サイトを徹底比較 | recruit-card-travel |
| `recruit-card-travel` | `/columns/recruit-card-travel` | リクルートカードは国内旅行好きにお得？ | 常時1.2%還元＋じゃらん連携。国内旅行ユースケースに絞ったリクルートカードの解説 | jalan-vs-rakuten-travel |
| `kitakyushu-airport-access` | `/columns/kitakyushu-airport-access` | 北九州空港アクセス改善は九州活性化のカギ？ | 24時間運用可能な海上空港・北九州空港のアクセス改善が九州全体の活性化につながりうるかを考察 | linear-to-hakata |
| `linear-to-hakata` | `/columns/linear-to-hakata` | リニアは博多まで来るのか？ | リニア中央新幹線の博多延伸の可能性を、歴史と現実の壁から考察 | kitakyushu-airport-access |

### 旅行記

（準備中）

---

## ニュース（news/）

### 鉄道ニュース

| スラッグ | パス | タイトル | 1行説明 | 関連記事 |
|---|---|---|---|---|
| `shinkansen-supreme-class` | `/news/shinkansen-supreme-class` | 東海道・山陽新幹線に最上級「Supreme Class」導入（2026-06-19） | JR東海・JR西日本がN700Sに最上級クラス導入。2026年10月に個室「Cabin」から・23年ぶり個室復活。設備・料金・発売日を整理 | shinkansen-vs-airplane-tokyo-osaka, luna-azul-2027-debut, sunrise-izumo |
| `luna-azul-2027-debut` | `/news/luna-azul-2027-debut` | 新夜行特急「ルナ・アズール」発表（2026-06-13） | JR東日本の新夜行特急の名称決定。2027年度デビュー予定・品川〜青森/長野原草津口 | sunrise-seto, sunrise-izumo |

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

最終更新: 2026-06-17（標準構成 早見表を追加）
