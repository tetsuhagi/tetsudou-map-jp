#!/usr/bin/env python3
"""
Generate イケハヤ風テキストサムネ (白背景・超大黒文字) for articles.

白背景 1200×630 に極太ゴシックのキャッチコピーを最大2行描画し、
OGP / 記事ヒーロー / TOPカード共用の PNG を出力する。
文言は Thread B (Routine) が記事内容から生成する
(ルール: docs/autonomous-publishing.md §3.5)。

Usage:
  python3 scripts/gen_thumbnail.py --line1 "リニアは" --line2 "博多まで来る？" \\
      --out assets/og/linear-to-hakata.png
  python3 scripts/gen_thumbnail.py --line1 "じゃらんか" --line2 "楽天か" \\
      --out assets/og/jalan-vs-rakuten-travel.png
  # 1行のみの場合 (--line2 省略) は中央に1行配置
  python3 scripts/gen_thumbnail.py --line1 "鉄道の未来" --out /tmp/test.png

Dependencies:
  Pillow のみ。未インストールなら:
    python3 -m pip install Pillow
  (macOS の pyenv 環境なら `pip install Pillow` でも可)

Font:
  assets/fonts/NotoSansJP-Black.otf (同梱済み)
  - Noto Sans JP Black (weight 900)、SIL Open Font License 1.1
  - 出典: https://github.com/googlefonts/noto-cjk (Sans/SubsetOTF/JP/)
  - ライセンス全文: assets/fonts/OFL.txt
  OFL なのでリポジトリ同梱・商用利用とも問題なし。

Design spec (2026-06 サムネ方針 — 運営者決定):
  - キャンバス 1200×630、背景 #FFFFFF
  - 本文: 黒 #111111、各行を幅 1040px (左右マージン80px) 内に
    自動フォントサイズ調整で収める。短い行も MAX_FONT_SIZE を超えない
  - 2行時の行間はゆったり (大きい方のフォントサイズの 22%)
  - テキストブロック全体は上下中央よりやや上 (中心 y=285)
  - 下部中央に「鉄道マップ全国版」(28px・グレー #9CA3AF)
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('ERROR: Pillow が必要です。 python3 -m pip install Pillow を実行してください')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, 'assets', 'fonts', 'NotoSansJP-Black.otf')

CANVAS_W, CANVAS_H = 1200, 630
BG_COLOR = '#FFFFFF'
TEXT_COLOR = '#111111'
BRAND_COLOR = '#9CA3AF'
BRAND_TEXT = '鉄道マップ全国版'
BRAND_SIZE = 28
BRAND_BOTTOM_MARGIN = 44   # ブランド文字のbboxボトムを 630-44 に置く

MAX_TEXT_WIDTH = 1040      # 1200 - 80*2
MAX_FONT_SIZE = 260        # 短い行 (2-3文字) が巨大化しすぎないよう上限
MIN_FONT_SIZE = 60
BLOCK_CENTER_Y = 280       # 上下中央(315)よりやや上
LINE_GAP_RATIO = 0.22      # 行間 = max(両行サイズ) * 0.22
MAX_BLOCK_H = 440          # 2行+行間の合計インク高さ上限 (ブランド域と重ならない)


def fit_font_size(draw, text, max_width, max_size=MAX_FONT_SIZE, min_size=MIN_FONT_SIZE):
    """Binary search the largest font size whose ink width fits max_width."""
    lo, hi, best = min_size, max_size, min_size
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(FONT_PATH, mid)
        x0, _, x1, _ = draw.textbbox((0, 0), text, font=font)
        if x1 - x0 <= max_width:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def text_ink_height(draw, text, font):
    _, y0, _, y1 = draw.textbbox((0, 0), text, font=font)
    return y1 - y0


def render(line1, line2, out_path):
    if not os.path.exists(FONT_PATH):
        sys.exit(f'ERROR: font not found: {FONT_PATH}\n'
                 'assets/fonts/NotoSansJP-Black.otf がリポジトリに含まれているか確認してください')

    img = Image.new('RGB', (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    lines = [line1] + ([line2] if line2 else [])
    sizes = [fit_font_size(draw, line, MAX_TEXT_WIDTH) for line in lines]
    fonts = [ImageFont.truetype(FONT_PATH, s) for s in sizes]
    heights = [text_ink_height(draw, ln, f) for ln, f in zip(lines, fonts)]

    # 2行の合計インク高さが MAX_BLOCK_H を超える場合は両行を等率で縮小
    # (下部ブランド文字と重ならず、余白も保つ)
    if len(lines) == 2:
        gap = int(max(sizes) * LINE_GAP_RATIO)
        total = heights[0] + gap + heights[1]
        if total > MAX_BLOCK_H:
            scale = MAX_BLOCK_H / total
            sizes = [max(MIN_FONT_SIZE, int(s * scale)) for s in sizes]
            fonts = [ImageFont.truetype(FONT_PATH, s) for s in sizes]
            heights = [text_ink_height(draw, ln, f) for ln, f in zip(lines, fonts)]

    if len(lines) == 1:
        draw.text((CANVAS_W // 2, BLOCK_CENTER_Y), lines[0],
                  font=fonts[0], fill=TEXT_COLOR, anchor='mm')
    else:
        gap = int(max(f.size for f in fonts) * LINE_GAP_RATIO)
        total = heights[0] + gap + heights[1]
        top = BLOCK_CENTER_Y - total // 2
        y1 = top + heights[0] // 2
        y2 = top + heights[0] + gap + heights[1] // 2
        draw.text((CANVAS_W // 2, y1), lines[0], font=fonts[0], fill=TEXT_COLOR, anchor='mm')
        draw.text((CANVAS_W // 2, y2), lines[1], font=fonts[1], fill=TEXT_COLOR, anchor='mm')

    # 下部ブランド
    brand_font = ImageFont.truetype(FONT_PATH, BRAND_SIZE)
    draw.text((CANVAS_W // 2, CANVAS_H - BRAND_BOTTOM_MARGIN), BRAND_TEXT,
              font=brand_font, fill=BRAND_COLOR, anchor='mb')

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path, 'PNG', optimize=True)
    kb = os.path.getsize(out_path) // 1024
    sizes = ' + '.join(f'{f.size}px' for f in fonts)
    print(f'saved: {out_path} ({kb}KB, font {sizes})')


def main():
    p = argparse.ArgumentParser(description='白背景テキストサムネ (1200x630 PNG) を生成')
    p.add_argument('--line1', required=True, help='1行目 (必須)')
    p.add_argument('--line2', default=None, help='2行目 (省略時は1行を中央配置)')
    p.add_argument('--out', required=True, help='出力PNGパス 例: assets/og/{slug}.png')
    args = p.parse_args()
    render(args.line1, args.line2, args.out)


if __name__ == '__main__':
    main()
