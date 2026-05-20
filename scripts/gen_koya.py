#!/usr/bin/env python3
"""
Generate 南海こうや timetable (難波 ⇔ 極楽橋).

南海電気鉄道高野線の特急「こうや」。世界遺産・高野山アクセスの山岳特急。
30000系・31000系の急勾配対応車両で運行 (橋本以南は急勾配区間)。
極楽橋駅から高野山ケーブルカー乗り換えで高野山へ。

経由路線: 南海電気鉄道 高野線 (難波〜極楽橋)
  ※ 高野線は MLIT 上で南海単独 (他社と衝突なし)

代表ダイヤ (こうや):
  - 2時間間隔 (毎時 :00 発、奇数時)
  - 難波発: 7:00, 9:00, 11:00, 13:00, 15:00, 17:00, 19:00 → 7本
  - 極楽橋発: 9:30, 11:30, 13:30, 15:30, 17:30, 19:30, 21:30 → 7本
  - 所要時間 100分 (1時間40分)
  - 1日 14本

実ダイヤとの差:
  - 実際の本数は1日5〜6往復程度。シミュレーション表示の見栄えのため
    7往復まで増やしている。
  - 一部の便は「りんかん」(橋本止) として運行され、橋本以南は別便接続。
    本テンプレートでは全便を極楽橋直通の代表ダイヤとして簡略化。

Stop intervals from 難波 (こうや代表):
  NAMBA            +0:00 dep
  SHIN_IMAMIYA     +0:03 arr / +0:04 dep
  TENGACHAYA       +0:06 arr / +0:07 dep
  SAKAITO          +0:14 arr / +0:15 dep
  KAWACHI_NAGANO   +0:33 arr / +0:34 dep
  HASHIMOTO        +1:05 arr / +1:07 dep   (急勾配区間突入、2分停車)
  GOKURAKUBASHI    +1:40 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KOYA')

STOPS_DOWN = [
    ('NAMBA',          None, 0),
    ('SHIN_IMAMIYA',   3,    4),
    ('TENGACHAYA',     6,    7),
    ('SAKAITO',        14,   15),
    ('KAWACHI_NAGANO', 33,   34),
    ('HASHIMOTO',      65,   67),
    ('GOKURAKUBASHI',  100,  None),
]
STOPS_UP = [
    ('GOKURAKUBASHI',  None, 0),
    ('HASHIMOTO',      33,   35),
    ('KAWACHI_NAGANO', 66,   67),
    ('SAKAITO',        85,   86),
    ('TENGACHAYA',     93,   94),
    ('SHIN_IMAMIYA',   96,   97),
    ('NAMBA',          100,  None),
]


def gen_every_2h(start_h, end_h, minute=0):
    """2時間ごとの発時刻"""
    return [f'{h:02d}:{minute:02d}' for h in range(start_h, end_h + 1, 2)]


def gen_every_2h_at(start_h, end_h, minute=30):
    return [f'{h:02d}:{minute:02d}' for h in range(start_h, end_h + 1, 2)]


# 2時間間隔
WEEKDAY_DOWN_DEPS = gen_every_2h(7, 19, minute=0)     # 7,9,11,13,15,17,19 → 7本
WEEKDAY_UP_DEPS   = gen_every_2h_at(9, 21, minute=30) # 9:30, 11:30, ..., 21:30 → 7本
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

    emit('KOYA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'こうや{n}', trains, sched_wd, 1)
    emit('KOYA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'こうや{n}', trains, sched_wd, 2)
    emit_schedule_only('KOYA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('KOYA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
