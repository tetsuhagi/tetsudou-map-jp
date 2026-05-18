#!/usr/bin/env python3
"""
Generate やくも timetable.

Real 2024 dia:
- やくも: ~15往復/方向/日
- 岡山-倉敷-備中高梁-新見-米子-松江-出雲市 (7駅)
- 岡山→出雲市 ~3h

Stop intervals from 岡山:
  OKAYAMA           +0:00 dep
  KURASHIKI         +0:14 arr / +0:15 dep
  BITCHU_TAKAHASHI  +0:33 arr / +0:34 dep
  NIIMI             +1:11 arr / +1:13 dep
  YONAGO            +2:16 arr / +2:18 dep
  MATSUE            +2:42 arr / +2:44 dep
  IZUMOSHI          +3:04 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'YAKUMO')

STOPS_DOWN = [
    ('OKAYAMA',          None,  0),
    ('KURASHIKI',        14,    15),
    ('BITCHU_TAKAHASHI', 33,    34),
    ('NIIMI',            71,    73),
    ('YONAGO',           136,   138),
    ('MATSUE',           162,   164),
    ('IZUMOSHI',         184,   None),
]
STOPS_UP = [
    ('IZUMOSHI',         None,  0),
    ('MATSUE',           20,    22),
    ('YONAGO',           46,    48),
    ('NIIMI',            111,   113),
    ('BITCHU_TAKAHASHI', 150,   151),
    ('KURASHIKI',        169,   170),
    ('OKAYAMA',          184,   None),
]

WEEKDAY_DOWN_DEPS = [
    '06:05', '07:05', '08:05',
    '09:05', '10:05', '11:05',
    '12:05', '13:05', '14:05',
    '15:05', '16:05', '17:05',
    '18:05', '19:05', '20:05',
]
WEEKDAY_UP_DEPS = [
    '05:25', '06:25', '07:30',
    '08:30', '09:30', '10:30',
    '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30',
    '17:30', '18:30', '19:30',
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

    emit('YAKUMO', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'やくも{n}', trains, sched_wd, 1)
    emit('YAKUMO', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'やくも{n}', trains, sched_wd, 2)
    emit_schedule_only('YAKUMO', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('YAKUMO', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
