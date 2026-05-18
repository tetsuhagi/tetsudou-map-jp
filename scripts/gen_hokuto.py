#!/usr/bin/env python3
"""
Generate 北斗 timetable.

Real 2024 dia:
- 北斗: ~12往復/方向/日
- 函館→札幌 ~3h37 (最速)

Stop intervals from 函館:
  HAKODATE             +0:00 dep
  SHIN_HAKODATE_HOKUTO +0:16 arr / +0:17 dep
  MORI                 +0:45 arr / +0:46 dep
  OSHAMAMBE            +1:22 arr / +1:23 dep
  HIGASHI_MURORAN      +2:23 arr / +2:25 dep
  TOMAKOMAI            +2:55 arr / +2:56 dep
  MINAMI_CHITOSE       +3:20 arr / +3:21 dep
  SAPPORO              +3:37 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HOKUTO')

STOPS_DOWN = [
    ('HAKODATE',             None,  0),
    ('SHIN_HAKODATE_HOKUTO', 16,    17),
    ('MORI',                 45,    46),
    ('OSHAMAMBE',            82,    83),
    ('HIGASHI_MURORAN',      143,   145),
    ('TOMAKOMAI',            175,   176),
    ('MINAMI_CHITOSE',       200,   201),
    ('SAPPORO',              217,   None),
]
STOPS_UP = [
    ('SAPPORO',              None,  0),
    ('MINAMI_CHITOSE',       16,    17),
    ('TOMAKOMAI',            41,    42),
    ('HIGASHI_MURORAN',      72,    74),
    ('OSHAMAMBE',            134,   135),
    ('MORI',                 171,   172),
    ('SHIN_HAKODATE_HOKUTO', 200,   201),
    ('HAKODATE',             217,   None),
]

WEEKDAY_DOWN_DEPS = [
    '06:00', '07:30',
    '09:08', '10:53',
    '12:43', '14:13',
    '15:43', '17:13',
    '18:43',
    '20:23',
    '21:30',
]
WEEKDAY_UP_DEPS = [
    '06:00', '07:30',
    '09:13', '10:58',
    '12:43', '14:18',
    '15:48', '17:18',
    '18:48',
    '20:28',
    '21:33',
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

    emit('HOKUTO', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', '北斗{n}', trains, sched_wd, 1)
    emit('HOKUTO', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   '北斗{n}', trains, sched_wd, 2)
    emit_schedule_only('HOKUTO', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HOKUTO', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
