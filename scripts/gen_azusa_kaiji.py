#!/usr/bin/env python3
"""
Generate あずさ・かいじ timetable.

Real 2024 dia:
- あずさ (松本行き): ~15-16本/方向, 新宿-松本 ~2h45
- かいじ (甲府行き): ~14-17本/方向, 新宿-甲府 ~1h30

Stop intervals from 新宿 (あずさ):
  SHINJUKU      +0:00 dep
  HACHIOJI      +0:32 arr / +0:33 dep
  OTSUKI        +1:04 arr / +1:05 dep
  KOFU          +1:25 arr / +1:27 dep
  KOBUCHIZAWA   +1:48 arr / +1:49 dep
  CHINO         +2:03 arr / +2:04 dep
  KAMISUWA      +2:11 arr / +2:12 dep
  SHIOJIRI      +2:30 arr / +2:31 dep
  MATSUMOTO     +2:45 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'AZUSA_KAIJI')

AZUSA_DOWN = [
    ('SHINJUKU',    None,  0),
    ('HACHIOJI',    32,    33),
    ('OTSUKI',      64,    65),
    ('KOFU',        85,    87),
    ('KOBUCHIZAWA', 108,   109),
    ('CHINO',       123,   124),
    ('KAMISUWA',    131,   132),
    ('SHIOJIRI',    150,   151),
    ('MATSUMOTO',   165,   None),
]
AZUSA_UP = [
    ('MATSUMOTO',   None,  0),
    ('SHIOJIRI',    14,    15),
    ('KAMISUWA',    33,    34),
    ('CHINO',       41,    42),
    ('KOBUCHIZAWA', 56,    57),
    ('KOFU',        78,    80),
    ('OTSUKI',      100,   101),
    ('HACHIOJI',    132,   133),
    ('SHINJUKU',    165,   None),
]

KAIJI_DOWN = [
    ('SHINJUKU', None,  0),
    ('HACHIOJI', 32,    33),
    ('OTSUKI',   65,    66),
    ('KOFU',     90,    None),
]
KAIJI_UP = [
    ('KOFU',     None,  0),
    ('OTSUKI',   24,    25),
    ('HACHIOJI', 57,    58),
    ('SHINJUKU', 90,    None),
]

AZUSA_WEEKDAY_DOWN = [
    '06:30', '08:00', '09:00',
    '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00',
    '16:00', '17:00', '18:00',
    '19:00', '20:00', '21:00',
]
AZUSA_WEEKDAY_UP = [
    '06:00', '07:00', '08:00',
    '09:00', '10:00', '11:00',
    '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00',
    '18:00', '19:00', '20:30',
]
AZUSA_HOLIDAY_DOWN = [
    '06:30', '08:00', '09:00',
    '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00',
    '16:00', '17:00',
    '19:00', '20:00',
]
AZUSA_HOLIDAY_UP = [
    '06:00', '07:00', '08:00',
    '09:00', '10:00', '11:00',
    '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00',
    '18:00', '20:30',
]

KAIJI_WEEKDAY_DOWN = [
    '07:00', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30', '21:30',
    '22:00',
]
KAIJI_WEEKDAY_UP = [
    '06:30',
    '07:30', '08:30',
    '09:30', '10:30',
    '11:30', '12:30',
    '13:30', '14:30',
    '15:30', '16:30',
    '17:30', '18:30',
    '19:30', '20:30',
    '21:30',
]
KAIJI_HOLIDAY_DOWN = [
    '07:00',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30', '21:30',
]
KAIJI_HOLIDAY_UP = [
    '06:30', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30',
]


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

    emit('AZUSA', AZUSA_WEEKDAY_DOWN, AZUSA_DOWN, 'down', 'あずさ{n}', trains, sched_wd, 1)
    emit('AZUSA', AZUSA_WEEKDAY_UP,   AZUSA_UP,   'up',   'あずさ{n}', trains, sched_wd, 2)
    emit_schedule_only('AZUSA', AZUSA_HOLIDAY_DOWN, AZUSA_DOWN, sched_hd, 1)
    emit_schedule_only('AZUSA', AZUSA_HOLIDAY_UP,   AZUSA_UP,   sched_hd, 2)

    emit('KAIJI', KAIJI_WEEKDAY_DOWN, KAIJI_DOWN, 'down', 'かいじ{n}', trains, sched_wd, 1)
    emit('KAIJI', KAIJI_WEEKDAY_UP,   KAIJI_UP,   'up',   'かいじ{n}', trains, sched_wd, 2)
    emit_schedule_only('KAIJI', KAIJI_HOLIDAY_DOWN, KAIJI_DOWN, sched_hd, 1)
    emit_schedule_only('KAIJI', KAIJI_HOLIDAY_UP,   KAIJI_UP,   sched_hd, 2)

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
    wd_d = len(AZUSA_WEEKDAY_DOWN) + len(KAIJI_WEEKDAY_DOWN)
    wd_u = len(AZUSA_WEEKDAY_UP) + len(KAIJI_WEEKDAY_UP)
    hd_d = len(AZUSA_HOLIDAY_DOWN) + len(KAIJI_HOLIDAY_DOWN)
    hd_u = len(AZUSA_HOLIDAY_UP) + len(KAIJI_HOLIDAY_UP)
    print(f'weekday: 下 {wd_d} + 上 {wd_u} = {wd_d + wd_u}本')
    print(f'holiday: 下 {hd_d} + 上 {hd_u} = {hd_d + hd_u}本')


if __name__ == '__main__':
    main()
