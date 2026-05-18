#!/usr/bin/env python3
"""
Generate 東海道新幹線 のぞみ timetable (trains.csv + weekday.csv + holiday.csv).

Real 2024 dia patterns:
- 東京下り: 06:00〜21:30, ピーク 7-9時/17-20時, 通常 9-16時
- 平日: 約115本/方向, 土日: 約100本/方向
- 全のぞみは東京・品川・新横浜・名古屋・京都・新大阪のみ停車

Standard stop intervals (東京基準):
  TOKYO    +0:00 dep
  SHINAGAWA  +0:07 arr / +0:08 dep
  SHIN_YOKOHAMA  +0:18 arr / +0:19 dep
  NAGOYA   +1:36 arr / +1:37 dep
  KYOTO    +2:10 arr / +2:11 dep
  SHIN_OSAKA +2:24 arr

Up direction uses same intervals reversed from 新大阪.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TOKAIDO_SHINKANSEN')

# Stop intervals from origin (minutes). Each entry: (station_id, arr_offset, dep_offset).
# arr_offset is None for the origin, dep_offset is None for the terminal.
STOPS_DOWN = [
    ('TOKYO',         None,   0),
    ('SHINAGAWA',     7,      8),
    ('SHIN_YOKOHAMA', 18,     19),
    ('NAGOYA',        96,     97),    # 1h36 / 1h37
    ('KYOTO',         130,    131),   # 2h10 / 2h11
    ('SHIN_OSAKA',    144,    None),  # 2h24
]

# Up direction: 新大阪 → 京都 → 名古屋 → 新横浜 → 品川 → 東京. Same intervals.
STOPS_UP = [
    ('SHIN_OSAKA',    None,   0),
    ('KYOTO',         13,     14),
    ('NAGOYA',        47,     48),
    ('SHIN_YOKOHAMA', 125,    126),
    ('SHINAGAWA',     136,    137),
    ('TOKYO',         144,    None),
]

# 東京発 のぞみ ダイヤ (平日) — 実2024ダイヤ近似 (HH:MM)
WEEKDAY_DOWN_DEPS = [
    '06:00', '06:21', '06:33', '06:50', '06:57',
    '07:00', '07:03', '07:09', '07:21', '07:30', '07:33', '07:42', '07:48', '07:51', '07:57',
    '08:00', '08:09', '08:21', '08:30', '08:33', '08:42', '08:51', '08:54', '08:57',
    '09:00', '09:09', '09:21', '09:30', '09:33', '09:42', '09:51',
    '10:00', '10:09', '10:21', '10:30', '10:42', '10:51',
    '11:00', '11:09', '11:21', '11:30', '11:42', '11:51',
    '12:00', '12:09', '12:21', '12:30', '12:42', '12:51',
    '13:00', '13:09', '13:21', '13:30', '13:42', '13:51',
    '14:00', '14:09', '14:21', '14:30', '14:42', '14:51',
    '15:00', '15:09', '15:21', '15:30', '15:42', '15:51',
    '16:00', '16:09', '16:21', '16:30', '16:42', '16:51',
    '17:00', '17:09', '17:21', '17:30', '17:42', '17:51',
    '18:00', '18:09', '18:21', '18:30', '18:42', '18:51',
    '19:00', '19:09', '19:21', '19:30', '19:42', '19:51',
    '20:00', '20:09', '20:21', '20:30', '20:42', '20:51',
    '21:00', '21:09', '21:23',
]

# 新大阪発 上り のぞみ ダイヤ (平日)
WEEKDAY_UP_DEPS = [
    '06:00', '06:13', '06:23', '06:37', '06:50', '06:56',
    '07:00', '07:13', '07:23', '07:33', '07:43', '07:50', '07:53',
    '08:00', '08:13', '08:23', '08:30', '08:42', '08:50', '08:53',
    '09:00', '09:13', '09:23', '09:30', '09:42', '09:50',
    '10:00', '10:13', '10:23', '10:30', '10:42', '10:50',
    '11:00', '11:13', '11:23', '11:30', '11:42', '11:50',
    '12:00', '12:13', '12:23', '12:30', '12:42', '12:50',
    '13:00', '13:13', '13:23', '13:30', '13:42', '13:50',
    '14:00', '14:13', '14:23', '14:30', '14:42', '14:50',
    '15:00', '15:13', '15:23', '15:30', '15:42', '15:50',
    '16:00', '16:13', '16:23', '16:30', '16:42', '16:50',
    '17:00', '17:13', '17:23', '17:30', '17:42', '17:50',
    '18:00', '18:13', '18:23', '18:30', '18:42', '18:50',
    '19:00', '19:13', '19:23', '19:30', '19:42', '19:50',
    '20:00', '20:13', '20:23', '20:30', '20:42', '20:50',
    '21:00', '21:13', '21:24',
]

# 土日ダイヤ: 早朝/夜間がやや薄い、ピーク本数控えめ
HOLIDAY_DOWN_DEPS = [
    '06:00', '06:21', '06:33', '06:50',
    '07:00', '07:09', '07:21', '07:30', '07:42', '07:51',
    '08:00', '08:09', '08:21', '08:30', '08:42', '08:51',
    '09:00', '09:09', '09:21', '09:30', '09:42', '09:51',
    '10:00', '10:09', '10:21', '10:30', '10:42', '10:51',
    '11:00', '11:09', '11:21', '11:30', '11:42', '11:51',
    '12:00', '12:09', '12:21', '12:30', '12:42', '12:51',
    '13:00', '13:09', '13:21', '13:30', '13:42', '13:51',
    '14:00', '14:09', '14:21', '14:30', '14:42', '14:51',
    '15:00', '15:09', '15:21', '15:30', '15:42', '15:51',
    '16:00', '16:09', '16:21', '16:30', '16:42', '16:51',
    '17:00', '17:09', '17:21', '17:30', '17:42', '17:51',
    '18:00', '18:09', '18:21', '18:30', '18:42', '18:51',
    '19:00', '19:09', '19:21', '19:30', '19:42', '19:51',
    '20:00', '20:09', '20:21', '20:30', '20:42',
    '21:00', '21:23',
]

HOLIDAY_UP_DEPS = [
    '06:00', '06:23', '06:37', '06:50',
    '07:00', '07:13', '07:23', '07:33', '07:43', '07:53',
    '08:00', '08:13', '08:23', '08:30', '08:42', '08:53',
    '09:00', '09:13', '09:23', '09:30', '09:42', '09:50',
    '10:00', '10:13', '10:23', '10:30', '10:42', '10:50',
    '11:00', '11:13', '11:23', '11:30', '11:42', '11:50',
    '12:00', '12:13', '12:23', '12:30', '12:42', '12:50',
    '13:00', '13:13', '13:23', '13:30', '13:42', '13:50',
    '14:00', '14:13', '14:23', '14:30', '14:42', '14:50',
    '15:00', '15:13', '15:23', '15:30', '15:42', '15:50',
    '16:00', '16:13', '16:23', '16:30', '16:42', '16:50',
    '17:00', '17:13', '17:23', '17:30', '17:42', '17:50',
    '18:00', '18:13', '18:23', '18:30', '18:42', '18:50',
    '19:00', '19:13', '19:23', '19:30', '19:42', '19:50',
    '20:00', '20:13', '20:23', '20:30', '20:42',
    '21:00', '21:24',
]


def parse_hhmm(s):
    h, m = s.split(':')
    return int(h) * 60 + int(m)


def fmt_hhmm(mins):
    return f'{mins // 60:02d}:{mins % 60:02d}'


def build_stops(base_dep_min, stops_def):
    """Return list of (station_id, arrival_str, departure_str) for one train."""
    rows = []
    for sid, arr_off, dep_off in stops_def:
        arr = fmt_hhmm(base_dep_min + arr_off) if arr_off is not None else ''
        dep = fmt_hhmm(base_dep_min + dep_off) if dep_off is not None else ''
        rows.append((sid, arr, dep))
    return rows


def main():
    # Build train list (down: odd-numbered, up: even-numbered)
    trains = []
    schedule_weekday = []
    schedule_holiday = []

    # Down: NOZOMI_1, 3, 5, ...
    n = 1
    for dep in WEEKDAY_DOWN_DEPS:
        tid = f'NOZOMI_{n}'
        trains.append((tid, f'のぞみ{n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    # Up: NOZOMI_2, 4, 6, ...
    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'NOZOMI_{n}'
        trains.append((tid, f'のぞみ{n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    # Holiday schedule (same train_ids — assume up to len(HOLIDAY_*) trains exist)
    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'NOZOMI_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'NOZOMI_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2

    # Write trains.csv (includes all train_ids — holiday-only trains are subset)
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
    print(f'weekday.csv: 下り {len(WEEKDAY_DOWN_DEPS)}本 + 上り {len(WEEKDAY_UP_DEPS)}本 = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本')
    print(f'holiday.csv: 下り {len(HOLIDAY_DOWN_DEPS)}本 + 上り {len(HOLIDAY_UP_DEPS)}本 = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
