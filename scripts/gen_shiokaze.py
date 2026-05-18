#!/usr/bin/env python3
"""
Generate しおかぜ timetable (岡山-松山).

Real 2024 dia:
- しおかぜ: ~13往復/方向, 岡山→松山 ~2h45

Stop intervals from 岡山:
  OKAYAMA    +0:00 dep
  KOJIMA     +0:18 arr / +0:19 dep
  UTAZU      +0:28 arr / +0:29 dep
  TADOTSU    +0:35 arr / +0:36 dep
  KANNONJI   +0:53 arr / +0:54 dep
  NIIHAMA    +1:35 arr / +1:37 dep
  IYO_SAIJO  +1:53 arr / +1:54 dep
  IMABARI    +2:15 arr / +2:17 dep
  MATSUYAMA  +2:45 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHIOKAZE')

STOPS_DOWN = [
    ('OKAYAMA',   None,  0),
    ('KOJIMA',    18,    19),
    ('UTAZU',     28,    29),
    ('TADOTSU',   35,    36),
    ('KANNONJI',  53,    54),
    ('NIIHAMA',   95,    97),
    ('IYO_SAIJO', 113,   114),
    ('IMABARI',   135,   137),
    ('MATSUYAMA', 165,   None),
]
STOPS_UP = [
    ('MATSUYAMA', None,  0),
    ('IMABARI',   28,    30),
    ('IYO_SAIJO', 51,    52),
    ('NIIHAMA',   68,    70),
    ('KANNONJI',  111,   112),
    ('TADOTSU',   129,   130),
    ('UTAZU',     136,   137),
    ('KOJIMA',    146,   147),
    ('OKAYAMA',   165,   None),
]

WEEKDAY_DOWN_DEPS = [
    '07:05',
    '08:05', '09:05',
    '10:05', '11:05',
    '12:05', '13:05',
    '14:05', '15:05',
    '16:05', '17:05',
    '18:05',
    '19:05',
    '20:05',
]
WEEKDAY_UP_DEPS = [
    '05:45', '06:45',
    '07:45', '08:45',
    '09:45', '10:45',
    '11:45', '12:45',
    '13:45', '14:45',
    '15:45', '16:45',
    '17:45',
    '19:00',
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

    emit('SHIOKAZE', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'しおかぜ{n}', trains, sched_wd, 1)
    emit('SHIOKAZE', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'しおかぜ{n}', trains, sched_wd, 2)
    emit_schedule_only('SHIOKAZE', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHIOKAZE', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
