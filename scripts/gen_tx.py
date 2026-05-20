#!/usr/bin/env python3
"""
Generate つくばエクスプレス快速 timetable (秋葉原 ⇔ つくば).

首都圏新都市鉄道「つくばエクスプレス (TX)」の快速種別。
TX-2000系/TX-3000系 (130km/h走行) で運行。
本マップでは「快速」種別を例外的に特急枠に追加。

経由路線: 首都圏新都市鉄道 常磐新線 (MLIT表記、TX路線の正式分類)

代表ダイヤ (快速):
  - 30分間隔 (毎時 :00 / :30 発)
  - 秋葉原発・つくば発とも 6:00〜22:00
  - 1日 各方向33本、合計66本
  - 所要時間 45分 (秋葉原→つくば)

実ダイヤとの差:
  - 実際は20分間隔程度の時間帯もある
  - 朝晩のみ快速、日中は区間快速や普通もあり
  - 本テンプレートでは終日快速として簡略化

Stop intervals from 秋葉原:
  AKIHABARA                  +0:00 dep
  KITASENJU                  +0:08 arr / +0:09 dep
  MINAMI_NAGAREYAMA          +0:18 arr / +0:19 dep
  NAGAREYAMA_OOTAKANOMORI    +0:25 arr / +0:26 dep
  MORIYA                     +0:35 arr / +0:36 dep
  TSUKUBA                    +0:45 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TX')

STOPS_DOWN = [
    ('AKIHABARA',               None, 0),
    ('KITASENJU',               8,    9),
    ('MINAMI_NAGAREYAMA',       18,   19),
    ('NAGAREYAMA_OOTAKANOMORI', 25,   26),
    ('MORIYA',                  35,   36),
    ('TSUKUBA',                 45,   None),
]
STOPS_UP = [
    ('TSUKUBA',                 None, 0),
    ('MORIYA',                  9,    10),
    ('NAGAREYAMA_OOTAKANOMORI', 19,   20),
    ('MINAMI_NAGAREYAMA',       26,   27),
    ('KITASENJU',               36,   37),
    ('AKIHABARA',               45,   None),
]


def gen_half_hourly(start_h, start_m, end_h, end_m):
    times = []
    h, m = start_h, start_m
    while (h, m) <= (end_h, end_m):
        times.append(f'{h:02d}:{m:02d}')
        if m == 0:
            m = 30
        else:
            m = 0
            h += 1
    return times


WEEKDAY_DOWN_DEPS = gen_half_hourly(6, 0, 22, 0)    # 33本
WEEKDAY_UP_DEPS   = gen_half_hourly(6, 0, 22, 0)    # 33本
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

    emit('TX', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'TX快速{n}', trains, sched_wd, 1)
    emit('TX', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'TX快速{n}', trains, sched_wd, 2)
    emit_schedule_only('TX', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TX', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
