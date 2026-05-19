#!/usr/bin/env python3
"""
Generate 東武スペーシア timetable (けごん系統: 浅草 ⇔ 東武日光).

東武鉄道の特急車両「スペーシア」(100系) と「スペーシアX」(N100系) の
代表系統「けごん」を実装。観光特急シリーズ第3弾。

特急種別 (スペーシア系):
  - けごん: 浅草 ⇔ 東武日光 (本テンプレートで実装)
  - きぬ:   浅草 ⇔ 鬼怒川温泉 (将来 SPACIA_KINU で追加予定)
  リバティ (500系) は別車両なので将来別 route_id で実装可能。

代表ダイヤ (けごん):
  - 60分間隔 (毎時 :30 発、観光特急らしくゆったり)
  - 始発: 浅草 7:30 / 東武日光 9:30
  - 終発: 浅草 21:30 / 東武日光 23:30
  - 所要時間 110分 (1時間50分)
  - 1日 30本 (各方向 15本)

実ダイヤとの差:
  - 実際は30〜60分間隔混在、本数も時間帯で変動。代表値で簡略化。
  - 浅草〜東武動物公園 は伊勢崎線、東武動物公園以北は日光線。

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


def gen_hourly(start_h, end_h, minute=30):
    """毎時 :MM 発を生成 (デフォルトは :30)"""
    return [f'{h:02d}:{minute:02d}' for h in range(start_h, end_h + 1)]


# 60分間隔 (毎時 :30 発、観光特急らしく)
WEEKDAY_DOWN_DEPS = gen_hourly(7, 21, minute=30)    # 15本 (7:30〜21:30)
WEEKDAY_UP_DEPS   = gen_hourly(9, 23, minute=30)    # 15本 (9:30〜23:30)
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

    emit('SPACIA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'けごん{n}', trains, sched_wd, 1)
    emit('SPACIA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'けごん{n}', trains, sched_wd, 2)
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
    print(f'weekday: 下 {len(WEEKDAY_DOWN_DEPS)} + 上 {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
