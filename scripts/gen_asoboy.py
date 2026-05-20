#!/usr/bin/env python3
"""
Generate あそぼーい！ timetable (別府 ⇔ 阿蘇).

JR九州 特急「あそぼーい！」。キハ183系1000番台で運用される
ファミリー向け観光特急。漫画調デザインと子供向けプレイルームが特徴。

ユーザー指定により、旧「九州横断特急」(2022年廃止) のロマンを継ぐ
位置付けで実装。現状は別府⇔阿蘇間で運行。

経由路線:
  - JR九州 日豊線 (別府〜大分)
  - JR九州 豊肥線 (大分〜阿蘇)

代表ダイヤ:
  - 1日2往復 (土日祝中心、シミュレーション見栄えで平日も同等運行)
  - 別府発: 08:00, 14:00
  - 阿蘇発: 11:30, 17:30
  - 所要 180分 (3時間)

実ダイヤとの差:
  - 実際は土日祝のみ1日1〜2本程度。本テンプレートでは平日/休日同一の
    2往復として簡略化。

Stop intervals from 別府:
  BEPPU   +0:00 dep
  OITA    +0:15 arr / +0:18 dep   (連結車両/客扱いで3分停車)
  ASO     +3:00 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ASOBOY')

STOPS_DOWN = [
    ('BEPPU', None, 0),
    ('OITA',  15,   18),
    ('ASO',   180,  None),
]
STOPS_UP = [
    ('ASO',   None, 0),
    ('OITA',  162,  165),
    ('BEPPU', 180,  None),
]

WEEKDAY_DOWN_DEPS = ['08:00', '14:00']
WEEKDAY_UP_DEPS   = ['11:30', '17:30']
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

    emit('ASOBOY', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'あそぼーい！{n}号', trains, sched_wd, 1)
    emit('ASOBOY', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'あそぼーい！{n}号', trains, sched_wd, 2)
    emit_schedule_only('ASOBOY', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('ASOBOY', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
