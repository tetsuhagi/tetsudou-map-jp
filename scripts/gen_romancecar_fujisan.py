#!/usr/bin/env python3
"""
Generate 小田急ロマンスカー ふじさん timetable (新宿 ⇔ 御殿場) — 実ダイヤ準拠版.

小田急電鉄60000形 MSE 専用の系統。新宿からJR御殿場線へ直通する稀少便。
2026年度ダイヤ (2022年3月改正以降、土休日臨時便廃止) を反映。

経由路線:
  - 小田急電鉄 小田原線 (新宿〜新松田)
  - JR東海 御殿場線 (松田〜御殿場)
  ※ 新松田駅と松田駅は徒歩100m程度の隣接駅、MLIT 上は別ノード

代表ダイヤ (実ダイヤ準拠、毎日3往復):
  下り (新宿発):
    ふじさん1号: 06:40 → 御殿場 08:13 (93分)
    ふじさん3号: 10:40 → 御殿場 12:24 (104分)
    ふじさん5号: 14:40 → 御殿場 16:21 (101分)
  上り (御殿場発):
    ふじさん2号: 08:48 → 新宿 10:28 (100分)
    ふじさん4号: 12:48 → 新宿 14:25 (97分)
    ふじさん6号: 17:23 → 新宿 19:05 (102分)

  合計 6本/日

実態の特徴:
  - 朝・昼・夕の3パターン (1往復ずつ)
  - 平日と土休日で同一ダイヤ (土休日臨時便は2022年に廃止)
  - 所要時間 93〜104分 (代表値 100分)

停車駅 (実態):
  新宿 → 新百合ヶ丘 → 相模大野 → 本厚木 → 秦野 → 新松田 → 御殿場
  ※ 町田・海老名は通過 (前実装で誤って停車していた)
  ※ 一部便は駿河小山停車 (本テンプレートでは省略)

Stop intervals from 新宿 (代表値 100分所要):
  SHINJUKU         +0:00 dep
  SHIN_YURIGAOKA   +0:20 arr / +0:21 dep
  SAGAMI_ONO       +0:30 arr / +0:31 dep
  HONATSUGI        +0:45 arr / +0:46 dep
  HADANO           +1:00 arr / +1:01 dep
  SHIN_MATSUDA     +1:15 arr / +1:17 dep   (渡り線で御殿場線へ転線、2分停車)
  GOTEMBA          +1:40 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ROMANCECAR_FUJISAN')

STOPS_DOWN = [
    ('SHINJUKU',       None, 0),
    ('SHIN_YURIGAOKA', 20,   21),
    ('SAGAMI_ONO',     30,   31),
    ('HONATSUGI',      45,   46),
    ('HADANO',         60,   61),
    ('SHIN_MATSUDA',   75,   77),
    ('GOTEMBA',        100,  None),
]
STOPS_UP = [
    ('GOTEMBA',        None, 0),
    ('SHIN_MATSUDA',   23,   25),
    ('HADANO',         39,   40),
    ('HONATSUGI',      54,   55),
    ('SAGAMI_ONO',     69,   70),
    ('SHIN_YURIGAOKA', 79,   80),
    ('SHINJUKU',       100,  None),
]

# 実ダイヤ準拠 (1日3往復、平日・休日同一)
WEEKDAY_DOWN_DEPS = ['06:40', '10:40', '14:40']
WEEKDAY_UP_DEPS   = ['08:48', '12:48', '17:23']
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

    emit('ROMANCECAR_FUJISAN', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ふじさん{n}号', trains, sched_wd, 1)
    emit('ROMANCECAR_FUJISAN', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ふじさん{n}号', trains, sched_wd, 2)
    emit_schedule_only('ROMANCECAR_FUJISAN', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('ROMANCECAR_FUJISAN', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
