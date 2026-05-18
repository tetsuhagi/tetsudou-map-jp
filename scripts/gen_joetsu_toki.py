#!/usr/bin/env python3
"""
Generate 上越新幹線 とき timetable.

Real 2024 dia:
- とき (最速種別): 約25-28本/方向/日
- 全とき停車駅 (最速パターン): 大宮・高崎・長岡・燕三条・新潟
- 一部とき: 上毛高原/越後湯沢/浦佐/熊谷/本庄早稲田にも停車 (本実装では最速パターンに統一)

Stop intervals from 大宮:
  OMIYA          +0:00 dep
  TAKASAKI       +0:25 arr / +0:26 dep
  NAGAOKA        +1:06 arr / +1:08 dep
  TSUBAME_SANJO  +1:18 arr / +1:19 dep
  NIIGATA        +1:30 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'JOETSU_SHINKANSEN')

STOPS_DOWN = [
    ('OMIYA',         None,  0),
    ('TAKASAKI',      25,    26),
    ('NAGAOKA',       66,    68),
    ('TSUBAME_SANJO', 78,    79),
    ('NIIGATA',       90,    None),
]

STOPS_UP = [
    ('NIIGATA',       None,  0),
    ('TSUBAME_SANJO', 12,    13),
    ('NAGAOKA',       23,    25),
    ('TAKASAKI',      65,    66),
    ('OMIYA',         90,    None),
]

# 大宮発下り とき (平日) — 東京発+25min相当
WEEKDAY_DOWN_DEPS = [
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

# 新潟発上り とき (平日)
WEEKDAY_UP_DEPS = [
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

HOLIDAY_DOWN_DEPS = [
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
    '17:13', '17:33',
    '18:23',
    '19:23',
    '20:23',
    '21:23',
]

HOLIDAY_UP_DEPS = [
    '06:08',
    '07:00',
    '08:00', '08:23',
    '09:00',
    '10:00',
    '11:00',
    '12:00',
    '13:00',
    '14:00',
    '15:00',
    '16:00',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00',
    '20:00',
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


def main():
    trains = []
    schedule_weekday = []
    schedule_holiday = []

    n = 1
    for dep in WEEKDAY_DOWN_DEPS:
        tid = f'TOKI_{n}'
        trains.append((tid, f'とき{n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'TOKI_{n}'
        trains.append((tid, f'とき{n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'TOKI_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'TOKI_{n}'
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
