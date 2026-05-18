#!/usr/bin/env python3
"""
Generate 北陸新幹線 かがやき timetable.

Real 2024 dia (敦賀延伸後):
- かがやき (最速種別): 約10-12本/方向/日
- 全かがやき停車駅 (最速パターン): 高崎・長野・富山・金沢・福井・敦賀
  (はくたか等の他種別は本実装では割愛)

Stop intervals from 高崎:
  TAKASAKI  +0:00 dep
  NAGANO    +0:47 arr / +0:49 dep
  TOYAMA    +1:46 arr / +1:48 dep
  KANAZAWA  +2:11 arr / +2:13 dep
  FUKUI     +2:58 arr / +3:00 dep
  TSURUGA   +3:20 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HOKURIKU_SHINKANSEN')

STOPS_DOWN = [
    ('TAKASAKI', None,  0),
    ('NAGANO',   47,    49),
    ('TOYAMA',   106,   108),
    ('KANAZAWA', 131,   133),
    ('FUKUI',    178,   180),
    ('TSURUGA',  200,   None),
]

STOPS_UP = [
    ('TSURUGA',  None,  0),
    ('FUKUI',    20,    22),
    ('KANAZAWA', 67,    69),
    ('TOYAMA',   92,    94),
    ('NAGANO',   151,   153),
    ('TAKASAKI', 200,   None),
]

# 高崎発下り かがやき (平日)
WEEKDAY_DOWN_DEPS = [
    '07:06',
    '07:46',
    '08:14',
    '10:14',
    '15:14',
    '17:14',
    '19:14',
    '20:14',
    '20:54',
    '21:54',
]

# 敦賀発上り かがやき (平日)
WEEKDAY_UP_DEPS = [
    '06:11',
    '07:00',
    '08:00',
    '10:00',
    '12:25',
    '14:25',
    '16:25',
    '18:25',
    '19:00',
    '20:11',
]

HOLIDAY_DOWN_DEPS = [
    '07:06',
    '07:46',
    '08:14',
    '10:14',
    '15:14',
    '17:14',
    '19:14',
    '20:14',
    '20:54',
]

HOLIDAY_UP_DEPS = [
    '06:11',
    '07:00',
    '08:00',
    '10:00',
    '14:25',
    '16:25',
    '18:25',
    '19:00',
    '20:11',
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
        tid = f'KAGAYAKI_{n}'
        trains.append((tid, f'かがやき{n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'KAGAYAKI_{n}'
        trains.append((tid, f'かがやき{n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'KAGAYAKI_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'KAGAYAKI_{n}'
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
