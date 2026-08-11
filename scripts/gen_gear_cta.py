#!/usr/bin/env python3
"""
鉄道旅行ガジェット（Amazon物販）CTA の生成・更新スクリプト。

■ 何のためのものか
Amazon の個別商品リンクは、半年〜1年で「型落ち商品へのリンク」になってしまう。
かといって PA-API による自動差し替えは、Amazon の利用条件（過去30日以内の
発送済み売上が必要）を満たせないと使えない。
そこで本サイトでは **Amazon の検索結果ページへリンクする** 方式を採り、
リンク定義を data/gear-picks.json の1ファイルに集約する。
売れ筋が入れ替わっても検索結果は自動で最新になるため、リンクは陳腐化しない。

■ 使い方
  記事HTML に次のマーカーを1行置く（Thread B の作業はこれだけ）:

      <!-- GEAR:mobile-battery -->

  そのうえで:

      python3 scripts/gen_gear_cta.py            # 全記事を生成・更新
      python3 scripts/gen_gear_cta.py --check    # 差分があるかだけ確認（書き込まない）

  マーカーの直後に CTA ブロックが挿入され、次回以降の実行では
  その中身が最新の定義で「置き換え」られる（何度実行しても結果は同じ＝冪等）。

■ 商品を入れ替えるとき
  data/gear-picks.json を編集して本スクリプトを再実行するだけ。
  記事側のマーカーは触らなくてよい。

■ 注意（Amazonアソシエイト運営規約）
  - 価格を本文に書かない（PA-API 経由以外での価格表示は不可）。価格は
    リンク先で確認してもらう
  - Amazon の商品画像を自前で保存して使わない
  - 「ベストセラー」「1位」等はランキング変動で事実と食い違うため断定しない
  - サイトには Amazonアソシエイト参加の表記が必要（本サイトはフッターに掲載済み）
"""
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'gear-picks.json')

MARKER_RE = re.compile(
    r'(?P<marker><!--\s*GEAR:(?P<id>[a-z0-9\-]+)\s*-->)'          # マーカー
    r'(?P<body>\s*<div class="affiliate-cta[^"]*">.*?</div>)?',   # 既存ブロック（あれば）
    re.S)


def build_url(item, tag):
    """url が空なら keyword から Amazon 検索URLを組み立てる。"""
    if item.get('url'):
        return item['url']
    kw = urllib.parse.quote_plus(item['keyword'])
    return f'https://www.amazon.co.jp/s?k={kw}&tag={tag}'


def render(item, tag, note):
    url = build_url(item, tag)
    return (
        f'\n  <div class="affiliate-cta">\n'
        f'    <p class="affiliate-cta__label">{item["label"]}</p>\n'
        f'    <a href="{url}" target="_blank" rel="nofollow sponsored noopener">{item["anchor"]}</a>\n'
        f'    <p class="affiliate-cta__note">{note}</p>\n'
        f'  </div>'
    )


def main():
    check_only = '--check' in sys.argv
    cfg = json.load(open(DATA, encoding='utf-8'))
    tag = cfg['_amazon_tag']
    note = cfg['_note_text']
    items = {it['id']: it for it in cfg['items']}

    targets = []
    for sub in ('routes', 'columns', 'news'):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.html') and f != 'index.html':
                targets.append(os.path.join(d, f))

    changed, used, unknown = 0, {}, set()
    for path in targets:
        src = open(path, encoding='utf-8').read()
        if '<!-- GEAR:' not in src:
            continue

        def sub(m):
            gid = m.group('id')
            if gid not in items:
                unknown.add(gid)
                return m.group(0)
            used[gid] = used.get(gid, 0) + 1
            return m.group('marker') + render(items[gid], tag, note)

        out = MARKER_RE.sub(sub, src)
        if out != src:
            changed += 1
            if not check_only:
                open(path, 'w', encoding='utf-8').write(out)

    mode = '[CHECK]' if check_only else '[WRITE]'
    print(f'{mode} 更新が必要/実施したファイル: {changed}')
    if used:
        print('  使用中のガジェット:')
        for gid, n in sorted(used.items()):
            print(f'    {gid:<18} {n}箇所')
    else:
        print('  （まだ記事に <!-- GEAR:xxx --> マーカーが置かれていません）')
    if unknown:
        print(f'  ⚠ data/gear-picks.json に未定義のID: {sorted(unknown)}')
    print(f'  定義済みガジェット: {", ".join(items)}')


if __name__ == '__main__':
    main()
