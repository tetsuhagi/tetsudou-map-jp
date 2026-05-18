#!/usr/bin/env python3
"""
Generate 山陽新幹線 のぞみ timetable (trains.csv + weekday.csv + holiday.csv).

Real 2024 dia patterns:
- 新大阪下り: 06:00〜21:30, ピーク 3-5本/時、通常 3-4本/時
- 平日: 約65本/方向, 土日: 約55本/方向
- 全のぞみは新大阪・新神戸・岡山・広島・小倉・博多のみ停車

Stop intervals from 新大阪:
  SHIN_OSAKA +0:00 dep
  SHIN_KOBE  +0:13 arr / +0:14 dep
  OKAYAMA    +0:46 arr / +0:47 dep
  HIROSHIMA  +1:24 arr / +1:25 dep
  KOKURA     +2:09 arr / +2:10 dep
  HAKATA     +2:25 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SANYO_SHINKANSEN')

STOPS_DOWN = [
    ('SHIN_OSAKA', None,  0),
    ('SHIN_KOBE',  13,    14),
    ('OKAYAMA',    46,    47),
    ('HIROSHIMA',  84,    85),
    ('KOKURA',     129,   130),
    ('HAKATA',     145,   None),
]

STOPS_UP = [
    ('HAKATA',     None,  0),
    ('KOKURA',     16,    17),
    ('HIROSHIMA',  61,    62),
    ('OKAYAMA',    99,    100),
    ('SHIN_KOBE',  132,   133),
    ('SHIN_OSAKA', 145,   None),
]

# 新大阪発下り のぞみ (平日)
WEEKDAY_DOWN_DEPS = [
    '06:00', '06:30', '06:50',
    '07:00', '07:13', '07:25', '07:43', '07:53',
    '08:00', '08:13', '08:25', '08:43', '08:53',
    '09:00', '09:13', '09:25', '09:43', '09:53',
    '10:00', '10:13', '10:25', '10:43', '10:53',
    '11:00', '11:13', '11:25', '11:43', '11:53',
    '12:00', '12:13', '12:25', '12:43', '12:53',
    '13:00', '13:13', '13:25', '13:43', '13:53',
    '14:00', '14:13', '14:25', '14:43', '14:53',
    '15:00', '15:13', '15:25', '15:43', '15:53',
    '16:00', '16:13', '16:25', '16:43', '16:53',
    '17:00', '17:13', '17:25', '17:43', '17:53',
    '18:00', '18:13', '18:25', '18:43', '18:53',
    '19:00', '19:13', '19:25', '19:43',
    '20:00', '20:13', '20:30',
    '21:00', '21:30',
]

# 博多発上り のぞみ (平日)
WEEKDAY_UP_DEPS = [
    '06:00', '06:23', '06:50',
    '07:00', '07:13', '07:25', '07:43', '07:53',
    '08:00', '08:13', '08:25', '08:43', '08:53',
    '09:00', '09:13', '09:25', '09:43', '09:53',
    '10:00', '10:13', '10:25', '10:43', '10:53',
    '11:00', '11:13', '11:25', '11:43', '11:53',
    '12:00', '12:13', '12:25', '12:43', '12:53',
    '13:00', '13:13', '13:25', '13:43', '13:53',
    '14:00', '14:13', '14:25', '14:43', '14:53',
    '15:00', '15:13', '15:25', '15:43', '15:53',
    '16:00', '16:13', '16:25', '16:43', '16:53',
    '17:00', '17:13', '17:25', '17:43', '17:53',
    '18:00', '18:13', '18:25', '18:43', '18:53',
    '19:00', '19:13', '19:25', '19:43',
    '20:00', '20:23',
]

HOLIDAY_DOWN_DEPS = [
    '06:00', '06:30',
    '07:00', '07:13', '07:25', '07:43', '07:53',
    '08:00', '08:13', '08:25', '08:53',
    '09:00', '09:13', '09:25', '09:53',
    '10:00', '10:13', '10:25', '10:53',
    '11:00', '11:13', '11:25', '11:53',
    '12:00', '12:13', '12:25', '12:53',
    '13:00', '13:13', '13:25', '13:53',
    '14:00', '14:13', '14:25', '14:53',
    '15:00', '15:13', '15:25', '15:53',
    '16:00', '16:13', '16:25', '16:43', '16:53',
    '17:00', '17:13', '17:25', '17:43', '17:53',
    '18:00', '18:13', '18:25', '18:43', '18:53',
    '19:00', '19:13', '19:25',
    '20:00', '20:30',
    '21:00',
]

HOLIDAY_UP_DEPS = [
    '06:00', '06:30',
    '07:00', '07:13', '07:25', '07:43', '07:53',
    '08:00', '08:13', '08:25', '08:53',
    '09:00', '09:13', '09:25', '09:53',
    '10:00', '10:13', '10:25', '10:53',
    '11:00', '11:13', '11:25', '11:53',
    '12:00', '12:13', '12:25', '12:53',
    '13:00', '13:13', '13:25', '13:53',
    '14:00', '14:13', '14:25', '14:53',
    '15:00', '15:13', '15:25', '15:53',
    '16:00', '16:13', '16:25', '16:43', '16:53',
    '17:00', '17:13', '17:25', '17:43', '17:53',
    '18:00', '18:13', '18:25', '18:43', '18:53',
    '19:00', '19:13', '19:25',
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
        tid = f'SANYO_{n}'
        trains.append((tid, f'のぞみ(山陽){n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'SANYO_{n}'
        trains.append((tid, f'のぞみ(山陽){n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'SANYO_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'SANYO_{n}'
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
    print(f'weekday: 下り {len(WEEKDAY_DOWN_DEPS)} + 上り {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本')
    print(f'holiday: 下り {len(HOLIDAY_DOWN_DEPS)} + 上り {len(HOLIDAY_UP_DEPS)} = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
