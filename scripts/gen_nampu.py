#!/usr/bin/env python3
"""
Generate 南風 timetable (岡山-高知).

Real 2024 dia:
- 南風: ~16往復/方向, 岡山→高知 ~2h35

Stop intervals from 岡山:
  OKAYAMA      +0:00 dep
  KOJIMA       +0:18 arr / +0:19 dep
  UTAZU        +0:28 arr / +0:29 dep
  TADOTSU      +0:35 arr / +0:36 dep
  KOTOHIRA     +0:54 arr / +0:55 dep
  AWA_IKEDA    +1:19 arr / +1:20 dep
  TOSA_YAMADA  +2:12 arr / +2:13 dep
  KOCHI        +2:35 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'NANPU')

STOPS_DOWN = [
    ('OKAYAMA',     None,  0),
    ('KOJIMA',      18,    19),
    ('UTAZU',       28,    29),
    ('TADOTSU',     35,    36),
    ('KOTOHIRA',    54,    55),
    ('AWA_IKEDA',   79,    80),
    ('TOSA_YAMADA', 132,   133),
    ('KOCHI',       155,   None),
]
STOPS_UP = [
    ('KOCHI',       None,  0),
    ('TOSA_YAMADA', 22,    23),
    ('AWA_IKEDA',   75,    76),
    ('KOTOHIRA',    100,   101),
    ('TADOTSU',     119,   120),
    ('UTAZU',       126,   127),
    ('KOJIMA',      136,   137),
    ('OKAYAMA',     155,   None),
]

WEEKDAY_DOWN_DEPS = [
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
WEEKDAY_UP_DEPS = [
    '05:50', '06:50',
    '07:50', '08:50',
    '09:50', '10:50',
    '11:50', '12:50',
    '13:50', '14:50',
    '15:50', '16:50',
    '17:50', '18:50',
    '19:50',
    '21:00',
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

    emit('NANPU', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', '南風{n}', trains, sched_wd, 1)
    emit('NANPU', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   '南風{n}', trains, sched_wd, 2)
    emit_schedule_only('NANPU', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('NANPU', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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


if __name__ == '__main__':
    main()
