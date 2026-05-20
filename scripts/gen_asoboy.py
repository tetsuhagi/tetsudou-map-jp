#!/usr/bin/env python3
"""
Generate あそぼーい！ timetable (熊本〜阿蘇〜宮地〜大分〜別府).

JR九州 特急「あそぼーい！」。キハ183系1000番台のファミリー向け観光特急。
2016年熊本震災で豊肥本線一部不通の影響を受けたが、2020年8月全線復旧
以降は **熊本⇔宮地 と 別府⇔阿蘇 の2系統** が併存運行されている。

経由路線:
  - JR九州 豊肥線 (熊本〜阿蘇〜宮地〜豊後竹田〜大分)
  - JR九州 日豊線 (大分〜別府)

2系統:
  ■ 別府発着系 (ASOBOY_B、1号・2号):
      別府⇔阿蘇 (大分経由) 1日1往復
      所要180分 (3時間)
  ■ 熊本発着系 (ASOBOY_K、3号・4号・5号・6号):
      熊本⇔宮地 (阿蘇経由) 1日2往復
      所要140分 (2時間20分)

設計のキモ「1 route_id 複数始終点」:
  routes.csv stations 列: KUMAMOTO|ASO|MIYAJI|OITA|BEPPU
  - 別府発着便: stop_order [BEPPU, OITA, ASO] - 東→西
  - 熊本発着便: stop_order [KUMAMOTO, ASO, MIYAJI] - 西→東
  あしずり方式 (1 route_id 複数終点) を更に拡張、両側からの運行も対応。

代表ダイヤ (1日3往復、計6本):
  1号: 別府 08:48 → 阿蘇 11:48
  2号: 阿蘇 14:00 → 別府 17:00
  3号: 熊本 08:32 → 宮地 10:52 (午前)
  4号: 宮地 11:30 → 熊本 13:50
  5号: 熊本 14:30 → 宮地 16:50 (午後)
  6号: 宮地 17:30 → 熊本 19:50

実ダイヤとの差:
  - 実運行は土日祝中心、1日1〜2往復程度の系統選択あり
  - 本テンプレートでは2系統並走の代表ダイヤとして毎日6本に設定

Stop intervals from 別府 (1号、別府発):
  BEPPU         +0:00 dep
  OITA          +0:15 arr / +0:18 dep
  ASO           +3:00 arr

Stop intervals from 熊本 (3号、熊本発):
  KUMAMOTO      +0:00 dep
  ASO           +2:10 arr / +2:11 dep   (1分停車)
  MIYAJI        +2:20 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ASOBOY')

# 別府発着 (1号・2号)
STOPS_B_DOWN = [
    ('BEPPU', None, 0),
    ('OITA',  15,   18),
    ('ASO',   180,  None),
]
STOPS_B_UP = [
    ('ASO',   None, 0),
    ('OITA',  162,  165),
    ('BEPPU', 180,  None),
]

# 熊本発着 (3号・4号・5号・6号)
STOPS_K_DOWN = [
    ('KUMAMOTO', None, 0),
    ('ASO',      130,  131),
    ('MIYAJI',   140,  None),
]
STOPS_K_UP = [
    ('MIYAJI',   None, 0),
    ('ASO',      9,    10),
    ('KUMAMOTO', 140,  None),
]

# 別府発着 (1日1往復)
WEEKDAY_B_DOWN = ['08:48']
WEEKDAY_B_UP   = ['14:00']

# 熊本発着 (1日2往復、午前・午後)
WEEKDAY_K_DOWN = ['08:32', '14:30']
WEEKDAY_K_UP   = ['11:30', '17:30']

HOLIDAY_B_DOWN = WEEKDAY_B_DOWN
HOLIDAY_B_UP   = WEEKDAY_B_UP
HOLIDAY_K_DOWN = WEEKDAY_K_DOWN
HOLIDAY_K_UP   = WEEKDAY_K_UP


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

    # 別府発着 (1号・2号)
    emit('ASOBOY_B', WEEKDAY_B_DOWN, STOPS_B_DOWN, 'down', 'あそぼーい！{n}号', trains, sched_wd, 1)
    emit('ASOBOY_B', WEEKDAY_B_UP,   STOPS_B_UP,   'up',   'あそぼーい！{n}号', trains, sched_wd, 2)
    emit_schedule_only('ASOBOY_B', HOLIDAY_B_DOWN, STOPS_B_DOWN, sched_hd, 1)
    emit_schedule_only('ASOBOY_B', HOLIDAY_B_UP,   STOPS_B_UP,   sched_hd, 2)

    # 熊本発着 (3号・4号・5号・6号)
    emit('ASOBOY_K', WEEKDAY_K_DOWN, STOPS_K_DOWN, 'down', 'あそぼーい！{n}号', trains, sched_wd, 3)
    emit('ASOBOY_K', WEEKDAY_K_UP,   STOPS_K_UP,   'up',   'あそぼーい！{n}号', trains, sched_wd, 4)
    emit_schedule_only('ASOBOY_K', HOLIDAY_K_DOWN, STOPS_K_DOWN, sched_hd, 3)
    emit_schedule_only('ASOBOY_K', HOLIDAY_K_UP,   STOPS_K_UP,   sched_hd, 4)

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

    beppu_n = sum(1 for tid, _, _ in trains if tid.startswith('ASOBOY_B'))
    kumamoto_n = sum(1 for tid, _, _ in trains if tid.startswith('ASOBOY_K'))
    print(f'trains.csv: {len(trains)}本 (別府発着 {beppu_n}, 熊本発着 {kumamoto_n})')


if __name__ == '__main__':
    main()
