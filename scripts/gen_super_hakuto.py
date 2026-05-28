#!/usr/bin/env python3
"""
Generate スーパーはくと timetable (京都⇔倉吉 / 京都⇔鳥取) — 実ダイヤ準拠版.

智頭急行・JR西日本 特急「スーパーはくと」(HOT7000系) の現行ダイヤを反映。
2025年3月15日改正の代表的なパターンを再現。

1 route_id 複数終点パターン:
  ■ スーパーはくと倉吉行 (HAKUTO_*): 9駅停車 (京都-...-倉吉)、所要 210分
    主流: 1日5往復/方向
  ■ スーパーはくと鳥取止 (HAKUTO_T_*): 8駅停車 (京都-...-鳥取)、所要 180分
    1日2往復/方向 (夕方〜夜便、鳥取で終端)

参考: 智頭急行 公式時刻表 / JR西日本 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

Stop intervals from 京都:
  KYOTO       +0:00 dep
  SHIN_OSAKA  +0:30 arr / +0:31 dep
  OSAKA       +0:35 arr / +0:36 dep
  SANNOMIYA   +1:05 arr / +1:06 dep
  HIMEJI      +1:40 arr / +1:41 dep
  KAMIGORI    +1:55 arr / +1:56 dep
  CHIZU       +2:25 arr / +2:26 dep
  TOTTORI     +3:00 arr (鳥取止: ここで終端) / +3:01 dep
  KURAYOSHI   +3:30 arr (倉吉行)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SUPER_HAKUTO')


# === 停車駅パターン ===

# スーパーはくと倉吉行 (9駅)
HAKUTO_DOWN = [
    ('KYOTO',      None,  0),
    ('SHIN_OSAKA', 30,    31),
    ('OSAKA',      35,    36),
    ('SANNOMIYA',  65,    66),
    ('HIMEJI',     100,   101),
    ('KAMIGORI',   115,   116),
    ('CHIZU',      145,   146),
    ('TOTTORI',    180,   181),
    ('KURAYOSHI',  210,   None),
]
HAKUTO_UP = [
    ('KURAYOSHI',  None,  0),
    ('TOTTORI',    29,    30),
    ('CHIZU',      64,    65),
    ('KAMIGORI',   94,    95),
    ('HIMEJI',     109,   110),
    ('SANNOMIYA',  144,   145),
    ('OSAKA',      174,   175),
    ('SHIN_OSAKA', 179,   180),
    ('KYOTO',      210,   None),
]

# スーパーはくと鳥取止 (8駅、倉吉区間カット)
HAKUTO_T_DOWN = [
    ('KYOTO',      None,  0),
    ('SHIN_OSAKA', 30,    31),
    ('OSAKA',      35,    36),
    ('SANNOMIYA',  65,    66),
    ('HIMEJI',     100,   101),
    ('KAMIGORI',   115,   116),
    ('CHIZU',      145,   146),
    ('TOTTORI',    180,   None),
]
HAKUTO_T_UP = [
    ('TOTTORI',    None,  0),
    ('CHIZU',      35,    36),
    ('KAMIGORI',   65,    66),
    ('HIMEJI',     80,    81),
    ('SANNOMIYA',  115,   116),
    ('OSAKA',      145,   146),
    ('SHIN_OSAKA', 150,   151),
    ('KYOTO',      180,   None),
]


# === 発車時刻 ===

# 倉吉行 (主流) - 5往復
HAKUTO_WD_DOWN = [
    '07:50', '09:24',
    '11:24', '13:24',
    '15:24',
]
HAKUTO_WD_UP = [
    '06:24', '08:24',
    '10:24', '12:24',
    '14:24',
]

# 鳥取止 (夕方便) - 2往復
HAKUTO_T_WD_DOWN = [
    '17:24',
    '19:24',
]
HAKUTO_T_WD_UP = [
    '16:24',
    '18:21',
]

HAKUTO_HD_DOWN   = HAKUTO_WD_DOWN
HAKUTO_HD_UP     = HAKUTO_WD_UP
HAKUTO_T_HD_DOWN = HAKUTO_T_WD_DOWN
HAKUTO_T_HD_UP   = HAKUTO_T_WD_UP


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

    # 倉吉行
    emit('HAKUTO', HAKUTO_WD_DOWN, HAKUTO_DOWN, 'down', 'スーパーはくと{n}号', trains, sched_wd, 1)
    emit('HAKUTO', HAKUTO_WD_UP,   HAKUTO_UP,   'up',   'スーパーはくと{n}号', trains, sched_wd, 2)
    emit_schedule_only('HAKUTO', HAKUTO_HD_DOWN, HAKUTO_DOWN, sched_hd, 1)
    emit_schedule_only('HAKUTO', HAKUTO_HD_UP,   HAKUTO_UP,   sched_hd, 2)

    # 鳥取止
    emit('HAKUTO_T', HAKUTO_T_WD_DOWN, HAKUTO_T_DOWN, 'down', 'スーパーはくと{n}号', trains, sched_wd, 1)
    emit('HAKUTO_T', HAKUTO_T_WD_UP,   HAKUTO_T_UP,   'up',   'スーパーはくと{n}号', trains, sched_wd, 2)
    emit_schedule_only('HAKUTO_T', HAKUTO_T_HD_DOWN, HAKUTO_T_DOWN, sched_hd, 1)
    emit_schedule_only('HAKUTO_T', HAKUTO_T_HD_UP,   HAKUTO_T_UP,   sched_hd, 2)

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

    n_k = sum(1 for t in trains if t[0].startswith('HAKUTO_') and t[0].split('_')[1].isdigit())
    n_t = sum(1 for t in trains if t[0].startswith('HAKUTO_T_'))
    print(f'SUPER_HAKUTO trains.csv: {len(trains)}本')
    print(f'  スーパーはくと倉吉行 {n_k} + スーパーはくと鳥取止 {n_t}')


if __name__ == '__main__':
    main()
