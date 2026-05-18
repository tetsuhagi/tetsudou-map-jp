#!/usr/bin/env python3
"""
Generate こうのとり timetable.

Real 2024 dia:
- こうのとり (城崎温泉): ~6往復 (新大阪→城崎温泉 ~2h30)
- こうのとり (福知山): ~7往復 (新大阪→福知山 ~1h25)

Stop intervals from 新大阪:
  SHIN_OSAKA      +0:00 dep
  AMAGASAKI       +0:08 arr / +0:09 dep
  TAKARAZUKA      +0:22 arr / +0:24 dep
  SANDA           +0:35 arr / +0:36 dep
  SASAYAMAGUCHI   +0:55 arr / +0:56 dep
  FUKUCHIYAMA     +1:25 arr / +1:27 dep
  WADAYAMA        +1:50 arr / +1:51 dep
  YOKA            +2:05 arr / +2:06 dep
  TOYOOKA         +2:18 arr / +2:19 dep
  KINOSAKI_ONSEN  +2:30 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KOUNOTORI')

FULL_DOWN = [
    ('SHIN_OSAKA',     None,  0),
    ('AMAGASAKI',      8,     9),
    ('TAKARAZUKA',     22,    24),
    ('SANDA',          35,    36),
    ('SASAYAMAGUCHI',  55,    56),
    ('FUKUCHIYAMA',    85,    87),
    ('WADAYAMA',       110,   111),
    ('YOKA',           125,   126),
    ('TOYOOKA',        138,   139),
    ('KINOSAKI_ONSEN', 150,   None),
]
FULL_UP = [
    ('KINOSAKI_ONSEN', None,  0),
    ('TOYOOKA',        11,    12),
    ('YOKA',           24,    25),
    ('WADAYAMA',       39,    40),
    ('FUKUCHIYAMA',    63,    65),
    ('SASAYAMAGUCHI',  94,    95),
    ('SANDA',          114,   115),
    ('TAKARAZUKA',     126,   128),
    ('AMAGASAKI',      141,   142),
    ('SHIN_OSAKA',     150,   None),
]

SHORT_DOWN = [
    ('SHIN_OSAKA',     None,  0),
    ('AMAGASAKI',      8,     9),
    ('TAKARAZUKA',     22,    24),
    ('SANDA',          35,    36),
    ('SASAYAMAGUCHI',  55,    56),
    ('FUKUCHIYAMA',    85,    None),
]
SHORT_UP = [
    ('FUKUCHIYAMA',    None,  0),
    ('SASAYAMAGUCHI',  29,    30),
    ('SANDA',          49,    50),
    ('TAKARAZUKA',     61,    63),
    ('AMAGASAKI',      76,    77),
    ('SHIN_OSAKA',     85,    None),
]

FULL_WEEKDAY_DOWN = ['07:14', '09:14', '11:14', '14:14', '17:14', '19:14']
FULL_WEEKDAY_UP   = ['06:00', '09:00', '12:00', '14:00', '16:00', '18:00']
FULL_HOLIDAY_DOWN = FULL_WEEKDAY_DOWN
FULL_HOLIDAY_UP   = FULL_WEEKDAY_UP

SHORT_WEEKDAY_DOWN = ['08:14', '10:14', '12:14', '13:14', '15:14', '16:14', '18:14']
SHORT_WEEKDAY_UP   = ['07:00', '08:00', '10:00', '11:00', '13:00', '15:00', '17:00']
SHORT_HOLIDAY_DOWN = SHORT_WEEKDAY_DOWN
SHORT_HOLIDAY_UP   = SHORT_WEEKDAY_UP


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

    emit('KOUNOTORI_F', FULL_WEEKDAY_DOWN, FULL_DOWN, 'down', 'こうのとり(城崎){n}', trains, sched_wd, 1)
    emit('KOUNOTORI_F', FULL_WEEKDAY_UP,   FULL_UP,   'up',   'こうのとり(城崎){n}', trains, sched_wd, 2)
    emit_schedule_only('KOUNOTORI_F', FULL_HOLIDAY_DOWN, FULL_DOWN, sched_hd, 1)
    emit_schedule_only('KOUNOTORI_F', FULL_HOLIDAY_UP,   FULL_UP,   sched_hd, 2)

    emit('KOUNOTORI_S', SHORT_WEEKDAY_DOWN, SHORT_DOWN, 'down', 'こうのとり(福知山){n}', trains, sched_wd, 1)
    emit('KOUNOTORI_S', SHORT_WEEKDAY_UP,   SHORT_UP,   'up',   'こうのとり(福知山){n}', trains, sched_wd, 2)
    emit_schedule_only('KOUNOTORI_S', SHORT_HOLIDAY_DOWN, SHORT_DOWN, sched_hd, 1)
    emit_schedule_only('KOUNOTORI_S', SHORT_HOLIDAY_UP,   SHORT_UP,   sched_hd, 2)

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
