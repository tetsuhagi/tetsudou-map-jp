#!/usr/bin/env python3
"""
Generate 近鉄しまかぜ 名古屋系統 timetable (近鉄名古屋 ⇔ 賢島).

近鉄50000系「しまかぜ」3起点モデルの名古屋系統。SHIMAKAZE_OSAKA /
SHIMAKAZE_KYOTO のペア。Phase 5/5、しまかぜ実装完了。

経由路線 (4路線):
  - 近畿日本鉄道 名古屋線 (近鉄名古屋〜伊勢中川)
  - 近畿日本鉄道 山田線 (伊勢中川〜宇治山田)
  - 近畿日本鉄道 鳥羽線 (宇治山田〜鳥羽)
  - 近畿日本鉄道 志摩線 (鳥羽〜賢島)

実ダイヤ:
  - 近鉄名古屋発 10:25 → 賢島着 12:38 (約2時間13分)
  - 賢島発 16:10 → 近鉄名古屋着 18:24 (約2時間14分)
  - 1日1往復 (木曜日運休)
  - 全車特別車

簡略化: 所要時間135分 (2時間15分)。曜日変動は無視。

Stop intervals from 近鉄名古屋:
  KINTETSU_NAGOYA      +0:00 dep
  KINTETSU_YOKKAICHI   +0:30 arr / +0:31 dep
  TSU                  +0:55 arr / +0:56 dep
  ISESHI               +1:50 arr / +1:51 dep
  UJIYAMADA            +1:55 arr / +1:56 dep
  TOBA                 +2:09 arr / +2:10 dep
  KASHIKOJIMA          +2:15 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHIMAKAZE_NAGOYA')

STOPS_DOWN = [
    ('KINTETSU_NAGOYA',    None, 0),
    ('KINTETSU_YOKKAICHI', 27,   28),
    ('TSU',                50,   51),
    ('ISESHI',             100,  101),
    ('UJIYAMADA',          105,  106),
    ('TOBA',               118,  119),
    ('KASHIKOJIMA',        122,  None),
]
STOPS_UP = [
    ('KASHIKOJIMA',        None, 0),
    ('TOBA',               5,    6),
    ('UJIYAMADA',          18,   19),
    ('ISESHI',             23,   24),
    ('TSU',                72,   73),
    ('KINTETSU_YOKKAICHI', 95,   96),
    ('KINTETSU_NAGOYA',    124,  None),
]

# 実ダイヤ (2026年版、tourist-train.info より):
#   下り: 近鉄名古屋 10:25 → 賢島 12:27 (122分) ← 前 135分 → 122分に修正
#   上り: 賢島 15:40 → 近鉄名古屋 17:44 (124分) ← 前 16:10 → 15:40 に修正
# 木曜定期運休だが本テンプレートでは毎日運行として簡略化
WEEKDAY_DOWN_DEPS = ['10:25']
WEEKDAY_UP_DEPS   = ['15:40']
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

    emit('SHIMAKAZE_NAGOYA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'しまかぜ{n}', trains, sched_wd, 1)
    emit('SHIMAKAZE_NAGOYA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'しまかぜ{n}', trains, sched_wd, 2)
    emit_schedule_only('SHIMAKAZE_NAGOYA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHIMAKAZE_NAGOYA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
