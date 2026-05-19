#!/usr/bin/env python3
"""
Generate 小田急ロマンスカー えのしま系統 timetable (新宿 ⇔ 片瀬江ノ島).

新宿から小田急小田原線、相模大野で江ノ島線へ分岐して片瀬江ノ島まで運行。
GSE/EXE/MSE が日や時間帯で運用される (車両は本テンプレートでは
表現せず、代表色は GSE/EXE 寄りの赤系)。

経由路線:
  - 小田急電鉄 小田原線 (新宿〜相模大野)
  - 小田急電鉄 江ノ島線 (相模大野〜片瀬江ノ島)

代表ダイヤ (えのしま):
  - 1日5往復 (朝夕中心の運行)
  - 新宿発: 7:00, 9:00, 11:00, 14:00, 17:00
  - 片瀬江ノ島発: 10:00, 13:00, 16:00, 18:00, 20:00
  - 所要時間 65分 (新宿→片瀬江ノ島)
  - 代表停車駅 5駅: 新宿 - 町田 - 大和 - 藤沢 - 片瀬江ノ島
    ※ 実際は相模大野・大野工場前なども一部停車だが、簡略化

Stop intervals from 新宿:
  SHINJUKU         +0:00 dep
  MACHIDA          +0:35 arr / +0:36 dep
  YAMATO           +0:46 arr / +0:47 dep
  FUJISAWA         +0:58 arr / +0:59 dep
  KATASE_ENOSHIMA  +1:05 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ROMANCECAR_ENOSHIMA')

STOPS_DOWN = [
    ('SHINJUKU',        None, 0),
    ('MACHIDA',         35,   36),
    ('YAMATO',          46,   47),
    ('FUJISAWA',        58,   59),
    ('KATASE_ENOSHIMA', 65,   None),
]
STOPS_UP = [
    ('KATASE_ENOSHIMA', None, 0),
    ('FUJISAWA',        6,    7),
    ('YAMATO',          18,   19),
    ('MACHIDA',         29,   30),
    ('SHINJUKU',        65,   None),
]

# 1日5往復
WEEKDAY_DOWN_DEPS = ['07:00', '09:00', '11:00', '14:00', '17:00']
WEEKDAY_UP_DEPS   = ['10:00', '13:00', '16:00', '18:00', '20:00']
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

    emit('ROMANCECAR_ENOSHIMA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'えのしま{n}', trains, sched_wd, 1)
    emit('ROMANCECAR_ENOSHIMA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'えのしま{n}', trains, sched_wd, 2)
    emit_schedule_only('ROMANCECAR_ENOSHIMA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('ROMANCECAR_ENOSHIMA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
