#!/usr/bin/env python3
"""
Generate 踊り子 timetable.

Real 2024 dia:
- 踊り子: ~8往復/方向/日
- 東京→伊豆急下田 ~2h50

Stop intervals from 東京:
  TOKYO           +0:00 dep
  SHINAGAWA       +0:07 arr / +0:08 dep
  YOKOHAMA        +0:25 arr / +0:27 dep
  ODAWARA         +1:07 arr / +1:08 dep
  ATAMI           +1:20 arr / +1:22 dep
  ITO             +1:45 arr / +1:47 dep
  IZUKOGEN        +2:05 arr / +2:07 dep
  KAWAZU          +2:35 arr / +2:36 dep
  IZUKYU_SHIMODA  +2:50 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ODORIKO')

STOPS_DOWN = [
    ('TOKYO',          None,  0),
    ('SHINAGAWA',      7,     8),
    ('YOKOHAMA',       25,    27),
    ('ODAWARA',        67,    68),
    ('ATAMI',          80,    82),
    ('ITO',            105,   107),
    ('IZUKOGEN',       125,   127),
    ('KAWAZU',         155,   156),
    ('IZUKYU_SHIMODA', 170,   None),
]
STOPS_UP = [
    ('IZUKYU_SHIMODA', None,  0),
    ('KAWAZU',         14,    15),
    ('IZUKOGEN',       43,    45),
    ('ITO',            63,    65),
    ('ATAMI',          88,    90),
    ('ODAWARA',        102,   103),
    ('YOKOHAMA',       143,   145),
    ('SHINAGAWA',      162,   163),
    ('TOKYO',          170,   None),
]

WEEKDAY_DOWN_DEPS = [
    '08:00', '09:00',
    '10:00', '11:00',
    '13:00', '15:00',
    '17:00', '19:00',
]
WEEKDAY_UP_DEPS = [
    '06:30', '08:00',
    '10:00', '11:30',
    '13:00', '15:00',
    '17:00', '18:30',
]
HOLIDAY_DOWN_DEPS = WEEKDAY_DOWN_DEPS
HOLIDAY_UP_DEPS = WEEKDAY_UP_DEPS


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

    emit('ODORIKO', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', '踊り子{n}', trains, sched_wd, 1)
    emit('ODORIKO', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   '踊り子{n}', trains, sched_wd, 2)
    emit_schedule_only('ODORIKO', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('ODORIKO', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
