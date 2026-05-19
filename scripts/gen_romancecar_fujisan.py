#!/usr/bin/env python3
"""
Generate 小田急ロマンスカー ふじさん系統 timetable (新宿 ⇔ 御殿場).

小田急60000形 MSE 専用の系統。新宿から小田急小田原線を南下し、新松田駅で
JR御殿場線へ渡り線経由で乗り入れて御殿場まで運行する直通特急。

経由路線:
  - 小田急電鉄 小田原線 (新宿〜新松田)
  - JR東海 御殿場線 (松田〜御殿場)
  ※ 新松田駅と松田駅は徒歩100m程度の隣接駅。MLIT 上は別ノードなので
    build_geometry.py の snap_meters パラメータで接続が必要。

代表ダイヤ (ふじさん):
  - 1日4往復 (実ダイヤ準拠)
  - 新宿発: 8:30, 11:30, 14:30, 17:30
  - 御殿場発: 10:30, 13:30, 16:30, 19:30
  - 所要時間 90分 (新宿→御殿場)

Stop intervals from 新宿:
  SHINJUKU      +0:00 dep
  MACHIDA       +0:35 arr / +0:36 dep
  EBINA         +0:44 arr / +0:45 dep
  HONATSUGI     +0:49 arr / +0:50 dep
  HADANO        +1:02 arr / +1:03 dep
  SHIN_MATSUDA  +1:13 arr / +1:15 dep   (渡り線で御殿場線へ転線、2分停車)
  GOTEMBA       +1:30 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ROMANCECAR_FUJISAN')

STOPS_DOWN = [
    ('SHINJUKU',     None, 0),
    ('MACHIDA',      35,   36),
    ('EBINA',        44,   45),
    ('HONATSUGI',    49,   50),
    ('HADANO',       62,   63),
    ('SHIN_MATSUDA', 73,   75),
    ('GOTEMBA',      90,   None),
]
STOPS_UP = [
    ('GOTEMBA',      None, 0),
    ('SHIN_MATSUDA', 15,   17),
    ('HADANO',       27,   28),
    ('HONATSUGI',    40,   41),
    ('EBINA',        45,   46),
    ('MACHIDA',      54,   55),
    ('SHINJUKU',     90,   None),
]

# 1日4往復 (実ダイヤ準拠)
WEEKDAY_DOWN_DEPS = ['08:30', '11:30', '14:30', '17:30']
WEEKDAY_UP_DEPS   = ['10:30', '13:30', '16:30', '19:30']
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

    emit('ROMANCECAR_FUJISAN', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ふじさん{n}', trains, sched_wd, 1)
    emit('ROMANCECAR_FUJISAN', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ふじさん{n}', trains, sched_wd, 2)
    emit_schedule_only('ROMANCECAR_FUJISAN', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('ROMANCECAR_FUJISAN', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
