#!/usr/bin/env python3
"""
Generate 東北新幹線 はやぶさ timetable.

Real 2024 dia:
- 東京発下り: 06:32〜21:20, 約29本/方向/日
- 平日: 約29本、土日: 約27本（やや少なめ）
- 全はやぶさ停車駅: 東京・上野・大宮・仙台・盛岡・新青森

Stop intervals from 東京:
  TOKYO       +0:00 dep
  UENO        +0:06 arr / +0:07 dep
  OMIYA       +0:25 arr / +0:26 dep
  SENDAI      +1:28 arr / +1:29 dep
  MORIOKA     +2:10 arr / +2:12 dep
  SHIN_AOMORI +3:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TOHOKU_SHINKANSEN')

STOPS_DOWN = [
    ('TOKYO',       None,  0),
    ('UENO',        6,     7),
    ('OMIYA',       25,    26),
    ('SENDAI',      88,    89),
    ('MORIOKA',     130,   132),
    ('SHIN_AOMORI', 180,   None),
]

STOPS_UP = [
    ('SHIN_AOMORI', None,  0),
    ('MORIOKA',     48,    50),
    ('SENDAI',      91,    92),
    ('OMIYA',       154,   155),
    ('UENO',        174,   175),
    ('TOKYO',       180,   None),
]

# 東京発下り はやぶさ (平日)
WEEKDAY_DOWN_DEPS = [
    '06:32',
    '07:08', '07:20', '07:32',
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

# 新青森発上り はやぶさ (平日)
WEEKDAY_UP_DEPS = [
    '06:11',
    '07:00', '07:46',
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

HOLIDAY_DOWN_DEPS = [
    '06:32',
    '07:08', '07:20', '07:32',
    '08:08', '08:32',
    '09:08', '09:36',
    '10:20', '10:36',
    '11:36',
    '12:36',
    '13:36',
    '14:36',
    '15:36',
    '16:08', '16:36',
    '17:08', '17:36',
    '18:08', '18:36',
    '19:08', '19:36',
    '20:08', '20:36',
    '21:08', '21:20',
]

HOLIDAY_UP_DEPS = [
    '06:11',
    '07:00', '07:46',
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


def main():
    trains = []
    schedule_weekday = []
    schedule_holiday = []

    n = 1
    for dep in WEEKDAY_DOWN_DEPS:
        tid = f'HAYABUSA_{n}'
        trains.append((tid, f'はやぶさ{n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'HAYABUSA_{n}'
        trains.append((tid, f'はやぶさ{n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'HAYABUSA_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'HAYABUSA_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'trains.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,name,direction\n')
        for tid, name, direction in trains:
            f.write(f'{tid},{name},{direction}\n')

    with open(os.path.join(OUT_DIR, 'weekday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for tid, order, sid, arr, dp in schedule_weekday:
            f.write(f'{tid},{order},{sid},{arr},{dp}\n')

    with open(os.path.join(OUT_DIR, 'holiday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for tid, order, sid, arr, dp in schedule_holiday:
            f.write(f'{tid},{order},{sid},{arr},{dp}\n')

    down_count = sum(1 for _, _, d in trains if d == 'down')
    up_count = sum(1 for _, _, d in trains if d == 'up')
    print(f'trains.csv: {len(trains)}本 (下り {down_count}, 上り {up_count})')
    print(f'weekday: 下 {len(WEEKDAY_DOWN_DEPS)} + 上 {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本')
    print(f'holiday: 下 {len(HOLIDAY_DOWN_DEPS)} + 上 {len(HOLIDAY_UP_DEPS)} = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
