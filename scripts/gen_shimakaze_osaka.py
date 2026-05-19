#!/usr/bin/env python3
"""
Generate 近鉄しまかぜ 大阪系統 timetable (大阪難波 ⇔ 賢島).

近畿日本鉄道50000系「しまかぜ」(2013年デビュー) の代表観光特急。
3起点 (大阪難波・京都・近鉄名古屋) から賢島へ1日1往復ずつ運行する
特殊な運用形態。本テンプレートは大阪系統。

経由路線 (5路線):
  - 近畿日本鉄道 難波線 (大阪難波〜大阪上本町)
  - 近畿日本鉄道 大阪線 (大阪上本町〜伊勢中川)
  - 近畿日本鉄道 山田線 (伊勢中川〜宇治山田)
  - 近畿日本鉄道 鳥羽線 (宇治山田〜鳥羽)
  - 近畿日本鉄道 志摩線 (鳥羽〜賢島)

実ダイヤ:
  - 大阪難波発 10:40 → 賢島着 12:53 (約2時間13分)
  - 賢島発 16:00 → 大阪難波着 18:14 (約2時間14分)
  - 1日1往復 (火曜日運休)
  - 全車特別車、「しまかぜ特別車両料金」が必要

本テンプレートでは曜日変動を無視して毎日同じダイヤとして運用。
所要時間は135分 (2時間15分) に統一。

Stop intervals from 大阪難波:
  OSAKA_NAMBA         +0:00 dep
  OSAKA_UEHOMMACHI    +0:04 arr / +0:05 dep
  TSURUHASHI          +0:08 arr / +0:09 dep
  YAMATO_YAGI         +0:36 arr / +0:37 dep
  UJIYAMADA           +1:55 arr / +1:56 dep
  TOBA                +2:09 arr / +2:10 dep
  KASHIKOJIMA         +2:15 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHIMAKAZE_OSAKA')

STOPS_DOWN = [
    ('OSAKA_NAMBA',      None, 0),
    ('OSAKA_UEHOMMACHI', 4,    5),
    ('TSURUHASHI',       8,    9),
    ('YAMATO_YAGI',      36,   37),
    ('UJIYAMADA',        115,  116),
    ('TOBA',             129,  130),
    ('KASHIKOJIMA',      135,  None),
]
STOPS_UP = [
    ('KASHIKOJIMA',      None, 0),
    ('TOBA',             5,    6),
    ('UJIYAMADA',        19,   20),
    ('YAMATO_YAGI',      98,   99),
    ('TSURUHASHI',       126,  127),
    ('OSAKA_UEHOMMACHI', 130,  131),
    ('OSAKA_NAMBA',      135,  None),
]

# 実ダイヤに合わせて1日1往復のみ (大阪難波 10:40 発、賢島 16:00 発)
WEEKDAY_DOWN_DEPS = ['10:40']
WEEKDAY_UP_DEPS   = ['16:00']
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

    emit('SHIMAKAZE_OSAKA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'しまかぜ{n}', trains, sched_wd, 1)
    emit('SHIMAKAZE_OSAKA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'しまかぜ{n}', trains, sched_wd, 2)
    emit_schedule_only('SHIMAKAZE_OSAKA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHIMAKAZE_OSAKA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
