#!/usr/bin/env python3
"""
Generate 宇和海 timetable (松山 ⇔ 宇和島).

JR四国 特急「宇和海」。2000系・N2000系で運用。予讃線 (松山〜宇和島)
を結ぶ四国の主要特急の1つ。

経由路線: JR四国 予讃線 (松山〜宇和島)

代表ダイヤ:
  - 30分間隔 (毎時 :00 / :30 発)
  - 松山発: 6:00〜21:30 → 32本/方向
  - 宇和島発: 6:00〜21:30 → 32本/方向
  - 1日 64本
  - 所要 80分 (1時間20分)

実ダイヤとの差:
  - 実際の本数は約15往復/方向 (約60分間隔)
  - シミュレーション表示で「常時動いてる」感を出すため30分間隔の
    代表ダイヤに増量

Stop intervals from 松山:
  MATSUYAMA    +0:00 dep
  UCHIKO       +0:25 arr / +0:26 dep
  IYO_OZU      +0:35 arr / +0:36 dep
  YAWATAHAMA   +0:55 arr / +0:56 dep
  UNOMACHI     +1:10 arr / +1:11 dep
  UWAJIMA      +1:20 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'UWAKAI')

STOPS_DOWN = [
    ('MATSUYAMA',  None, 0),
    ('UCHIKO',     25,   26),
    ('IYO_OZU',    35,   36),
    ('YAWATAHAMA', 55,   56),
    ('UNOMACHI',   70,   71),
    ('UWAJIMA',    80,   None),
]
STOPS_UP = [
    ('UWAJIMA',    None, 0),
    ('UNOMACHI',   9,    10),
    ('YAWATAHAMA', 24,   25),
    ('IYO_OZU',    44,   45),
    ('UCHIKO',     54,   55),
    ('MATSUYAMA',  80,   None),
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


WEEKDAY_DOWN_DEPS = gen_half_hourly(6, 0, 21, 30)    # 32本
WEEKDAY_UP_DEPS   = gen_half_hourly(6, 0, 21, 30)    # 32本
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

    emit('UWAKAI', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', '宇和海{n}号', trains, sched_wd, 1)
    emit('UWAKAI', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   '宇和海{n}号', trains, sched_wd, 2)
    emit_schedule_only('UWAKAI', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('UWAKAI', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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


if __name__ == '__main__':
    main()
