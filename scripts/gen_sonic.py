#!/usr/bin/env python3
"""
Generate ソニック timetable.

Real 2024 dia:
- ソニック: ~30往復/方向/日 (毎時1-2本)
- 博多→大分 ~2h

Stop intervals from 博多:
  HAKATA   +0:00 dep
  KOKURA   +0:38 arr / +0:39 dep
  NAKATSU  +1:10 arr / +1:11 dep
  USA      +1:25 arr / +1:26 dep
  BEPPU    +1:50 arr / +1:51 dep
  OITA     +2:02 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SONIC')

STOPS_DOWN = [
    ('HAKATA',  None,  0),
    ('KOKURA',  38,    39),
    ('NAKATSU', 70,    71),
    ('USA',     85,    86),
    ('BEPPU',   110,   111),
    ('OITA',    122,   None),
]
STOPS_UP = [
    ('OITA',    None,  0),
    ('BEPPU',   11,    12),
    ('USA',     36,    37),
    ('NAKATSU', 51,    52),
    ('KOKURA',  83,    84),
    ('HAKATA',  122,   None),
]


def gen_hourly_pattern(start_h, end_h, minute_marks):
    times = []
    for h in range(start_h, end_h + 1):
        for m in minute_marks:
            times.append(f'{h:02d}:{m:02d}')
    return times


# ソニック: 毎時 :05, :35 をベースに前後足す
WEEKDAY_DOWN_DEPS = gen_hourly_pattern(6, 21, [5, 35])
WEEKDAY_UP_DEPS   = gen_hourly_pattern(6, 21, [10, 40])
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

    emit('SONIC', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ソニック{n}', trains, sched_wd, 1)
    emit('SONIC', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ソニック{n}', trains, sched_wd, 2)
    emit_schedule_only('SONIC', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SONIC', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
