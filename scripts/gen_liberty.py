#!/usr/bin/env python3
"""
Generate 東武リバティ会津系統 timetable (浅草 ⇔ 会津田島).

東武500系「リバティ (REVATY)」(2017年デビュー) の代表系統「リバティ会津」。
東武鉄道 → 野岩鉄道 → 会津鉄道 の **3社直通運行** という珍しい運用。

経由路線 (5路線):
  - 東武鉄道 伊勢崎線 (浅草〜東武動物公園)
  - 東武鉄道 日光線   (東武動物公園〜下今市)
  - 東武鉄道 鬼怒川線 (下今市〜新藤原)
  - 野岩鉄道 会津鬼怒川線 (新藤原〜会津高原尾瀬口)
  - 会津鉄道 会津線    (会津高原尾瀬口〜会津田島)

代表ダイヤ (リバティ会津):
  - 2時間間隔 (毎時 :00 発、奇数時)
  - 始発: 浅草 7:00 / 会津田島 8:00
  - 終発: 浅草 21:00 / 会津田島 22:00
  - 所要時間 200分 (3時間20分)
  - 1日 16本 (各方向 8本)

実ダイヤとの差:
  - 実際は1日4〜6本/方向程度。シミュレーション表示の見栄えを考慮し
    2時間間隔の代表ダイヤで多めに設定。
  - リバティは併結・分割運用 (途中駅で「会津」と「けごん/きぬ」が併結
    分離) があるが、本テンプレートでは単独運用として簡略化。

Stop intervals from 浅草:
  ASAKUSA           +0:00 dep
  TOKYO_SKYTREE     +0:03 arr / +0:04 dep
  KITASENJU         +0:12 arr / +0:13 dep
  KASUKABE          +0:30 arr / +0:31 dep
  TOCHIGI           +1:05 arr / +1:06 dep
  SHIN_KANUMA       +1:25 arr / +1:26 dep
  SHIMOIMAICHI      +1:38 arr / +1:39 dep
  KINUGAWA_ONSEN    +1:55 arr / +1:57 dep   (鬼怒川温泉で2分停車)
  SHIN_FUJIWARA     +2:10 arr / +2:11 dep   (野岩鉄道へ)
  AIZU_KOGEN_OZE    +2:40 arr / +2:41 dep   (会津鉄道へ)
  AIZU_TAJIMA       +3:20 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'LIBERTY')

STOPS_DOWN = [
    ('ASAKUSA',         None, 0),
    ('TOKYO_SKYTREE',   3,    4),
    ('KITASENJU',       12,   13),
    ('KASUKABE',        30,   31),
    ('TOCHIGI',         65,   66),
    ('SHIN_KANUMA',     85,   86),
    ('SHIMOIMAICHI',    98,   99),
    ('KINUGAWA_ONSEN',  115,  117),
    ('SHIN_FUJIWARA',   130,  131),
    ('AIZU_KOGEN_OZE',  160,  161),
    ('AIZU_TAJIMA',     200,  None),
]
STOPS_UP = [
    ('AIZU_TAJIMA',     None, 0),
    ('AIZU_KOGEN_OZE',  39,   40),
    ('SHIN_FUJIWARA',   69,   70),
    ('KINUGAWA_ONSEN',  83,   85),
    ('SHIMOIMAICHI',    101,  102),
    ('SHIN_KANUMA',     114,  115),
    ('TOCHIGI',         134,  135),
    ('KASUKABE',        169,  170),
    ('KITASENJU',       187,  188),
    ('TOKYO_SKYTREE',   196,  197),
    ('ASAKUSA',         200,  None),
]


# 実態 (Wikipediaより): リバティ会津は1日4往復 (前 8往復 → 4往復に修正)
# ほぼ全便がリバティけごんと併結、下今市で分割・併合
WEEKDAY_DOWN_DEPS = ['08:00', '11:00', '14:00', '17:00']
WEEKDAY_UP_DEPS   = ['09:00', '12:00', '15:00', '18:00']
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

    emit('LIBERTY', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'リバティ会津{n}', trains, sched_wd, 1)
    emit('LIBERTY', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'リバティ会津{n}', trains, sched_wd, 2)
    emit_schedule_only('LIBERTY', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('LIBERTY', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
