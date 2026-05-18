#!/usr/bin/env python3
"""
Generate しなの timetable.

Real 2024 dia:
- しなの: ~14往復/方向/日 (毎時1本ベース)
- 名古屋→長野 ~3h07

Stop intervals from 名古屋:
  NAGOYA          +0:00 dep
  CHIKUSA         +0:05 arr / +0:06 dep
  TAJIMI          +0:25 arr / +0:26 dep
  NAKATSUGAWA     +0:50 arr / +0:51 dep
  KISO_FUKUSHIMA  +1:30 arr / +1:31 dep
  SHIOJIRI        +2:10 arr / +2:12 dep
  MATSUMOTO      +2:25 arr / +2:27 dep
  SHINONOI        +2:55 arr / +2:56 dep
  NAGANO          +3:07 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHINANO')

STOPS_DOWN = [
    ('NAGOYA',         None,  0),
    ('CHIKUSA',        5,     6),
    ('TAJIMI',         25,    26),
    ('NAKATSUGAWA',    50,    51),
    ('KISO_FUKUSHIMA', 90,    91),
    ('SHIOJIRI',       130,   132),
    ('MATSUMOTO',      145,   147),
    ('SHINONOI',       175,   176),
    ('NAGANO',         187,   None),
]
STOPS_UP = [
    ('NAGANO',         None,  0),
    ('SHINONOI',       11,    12),
    ('MATSUMOTO',      40,    42),
    ('SHIOJIRI',       55,    57),
    ('KISO_FUKUSHIMA', 96,    97),
    ('NAKATSUGAWA',    136,   137),
    ('TAJIMI',         161,   162),
    ('CHIKUSA',        181,   182),
    ('NAGOYA',         187,   None),
]

WEEKDAY_DOWN_DEPS = [
    '07:00', '08:00',
    '09:00', '10:00',
    '11:00', '12:00',
    '13:00', '14:00',
    '15:00', '16:00',
    '17:00', '18:00',
    '19:00', '20:00',
]
WEEKDAY_UP_DEPS = [
    '06:00', '07:00',
    '08:00', '09:00',
    '10:00', '11:00',
    '12:00', '13:00',
    '14:00', '15:00',
    '16:00', '17:00',
    '18:00', '19:00',
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

    emit('SHINANO', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'しなの{n}', trains, sched_wd, 1)
    emit('SHINANO', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'しなの{n}', trains, sched_wd, 2)
    emit_schedule_only('SHINANO', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHINANO', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
