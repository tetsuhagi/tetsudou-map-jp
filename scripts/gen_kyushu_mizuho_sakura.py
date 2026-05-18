#!/usr/bin/env python3
"""
Generate 九州新幹線 timetable (みずほ・さくら + つばめ).

Real 2024 dia:
- みずほ+さくら統合 (高速種別): ~28本/方向、5駅停車、1h30min
- つばめ (各駅停車): ~14本/方向、博多-熊本シャトル、7駅停車、50min
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KYUSHU_SHINKANSEN')

STOPS_DOWN = [
    ('HAKATA',         None,  0),
    ('SHIN_TOSU',      12,    13),
    ('KURUME',         18,    19),
    ('KUMAMOTO',       50,    52),
    ('KAGOSHIMA_CHUO', 90,    None),
]

STOPS_UP = [
    ('KAGOSHIMA_CHUO', None,  0),
    ('KUMAMOTO',       38,    40),
    ('KURUME',         71,    72),
    ('SHIN_TOSU',      77,    78),
    ('HAKATA',         90,    None),
]

# つばめ: 博多-熊本シャトル、各駅停車
TSUBAME_STOPS_DOWN = [
    ('HAKATA',            None,  0),
    ('SHIN_TOSU',         12,    13),
    ('KURUME',            18,    19),
    ('CHIKUGO_FUNAGOYA',  25,    26),
    ('SHIN_OMUTA',        32,    33),
    ('SHIN_TAMANA',       40,    41),
    ('KUMAMOTO',          50,    None),
]
TSUBAME_STOPS_UP = [
    ('KUMAMOTO',          None,  0),
    ('SHIN_TAMANA',       9,     10),
    ('SHIN_OMUTA',        17,    18),
    ('CHIKUGO_FUNAGOYA',  24,    25),
    ('KURUME',            31,    32),
    ('SHIN_TOSU',         37,    38),
    ('HAKATA',            50,    None),
]

TSUBAME_WEEKDAY_DOWN = [
    '06:36', '07:36', '08:00', '08:36',
    '09:36', '10:36', '11:36', '12:36',
    '13:36', '14:36', '15:36',
    '17:00', '18:30', '20:00',
]
TSUBAME_WEEKDAY_UP = [
    '06:48', '07:36', '08:24', '09:30',
    '10:30', '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30', '17:30',
    '18:30', '19:30',
]
TSUBAME_HOLIDAY_DOWN = [
    '06:36', '07:36', '08:36',
    '09:36', '10:36', '11:36', '12:36',
    '13:36', '14:36', '15:36',
    '17:00', '18:30', '20:00',
]
TSUBAME_HOLIDAY_UP = [
    '06:48', '07:36', '08:24',
    '10:30', '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30', '17:30',
    '18:30', '19:30',
]

WEEKDAY_DOWN_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30', '07:48',
    '08:13', '08:30',
    '09:00', '09:30',
    '10:00', '10:30', '10:48',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30', '13:48',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30', '16:48',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30', '19:48',
    '20:00', '20:30',
    '21:00', '21:30', '21:55',
]

WEEKDAY_UP_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:00', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:00',
]

HOLIDAY_DOWN_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30',
    '08:13', '08:30',
    '09:00', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:00', '21:30',
]

HOLIDAY_UP_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:00', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00',
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

    emit('KYUSHU', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'みずほ/さくら{n}', trains, sched_wd, 1)
    emit('KYUSHU', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'みずほ/さくら{n}', trains, sched_wd, 2)
    emit_schedule_only('KYUSHU', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('KYUSHU', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

    emit('TSUBAME', TSUBAME_WEEKDAY_DOWN, TSUBAME_STOPS_DOWN, 'down', 'つばめ{n}', trains, sched_wd, 1)
    emit('TSUBAME', TSUBAME_WEEKDAY_UP,   TSUBAME_STOPS_UP,   'up',   'つばめ{n}', trains, sched_wd, 2)
    emit_schedule_only('TSUBAME', TSUBAME_HOLIDAY_DOWN, TSUBAME_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TSUBAME', TSUBAME_HOLIDAY_UP,   TSUBAME_STOPS_UP,   sched_hd, 2)

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
    wd_d = len(WEEKDAY_DOWN_DEPS) + len(TSUBAME_WEEKDAY_DOWN)
    wd_u = len(WEEKDAY_UP_DEPS) + len(TSUBAME_WEEKDAY_UP)
    hd_d = len(HOLIDAY_DOWN_DEPS) + len(TSUBAME_HOLIDAY_DOWN)
    hd_u = len(HOLIDAY_UP_DEPS) + len(TSUBAME_HOLIDAY_UP)
    print(f'weekday: 下 {wd_d} + 上 {wd_u} = {wd_d + wd_u}本')
    print(f'holiday: 下 {hd_d} + 上 {hd_u} = {hd_d + hd_u}本')


if __name__ == '__main__':
    main()
