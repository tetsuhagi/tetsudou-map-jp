#!/usr/bin/env python3
"""
Generate リゾートしらかみ timetable (秋田 ⇔ 青森).

JR東日本「リゾートしらかみ」(快速)。HB-E300系3編成 (青池/ブナ/くまげら)
で運用される観光快速。日本海沿岸の絶景区間 (能代〜深浦〜鯵ヶ沢〜五所川原)
を走破する5時間の旅。

経由路線:
  - JR東日本 奥羽線 (秋田〜東能代)
  - JR東日本 五能線 (東能代〜川部)
  - JR東日本 奥羽線 (川部〜青森)
  ※ 川部駅で五能線が奥羽線に合流、地理的にループせず直線的接続

代表停車駅 (簡略化):
  秋田 - 東能代 - 五所川原 - 弘前 - 青森

実ダイヤは沿岸の観光地 (深浦・千畳敷・ウェスパ椿山・十二湖など) にも
停車するが、本テンプレートでは主要5駅版で簡略化。

代表ダイヤ:
  - 1日2往復
  - 秋田発: 08:00, 14:00
  - 青森発: 09:00, 15:00
  - 所要 300分 (5時間)
  - 平日/休日同一 (実態は土日祝中心の運行だが簡略化)

Stop intervals from 秋田:
  AKITA              +0:00 dep
  HIGASHI_NOSHIRO    +0:50 arr / +0:51 dep
  GOSHOGAWARA        +3:30 arr / +3:31 dep   (絶景区間後の主要駅)
  HIROSAKI           +4:20 arr / +4:21 dep
  AOMORI             +5:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'RESORT_SHIRAKAMI')

STOPS_DOWN = [
    ('AKITA',           None, 0),
    ('HIGASHI_NOSHIRO', 50,   51),
    ('FUKAURA',         140,  141),
    ('GOSHOGAWARA',     210,  211),
    ('HIROSAKI',        260,  261),
    ('AOMORI',          300,  None),
]
STOPS_UP = [
    ('AOMORI',          None, 0),
    ('HIROSAKI',        39,   40),
    ('GOSHOGAWARA',     89,   90),
    ('FUKAURA',         159,  160),
    ('HIGASHI_NOSHIRO', 249,  250),
    ('AKITA',           300,  None),
]

WEEKDAY_DOWN_DEPS = ['08:00', '14:00']
WEEKDAY_UP_DEPS   = ['09:00', '15:00']
HOLIDAY_DOWN_DEPS = WEEKDAY_DOWN_DEPS
HOLIDAY_UP_DEPS   = WEEKDAY_UP_DEPS


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

    emit('RESORT_SHIRAKAMI', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'リゾートしらかみ{n}号', trains, sched_wd, 1)
    emit('RESORT_SHIRAKAMI', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'リゾートしらかみ{n}号', trains, sched_wd, 2)
    emit_schedule_only('RESORT_SHIRAKAMI', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('RESORT_SHIRAKAMI', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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


if __name__ == '__main__':
    main()
