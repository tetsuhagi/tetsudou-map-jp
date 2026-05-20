#!/usr/bin/env python3
"""
Generate 東京モノレール空港快速 timetable (モノレール浜松町 ⇔ 羽田空港第2ターミナル).

東京モノレール羽田空港線「空港快速」種別。本マップで「快速」種別を
例外的に特急枠に追加した第2例 (1例目: つくばエクスプレス快速)。
京急エアポート快特と **並走する別経路** で、羽田アクセス2系統がマップ上で
描画される。

経由路線: 東京モノレール 東京モノレール羽田線 (MLIT表記)

代表ダイヤ (空港快速):
  - 20分間隔 (毎時 :00 / :20 / :40 発)
  - モノレール浜松町発 5:30〜23:00 → 54本/方向
  - 羽田空港第2T発     5:50〜23:20 → 54本/方向
  - 1日 108本 (各方向54本) ※ 京急エアポート快特に次ぐ多さ
  - 所要 19分 (モノレール浜松町→羽田空港第2T)

実ダイヤとの差:
  - 実際は時間帯により7〜12分間隔の超頻発運行
  - 朝晩深夜は本数増減あり
  - 本テンプレートでは終日 20分間隔の代表ダイヤで簡略化

Stop intervals from モノレール浜松町:
  MONO_HAMAMATSUCHO    +0:00 dep
  MONO_HANEDA_T3       +0:12 arr / +0:13 dep
  MONO_HANEDA_T1       +0:16 arr / +0:17 dep
  MONO_HANEDA_T2       +0:19 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TOKYO_MONORAIL')

STOPS_DOWN = [
    ('MONO_HAMAMATSUCHO', None, 0),
    ('MONO_HANEDA_T3',    12,   13),
    ('MONO_HANEDA_T1',    16,   17),
    ('MONO_HANEDA_T2',    19,   None),
]
STOPS_UP = [
    ('MONO_HANEDA_T2',    None, 0),
    ('MONO_HANEDA_T1',    3,    4),
    ('MONO_HANEDA_T3',    7,    8),
    ('MONO_HAMAMATSUCHO', 19,   None),
]


def gen_every_20(start_h, start_m, end_h, end_m):
    times = []
    h, m = start_h, start_m
    while (h, m) <= (end_h, end_m):
        times.append(f'{h:02d}:{m:02d}')
        m += 20
        if m >= 60:
            m -= 60
            h += 1
    return times


WEEKDAY_DOWN_DEPS = gen_every_20(5, 30, 23, 0)
WEEKDAY_UP_DEPS   = gen_every_20(5, 50, 23, 20)
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

    emit('TOKYO_MONORAIL', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', '空港快速{n}', trains, sched_wd, 1)
    emit('TOKYO_MONORAIL', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   '空港快速{n}', trains, sched_wd, 2)
    emit_schedule_only('TOKYO_MONORAIL', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TOKYO_MONORAIL', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
