#!/usr/bin/env python3
"""
Generate サンダーバード timetable.

Real 2024 dia (敦賀延伸後):
- サンダーバード: ~22-23往復/方向/日
- 大阪-新大阪-京都-敦賀 (4駅停車)
- 大阪→敦賀 ~1h17

Stop intervals from 大阪:
  OSAKA       +0:00 dep
  SHIN_OSAKA  +0:04 arr / +0:05 dep
  KYOTO       +0:26 arr / +0:27 dep
  TSURUGA     +1:17 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'THUNDERBIRD')

STOPS_DOWN = [
    ('OSAKA',      None,  0),
    ('SHIN_OSAKA', 4,     5),
    ('KYOTO',      26,    27),
    ('TSURUGA',    77,    None),
]
STOPS_UP = [
    ('TSURUGA',    None,  0),
    ('KYOTO',      50,    52),
    ('SHIN_OSAKA', 73,    74),
    ('OSAKA',      77,    None),
]

WEEKDAY_DOWN_DEPS = [
    '06:00', '06:42',
    '07:12', '07:42',
    '08:12', '08:42',
    '09:12', '09:42',
    '10:42',
    '11:42',
    '12:42',
    '13:42',
    '14:42',
    '15:42',
    '16:42',
    '17:12', '17:42',
    '18:12', '18:42',
    '19:12', '19:42',
    '20:42',
    '22:00',
]
WEEKDAY_UP_DEPS = [
    '06:00',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:30',
    '10:30',
    '11:30',
    '12:30',
    '13:30',
    '14:30',
    '15:30',
    '16:30',
    '17:30',
    '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:00',
]
HOLIDAY_DOWN_DEPS = [
    '06:00', '06:42',
    '07:12', '07:42',
    '08:12', '08:42',
    '09:42',
    '10:42',
    '11:42',
    '12:42',
    '13:42',
    '14:42',
    '15:42',
    '16:42',
    '17:12', '17:42',
    '18:42', '19:42',
    '20:42',
    '22:00',
]
HOLIDAY_UP_DEPS = [
    '06:00',
    '07:00', '07:30',
    '08:30',
    '09:30',
    '10:30',
    '11:30',
    '12:30',
    '13:30',
    '14:30',
    '15:30',
    '16:30',
    '17:30',
    '18:30',
    '19:30',
    '20:30',
    '21:00',
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

    emit('THUNDERBIRD', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'サンダーバード{n}', trains, sched_wd, 1)
    emit('THUNDERBIRD', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'サンダーバード{n}', trains, sched_wd, 2)
    emit_schedule_only('THUNDERBIRD', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('THUNDERBIRD', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
