#!/usr/bin/env python3
"""
Generate 西武ラビュー timetable (ちちぶ系統: 池袋 ⇔ 西武秩父).

西武鉄道001系「ラビュー (Laview)」は2019年デビューの観光特急。
妹島和世デザインの大型曲面ガラス窓と Laview Yellow のアクセントが特徴。

特急種別:
  - ちちぶ: 池袋 ⇔ 西武秩父 (メイン系統、本テンプレートで実装)
  - むさし: 池袋 ⇔ 飯能 (短距離、平日朝夕中心)
  S-TRAINは40000系運用なのでラビュー系統には含まない。

代表ダイヤ (ちちぶ):
  - 30分間隔 (毎時 :00 / :30)
  - 始発: 池袋 7:00 / 西武秩父 9:00
  - 終発: 池袋 21:30 / 西武秩父 23:30
  - 所要時間 77分 (代表値)
  - 1日 60本 (各方向 30本)

実ダイヤとの差:
  - 実際の本数は平日約15本/方向程度。本テンプレートでは30分間隔の
    代表ダイヤとして簡略化 (シミュレーション動作確認のため多めに)
  - 飯能でスイッチバックする (池袋方面ホームと秩父方面ホームが対向)
    ジオメトリ上は飯能で折り返す形となり、列車アイコンも一旦戻る形で
    秩父方面に進む

Stop intervals from 池袋 (ちちぶ代表):
  IKEBUKURO       +0:00 dep
  TOKOROZAWA      +0:21 arr / +0:22 dep
  IRUMASHI        +0:39 arr / +0:40 dep
  HANNO           +0:47 arr / +0:49 dep  (スイッチバックで2分停車)
  YOKOZE          +1:13 arr / +1:14 dep
  SEIBU_CHICHIBU  +1:17 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'LAVIEW')

STOPS_DOWN = [
    ('IKEBUKURO',      None, 0),
    ('TOKOROZAWA',     21,   22),
    ('IRUMASHI',       39,   40),
    ('HANNO',          47,   49),
    ('YOKOZE',         73,   74),
    ('SEIBU_CHICHIBU', 77,   None),
]
STOPS_UP = [
    ('SEIBU_CHICHIBU', None, 0),
    ('YOKOZE',         3,    4),
    ('HANNO',          28,   30),
    ('IRUMASHI',       37,   38),
    ('TOKOROZAWA',     55,   56),
    ('IKEBUKURO',      77,   None),
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


WEEKDAY_DOWN_DEPS = gen_half_hourly(7, 0, 21, 30)    # 30本
WEEKDAY_UP_DEPS   = gen_half_hourly(9, 0, 23, 30)    # 30本
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

    emit('LAVIEW', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ちちぶ{n}', trains, sched_wd, 1)
    emit('LAVIEW', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ちちぶ{n}', trains, sched_wd, 2)
    emit_schedule_only('LAVIEW', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('LAVIEW', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
