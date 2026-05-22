#!/usr/bin/env python3
"""
Generate 東武スペーシア系統 timetable (浅草 ⇔ 東武日光) — 実態本数準拠版.

東武鉄道の浅草〜東武日光間 特急 (けごん種別) を統合して表現。
車両ごとに区別せず、「東武日光行き特急全般」として運用:
  - 100系スペーシア (旧、5往復程度)
  - N100系スペーシアX (新、4往復、tourist-train.info より)
  - 500系リバティけごん (5往復程度、リバティ会津と併結区間あり)
  合計 約14往復/日

経由路線:
  - 東武鉄道 伊勢崎線 (浅草〜東武動物公園)
  - 東武鉄道 日光線 (東武動物公園〜東武日光)

代表ダイヤ (実態+推定):
  下り (浅草発) 14本:
    スペーシアX (4本): 07:50, 09:00, 10:00, 14:00 (推定)
    その他けごん・リバティけごん (10本): 06:30, 07:30, 11:00, 12:00, 13:00,
      15:00, 16:00, 17:00, 18:00, 19:00
  上り (東武日光発) 14本:
    スペーシアX (4本): 10:20, 11:55, 15:30 (推定), 17:00 (推定)
    その他 (10本): 07:00, 08:00, 09:00, 13:00, 14:00, 15:00, 16:30, 18:00,
      19:00, 20:00

  合計 28本/日

  ※ スペーシアX の時刻は tourist-train.info より正確、他は実本数 +
    1時間間隔の典型パターンから推定。実時刻は時間帯偏在あり。
  ※ 平日/休日でほぼ同等、本マップでは統一

所要時間: 110分 (1時間50分) ※ 車両性能で多少差あり、代表値

Stop intervals from 浅草:
  ASAKUSA         +0:00 dep
  TOKYO_SKYTREE   +0:03 arr / +0:04 dep
  KITASENJU       +0:12 arr / +0:13 dep
  KASUKABE        +0:30 arr / +0:31 dep
  TOCHIGI         +1:05 arr / +1:06 dep
  SHIN_KANUMA     +1:25 arr / +1:26 dep
  SHIMOIMAICHI    +1:38 arr / +1:39 dep
  TOBU_NIKKO      +1:50 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SPACIA')

STOPS_DOWN = [
    ('ASAKUSA',       None, 0),
    ('TOKYO_SKYTREE', 3,    4),
    ('KITASENJU',     12,   13),
    ('KASUKABE',      30,   31),
    ('TOCHIGI',       65,   66),
    ('SHIN_KANUMA',   85,   86),
    ('SHIMOIMAICHI',  98,   99),
    ('TOBU_NIKKO',    110,  None),
]
STOPS_UP = [
    ('TOBU_NIKKO',    None, 0),
    ('SHIMOIMAICHI',  11,   12),
    ('SHIN_KANUMA',   24,   25),
    ('TOCHIGI',       44,   45),
    ('KASUKABE',      79,   80),
    ('KITASENJU',     97,   98),
    ('TOKYO_SKYTREE', 106,  107),
    ('ASAKUSA',       110,  None),
]

# 下り 14本 (スペーシアX 4本実時刻 + その他10本推定)
WEEKDAY_DOWN_DEPS = [
    '06:30',  # リバティけごん
    '07:30',  # けごん (100系)
    '07:50',  # スペーシアX 1号
    '09:00',  # スペーシアX 3号
    '10:00',  # スペーシアX 5号
    '11:00',  # けごん
    '12:00',  # リバティけごん
    '13:00',  # けごん
    '14:00',  # スペーシアX 7号 (推定)
    '15:00',  # けごん
    '16:00',  # リバティけごん
    '17:00',  # けごん
    '18:00',  # リバティけごん
    '19:00',  # けごん
]

# 上り 14本
WEEKDAY_UP_DEPS = [
    '07:00',  # けごん
    '08:00',  # リバティけごん
    '09:00',  # けごん
    '10:20',  # スペーシアX 2号
    '11:55',  # スペーシアX 4号
    '13:00',  # リバティけごん
    '14:00',  # けごん
    '15:00',  # リバティけごん
    '15:30',  # スペーシアX 6号 (推定)
    '16:30',  # けごん
    '17:00',  # スペーシアX 8号 (推定)
    '18:00',  # リバティけごん
    '19:00',  # けごん
    '20:00',  # リバティけごん
]

# 休日も同等で簡略化
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

    emit('SPACIA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'けごん{n}号', trains, sched_wd, 1)
    emit('SPACIA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'けごん{n}号', trains, sched_wd, 2)
    emit_schedule_only('SPACIA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SPACIA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
