#!/usr/bin/env python3
"""
Generate ライラック・カムイ timetable (combined).

Real 2024 dia:
- ライラック+カムイ統合: ~24往復/方向/日 (~30分間隔)
- 札幌-岩見沢-美唄-砂川-滝川-深川-旭川 (~1h25)

Stop intervals from 札幌:
  SAPPORO     +0:00 dep
  IWAMIZAWA   +0:27 arr / +0:28 dep
  BIBAI       +0:42 arr / +0:43 dep
  SUNAGAWA    +0:50 arr / +0:51 dep
  TAKIKAWA    +0:57 arr / +0:58 dep
  FUKAGAWA    +1:13 arr / +1:14 dep
  ASAHIKAWA   +1:25 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'LILAC_KAMUI')

STOPS_DOWN = [
    ('SAPPORO',   None,  0),
    ('IWAMIZAWA', 27,    28),
    ('BIBAI',     42,    43),
    ('SUNAGAWA',  50,    51),
    ('TAKIKAWA',  57,    58),
    ('FUKAGAWA',  73,    74),
    ('ASAHIKAWA', 85,    None),
]
STOPS_UP = [
    ('ASAHIKAWA', None,  0),
    ('FUKAGAWA',  11,    12),
    ('TAKIKAWA',  27,    28),
    ('SUNAGAWA',  34,    35),
    ('BIBAI',     42,    43),
    ('IWAMIZAWA', 57,    58),
    ('SAPPORO',   85,    None),
]


def gen_pattern(start_h, end_h, minute_marks):
    times = []
    for h in range(start_h, end_h + 1):
        for m in minute_marks:
            times.append(f'{h:02d}:{m:02d}')
    return times


WEEKDAY_DOWN_DEPS = gen_pattern(6, 21, [0, 30])
WEEKDAY_UP_DEPS   = gen_pattern(6, 21, [10, 40])
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

    emit('LILAC_KAMUI', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ライラック/カムイ{n}', trains, sched_wd, 1)
    emit('LILAC_KAMUI', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ライラック/カムイ{n}', trains, sched_wd, 2)
    emit_schedule_only('LILAC_KAMUI', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('LILAC_KAMUI', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
