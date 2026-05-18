#!/usr/bin/env python3
"""
Generate くろしお timetable.

Real 2024 dia:
- くろしお新宮行き: ~5往復/方向 (新大阪-新宮 ~4h)
- くろしお白浜行き (折り返し): ~12往復/方向 (新大阪-白浜 ~2h25)

Stop intervals from 新大阪 (full):
  SHIN_OSAKA      +0:00 dep
  TENNOJI         +0:15 arr / +0:17 dep
  WAKAYAMA        +0:50 arr / +0:52 dep
  KAINAN          +1:00 arr / +1:01 dep
  GOBO            +1:30 arr / +1:31 dep
  KII_TANABE      +2:15 arr / +2:17 dep
  SHIRAHAMA       +2:25 arr / +2:27 dep
  SUSAMI          +2:47 arr / +2:48 dep
  KUSHIMOTO       +3:15 arr / +3:16 dep
  KII_KATSUURA    +3:40 arr / +3:41 dep
  SHINGU          +4:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KUROSHIO')

FULL_DOWN = [
    ('SHIN_OSAKA',    None,  0),
    ('TENNOJI',       15,    17),
    ('WAKAYAMA',      50,    52),
    ('KAINAN',        60,    61),
    ('GOBO',          90,    91),
    ('KII_TANABE',    135,   137),
    ('SHIRAHAMA',     145,   147),
    ('SUSAMI',        167,   168),
    ('KUSHIMOTO',     195,   196),
    ('KII_KATSUURA',  220,   221),
    ('SHINGU',        240,   None),
]
FULL_UP = [
    ('SHINGU',        None,  0),
    ('KII_KATSUURA',  19,    20),
    ('KUSHIMOTO',     44,    45),
    ('SUSAMI',        72,    73),
    ('SHIRAHAMA',     93,    95),
    ('KII_TANABE',    103,   105),
    ('GOBO',          149,   150),
    ('KAINAN',        179,   180),
    ('WAKAYAMA',      188,   190),
    ('TENNOJI',       223,   225),
    ('SHIN_OSAKA',    240,   None),
]

SHIRAHAMA_DOWN = [
    ('SHIN_OSAKA',    None,  0),
    ('TENNOJI',       15,    17),
    ('WAKAYAMA',      50,    52),
    ('KAINAN',        60,    61),
    ('GOBO',          90,    91),
    ('KII_TANABE',    135,   137),
    ('SHIRAHAMA',     145,   None),
]
SHIRAHAMA_UP = [
    ('SHIRAHAMA',     None,  0),
    ('KII_TANABE',    8,     10),
    ('GOBO',          54,    55),
    ('KAINAN',        84,    85),
    ('WAKAYAMA',      93,    95),
    ('TENNOJI',       128,   130),
    ('SHIN_OSAKA',    145,   None),
]

FULL_WEEKDAY_DOWN = ['07:15', '09:15', '11:15', '13:15', '16:15']
FULL_WEEKDAY_UP   = ['06:45', '08:45', '10:45', '14:45', '16:45']
FULL_HOLIDAY_DOWN = FULL_WEEKDAY_DOWN
FULL_HOLIDAY_UP   = FULL_WEEKDAY_UP

SHIRAHAMA_WEEKDAY_DOWN = [
    '07:45', '08:15', '08:45',
    '10:15', '11:45',
    '12:45', '13:45', '14:15',
    '15:15', '15:45',
    '17:15', '18:15',
    '19:15', '20:15',
    '21:15',
]
SHIRAHAMA_WEEKDAY_UP = [
    '07:00', '07:30',
    '09:30', '10:30',
    '11:30', '12:30',
    '13:30', '14:30',
    '15:30', '16:00',
    '17:30',
    '18:30',
    '19:30',
    '20:30',
    '21:00',
]
SHIRAHAMA_HOLIDAY_DOWN = SHIRAHAMA_WEEKDAY_DOWN
SHIRAHAMA_HOLIDAY_UP = SHIRAHAMA_WEEKDAY_UP


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

    emit('KUROSHIO_S', FULL_WEEKDAY_DOWN, FULL_DOWN, 'down', 'くろしお(新宮){n}', trains, sched_wd, 1)
    emit('KUROSHIO_S', FULL_WEEKDAY_UP,   FULL_UP,   'up',   'くろしお(新宮){n}', trains, sched_wd, 2)
    emit_schedule_only('KUROSHIO_S', FULL_HOLIDAY_DOWN, FULL_DOWN, sched_hd, 1)
    emit_schedule_only('KUROSHIO_S', FULL_HOLIDAY_UP,   FULL_UP,   sched_hd, 2)

    emit('KUROSHIO_H', SHIRAHAMA_WEEKDAY_DOWN, SHIRAHAMA_DOWN, 'down', 'くろしお(白浜){n}', trains, sched_wd, 1)
    emit('KUROSHIO_H', SHIRAHAMA_WEEKDAY_UP,   SHIRAHAMA_UP,   'up',   'くろしお(白浜){n}', trains, sched_wd, 2)
    emit_schedule_only('KUROSHIO_H', SHIRAHAMA_HOLIDAY_DOWN, SHIRAHAMA_DOWN, sched_hd, 1)
    emit_schedule_only('KUROSHIO_H', SHIRAHAMA_HOLIDAY_UP,   SHIRAHAMA_UP,   sched_hd, 2)

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
    wd = len(FULL_WEEKDAY_DOWN) + len(FULL_WEEKDAY_UP) + len(SHIRAHAMA_WEEKDAY_DOWN) + len(SHIRAHAMA_WEEKDAY_UP)
    hd = len(FULL_HOLIDAY_DOWN) + len(FULL_HOLIDAY_UP) + len(SHIRAHAMA_HOLIDAY_DOWN) + len(SHIRAHAMA_HOLIDAY_UP)
    print(f'weekday: {wd}本')
    print(f'holiday: {hd}本')


if __name__ == '__main__':
    main()
