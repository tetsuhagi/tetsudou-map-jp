#!/usr/bin/env python3
"""
Generate ひだ timetable (名古屋⇔富山 / 名古屋⇔高山) — 実ダイヤ準拠版.

JR東海・JR西日本「ひだ」(HC85系) の現行ダイヤを反映。
2025年3月15日改正の代表的なパターンを再現。

1 route_id 複数終点パターン:
  ■ ひだ富山行 (HIDA_*): 7駅停車 (NAGOYA-...-TOYAMA)、所要 240分
    1日3本/方向 (1号・5号・15号 が代表)
  ■ ひだ高山行 (HIDA_T_*): 5駅停車 (NAGOYA-...-TAKAYAMA)、所要 145分
    1日7本/方向 (主流)

  ※ 大阪-高山 直通の「ひだ」(1日1本) は別系統で本マップ未対応.
  ※ HC85系投入後はキハ85時代より所要時間が短縮しているが、おおむね近似.

参考: JR東海 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

注: 実在の特定列車番号と一致させる意図はない. 代表的な発車時刻を採用.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HIDA')


# === 停車駅パターン (offset from base departure, in minutes) ===

# ひだ富山行: NAGOYA-GIFU-MINO_OTA-GERO-TAKAYAMA-HIDA_FURUKAWA-TOYAMA
STOPS_DOWN = [
    ('NAGOYA',        None,  0),
    ('GIFU',          19,    20),
    ('MINO_OTA',      45,    46),
    ('GERO',          100,   102),
    ('TAKAYAMA',      140,   145),
    ('HIDA_FURUKAWA', 158,   159),
    ('TOYAMA',        240,   None),
]
STOPS_UP = [
    ('TOYAMA',        None,  0),
    ('HIDA_FURUKAWA', 81,    82),
    ('TAKAYAMA',      95,    100),
    ('GERO',          138,   140),
    ('MINO_OTA',      194,   195),
    ('GIFU',          220,   221),
    ('NAGOYA',        240,   None),
]

# ひだ高山行: NAGOYA-GIFU-MINO_OTA-GERO-TAKAYAMA (高山止)
STOPS_T_DOWN = [
    ('NAGOYA',        None,  0),
    ('GIFU',          19,    20),
    ('MINO_OTA',      45,    46),
    ('GERO',          100,   102),
    ('TAKAYAMA',      140,   None),
]
STOPS_T_UP = [
    ('TAKAYAMA',      None,  0),
    ('GERO',          38,    40),
    ('MINO_OTA',      94,    95),
    ('GIFU',          120,   121),
    ('NAGOYA',        140,   None),
]


# === 発車時刻 (実2024ダイヤ準拠) ===

# 富山行 (1号・5号・15号 を代表) - 3本/方向
HIDA_F_WD_DOWN = [
    '06:38',
    '08:43',
    '16:03',
]
HIDA_F_WD_UP = [
    '06:23',
    '12:36',
    '17:51',
]
HIDA_F_HD_DOWN = HIDA_F_WD_DOWN
HIDA_F_HD_UP   = HIDA_F_WD_UP

# 高山行 (3号・7号・9号・11号・13号・17号・19号) - 7本/方向
HIDA_T_WD_DOWN = [
    '07:43',
    '09:39',
    '11:43',
    '12:48',
    '14:48',
    '17:48',
    '19:08',
]
HIDA_T_WD_UP = [
    '08:32',
    '09:51',
    '13:51',
    '14:36',
    '15:51',
    '18:51',
    '20:08',
]
HIDA_T_HD_DOWN = HIDA_T_WD_DOWN
HIDA_T_HD_UP   = HIDA_T_WD_UP


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

    # ひだ富山行 (HIDA prefix)
    emit('HIDA', HIDA_F_WD_DOWN, STOPS_DOWN, 'down', 'ひだ{n}号', trains, sched_wd, 1)
    emit('HIDA', HIDA_F_WD_UP,   STOPS_UP,   'up',   'ひだ{n}号', trains, sched_wd, 2)
    emit_schedule_only('HIDA', HIDA_F_HD_DOWN, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HIDA', HIDA_F_HD_UP,   STOPS_UP,   sched_hd, 2)

    # ひだ高山行 (HIDA_T prefix)
    emit('HIDA_T', HIDA_T_WD_DOWN, STOPS_T_DOWN, 'down', 'ひだ{n}号', trains, sched_wd, 1)
    emit('HIDA_T', HIDA_T_WD_UP,   STOPS_T_UP,   'up',   'ひだ{n}号', trains, sched_wd, 2)
    emit_schedule_only('HIDA_T', HIDA_T_HD_DOWN, STOPS_T_DOWN, sched_hd, 1)
    emit_schedule_only('HIDA_T', HIDA_T_HD_UP,   STOPS_T_UP,   sched_hd, 2)

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

    n_f = sum(1 for t in trains if t[0].startswith('HIDA_') and not t[0].startswith('HIDA_T'))
    # HIDA_T_* counts as 高山行, plain HIDA_<n>_ as 富山行
    n_full = sum(1 for t in trains if t[0].startswith('HIDA_') and t[0].split('_')[1].isdigit())
    n_t = sum(1 for t in trains if t[0].startswith('HIDA_T_'))
    print(f'HIDA trains.csv: {len(trains)}本')
    print(f'  ひだ富山行 {n_full} + ひだ高山行 {n_t}')


if __name__ == '__main__':
    main()
