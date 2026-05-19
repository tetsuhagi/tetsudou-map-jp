#!/usr/bin/env python3
"""
Generate 京急エアポート快特 timetable (品川 ⇔ 羽田空港第1・第2ターミナル).

京浜急行電鉄の最速種別「エアポート快特」。厳密には「特急」ではなく
「快速特急」だが、羽田空港アクセスの主役なので本マップでは例外的に
特急枠に追加。

経由路線:
  - 京浜急行電鉄 本線 (品川〜京急蒲田)
  - 京浜急行電鉄 空港線 (京急蒲田〜羽田空港第1・第2ターミナル)

代表ダイヤ:
  - 20分間隔 (毎時 :00 / :20 / :40)
  - 品川発 6:00〜22:40 → 51本
  - 羽田 T1T2 発 6:20〜23:00 → 51本
  - 合計 102本/日
  - 所要 18分 (品川→羽田)

実ダイヤとの差:
  - 実際の本数は約60本/方向、運行時間帯は5時台〜0時台
  - 朝晩は本数増、深夜は減と変動あり。本テンプレートは終日 20分間隔
    の代表ダイヤで簡略化。
  - エアポート快特は時間帯により都営浅草線・京成線方面からの直通便
    (北総線方面・成田スカイアクセス線方面など) もあるが、本テンプレート
    では品川〜羽田の閉じた区間のみ。

Stop intervals from 品川:
  SHINAGAWA       +0:00 dep
  KEIKYU_KAMATA   +0:09 arr / +0:10 dep
  HANEDA_T3       +0:13 arr / +0:14 dep
  HANEDA_T1_T2    +0:18 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KEIKYU_AIRPORT')

STOPS_DOWN = [
    ('SHINAGAWA',     None, 0),
    ('KEIKYU_KAMATA', 9,    10),
    ('HANEDA_T3',     13,   14),
    ('HANEDA_T1_T2',  18,   None),
]
STOPS_UP = [
    ('HANEDA_T1_T2',  None, 0),
    ('HANEDA_T3',     2,    3),
    ('KEIKYU_KAMATA', 7,    8),
    ('SHINAGAWA',     18,   None),
]


def gen_every_20(start_h, start_m, end_h, end_m):
    """毎時 :00, :20, :40 の発時刻を生成"""
    times = []
    h, m = start_h, start_m
    while (h, m) <= (end_h, end_m):
        times.append(f'{h:02d}:{m:02d}')
        m += 20
        if m >= 60:
            m -= 60
            h += 1
    return times


# 20分間隔、6:00〜22:40 (51本/方向)
WEEKDAY_DOWN_DEPS = gen_every_20(6, 0,  22, 40)
WEEKDAY_UP_DEPS   = gen_every_20(6, 20, 23, 0)
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

    emit('KEIKYU_AIRPORT', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'エアポート快特{n}', trains, sched_wd, 1)
    emit('KEIKYU_AIRPORT', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'エアポート快特{n}', trains, sched_wd, 2)
    emit_schedule_only('KEIKYU_AIRPORT', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('KEIKYU_AIRPORT', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
