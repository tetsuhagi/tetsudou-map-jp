#!/usr/bin/env python3
"""
Generate ひだ timetable.

Real 2024 dia:
- ひだ: ~10往復/方向/日 (主に名古屋-富山 or 名古屋-高山)
- 名古屋→富山 ~4h

Stop intervals from 名古屋:
  NAGOYA          +0:00 dep
  GIFU            +0:19 arr / +0:20 dep
  MINO_OTA        +0:45 arr / +0:46 dep
  GERO            +1:40 arr / +1:42 dep
  TAKAYAMA        +2:20 arr / +2:25 dep
  HIDA_FURUKAWA   +2:38 arr / +2:39 dep
  TOYAMA          +4:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HIDA')

STOPS_DOWN = [
    ('NAGOYA',        None,  0),
    ('GIFU',          19,    20),
    ('MINO_OTA',      45,    46),
    ('GERO',          100,   102),
    ('TAKAYAMA',      140,   145),
    ('HIDA_FURUKAWA', 158,   159),
    ('TOYAMA',        240,   None),
]
STOPS_UP = [
    ('TOYAMA',        None,  0),
    ('HIDA_FURUKAWA', 81,    82),
    ('TAKAYAMA',      95,    100),
    ('GERO',          138,   140),
    ('MINO_OTA',      194,   195),
    ('GIFU',          220,   221),
    ('NAGOYA',        240,   None),
]

WEEKDAY_DOWN_DEPS = [
    '06:38',
    '07:43',
    '09:39',
    '11:43',
    '12:48',
    '14:48',
    '15:48',
    '17:03',
    '18:08',
    '20:08',
]
WEEKDAY_UP_DEPS = [
    '06:23',
    '08:32',
    '09:51',
    '12:36',
    '13:51',
    '14:36',
    '15:51',
    '17:51',
    '18:51',
    '20:08',
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

    emit('HIDA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ひだ{n}', trains, sched_wd, 1)
    emit('HIDA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ひだ{n}', trains, sched_wd, 2)
    emit_schedule_only('HIDA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HIDA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
