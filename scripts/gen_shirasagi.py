#!/usr/bin/env python3
"""
Generate しらさぎ timetable.

Real 2024 dia (敦賀延伸後):
- しらさぎ: ~16往復/方向/日
- 名古屋-岐阜-米原-長浜-敦賀 (~1h40)

Stop intervals from 名古屋:
  NAGOYA    +0:00 dep
  GIFU      +0:19 arr / +0:20 dep
  MAIBARA   +0:51 arr / +0:53 dep
  NAGAHAMA  +1:00 arr / +1:01 dep
  TSURUGA   +1:40 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHIRASAGI')

STOPS_DOWN = [
    ('NAGOYA',   None,  0),
    ('GIFU',     19,    20),
    ('MAIBARA',  51,    53),
    ('NAGAHAMA', 60,    61),
    ('TSURUGA',  100,   None),
]
STOPS_UP = [
    ('TSURUGA',  None,  0),
    ('NAGAHAMA', 39,    40),
    ('MAIBARA',  47,    49),
    ('GIFU',     80,    81),
    ('NAGOYA',   100,   None),
]

WEEKDAY_DOWN_DEPS = [
    '06:00', '07:00',
    '08:00', '09:00',
    '10:00', '11:00',
    '12:00', '13:00',
    '14:00', '15:00',
    '16:00', '17:00',
    '18:00', '19:00',
    '20:00', '21:00',
]
WEEKDAY_UP_DEPS = [
    '06:30', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30', '21:30',
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

    emit('SHIRASAGI', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'しらさぎ{n}', trains, sched_wd, 1)
    emit('SHIRASAGI', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'しらさぎ{n}', trains, sched_wd, 2)
    emit_schedule_only('SHIRASAGI', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHIRASAGI', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
