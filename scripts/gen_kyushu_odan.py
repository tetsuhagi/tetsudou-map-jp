#!/usr/bin/env python3
"""
Generate 九州横断特急 timetable (熊本〜阿蘇〜大分〜別府) — 実ダイヤ準拠版.

JR九州 特急「九州横断特急」(キハ185系)。
2025年3月15日改正後の現行ダイヤを反映。

経由路線:
  - JR九州 豊肥線 (熊本〜阿蘇〜宮地〜豊後竹田〜大分)
  - JR九州 日豊線 (大分〜別府)

2025-03-15 改正の主な変更点:
  - 旧「あそ」(2代) は廃止、九州横断特急が役割を引き継ぎ
  - 旧「あそぼーい！」も別府乗入終了で熊本〜宮地のみに短縮
    (本マップでは 2026-05 に ASOBOY → KYUSHU_ODAN へ route_id 変更)
  - 水前寺・武蔵塚・光の森・赤水・中判田の5駅は全列車通過化

1 route_id 複数終点パターン:
  ■ 九州横断特急 大分行 (KO_*): 11駅停車、所要 145分
    1日2往復: 1号(熊本09:56→大分), 3号(熊本11:51→大分),
              4号(大分12:09→熊本), 6号(大分15:32→熊本)
  ■ 九州横断特急 別府行 (KO_B_*): 全12駅停車、所要 160分
    1日1往復: 5号(熊本15:23→別府), 2号(別府発→大分08:07経由→熊本)

参考: JR九州 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

Stop intervals from 熊本 (大分行):
  KUMAMOTO       +0:00 dep
  SHIN_SUIZENJI  +0:06 arr / +0:07 dep
  HIGO_OZU       +0:22 arr / +0:23 dep
  TATENO         +0:40 arr / +0:41 dep
  ASO            +0:58 arr / +0:59 dep
  MIYAJI         +1:02 arr / +1:03 dep
  BUNGO_OGI      +1:25 arr / +1:26 dep
  BUNGO_TAKETA   +1:36 arr / +1:37 dep
  OGATA          +1:47 arr / +1:48 dep
  MIE_MACHI      +1:58 arr / +1:59 dep
  OITA           +2:25 arr               (大分行: ここで終端) / +2:27 dep
  BEPPU          +2:40 arr               (別府行)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KYUSHU_ODAN')


# === 停車駅パターン ===

# 大分行 (11駅、別府区間カット)
STOPS_O_DOWN = [
    ('KUMAMOTO',      None, 0),
    ('SHIN_SUIZENJI', 6,    7),
    ('HIGO_OZU',      22,   23),
    ('TATENO',        40,   41),
    ('ASO',           58,   59),
    ('MIYAJI',        62,   63),
    ('BUNGO_OGI',     85,   86),
    ('BUNGO_TAKETA',  96,   97),
    ('OGATA',         107,  108),
    ('MIE_MACHI',     118,  119),
    ('OITA',          145,  None),
]
STOPS_O_UP = [
    ('OITA',          None, 0),
    ('MIE_MACHI',     27,   28),
    ('OGATA',         38,   39),
    ('BUNGO_TAKETA',  49,   50),
    ('BUNGO_OGI',     60,   61),
    ('MIYAJI',        83,   84),
    ('ASO',           87,   88),
    ('TATENO',        105,  106),
    ('HIGO_OZU',      123,  124),
    ('SHIN_SUIZENJI', 139,  140),
    ('KUMAMOTO',      145,  None),
]

# 別府行 (全12駅)
STOPS_B_DOWN = [
    ('KUMAMOTO',      None, 0),
    ('SHIN_SUIZENJI', 6,    7),
    ('HIGO_OZU',      22,   23),
    ('TATENO',        40,   41),
    ('ASO',           58,   59),
    ('MIYAJI',        62,   63),
    ('BUNGO_OGI',     85,   86),
    ('BUNGO_TAKETA',  96,   97),
    ('OGATA',         107,  108),
    ('MIE_MACHI',     118,  119),
    ('OITA',          145,  147),
    ('BEPPU',         160,  None),
]
STOPS_B_UP = [
    ('BEPPU',         None, 0),
    ('OITA',          13,   15),
    ('MIE_MACHI',     42,   43),
    ('OGATA',         53,   54),
    ('BUNGO_TAKETA',  64,   65),
    ('BUNGO_OGI',     75,   76),
    ('MIYAJI',        98,   99),
    ('ASO',           102,  103),
    ('TATENO',        120,  121),
    ('HIGO_OZU',      138,  139),
    ('SHIN_SUIZENJI', 154,  155),
    ('KUMAMOTO',      160,  None),
]


# === 発車時刻 (実2025年3月15日改正ダイヤ) ===

# 大分行 (1号・3号 下り、4号・6号 上り)
KO_WD_DOWN = [
    '09:56',  # 1号
    '11:51',  # 3号
]
KO_WD_UP = [
    '12:09',  # 4号 大分発
    '15:32',  # 6号 大分発
]

# 別府行 (5号 下り、2号 上り)
# 2号 大分通過 08:07 → 別府発は逆算で 約 07:52 (大分→別府 ≈ 15分)
KO_B_WD_DOWN = [
    '15:23',  # 5号
]
KO_B_WD_UP = [
    '07:52',  # 2号 (別府発)
]

# 土休日も同一ダイヤ
KO_HD_DOWN   = KO_WD_DOWN
KO_HD_UP     = KO_WD_UP
KO_B_HD_DOWN = KO_B_WD_DOWN
KO_B_HD_UP   = KO_B_WD_UP


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


def emit(prefix, deps, stops_def, direction, name_template, trains, schedule, start_n, step=2):
    n = start_n
    for dep in deps:
        tid = f'{prefix}_{n}'
        trains.append((tid, name_template.format(n=n), direction))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), stops_def), 1):
            schedule.append((tid, order, sid, arr, dp))
        n += step


def emit_schedule_only(prefix, deps, stops_def, schedule, start_n, step=2):
    n = start_n
    for dep in deps:
        tid = f'{prefix}_{n}'
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), stops_def), 1):
            schedule.append((tid, order, sid, arr, dp))
        n += step


def main():
    trains = []
    sched_wd = []
    sched_hd = []

    # 大分行 (KO_*: 下り 1号→KO_1, 3号→KO_3 / 上り 4号→KO_4, 6号→KO_6)
    emit('KO', KO_WD_DOWN, STOPS_O_DOWN, 'down', '九州横断特急{n}号', trains, sched_wd, 1)
    emit('KO', KO_WD_UP,   STOPS_O_UP,   'up',   '九州横断特急{n}号', trains, sched_wd, 4)
    emit_schedule_only('KO', KO_HD_DOWN, STOPS_O_DOWN, sched_hd, 1)
    emit_schedule_only('KO', KO_HD_UP,   STOPS_O_UP,   sched_hd, 4)

    # 別府行 (KO_B_*: 下り 5号→KO_B_5 / 上り 2号→KO_B_2)
    emit('KO_B', KO_B_WD_DOWN, STOPS_B_DOWN, 'down', '九州横断特急{n}号', trains, sched_wd, 5)
    emit('KO_B', KO_B_WD_UP,   STOPS_B_UP,   'up',   '九州横断特急{n}号', trains, sched_wd, 2)
    emit_schedule_only('KO_B', KO_B_HD_DOWN, STOPS_B_DOWN, sched_hd, 5)
    emit_schedule_only('KO_B', KO_B_HD_UP,   STOPS_B_UP,   sched_hd, 2)

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

    n_o = sum(1 for t in trains if t[0].startswith('KO_') and t[0].split('_')[1].isdigit())
    n_b = sum(1 for t in trains if t[0].startswith('KO_B_'))
    print(f'KYUSHU_ODAN trains.csv: {len(trains)}本')
    print(f'  九州横断特急 大分行 {n_o} + 別府行 {n_b}')


if __name__ == '__main__':
    main()
