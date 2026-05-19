#!/usr/bin/env python3
"""
Generate 近鉄しまかぜ 京都系統 timetable (京都 ⇔ 賢島).

近鉄50000系「しまかぜ」3起点モデルの京都系統。SHIMAKAZE_OSAKA の
ペア。Phase 4/5。

経由路線 (6路線):
  - 近畿日本鉄道 京都線 (京都〜大和西大寺)
  - 近畿日本鉄道 橿原線 (大和西大寺〜大和八木)
  - 近畿日本鉄道 大阪線 (大和八木〜伊勢中川)
  - 近畿日本鉄道 山田線 (伊勢中川〜宇治山田)
  - 近畿日本鉄道 鳥羽線 (宇治山田〜鳥羽)
  - 近畿日本鉄道 志摩線 (鳥羽〜賢島)

実ダイヤ:
  - 京都発 09:00 → 賢島着 11:43 (約2時間43分)
  - 賢島発 16:10 → 京都着 18:55 (約2時間45分)
  - 1日1往復 (水曜日運休)
  - 全車特別車

簡略化: 所要時間165分 (2時間45分) に統一。曜日変動は無視。

Stop intervals from 京都:
  KYOTO            +0:00 dep
  YAMATO_SAIDAIJI  +0:35 arr / +0:36 dep
  YAMATO_YAGI      +1:00 arr / +1:01 dep
  ISESHI           +2:30 arr / +2:31 dep
  UJIYAMADA        +2:35 arr / +2:36 dep
  TOBA             +2:50 arr / +2:51 dep
  KASHIKOJIMA      +2:45 arr     ←最終に注意 (修正版下記)

実際の運行時刻に合わせた版:
  KYOTO            +0:00 dep
  YAMATO_SAIDAIJI  +0:35 arr / +0:36 dep
  YAMATO_YAGI      +1:00 arr / +1:01 dep
  ISESHI           +2:25 arr / +2:26 dep
  UJIYAMADA        +2:30 arr / +2:31 dep
  TOBA             +2:43 arr / +2:44 dep
  KASHIKOJIMA      +2:45 arr (実時刻 11:43 → 2h43m)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHIMAKAZE_KYOTO')

STOPS_DOWN = [
    ('KYOTO',           None, 0),
    ('YAMATO_SAIDAIJI', 35,   36),
    ('YAMATO_YAGI',     60,   61),
    ('ISESHI',          145,  146),
    ('UJIYAMADA',       150,  151),
    ('TOBA',            163,  164),
    ('KASHIKOJIMA',     165,  None),
]
STOPS_UP = [
    ('KASHIKOJIMA',     None, 0),
    ('TOBA',            2,    3),
    ('UJIYAMADA',       15,   16),
    ('ISESHI',          20,   21),
    ('YAMATO_YAGI',     105,  106),
    ('YAMATO_SAIDAIJI', 130,  131),
    ('KYOTO',           165,  None),
]

# 実ダイヤ: 京都 09:00 発、賢島 16:10 発
WEEKDAY_DOWN_DEPS = ['09:00']
WEEKDAY_UP_DEPS   = ['16:10']
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

    emit('SHIMAKAZE_KYOTO', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'しまかぜ{n}', trains, sched_wd, 1)
    emit('SHIMAKAZE_KYOTO', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'しまかぜ{n}', trains, sched_wd, 2)
    emit_schedule_only('SHIMAKAZE_KYOTO', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHIMAKAZE_KYOTO', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
