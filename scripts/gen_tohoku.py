#!/usr/bin/env python3
"""
Generate 東北新幹線 timetable (はやぶさ + やまびこ + なすの).

Real 2024 dia:
- はやぶさ (最速): ~29本/方向 (東京-上野-大宮-仙台-盛岡-新青森)
- やまびこ (標準): ~25本/方向 (東京-上野-大宮-宇都宮-郡山-福島-仙台, 一部盛岡延長)
- なすの (区間): ~10本/方向 (東京-上野-大宮-小山-宇都宮-那須塩原)
- つばさ (山形新幹線) は別路線扱い
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TOHOKU_SHINKANSEN')

HAYABUSA_STOPS_DOWN = [
    ('TOKYO',       None,  0),
    ('UENO',        6,     7),
    ('OMIYA',       25,    26),
    ('SENDAI',      88,    89),
    ('MORIOKA',     130,   132),
    ('SHIN_AOMORI', 180,   None),
]
HAYABUSA_STOPS_UP = [
    ('SHIN_AOMORI', None,  0),
    ('MORIOKA',     48,    50),
    ('SENDAI',      91,    92),
    ('OMIYA',       154,   155),
    ('UENO',        174,   175),
    ('TOKYO',       180,   None),
]

YAMABIKO_STOPS_DOWN = [
    ('TOKYO',      None,  0),
    ('UENO',       6,     7),
    ('OMIYA',      25,    26),
    ('UTSUNOMIYA', 67,    69),
    ('KORIYAMA',   110,   112),
    ('FUKUSHIMA',  132,   134),
    ('SENDAI',     167,   None),
]
YAMABIKO_STOPS_UP = [
    ('SENDAI',     None,  0),
    ('FUKUSHIMA',  33,    35),
    ('KORIYAMA',   55,    57),
    ('UTSUNOMIYA', 98,    100),
    ('OMIYA',      141,   142),
    ('UENO',       160,   161),
    ('TOKYO',      167,   None),
]

NASUNO_STOPS_DOWN = [
    ('TOKYO',         None,  0),
    ('UENO',          6,     7),
    ('OMIYA',         25,    26),
    ('OYAMA',         53,    54),
    ('UTSUNOMIYA',    70,    71),
    ('NASU_SHIOBARA', 88,    None),
]
NASUNO_STOPS_UP = [
    ('NASU_SHIOBARA', None,  0),
    ('UTSUNOMIYA',    17,    18),
    ('OYAMA',         34,    35),
    ('OMIYA',         62,    63),
    ('UENO',          81,    82),
    ('TOKYO',         88,    None),
]

HAYABUSA_WEEKDAY_DOWN = [
    '06:32', '07:08', '07:20', '07:32',
    '08:08', '08:20', '08:32',
    '09:08', '09:36',
    '10:20', '10:36',
    '11:36',
    '12:36',
    '13:36',
    '14:36',
    '15:08', '15:36',
    '16:08', '16:36',
    '17:08', '17:36',
    '18:08', '18:36',
    '19:08', '19:36',
    '20:08', '20:36',
    '21:08', '21:20',
]
HAYABUSA_WEEKDAY_UP = [
    '06:11', '07:00', '07:46',
    '08:30',
    '09:00', '09:34',
    '10:00', '10:36',
    '11:00', '11:36',
    '12:00', '12:36',
    '13:00', '13:36',
    '14:00', '14:36',
    '15:00', '15:36',
    '16:00', '16:36',
    '17:00', '17:36',
    '18:00',
    '19:09',
    '20:09',
    '21:00',
]
HAYABUSA_HOLIDAY_DOWN = [
    '06:32', '07:08', '07:20', '07:32',
    '08:08', '08:32',
    '09:08', '09:36',
    '10:20', '10:36',
    '11:36', '12:36', '13:36', '14:36',
    '15:36',
    '16:08', '16:36',
    '17:08', '17:36',
    '18:08', '18:36',
    '19:08', '19:36',
    '20:08', '20:36',
    '21:08', '21:20',
]
HAYABUSA_HOLIDAY_UP = [
    '06:11', '07:00', '07:46',
    '08:30',
    '09:00', '09:34',
    '10:00', '10:36',
    '11:00', '11:36',
    '12:00', '12:36',
    '13:00', '13:36',
    '14:00', '14:36',
    '15:00', '15:36',
    '16:00', '16:36',
    '17:00', '17:36',
    '18:00',
    '19:09',
    '20:09',
]

YAMABIKO_WEEKDAY_DOWN = [
    '06:08', '06:44',
    '07:44',
    '08:44',
    '09:44',
    '10:08', '10:44',
    '11:08', '11:44',
    '12:08', '12:44',
    '13:08', '13:44',
    '14:08', '14:44',
    '15:44',
    '16:44',
    '17:08', '17:44',
    '18:08', '18:44',
    '19:08', '19:44',
    '20:08', '20:44',
    '21:44',
]
YAMABIKO_WEEKDAY_UP = [
    '06:14', '06:54',
    '07:51',
    '08:51',
    '09:51',
    '10:14', '10:51',
    '11:14', '11:51',
    '12:14', '12:51',
    '13:14', '13:51',
    '14:14', '14:51',
    '15:14', '15:51',
    '16:14', '16:51',
    '17:14',
    '18:14',
    '19:14',
    '20:11',
    '21:18',
]
YAMABIKO_HOLIDAY_DOWN = [
    '06:08', '06:44',
    '07:44',
    '08:44',
    '09:44',
    '10:44',
    '11:44',
    '12:44',
    '13:44',
    '14:44',
    '15:44',
    '16:44',
    '17:08', '17:44',
    '18:08', '18:44',
    '19:08', '19:44',
    '20:08', '20:44',
    '21:44',
]
YAMABIKO_HOLIDAY_UP = [
    '06:14', '06:54',
    '07:51',
    '08:51',
    '09:51',
    '10:51',
    '11:51',
    '12:51',
    '13:51',
    '14:51',
    '15:14', '15:51',
    '16:14', '16:51',
    '17:14',
    '18:14',
    '19:14',
    '20:11',
    '21:18',
]

NASUNO_WEEKDAY_DOWN = [
    '06:18',
    '08:28',
    '10:28', '12:28', '14:28', '16:28',
    '18:28',
    '19:28', '20:28', '21:28', '22:28',
]
NASUNO_WEEKDAY_UP = [
    '06:34',
    '07:32',
    '08:32',
    '10:32', '12:32', '14:32',
    '16:32',
    '18:32', '20:32', '21:32',
]
NASUNO_HOLIDAY_DOWN = [
    '06:18',
    '08:28', '10:28', '12:28', '14:28', '16:28',
    '18:28', '19:28', '20:28', '21:28',
]
NASUNO_HOLIDAY_UP = [
    '06:34',
    '08:32',
    '10:32', '12:32', '14:32', '16:32',
    '18:32', '20:32',
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

    emit('HAYABUSA', HAYABUSA_WEEKDAY_DOWN, HAYABUSA_STOPS_DOWN, 'down', 'はやぶさ{n}', trains, sched_wd, 1)
    emit('HAYABUSA', HAYABUSA_WEEKDAY_UP,   HAYABUSA_STOPS_UP,   'up',   'はやぶさ{n}', trains, sched_wd, 2)
    emit_schedule_only('HAYABUSA', HAYABUSA_HOLIDAY_DOWN, HAYABUSA_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HAYABUSA', HAYABUSA_HOLIDAY_UP,   HAYABUSA_STOPS_UP,   sched_hd, 2)

    emit('YAMABIKO', YAMABIKO_WEEKDAY_DOWN, YAMABIKO_STOPS_DOWN, 'down', 'やまびこ{n}', trains, sched_wd, 1)
    emit('YAMABIKO', YAMABIKO_WEEKDAY_UP,   YAMABIKO_STOPS_UP,   'up',   'やまびこ{n}', trains, sched_wd, 2)
    emit_schedule_only('YAMABIKO', YAMABIKO_HOLIDAY_DOWN, YAMABIKO_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('YAMABIKO', YAMABIKO_HOLIDAY_UP,   YAMABIKO_STOPS_UP,   sched_hd, 2)

    emit('NASUNO', NASUNO_WEEKDAY_DOWN, NASUNO_STOPS_DOWN, 'down', 'なすの{n}', trains, sched_wd, 1)
    emit('NASUNO', NASUNO_WEEKDAY_UP,   NASUNO_STOPS_UP,   'up',   'なすの{n}', trains, sched_wd, 2)
    emit_schedule_only('NASUNO', NASUNO_HOLIDAY_DOWN, NASUNO_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('NASUNO', NASUNO_HOLIDAY_UP,   NASUNO_STOPS_UP,   sched_hd, 2)

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
    wd_d = len(HAYABUSA_WEEKDAY_DOWN) + len(YAMABIKO_WEEKDAY_DOWN) + len(NASUNO_WEEKDAY_DOWN)
    wd_u = len(HAYABUSA_WEEKDAY_UP) + len(YAMABIKO_WEEKDAY_UP) + len(NASUNO_WEEKDAY_UP)
    hd_d = len(HAYABUSA_HOLIDAY_DOWN) + len(YAMABIKO_HOLIDAY_DOWN) + len(NASUNO_HOLIDAY_DOWN)
    hd_u = len(HAYABUSA_HOLIDAY_UP) + len(YAMABIKO_HOLIDAY_UP) + len(NASUNO_HOLIDAY_UP)
    print(f'weekday: 下 {wd_d} + 上 {wd_u} = {wd_d + wd_u}本')
    print(f'holiday: 下 {hd_d} + 上 {hd_u} = {hd_d + hd_u}本')


if __name__ == '__main__':
    main()
