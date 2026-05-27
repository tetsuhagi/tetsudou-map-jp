#!/usr/bin/env python3
"""
Generate しなの timetable (名古屋⇔長野 / 名古屋⇔松本) — 実ダイヤ準拠版.

JR東海「しなの」(383系) の現行ダイヤを反映。
2025年3月15日改正の代表的なパターンを再現。

1 route_id 複数終点パターン:
  ■ しなの長野行 (SHINANO_*): 9駅停車 (NAGOYA-...-NAGANO)、所要 187分
    1日12本/方向 (主流、毎時1本ベース)
  ■ しなの松本止 (SHINANO_M_*): 7駅停車 (NAGOYA-...-MATSUMOTO)、所要 147分
    1日2本/方向 (区間運転便)

参考: JR東海 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

注: 実在の特定列車番号と一致させる意図はない. 代表的な発車時刻を採用.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'SHINANO')


# === 停車駅パターン (offset from base departure, in minutes) ===

# しなの長野行: 9駅 (full route)
STOPS_DOWN = [
    ('NAGOYA',         None,  0),
    ('CHIKUSA',        5,     6),
    ('TAJIMI',         25,    26),
    ('NAKATSUGAWA',    50,    51),
    ('KISO_FUKUSHIMA', 90,    91),
    ('SHIOJIRI',       130,   132),
    ('MATSUMOTO',      145,   147),
    ('SHINONOI',       175,   176),
    ('NAGANO',         187,   None),
]
STOPS_UP = [
    ('NAGANO',         None,  0),
    ('SHINONOI',       11,    12),
    ('MATSUMOTO',      40,    42),
    ('SHIOJIRI',       55,    57),
    ('KISO_FUKUSHIMA', 96,    97),
    ('NAKATSUGAWA',    136,   137),
    ('TAJIMI',         161,   162),
    ('CHIKUSA',        181,   182),
    ('NAGOYA',         187,   None),
]

# しなの松本止: 7駅 (松本で終端)
STOPS_M_DOWN = [
    ('NAGOYA',         None,  0),
    ('CHIKUSA',        5,     6),
    ('TAJIMI',         25,    26),
    ('NAKATSUGAWA',    50,    51),
    ('KISO_FUKUSHIMA', 90,    91),
    ('SHIOJIRI',       130,   132),
    ('MATSUMOTO',      145,   None),
]
STOPS_M_UP = [
    ('MATSUMOTO',      None,  0),
    ('SHIOJIRI',       15,    17),
    ('KISO_FUKUSHIMA', 56,    57),
    ('NAKATSUGAWA',    96,    97),
    ('TAJIMI',         121,   122),
    ('CHIKUSA',        141,   142),
    ('NAGOYA',         147,   None),
]


# === 発車時刻 (実2024ダイヤ準拠) ===

# 長野行 (主流) - 12本/方向
SHINANO_WD_DOWN = [
    '07:00', '08:00',
    '09:00', '10:00',
    '11:00', '12:00',
    '13:00', '14:00',
    '15:00', '17:00',
    '18:00', '20:00',
]
SHINANO_WD_UP = [
    '06:00', '07:00',
    '08:00', '09:00',
    '10:00', '11:00',
    '12:00', '13:00',
    '14:00', '15:00',
    '16:00', '18:00',
]

# 松本止 - 2本/方向 (午後・夜の区間便)
SHINANO_M_WD_DOWN = [
    '16:00',
    '19:00',
]
SHINANO_M_WD_UP = [
    '17:00',
    '19:00',
]

SHINANO_HD_DOWN   = SHINANO_WD_DOWN
SHINANO_HD_UP     = SHINANO_WD_UP
SHINANO_M_HD_DOWN = SHINANO_M_WD_DOWN
SHINANO_M_HD_UP   = SHINANO_M_WD_UP


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

    # 長野行 (SHINANO prefix)
    emit('SHINANO', SHINANO_WD_DOWN, STOPS_DOWN, 'down', 'しなの{n}号', trains, sched_wd, 1)
    emit('SHINANO', SHINANO_WD_UP,   STOPS_UP,   'up',   'しなの{n}号', trains, sched_wd, 2)
    emit_schedule_only('SHINANO', SHINANO_HD_DOWN, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('SHINANO', SHINANO_HD_UP,   STOPS_UP,   sched_hd, 2)

    # 松本止 (SHINANO_M prefix)
    emit('SHINANO_M', SHINANO_M_WD_DOWN, STOPS_M_DOWN, 'down', 'しなの{n}号', trains, sched_wd, 1)
    emit('SHINANO_M', SHINANO_M_WD_UP,   STOPS_M_UP,   'up',   'しなの{n}号', trains, sched_wd, 2)
    emit_schedule_only('SHINANO_M', SHINANO_M_HD_DOWN, STOPS_M_DOWN, sched_hd, 1)
    emit_schedule_only('SHINANO_M', SHINANO_M_HD_UP,   STOPS_M_UP,   sched_hd, 2)

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

    n_n = sum(1 for t in trains if t[0].startswith('SHINANO_') and t[0].split('_')[1].isdigit())
    n_m = sum(1 for t in trains if t[0].startswith('SHINANO_M_'))
    print(f'SHINANO trains.csv: {len(trains)}本')
    print(f'  しなの長野行 {n_n} + しなの松本止 {n_m}')


if __name__ == '__main__':
    main()
