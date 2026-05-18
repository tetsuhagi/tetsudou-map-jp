#!/usr/bin/env python3
"""
Generate オホーツク・大雪 timetable.

Real 2024 dia:
- オホーツク (札幌-網走): ~2往復/方向 (~5h30)
- 大雪 (旭川-網走): ~2往復/方向 (~4h)

Stop intervals from 札幌 (オホーツク):
  SAPPORO    +0:00 dep
  ASAHIKAWA  +1:25 arr / +1:30 dep
  KAMIKAWA   +2:17 arr / +2:18 dep
  ENGARU     +3:20 arr / +3:21 dep
  KITAMI     +4:14 arr / +4:16 dep
  ABASHIRI   +5:30 arr

Stop intervals from 旭川 (大雪):
  ASAHIKAWA  +0:00 dep
  KAMIKAWA   +0:52 arr / +0:53 dep
  ENGARU     +1:55 arr / +1:56 dep
  KITAMI     +2:49 arr / +2:51 dep
  ABASHIRI   +4:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'OKHOTSK_TAISETSU')

OKHOTSK_DOWN = [
    ('SAPPORO',   None,  0),
    ('ASAHIKAWA', 85,    90),
    ('KAMIKAWA',  137,   138),
    ('ENGARU',    200,   201),
    ('KITAMI',    254,   256),
    ('ABASHIRI',  330,   None),
]
OKHOTSK_UP = [
    ('ABASHIRI',  None,  0),
    ('KITAMI',    74,    76),
    ('ENGARU',    129,   130),
    ('KAMIKAWA',  192,   193),
    ('ASAHIKAWA', 240,   245),
    ('SAPPORO',   330,   None),
]

TAISETSU_DOWN = [
    ('ASAHIKAWA', None,  0),
    ('KAMIKAWA',  52,    53),
    ('ENGARU',    115,   116),
    ('KITAMI',    169,   171),
    ('ABASHIRI',  240,   None),
]
TAISETSU_UP = [
    ('ABASHIRI',  None,  0),
    ('KITAMI',    69,    71),
    ('ENGARU',    124,   125),
    ('KAMIKAWA',  187,   188),
    ('ASAHIKAWA', 240,   None),
]

OKHOTSK_WEEKDAY_DOWN = ['06:56', '17:30']
OKHOTSK_WEEKDAY_UP   = ['08:05', '17:25']
TAISETSU_WEEKDAY_DOWN = ['11:05', '17:25']
TAISETSU_WEEKDAY_UP   = ['07:09', '13:30']


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

    emit('OKHOTSK', OKHOTSK_WEEKDAY_DOWN, OKHOTSK_DOWN, 'down', 'オホーツク{n}', trains, sched, 1)
    emit('OKHOTSK', OKHOTSK_WEEKDAY_UP,   OKHOTSK_UP,   'up',   'オホーツク{n}', trains, sched, 2)
    emit('TAISETSU', TAISETSU_WEEKDAY_DOWN, TAISETSU_DOWN, 'down', '大雪{n}', trains, sched, 1)
    emit('TAISETSU', TAISETSU_WEEKDAY_UP,   TAISETSU_UP,   'up',   '大雪{n}', trains, sched, 2)

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
