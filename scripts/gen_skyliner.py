#!/usr/bin/env python3
"""
Generate スカイライナー timetable (京成上野 ⇔ 成田空港).

京成スカイライナーは京成電鉄AE形による空港アクセス特急。
京成本線 → 北総線 → 成田空港線 (通称「成田スカイアクセス線」) を経由。

2026年5月時点の概略を簡略化:
  - 停車駅は4駅のみ (京成上野・日暮里・空港第2ビル・成田空港)
  - 京成上野 → 成田空港 約41分
  - 日中は20分間隔 (毎時 :00 / :20 / :40 発)
  - 1日 約40本/方向の実ダイヤに対し、簡略化して 45本/方向 (合計 90本/日)

実ダイヤでは:
  - 朝晩は本数が減る (40分間隔の時間帯あり)
  - 始発/終発時刻も日によって異なる
本テンプレートでは終日 20分間隔として簡略化。

Stop intervals from 京成上野:
  KEISEI_UENO          +0:00 dep
  NIPPORI              +0:02 arr / +0:03 dep
  AIRPORT_TERMINAL_2   +0:38 arr / +0:39 dep
  NARITA_AIRPORT       +0:41 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SKYLINER')

# (station_id, arrival_offset_min, departure_offset_min)
STOPS_DOWN = [
    ('KEISEI_UENO',         None, 0),
    ('NIPPORI',             2,    3),
    ('AIRPORT_TERMINAL_2',  38,   39),
    ('NARITA_AIRPORT',      41,   None),
]
STOPS_UP = [
    ('NARITA_AIRPORT',      None, 0),
    ('AIRPORT_TERMINAL_2',  3,    4),
    ('NIPPORI',             38,   39),
    ('KEISEI_UENO',         41,   None),
]


def gen_every_20(start_h, start_m, end_h, end_m):
    """毎時 :00, :20, :40 の発時刻を start..end 区間で生成"""
    times = []
    h, m = start_h, start_m
    while (h, m) <= (end_h, end_m):
        times.append(f'{h:02d}:{m:02d}')
        m += 20
        if m >= 60:
            m -= 60
            h += 1
    return times


# 上野発 7:00〜21:40、空港発 8:00〜22:40 (代表ダイヤ、終日 20分間隔)
WEEKDAY_DOWN_DEPS = gen_every_20(7, 0, 21, 40)
WEEKDAY_UP_DEPS   = gen_every_20(8, 0, 22, 40)
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

    emit('SKYLINER', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'スカイライナー{n}', trains, sched_wd, 1)
    emit('SKYLINER', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'スカイライナー{n}', trains, sched_wd, 2)
    emit_schedule_only('SKYLINER', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SKYLINER', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
    print(f'holiday: 下 {len(HOLIDAY_DOWN_DEPS)} + 上 {len(HOLIDAY_UP_DEPS)} = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
