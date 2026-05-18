#!/usr/bin/env python3
"""
Generate おおぞら・とかち timetable.

Real 2024 dia:
- おおぞら: 札幌-釧路 ~6往復/方向 (~4h)
- とかち: 札幌-帯広 ~5往復/方向 (~2h40)

Stop intervals from 札幌:
  SAPPORO         +0:00 dep
  MINAMI_CHITOSE  +0:33 arr / +0:34 dep
  SHIN_YUBARI     +0:70 arr / +0:71 dep
  TOMAMU          +0:90 arr / +0:91 dep
  SHINTOKU        +2:10 arr / +2:11 dep
  OBIHIRO         +2:40 arr / +2:43 dep
  IKEDA           +3:05 arr / +3:06 dep
  KUSHIRO         +4:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'OZORA_TOKACHI')

OZORA_DOWN = [
    ('SAPPORO',         None,  0),
    ('MINAMI_CHITOSE',  33,    34),
    ('SHIN_YUBARI',     70,    71),
    ('TOMAMU',          90,    91),
    ('SHINTOKU',        130,   131),
    ('OBIHIRO',         160,   163),
    ('IKEDA',           185,   186),
    ('KUSHIRO',         240,   None),
]
OZORA_UP = [
    ('KUSHIRO',         None,  0),
    ('IKEDA',           54,    55),
    ('OBIHIRO',         77,    80),
    ('SHINTOKU',        109,   110),
    ('TOMAMU',          149,   150),
    ('SHIN_YUBARI',     169,   170),
    ('MINAMI_CHITOSE',  206,   207),
    ('SAPPORO',         240,   None),
]

TOKACHI_DOWN = [
    ('SAPPORO',         None,  0),
    ('MINAMI_CHITOSE',  33,    34),
    ('SHIN_YUBARI',     70,    71),
    ('TOMAMU',          90,    91),
    ('SHINTOKU',        130,   131),
    ('OBIHIRO',         160,   None),
]
TOKACHI_UP = [
    ('OBIHIRO',         None,  0),
    ('SHINTOKU',        29,    30),
    ('TOMAMU',          69,    70),
    ('SHIN_YUBARI',     89,    90),
    ('MINAMI_CHITOSE',  126,   127),
    ('SAPPORO',         160,   None),
]

OZORA_WEEKDAY_DOWN = ['06:53', '08:21', '11:35', '13:39', '17:08', '19:48']
OZORA_WEEKDAY_UP   = ['05:55', '08:14', '10:34', '13:00', '16:05', '19:17']
OZORA_HOLIDAY_DOWN = OZORA_WEEKDAY_DOWN
OZORA_HOLIDAY_UP   = OZORA_WEEKDAY_UP

TOKACHI_WEEKDAY_DOWN = ['07:34', '10:38', '14:48', '16:18', '19:11']
TOKACHI_WEEKDAY_UP   = ['06:48', '10:50', '13:50', '16:50', '18:55']
TOKACHI_HOLIDAY_DOWN = TOKACHI_WEEKDAY_DOWN
TOKACHI_HOLIDAY_UP   = TOKACHI_WEEKDAY_UP


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

    emit('OZORA', OZORA_WEEKDAY_DOWN, OZORA_DOWN, 'down', 'おおぞら{n}', trains, sched_wd, 1)
    emit('OZORA', OZORA_WEEKDAY_UP,   OZORA_UP,   'up',   'おおぞら{n}', trains, sched_wd, 2)
    emit_schedule_only('OZORA', OZORA_HOLIDAY_DOWN, OZORA_DOWN, sched_hd, 1)
    emit_schedule_only('OZORA', OZORA_HOLIDAY_UP,   OZORA_UP,   sched_hd, 2)

    emit('TOKACHI', TOKACHI_WEEKDAY_DOWN, TOKACHI_DOWN, 'down', 'とかち{n}', trains, sched_wd, 1)
    emit('TOKACHI', TOKACHI_WEEKDAY_UP,   TOKACHI_UP,   'up',   'とかち{n}', trains, sched_wd, 2)
    emit_schedule_only('TOKACHI', TOKACHI_HOLIDAY_DOWN, TOKACHI_DOWN, sched_hd, 1)
    emit_schedule_only('TOKACHI', TOKACHI_HOLIDAY_UP,   TOKACHI_UP,   sched_hd, 2)

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
