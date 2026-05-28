#!/usr/bin/env python3
"""
Generate わかしお timetable (東京⇔安房鴨川 / 東京⇔勝浦) — 実ダイヤ準拠版.

JR東日本 特急「わかしお」(E257系500番台) の現行ダイヤを反映。
2025年3月15日改正の代表的なパターンを再現。

1 route_id 複数終点パターン:
  ■ わかしお安房鴨川行 (WAKASHIO_*): 7駅停車 (東京-...-安房鴨川)、所要 130分
    主流: 1日8往復/方向
  ■ わかしお勝浦止 (WAKASHIO_K_*): 6駅停車 (東京-...-勝浦)、所要 105分
    1日2往復/方向 (朝の早便と夜便など)

参考: JR東日本 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

Stop intervals from 東京:
  TOKYO         +0:00 dep
  SOGA          +0:40 arr / +0:41 dep
  OAMI          +0:55 arr / +0:56 dep
  MOBARA        +1:05 arr / +1:06 dep
  OHARA         +1:28 arr / +1:29 dep
  KATSUURA      +1:45 arr (勝浦止: ここで終端) / +1:46 dep
  AWA_KAMOGAWA  +2:10 arr (安房鴨川行)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'WAKASHIO')


# === 停車駅パターン ===

# 安房鴨川行 (7駅)
WAKASHIO_DOWN = [
    ('TOKYO',        None,  0),
    ('SOGA',         40,    41),
    ('OAMI',         55,    56),
    ('MOBARA',       65,    66),
    ('OHARA',        88,    89),
    ('KATSUURA',     105,   106),
    ('AWA_KAMOGAWA', 130,   None),
]
WAKASHIO_UP = [
    ('AWA_KAMOGAWA', None,  0),
    ('KATSUURA',     24,    25),
    ('OHARA',        41,    42),
    ('MOBARA',       64,    65),
    ('OAMI',         74,    75),
    ('SOGA',         89,    90),
    ('TOKYO',        130,   None),
]

# 勝浦止 (6駅、安房鴨川区間カット)
WAKASHIO_K_DOWN = [
    ('TOKYO',    None,  0),
    ('SOGA',     40,    41),
    ('OAMI',     55,    56),
    ('MOBARA',   65,    66),
    ('OHARA',    88,    89),
    ('KATSUURA', 105,   None),
]
WAKASHIO_K_UP = [
    ('KATSUURA', None,  0),
    ('OHARA',    17,    18),
    ('MOBARA',   40,    41),
    ('OAMI',     50,    51),
    ('SOGA',     65,    66),
    ('TOKYO',    105,   None),
]


# === 発車時刻 ===

# 安房鴨川行 (主流) - 8往復
WAKASHIO_WD_DOWN = [
    '08:50', '09:50', '10:50',
    '11:50', '13:50', '15:50',
    '17:50', '18:50',
]
WAKASHIO_WD_UP = [
    '07:09', '08:38', '09:38',
    '11:38', '13:38', '15:38',
    '17:01', '18:38',
]

# 勝浦止 - 2往復 (朝の早便+夜便)
WAKASHIO_K_WD_DOWN = [
    '07:00',
    '20:00',
]
WAKASHIO_K_WD_UP = [
    '05:48',
    '20:01',
]

WAKASHIO_HD_DOWN   = WAKASHIO_WD_DOWN
WAKASHIO_HD_UP     = WAKASHIO_WD_UP
WAKASHIO_K_HD_DOWN = WAKASHIO_K_WD_DOWN
WAKASHIO_K_HD_UP   = WAKASHIO_K_WD_UP


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

    # 安房鴨川行
    emit('WAKASHIO', WAKASHIO_WD_DOWN, WAKASHIO_DOWN, 'down', 'わかしお{n}号', trains, sched_wd, 1)
    emit('WAKASHIO', WAKASHIO_WD_UP,   WAKASHIO_UP,   'up',   'わかしお{n}号', trains, sched_wd, 2)
    emit_schedule_only('WAKASHIO', WAKASHIO_HD_DOWN, WAKASHIO_DOWN, sched_hd, 1)
    emit_schedule_only('WAKASHIO', WAKASHIO_HD_UP,   WAKASHIO_UP,   sched_hd, 2)

    # 勝浦止
    emit('WAKASHIO_K', WAKASHIO_K_WD_DOWN, WAKASHIO_K_DOWN, 'down', 'わかしお{n}号', trains, sched_wd, 1)
    emit('WAKASHIO_K', WAKASHIO_K_WD_UP,   WAKASHIO_K_UP,   'up',   'わかしお{n}号', trains, sched_wd, 2)
    emit_schedule_only('WAKASHIO_K', WAKASHIO_K_HD_DOWN, WAKASHIO_K_DOWN, sched_hd, 1)
    emit_schedule_only('WAKASHIO_K', WAKASHIO_K_HD_UP,   WAKASHIO_K_UP,   sched_hd, 2)

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

    n_a = sum(1 for t in trains if t[0].startswith('WAKASHIO_') and t[0].split('_')[1].isdigit())
    n_k = sum(1 for t in trains if t[0].startswith('WAKASHIO_K_'))
    print(f'WAKASHIO trains.csv: {len(trains)}本')
    print(f'  わかしお安房鴨川行 {n_a} + わかしお勝浦止 {n_k}')


if __name__ == '__main__':
    main()
