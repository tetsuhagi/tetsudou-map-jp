#!/usr/bin/env python3
"""
Generate 上越新幹線 timetable (とき + たにがわ).

Real 2024 dia:
- とき (最速): 約25本/方向, 大宮-高崎-長岡-燕三条-新潟
- たにがわ: 約10本/方向, 大宮-熊谷-本庄早稲田-高崎-上毛高原-越後湯沢 (短距離)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'JOETSU_SHINKANSEN')

TOKI_STOPS_DOWN = [
    ('OMIYA',         None,  0),
    ('TAKASAKI',      25,    26),
    ('NAGAOKA',       66,    68),
    ('TSUBAME_SANJO', 78,    79),
    ('NIIGATA',       90,    None),
]

TOKI_STOPS_UP = [
    ('NIIGATA',       None,  0),
    ('TSUBAME_SANJO', 12,    13),
    ('NAGAOKA',       23,    25),
    ('TAKASAKI',      65,    66),
    ('OMIYA',         90,    None),
]

TANIGAWA_STOPS_DOWN = [
    ('OMIYA',          None,  0),
    ('KUMAGAYA',       11,    12),
    ('HONJO_WASEDA',   21,    22),
    ('TAKASAKI',       31,    32),
    ('JOMOKOGEN',      52,    53),
    ('ECHIGO_YUZAWA',  70,    None),
]

TANIGAWA_STOPS_UP = [
    ('ECHIGO_YUZAWA',  None,  0),
    ('JOMOKOGEN',      17,    18),
    ('TAKASAKI',       38,    39),
    ('HONJO_WASEDA',   48,    49),
    ('KUMAGAYA',       58,    59),
    ('OMIYA',          70,    None),
]

TOKI_WEEKDAY_DOWN = [
    '06:33',
    '07:25', '07:48',
    '08:13', '08:33', '08:48',
    '09:13', '09:33',
    '10:23',
    '11:33',
    '12:23',
    '13:23',
    '14:23',
    '15:23',
    '16:23',
    '17:13', '17:33', '17:48',
    '18:23', '18:48',
    '19:23',
    '20:23',
    '21:23',
    '22:25',
]
TOKI_WEEKDAY_UP = [
    '06:08',
    '07:00', '07:33',
    '08:00', '08:23',
    '09:00', '09:23',
    '10:00',
    '11:00',
    '12:00',
    '13:00',
    '14:00',
    '15:00',
    '16:00', '16:38',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00',
    '21:00',
]
TOKI_HOLIDAY_DOWN = [
    '06:33',
    '07:25', '07:48',
    '08:13', '08:33', '08:48',
    '09:13', '09:33',
    '10:23',
    '11:33', '12:23', '13:23', '14:23', '15:23', '16:23',
    '17:13', '17:33',
    '18:23',
    '19:23', '20:23', '21:23',
]
TOKI_HOLIDAY_UP = [
    '06:08',
    '07:00',
    '08:00', '08:23',
    '09:00',
    '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '20:00', '21:00',
]

TANIGAWA_WEEKDAY_DOWN = [
    '07:08', '08:08', '09:08',
    '10:48', '12:48', '14:48', '16:48',
    '18:08', '19:08', '20:48',
]
TANIGAWA_WEEKDAY_UP = [
    '06:45', '07:45',
    '09:30', '11:30', '13:30', '15:30',
    '17:30', '18:30', '19:30', '20:30',
]
TANIGAWA_HOLIDAY_DOWN = [
    '07:08', '08:08', '09:08',
    '10:48', '12:48', '14:48', '16:48',
    '18:08', '19:08',
]
TANIGAWA_HOLIDAY_UP = [
    '06:45', '07:45',
    '09:30', '11:30', '13:30', '15:30',
    '17:30', '18:30', '19:30',
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

    emit('TOKI', TOKI_WEEKDAY_DOWN, TOKI_STOPS_DOWN, 'down', 'とき{n}', trains, sched_wd, 1)
    emit('TOKI', TOKI_WEEKDAY_UP,   TOKI_STOPS_UP,   'up',   'とき{n}', trains, sched_wd, 2)
    emit_schedule_only('TOKI', TOKI_HOLIDAY_DOWN, TOKI_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TOKI', TOKI_HOLIDAY_UP,   TOKI_STOPS_UP,   sched_hd, 2)

    emit('TANIGAWA', TANIGAWA_WEEKDAY_DOWN, TANIGAWA_STOPS_DOWN, 'down', 'たにがわ{n}', trains, sched_wd, 1)
    emit('TANIGAWA', TANIGAWA_WEEKDAY_UP,   TANIGAWA_STOPS_UP,   'up',   'たにがわ{n}', trains, sched_wd, 2)
    emit_schedule_only('TANIGAWA', TANIGAWA_HOLIDAY_DOWN, TANIGAWA_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TANIGAWA', TANIGAWA_HOLIDAY_UP,   TANIGAWA_STOPS_UP,   sched_hd, 2)

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
    wd_d = len(TOKI_WEEKDAY_DOWN) + len(TANIGAWA_WEEKDAY_DOWN)
    wd_u = len(TOKI_WEEKDAY_UP) + len(TANIGAWA_WEEKDAY_UP)
    hd_d = len(TOKI_HOLIDAY_DOWN) + len(TANIGAWA_HOLIDAY_DOWN)
    hd_u = len(TOKI_HOLIDAY_UP) + len(TANIGAWA_HOLIDAY_UP)
    print(f'weekday: 下 {wd_d} + 上 {wd_u} = {wd_d + wd_u}本')
    print(f'holiday: 下 {hd_d} + 上 {hd_u} = {hd_d + hd_u}本')


if __name__ == '__main__':
    main()
