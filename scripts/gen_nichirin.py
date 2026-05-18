#!/usr/bin/env python3
"""
Generate にちりん timetable.

Real 2024 dia:
- にちりん: ~10往復/方向/日 (主に 大分-宮崎)
- 大分→宮崎 ~3h10
- 路線polylineは小倉始発だが、ほとんどのにちりんは大分-宮崎区間運転

Stop intervals from 大分:
  OITA       +0:00 dep
  SAIKI      +0:55 arr / +0:57 dep
  NOBEOKA    +1:45 arr / +1:47 dep
  HYUGASHI   +2:25 arr / +2:26 dep
  MIYAZAKI   +3:10 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'NICHIRIN')

STOPS_DOWN = [
    ('OITA',     None,  0),
    ('SAIKI',    55,    57),
    ('NOBEOKA',  105,   107),
    ('HYUGASHI', 145,   146),
    ('MIYAZAKI', 190,   None),
]
STOPS_UP = [
    ('MIYAZAKI', None,  0),
    ('HYUGASHI', 44,    45),
    ('NOBEOKA',  84,    85),
    ('SAIKI',    133,   135),
    ('OITA',     190,   None),
]

WEEKDAY_DOWN_DEPS = [
    '06:13',
    '07:30',
    '09:00',
    '10:30',
    '12:00',
    '13:30',
    '15:00',
    '16:30',
    '18:00',
    '20:00',
]
WEEKDAY_UP_DEPS = [
    '05:43',
    '07:13',
    '08:30',
    '10:00',
    '11:30',
    '13:30',
    '15:00',
    '16:30',
    '18:00',
    '19:30',
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

    emit('NICHIRIN', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'にちりん{n}', trains, sched_wd, 1)
    emit('NICHIRIN', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'にちりん{n}', trains, sched_wd, 2)
    emit_schedule_only('NICHIRIN', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('NICHIRIN', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
