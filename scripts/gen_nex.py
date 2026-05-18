#!/usr/bin/env python3
"""
Generate 成田エクスプレス (NEX) timetable.

Real 2024 dia:
- NEX: ~22-25往復/方向/日 (~30min間隔)
- 大船-横浜-品川-東京-成田-空港第2-成田空港

Stop intervals from 大船:
  OFUNA               +0:00 dep
  YOKOHAMA            +0:19 arr / +0:20 dep
  SHINAGAWA           +0:50 arr / +0:51 dep
  TOKYO               +1:00 arr / +1:02 dep
  NARITA              +1:55 arr / +1:56 dep
  AIRPORT_TERMINAL_2  +2:05 arr / +2:06 dep
  NARITA_AIRPORT      +2:10 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'NEX_YOKOHAMA')

STOPS_DOWN = [
    ('OFUNA',              None,  0),
    ('YOKOHAMA',           19,    20),
    ('SHINAGAWA',          50,    51),
    ('TOKYO',              60,    62),
    ('NARITA',             115,   116),
    ('AIRPORT_TERMINAL_2', 125,   126),
    ('NARITA_AIRPORT',     130,   None),
]
STOPS_UP = [
    ('NARITA_AIRPORT',     None,  0),
    ('AIRPORT_TERMINAL_2', 4,     5),
    ('NARITA',             15,    16),
    ('TOKYO',              68,    70),
    ('SHINAGAWA',          80,    81),
    ('YOKOHAMA',           110,   111),
    ('OFUNA',              130,   None),
]


def gen_pattern(start_h, end_h, minute_marks):
    times = []
    for h in range(start_h, end_h + 1):
        for m in minute_marks:
            times.append(f'{h:02d}:{m:02d}')
    return times


WEEKDAY_DOWN_DEPS = gen_pattern(5, 19, [15, 45])  # 大船発、空港方面
WEEKDAY_UP_DEPS   = gen_pattern(7, 21, [9, 39])   # 空港発、大船方面
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

    emit('NEX', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'NEX{n}', trains, sched_wd, 1)
    emit('NEX', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'NEX{n}', trains, sched_wd, 2)
    emit_schedule_only('NEX', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('NEX', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
