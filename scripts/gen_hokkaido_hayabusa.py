#!/usr/bin/env python3
"""
Generate 北海道新幹線 はやぶさ timetable (新青森-新函館北斗 portion).

Real 2024 dia:
- 約12-13本/方向/日
- 新青森発下り: 06:38〜22:15
- 全はやぶさ停車駅: 新青森・奥津軽いまべつ・木古内・新函館北斗
  (一部のはやぶさは奥津軽いまべつ/木古内通過するが本実装では全停車に統一)

Stop intervals from 新青森:
  SHIN_AOMORI            +0:00 dep
  OKUTSUGARU_IMABETSU    +0:27 arr / +0:28 dep
  KIKONAI                +0:60 arr / +0:61 dep
  SHIN_HAKODATE_HOKUTO   +0:80 arr (1h20)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HOKKAIDO_SHINKANSEN')

STOPS_DOWN = [
    ('SHIN_AOMORI',           None,  0),
    ('OKUTSUGARU_IMABETSU',   27,    28),
    ('KIKONAI',               60,    61),
    ('SHIN_HAKODATE_HOKUTO',  80,    None),
]

STOPS_UP = [
    ('SHIN_HAKODATE_HOKUTO',  None,  0),
    ('KIKONAI',               19,    20),
    ('OKUTSUGARU_IMABETSU',   52,    53),
    ('SHIN_AOMORI',           80,    None),
]

WEEKDAY_DOWN_DEPS = [
    '06:38',
    '09:32', '09:48',
    '11:53',
    '13:35',
    '14:35',
    '15:38',
    '16:38',
    '17:38',
    '18:38',
    '19:48',
    '21:38', '22:15',
]

WEEKDAY_UP_DEPS = [
    '06:35',
    '07:43',
    '08:42',
    '09:35',
    '10:53',
    '12:36',
    '14:53',
    '16:36',
    '17:45',
    '19:35',
    '20:42',
    '22:00',
]

HOLIDAY_DOWN_DEPS = [
    '06:38',
    '09:32', '09:48',
    '11:53',
    '13:35',
    '14:35',
    '15:38',
    '16:38',
    '17:38',
    '18:38',
    '19:48',
    '21:38',
]

HOLIDAY_UP_DEPS = [
    '06:35',
    '07:43',
    '08:42',
    '09:35',
    '10:53',
    '12:36',
    '14:53',
    '16:36',
    '17:45',
    '19:35',
    '20:42',
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
        tid = f'HAYABUSA_HKD_{n}'
        trains.append((tid, f'はやぶさ(北海道){n}', 'down'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 2
    for dep in WEEKDAY_UP_DEPS:
        tid = f'HAYABUSA_HKD_{n}'
        trains.append((tid, f'はやぶさ(北海道){n}', 'up'))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_UP), 1):
            schedule_weekday.append((tid, order, sid, arr, dp))
        n += 2

    n = 1
    for dep in HOLIDAY_DOWN_DEPS:
        tid = f'HAYABUSA_HKD_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), STOPS_DOWN), 1):
            schedule_holiday.append((tid, order, sid, arr, dp))
        n += 2
    n = 2
    for dep in HOLIDAY_UP_DEPS:
        tid = f'HAYABUSA_HKD_{n}'
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
