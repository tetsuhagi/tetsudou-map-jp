#!/usr/bin/env python3
"""
Generate いなほ timetable.

Real 2024 dia:
- いなほ: ~7-8往復/方向/日 (新潟-秋田 or 新潟-酒田)
- 新潟→秋田 ~3h30

Stop intervals from 新潟:
  NIIGATA    +0:00 dep
  SHIBATA    +0:25 arr / +0:26 dep
  MURAKAMI   +0:55 arr / +0:56 dep
  TSURUOKA   +1:50 arr / +1:51 dep
  SAKATA     +2:10 arr / +2:11 dep
  UGO_HONJO  +3:00 arr / +3:01 dep
  AKITA      +3:30 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'INAHO')

FULL_DOWN = [
    ('NIIGATA',    None,  0),
    ('SHIBATA',    25,    26),
    ('MURAKAMI',   55,    56),
    ('TSURUOKA',   110,   111),
    ('SAKATA',     130,   131),
    ('UGO_HONJO',  180,   181),
    ('AKITA',      210,   None),
]
FULL_UP = [
    ('AKITA',      None,  0),
    ('UGO_HONJO',  29,    30),
    ('SAKATA',     79,    80),
    ('TSURUOKA',   99,    100),
    ('MURAKAMI',   154,   155),
    ('SHIBATA',    184,   185),
    ('NIIGATA',    210,   None),
]

SHORT_DOWN = [  # 新潟-酒田
    ('NIIGATA',    None,  0),
    ('SHIBATA',    25,    26),
    ('MURAKAMI',   55,    56),
    ('TSURUOKA',   110,   111),
    ('SAKATA',     130,   None),
]
SHORT_UP = [
    ('SAKATA',     None,  0),
    ('TSURUOKA',   19,    20),
    ('MURAKAMI',   74,    75),
    ('SHIBATA',    104,   105),
    ('NIIGATA',    130,   None),
]

FULL_WEEKDAY_DOWN = ['07:50', '11:35', '14:20', '17:42']
FULL_WEEKDAY_UP   = ['06:25', '09:43', '13:25', '17:25']
SHORT_WEEKDAY_DOWN = ['09:36', '13:20', '15:54', '19:14']
SHORT_WEEKDAY_UP   = ['07:38', '11:08', '14:38', '18:08']


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


def main():
    trains = []
    sched = []

    emit('INAHO_F', FULL_WEEKDAY_DOWN, FULL_DOWN, 'down', 'いなほ(秋田){n}', trains, sched, 1)
    emit('INAHO_F', FULL_WEEKDAY_UP,   FULL_UP,   'up',   'いなほ(秋田){n}', trains, sched, 2)
    emit('INAHO_S', SHORT_WEEKDAY_DOWN, SHORT_DOWN, 'down', 'いなほ(酒田){n}', trains, sched, 1)
    emit('INAHO_S', SHORT_WEEKDAY_UP,   SHORT_UP,   'up',   'いなほ(酒田){n}', trains, sched, 2)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'trains.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,name,direction\n')
        for tid, name, direction in trains:
            f.write(f'{tid},{name},{direction}\n')

    with open(os.path.join(OUT_DIR, 'weekday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched:
            f.write(','.join(map(str, row)) + '\n')

    with open(os.path.join(OUT_DIR, 'holiday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched:
            f.write(','.join(map(str, row)) + '\n')

    down = sum(1 for _, _, d in trains if d == 'down')
    up = sum(1 for _, _, d in trains if d == 'up')
    print(f'trains.csv: {len(trains)}本 (下り {down}, 上り {up})')


if __name__ == '__main__':
    main()
