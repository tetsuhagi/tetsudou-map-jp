#!/usr/bin/env python3
"""
Generate はるか timetable.

Real 2024 dia:
- はるか: ~30往復/方向/日 (主に30分間隔)
- 京都-新大阪-天王寺-日根野-関西空港
- 京都→関空 ~1h20

Stop intervals from 京都:
  KYOTO            +0:00 dep
  SHIN_OSAKA       +0:31 arr / +0:32 dep
  TENNOJI          +0:49 arr / +0:50 dep
  HINENO           +1:10 arr / +1:11 dep
  KANSAI_AIRPORT   +1:20 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HARUKA')

STOPS_DOWN = [
    ('KYOTO',          None,  0),
    ('SHIN_OSAKA',     31,    32),
    ('TENNOJI',        49,    50),
    ('HINENO',         70,    71),
    ('KANSAI_AIRPORT', 80,    None),
]
STOPS_UP = [
    ('KANSAI_AIRPORT', None,  0),
    ('HINENO',         9,     10),
    ('TENNOJI',        30,    31),
    ('SHIN_OSAKA',     48,    49),
    ('KYOTO',          80,    None),
]


def gen_half_hourly(start_h, start_m, end_h, end_m):
    """Generate departures at :00 and :30 from start to end."""
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


WEEKDAY_DOWN_DEPS = gen_half_hourly(6, 30, 22, 0)
WEEKDAY_UP_DEPS   = gen_half_hourly(6, 16, 22, 16)
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

    emit('HARUKA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'はるか{n}', trains, sched_wd, 1)
    emit('HARUKA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'はるか{n}', trains, sched_wd, 2)
    emit_schedule_only('HARUKA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HARUKA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
