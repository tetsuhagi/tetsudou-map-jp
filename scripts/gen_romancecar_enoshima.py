#!/usr/bin/env python3
"""
Generate 小田急ロマンスカー えのしま timetable (新宿 ⇔ 片瀬江ノ島) — 実ダイヤ準拠版.

小田急電鉄の特急ロマンスカー「えのしま」系統と関連通勤特急
(ホームウェイ江ノ島行・モーニングウェイ藤沢始発) の現行ダイヤを
反映。Wikipedia + NAVITIME 情報から再構築 (2026年3月14日改正後)。

経由路線:
  - 小田急電鉄 小田原線 (新宿〜相模大野)
  - 小田急電鉄 江ノ島線 (相模大野〜片瀬江ノ島)

実態の特徴:
  - 「えのしま号」純粋系統は **土休日に集中**、平日は少ない
  - 平日は朝の上り (モーニングウェイ系統、藤沢始発) + 夕方下り (ホーム
    ウェイ系統、江ノ島行) で5本程度
  - 土休日は片瀬江ノ島行 下り6本・上り8本
  - 全列車が藤沢駅でスイッチバック (進行方向転換)
  - メトロえのしま (北千住直通) は本テンプレート対象外

代表ダイヤ:
  平日 (5本):
    下り 2本: 藤沢行 07:00, 片瀬江ノ島行 17:00 (ホームウェイ系)
    上り 3本: 片瀬江ノ島発 07:00, 08:00, 09:00 (モーニングウェイ系)
  土休日 (14本):
    下り 6本: 07:00, 09:00, 10:00, 11:00, 14:00, 17:00
    上り 8本: 09:00, 10:00, 12:00, 14:00, 16:00, 17:00, 19:00, 20:00

所要時間: 65分 (新宿⇔片瀬江ノ島)

簡略化事項:
  - 平日下り1本 (07:00) は実態では藤沢行だが、本テンプレートでは
    片瀬江ノ島行として統一 (停車駅セットが同じため)
  - メトロえのしまは対象外
  - 時刻は実態の傾向を反映した推定値 (NAVITIMEで完全取得できず)

Stop intervals from 新宿:
  SHINJUKU         +0:00 dep
  MACHIDA          +0:35 arr / +0:36 dep
  YAMATO           +0:46 arr / +0:47 dep
  FUJISAWA         +0:58 arr / +0:59 dep   (ここでスイッチバック)
  KATASE_ENOSHIMA  +1:05 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ROMANCECAR_ENOSHIMA')

STOPS_DOWN = [
    ('SHINJUKU',        None, 0),
    ('MACHIDA',         35,   36),
    ('YAMATO',          46,   47),
    ('FUJISAWA',        58,   59),
    ('KATASE_ENOSHIMA', 65,   None),
]
STOPS_UP = [
    ('KATASE_ENOSHIMA', None, 0),
    ('FUJISAWA',        6,    7),
    ('YAMATO',          18,   19),
    ('MACHIDA',         29,   30),
    ('SHINJUKU',        65,   None),
]

# 平日 (実態少なめ、朝の上り中心 + 夕方下り)
WEEKDAY_DOWN_DEPS = [
    '07:00',  # 藤沢行 (本テンプレートでは片瀬江ノ島行統一)
    '17:00',  # ホームウェイ系 (片瀬江ノ島行)
]
WEEKDAY_UP_DEPS = [
    '07:00',  # モーニングウェイ系
    '08:00',
    '09:00',
]

# 土休日 (観光ピーク、本数多い)
HOLIDAY_DOWN_DEPS = [
    '07:00', '09:00', '10:00', '11:00', '14:00', '17:00',
]
HOLIDAY_UP_DEPS = [
    '09:00', '10:00', '12:00', '14:00', '16:00', '17:00', '19:00', '20:00',
]


def parse_hhmm(s):
    h, m = s.split(':')
    return int(h) * 60 + int(m)


def fmt_hhmm(mins):
    return f'{mins // 60:02d}:{mins % 60:02d}'


def build_stops(base_dep_min, stops_def):
    rows = []
    for sid, arr_off, dep_off in stops_def:
        arr = fmt_hhmm(base_dep_min + arr_off) if arr_off is not None else ''
        dep = fmt_hhmm(base_dep_min + dep_off) if dep_off is not None else ''
        rows.append((sid, arr, dep))
    return rows


def emit(prefix, deps, stops_def, direction, name_template, trains, schedule, start_n):
    n = start_n
    for dep in deps:
        tid = f'{prefix}_{n}'
        trains.append((tid, name_template.format(n=n), direction))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), stops_def), 1):
            schedule.append((tid, order, sid, arr, dp))
        n += 2


def emit_schedule_only(prefix, deps, stops_def, schedule, start_n):
    n = start_n
    for dep in deps:
        tid = f'{prefix}_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), stops_def), 1):
            schedule.append((tid, order, sid, arr, dp))
        n += 2


def main():
    trains = []
    sched_wd = []
    sched_hd = []

    # 平日と休日で時刻・本数が大きく異なるため、train_id を分離 (W/H)
    emit('ROMANCECAR_ENOSHIMA_W', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'えのしま{n}', trains, sched_wd, 1)
    emit('ROMANCECAR_ENOSHIMA_W', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'えのしま{n}', trains, sched_wd, 2)
    emit('ROMANCECAR_ENOSHIMA_H', HOLIDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'えのしま{n}', trains, sched_hd, 1)
    emit('ROMANCECAR_ENOSHIMA_H', HOLIDAY_UP_DEPS,   STOPS_UP,   'up',   'えのしま{n}', trains, sched_hd, 2)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'trains.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,name,direction\n')
        for tid, name, direction in trains:
            f.write(f'{tid},{name},{direction}\n')

    with open(os.path.join(OUT_DIR, 'weekday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched_wd:
            f.write(','.join(map(str, row)) + '\n')

    with open(os.path.join(OUT_DIR, 'holiday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched_hd:
            f.write(','.join(map(str, row)) + '\n')

    print(f'trains.csv: {len(trains)}本 (平日: 下 {len(WEEKDAY_DOWN_DEPS)} + 上 {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本)')
    print(f'           (休日: 下 {len(HOLIDAY_DOWN_DEPS)} + 上 {len(HOLIDAY_UP_DEPS)} = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本)')


if __name__ == '__main__':
    main()
