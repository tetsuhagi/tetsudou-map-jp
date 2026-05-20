#!/usr/bin/env python3
"""
Generate 近鉄ひのとり timetable (大阪難波 ⇔ 近鉄名古屋) — 実本数準拠版.

近畿日本鉄道80000系「ひのとり (Hinotori)」(2020年デビュー)。
名阪甲特急の主力車両だが、アーバンライナー (21000系) と併存運行のため
名阪特急全体の **半分程度** がひのとり、残りはアーバンライナー。

Wikipedia (2022年12月時点) によると、ひのとりは:
  - 平日 15往復 (30本/日)
  - 土休日 19往復 (38本/日)
  これに対応するアーバンライナーが別途運行 (合計で30分間隔の名阪特急網)。

経由路線:
  - 近畿日本鉄道 難波線 + 大阪線 + 名古屋線
  - 伊勢中川駅をデルタ線/短絡線経由 (通過)

代表ダイヤ (実本数準拠、時刻は典型パターン推定):
  平日 15往復:
    毎時 :00 発を基本に 6:00〜20:00 (15本/方向)
    アーバンライナーが :30 発 (本マップ未実装)
  土休日 19往復:
    平日に加え、朝・夕ピーク時に :30 発も配置 (19本/方向)
    観光・帰省需要対応

特徴:
  - 全便を「全停車型」(代表停車パターン) として簡略化
  - 実態では一部速達便 (大和八木・津・近鉄四日市通過) もあるが省略
  - 平日と休日で train_id を分離 (HINOTORI_W / HINOTORI_H)

注: 具体的な時刻はNAVITIME/近鉄公式の取得が困難だったため、本数 (Wikipedia)
と近鉄名阪特急の伝統的な毎時 :00 / :30 パターンから推定で構築。
実時刻取得後、改めて精緻化したい。

Stop intervals from 大阪難波:
  OSAKA_NAMBA          +0:00 dep
  OSAKA_UEHOMMACHI     +0:04 arr / +0:05 dep
  TSURUHASHI           +0:08 arr / +0:09 dep
  YAMATO_YAGI          +0:36 arr / +0:37 dep
  TSU                  +1:35 arr / +1:36 dep
  KINTETSU_YOKKAICHI   +1:50 arr / +1:51 dep
  KINTETSU_NAGOYA      +2:05 arr (=125分)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HINOTORI')

STOPS_DOWN = [
    ('OSAKA_NAMBA',        None, 0),
    ('OSAKA_UEHOMMACHI',   4,    5),
    ('TSURUHASHI',         8,    9),
    ('YAMATO_YAGI',        36,   37),
    ('TSU',                95,   96),
    ('KINTETSU_YOKKAICHI', 110,  111),
    ('KINTETSU_NAGOYA',    125,  None),
]
STOPS_UP = [
    ('KINTETSU_NAGOYA',    None, 0),
    ('KINTETSU_YOKKAICHI', 14,   15),
    ('TSU',                29,   30),
    ('YAMATO_YAGI',        88,   89),
    ('TSURUHASHI',         116,  117),
    ('OSAKA_UEHOMMACHI',   120,  121),
    ('OSAKA_NAMBA',        125,  None),
]

# 平日 15往復 (毎時 :00 発、6:00-20:00)
WEEKDAY_DOWN_DEPS = [
    '06:00', '07:00', '08:00', '09:00', '10:00',
    '11:00', '12:00', '13:00', '14:00', '15:00',
    '16:00', '17:00', '18:00', '19:00', '20:00',
]
WEEKDAY_UP_DEPS = [
    '06:00', '07:00', '08:00', '09:00', '10:00',
    '11:00', '12:00', '13:00', '14:00', '15:00',
    '16:00', '17:00', '18:00', '19:00', '20:00',
]

# 土休日 19往復 (毎時 :00 + 朝夕ピーク :30 を追加)
HOLIDAY_DOWN_DEPS = [
    '06:00', '07:00', '07:30', '08:00', '09:00',
    '09:30', '10:00', '11:00', '12:00', '13:00',
    '14:00', '14:30', '15:00', '16:00', '16:30',
    '17:00', '18:00', '19:00', '20:00',
]
HOLIDAY_UP_DEPS = [
    '06:00', '07:00', '07:30', '08:00', '09:00',
    '09:30', '10:00', '11:00', '12:00', '13:00',
    '14:00', '14:30', '15:00', '16:00', '16:30',
    '17:00', '18:00', '19:00', '20:00',
]


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

    # 平日と休日で時刻が異なるため、train_id を分離
    emit('HINOTORI_W', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ひのとり{n}', trains, sched_wd, 1)
    emit('HINOTORI_W', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ひのとり{n}', trains, sched_wd, 2)
    emit('HINOTORI_H', HOLIDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ひのとり{n}', trains, sched_hd, 1)
    emit('HINOTORI_H', HOLIDAY_UP_DEPS,   STOPS_UP,   'up',   'ひのとり{n}', trains, sched_hd, 2)

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

    print(f'trains.csv: {len(trains)}本')
    print(f'  平日: 下 {len(WEEKDAY_DOWN_DEPS)} + 上 {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本 (15往復)')
    print(f'  休日: 下 {len(HOLIDAY_DOWN_DEPS)} + 上 {len(HOLIDAY_UP_DEPS)} = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本 (19往復)')


if __name__ == '__main__':
    main()
