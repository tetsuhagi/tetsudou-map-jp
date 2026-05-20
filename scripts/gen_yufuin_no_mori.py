#!/usr/bin/env python3
"""
Generate ゆふいんの森 timetable (博多 ⇔ 別府).

JR九州の観光特急「ゆふいんの森」。キハ72系・キハ185系2200番台で運用。
深いダークグリーン+金のヨーロピアン調デザインが特徴。

経由路線:
  - JR九州 鹿児島線 (博多〜久留米)
  - JR九州 久大線 (久留米〜大分)
  - JR九州 日豊線 (大分〜別府)

代表ダイヤ:
  - 1日3往復
  - 博多発: 9:00, 12:30, 15:30
  - 別府発: 11:00, 14:30, 18:00
  - 所要 190分 (3時間10分)

実ダイヤとの差:
  - 実際は 由布院止2本+別府まで1本 の運用が多いが、本テンプレートでは
    全便を別府まで運行として簡略化。

Stop intervals from 博多:
  HAKATA      +0:00 dep
  KURUME      +0:35 arr / +0:36 dep
  HITA        +1:15 arr / +1:16 dep
  YUFUIN      +2:10 arr / +2:12 dep   (観光客乗降で2分停車)
  OITA        +2:55 arr / +2:57 dep
  BEPPU       +3:10 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'YUFUIN_FOREST')

STOPS_DOWN = [
    ('HAKATA',  None, 0),
    ('KURUME',  35,   36),
    ('HITA',    75,   76),
    ('YUFUIN',  130,  132),
    ('OITA',    175,  177),
    ('BEPPU',   190,  None),
]
STOPS_UP = [
    ('BEPPU',   None, 0),
    ('OITA',    13,   15),
    ('YUFUIN',  58,   60),
    ('HITA',    114,  115),
    ('KURUME',  154,  155),
    ('HAKATA',  190,  None),
]

WEEKDAY_DOWN_DEPS = ['09:00', '12:30', '15:30']
WEEKDAY_UP_DEPS   = ['11:00', '14:30', '18:00']
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

    emit('YUFUIN_FOREST', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ゆふいんの森{n}号', trains, sched_wd, 1)
    emit('YUFUIN_FOREST', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ゆふいんの森{n}号', trains, sched_wd, 2)
    emit_schedule_only('YUFUIN_FOREST', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('YUFUIN_FOREST', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
