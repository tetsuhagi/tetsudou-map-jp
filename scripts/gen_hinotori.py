#!/usr/bin/env python3
"""
Generate 近鉄ひのとり timetable (大阪難波 ⇔ 近鉄名古屋).

近畿日本鉄道80000系「ひのとり (Hinotori)」(2020年デビュー)。
名阪特急の主力車両で、ひのとり甲特急 (名阪甲特急の置き換え) として運行。
ひのとり= 火の鳥 = フェニックスから命名された名阪間のフラッグシップ。

経由路線 (3路線):
  - 近畿日本鉄道 難波線 (大阪難波〜大阪上本町)
  - 近畿日本鉄道 大阪線 (大阪上本町〜伊勢中川)
  - 近畿日本鉄道 名古屋線 (伊勢中川〜近鉄名古屋)
  ※ 伊勢中川駅は通過 (デルタ線/短絡線経由)

代表ダイヤ:
  - 30分間隔 (毎時 :00 / :30 発)
  - 大阪難波発 6:00〜22:00 → 33本
  - 近鉄名古屋発 6:00〜22:00 → 33本
  - 1日 66本/方向
  - 所要時間 125分 (2時間5分)

実ダイヤとの差:
  - 実際の本数は約30本/方向 (ほぼ30分間隔で運行中)。
  - 一部の便は大和八木・津・近鉄四日市を通過する速達タイプあり。
    本テンプレートでは全便を全停車型 (代表停車パターン) で簡略化。
  - 近鉄では「アーバンライナー」(21000系) との併存運行で名阪特急が
    構成されるが、本テンプレートは HINOTORI のみ。アーバンライナーは
    将来 URBAN_LINER で追加予定。

Stop intervals from 大阪難波:
  OSAKA_NAMBA          +0:00 dep
  OSAKA_UEHOMMACHI     +0:04 arr / +0:05 dep
  TSURUHASHI           +0:08 arr / +0:09 dep
  YAMATO_YAGI          +0:36 arr / +0:37 dep
  TSU                  +1:35 arr / +1:36 dep
  KINTETSU_YOKKAICHI   +1:50 arr / +1:51 dep
  KINTETSU_NAGOYA      +2:05 arr (=125min)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HINOTORI')

STOPS_DOWN = [
    ('OSAKA_NAMBA',        None, 0),
    ('OSAKA_UEHOMMACHI',   4,    5),
    ('TSURUHASHI',         8,    9),
    ('YAMATO_YAGI',        36,   37),
    ('TSU',                95,   96),
    ('KINTETSU_YOKKAICHI', 110,  111),
    ('KINTETSU_NAGOYA',    125,  None),
]
STOPS_UP = [
    ('KINTETSU_NAGOYA',    None, 0),
    ('KINTETSU_YOKKAICHI', 14,   15),
    ('TSU',                29,   30),
    ('YAMATO_YAGI',        88,   89),
    ('TSURUHASHI',         116,  117),
    ('OSAKA_UEHOMMACHI',   120,  121),
    ('OSAKA_NAMBA',        125,  None),
]


def gen_half_hourly(start_h, start_m, end_h, end_m):
    times = []
    h, m = start_h, start_m
    while (h, m) <= (end_h, end_m):
        times.append(f'{h:02d}:{m:02d}')
        if m == 0:
            m = 30
        else:
            m = 0
            h += 1
    return times


# 30分間隔、6:00〜22:00 (33本/方向)
WEEKDAY_DOWN_DEPS = gen_half_hourly(6, 0, 22, 0)
WEEKDAY_UP_DEPS   = gen_half_hourly(6, 0, 22, 0)
HOLIDAY_DOWN_DEPS = WEEKDAY_DOWN_DEPS
HOLIDAY_UP_DEPS   = WEEKDAY_UP_DEPS


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

    emit('HINOTORI', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ひのとり{n}', trains, sched_wd, 1)
    emit('HINOTORI', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ひのとり{n}', trains, sched_wd, 2)
    emit_schedule_only('HINOTORI', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HINOTORI', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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

    down = sum(1 for _, _, d in trains if d == 'down')
    up = sum(1 for _, _, d in trains if d == 'up')
    print(f'trains.csv: {len(trains)}本 (下り {down}, 上り {up})')
    print(f'weekday: 下 {len(WEEKDAY_DOWN_DEPS)} + 上 {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
