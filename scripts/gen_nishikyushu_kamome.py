#!/usr/bin/env python3
"""
Generate 西九州新幹線 かもめ timetable.

Real 2024 dia:
- かもめ: 約22往復/方向/日 (約30min, 武雄温泉〜長崎)
- 全かもめ停車駅: 武雄温泉・嬉野温泉・新大村・諫早・長崎

Stop intervals from 武雄温泉:
  TAKEO_ONSEN     +0:00 dep
  URESHINO_ONSEN  +0:07 arr / +0:08 dep
  SHIN_OMURA      +0:18 arr / +0:19 dep
  ISAHAYA         +0:23 arr / +0:24 dep
  NAGASAKI        +0:30 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'NISHI_KYUSHU_SHINKANSEN')

STOPS_DOWN = [
    ('TAKEO_ONSEN',    None,  0),
    ('URESHINO_ONSEN', 7,     8),
    ('SHIN_OMURA',     18,    19),
    ('ISAHAYA',        23,    24),
    ('NAGASAKI',       30,    None),
]

STOPS_UP = [
    ('NAGASAKI',       None,  0),
    ('ISAHAYA',        7,     8),
    ('SHIN_OMURA',     12,    13),
    ('URESHINO_ONSEN', 22,    23),
    ('TAKEO_ONSEN',    30,    None),
]

WEEKDAY_DOWN_DEPS = [
    '06:00', '06:23', '06:45',
    '07:08', '07:23', '07:38', '07:54',
    '08:10', '08:25', '08:40', '08:55',
    '09:10', '09:25', '09:40', '09:55',
    '10:25', '10:55',
    '11:25', '11:55',
    '12:25', '12:55',
    '13:25', '13:55',
    '14:25', '14:55',
    '15:25', '15:55',
    '16:10', '16:25', '16:55',
    '17:10', '17:25', '17:55',
    '18:10', '18:25', '18:55',
    '19:25', '19:55',
    '20:25', '20:55',
    '21:25', '21:55',
]

WEEKDAY_UP_DEPS = [
    '06:00', '06:30', '06:45',
    '07:00', '07:15', '07:30', '07:45',
    '08:00', '08:15', '08:30', '08:45',
    '09:00', '09:15', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:15', '16:30',
    '17:00', '17:15', '17:30',
    '18:00', '18:15', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:00', '21:30',
]

HOLIDAY_DOWN_DEPS = [
    '06:23',
    '07:25', '07:55',
    '08:25', '08:55',
    '09:25', '09:55',
    '10:25', '10:55',
    '11:25', '11:55',
    '12:25', '12:55',
    '13:25', '13:55',
    '14:25', '14:55',
    '15:25', '15:55',
    '16:25', '16:55',
    '17:25', '17:55',
    '18:25', '18:55',
    '19:25', '19:55',
    '20:25',
    '21:25',
]

HOLIDAY_UP_DEPS = [
    '06:00',
    '07:00',
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


def main():
    trains = []
    schedule_weekday = []
    schedule_holiday = []

    n = 1
    for dep in WEEKDAY_DOWN_DEPS:
        tid = f'KAMOME_{n}'
        trains.append((tid, f'かもめ{n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'KAMOME_{n}'
        trains.append((tid, f'かもめ{n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'KAMOME_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'KAMOME_{n}'
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
