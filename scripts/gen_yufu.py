#!/usr/bin/env python3
"""
Generate ゆふ timetable (博多 ⇔ 別府).

JR九州 特急「ゆふ」。キハ185系で運用。観光特急「ゆふいんの森」の
通常特急版兄弟系統。停車駅・経由路線は同じだが車両性格 (普通特急 vs
観光特急) で別 route_id に分けて識別性を確保。

経由路線: ゆふいんの森と同じ
  - JR九州 鹿児島線 (博多〜久留米)
  - JR九州 久大線 (久留米〜大分)
  - JR九州 日豊線 (大分〜別府)

代表ダイヤ:
  - 1日3往復
  - 博多発: 08:00, 11:00, 17:00
  - 別府発: 10:00, 13:00, 19:00
  - 所要 200分 (3時間20分) ※ ゆふいんの森より10分長め (車両性能差)

Stop intervals from 博多 (ゆふいんの森とほぼ同じ、由布院・大分の停車時間
だけ少し短め):
  HAKATA      +0:00 dep
  KURUME      +0:35 arr / +0:36 dep
  HITA        +1:18 arr / +1:19 dep
  YUFUIN      +2:18 arr / +2:19 dep
  OITA        +3:05 arr / +3:06 dep
  BEPPU       +3:20 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'YUFU')

STOPS_DOWN = [
    ('HAKATA',  None, 0),
    ('KURUME',  35,   36),
    ('HITA',    78,   79),
    ('YUFUIN',  138,  139),
    ('OITA',    185,  186),
    ('BEPPU',   200,  None),
]
STOPS_UP = [
    ('BEPPU',   None, 0),
    ('OITA',    14,   15),
    ('YUFUIN',  61,   62),
    ('HITA',    121,  122),
    ('KURUME',  164,  165),
    ('HAKATA',  200,  None),
]

WEEKDAY_DOWN_DEPS = ['08:00', '11:00', '17:00']
WEEKDAY_UP_DEPS   = ['10:00', '13:00', '19:00']
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

    emit('YUFU', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ゆふ{n}号', trains, sched_wd, 1)
    emit('YUFU', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ゆふ{n}号', trains, sched_wd, 2)
    emit_schedule_only('YUFU', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('YUFU', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
