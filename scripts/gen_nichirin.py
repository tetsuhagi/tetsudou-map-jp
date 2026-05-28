#!/usr/bin/env python3
"""
Generate にちりん timetable (大分⇔宮崎 / 小倉⇔宮崎) — 実ダイヤ準拠版.

JR九州 特急「にちりん」(787系/783系) の現行ダイヤを反映。
2025年3月15日改正の代表的なパターンを再現。

1 route_id 複数始点パターン:
  ■ にちりん (NICHIRIN_*): 5駅停車 (OITA-...-MIYAZAKI)、所要 190分
    主流: 1日10往復/方向 (大分-宮崎 区間運転)
  ■ にちりんシーガイア (NICHIRIN_S_*): 9駅停車 (KOKURA-...-MIYAZAKI)、所要 282分
    1日1往復/方向 (小倉⇔宮崎、787系運用)
    ※実際は博多⇔宮崎空港まで運転だが、本マップでは小倉⇔宮崎を表現.

参考: JR九州 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

Stop intervals from 大分 (通常にちりん):
  OITA       +0:00 dep
  SAIKI      +0:55 arr / +0:57 dep
  NOBEOKA    +1:45 arr / +1:47 dep
  HYUGASHI   +2:25 arr / +2:26 dep
  MIYAZAKI   +3:10 arr

Stop intervals from 小倉 (にちりんシーガイア):
  KOKURA     +0:00 dep
  NAKATSU    +0:40 arr / +0:41 dep
  USA        +0:55 arr / +0:56 dep
  BEPPU      +1:20 arr / +1:21 dep
  OITA       +1:30 arr / +1:32 dep
  SAIKI      +2:27 arr / +2:29 dep
  NOBEOKA    +3:17 arr / +3:19 dep
  HYUGASHI   +3:57 arr / +3:58 dep
  MIYAZAKI   +4:42 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'NICHIRIN')


# === 停車駅パターン ===

# にちりん通常 (大分⇔宮崎)
STOPS_DOWN = [
    ('OITA',     None,  0),
    ('SAIKI',    55,    57),
    ('NOBEOKA',  105,   107),
    ('HYUGASHI', 145,   146),
    ('MIYAZAKI', 190,   None),
]
STOPS_UP = [
    ('MIYAZAKI', None,  0),
    ('HYUGASHI', 44,    45),
    ('NOBEOKA',  84,    85),
    ('SAIKI',    133,   135),
    ('OITA',     190,   None),
]

# にちりんシーガイア (小倉⇔宮崎、全9駅停車)
STOPS_S_DOWN = [
    ('KOKURA',   None,  0),
    ('NAKATSU',  40,    41),
    ('USA',      55,    56),
    ('BEPPU',    80,    81),
    ('OITA',     90,    92),
    ('SAIKI',    147,   149),
    ('NOBEOKA',  197,   199),
    ('HYUGASHI', 237,   238),
    ('MIYAZAKI', 282,   None),
]
STOPS_S_UP = [
    ('MIYAZAKI', None,  0),
    ('HYUGASHI', 44,    45),
    ('NOBEOKA',  84,    85),
    ('SAIKI',    133,   135),
    ('OITA',     190,   192),
    ('BEPPU',    202,   203),
    ('USA',      227,   228),
    ('NAKATSU',  242,   243),
    ('KOKURA',   282,   None),
]


# === 発車時刻 ===

# にちりん通常 - 10本/方向
WEEKDAY_DOWN_DEPS = [
    '06:13', '07:30',
    '09:00', '10:30',
    '12:00', '13:30',
    '15:00', '16:30',
    '18:00', '20:00',
]
WEEKDAY_UP_DEPS = [
    '05:43', '07:13',
    '08:30', '10:00',
    '11:30', '13:30',
    '15:00', '16:30',
    '18:00', '19:30',
]

# にちりんシーガイア - 1往復
SEAGAIA_WD_DOWN = [
    '07:00',
]
SEAGAIA_WD_UP = [
    '14:30',
]

HOLIDAY_DOWN_DEPS = WEEKDAY_DOWN_DEPS
HOLIDAY_UP_DEPS   = WEEKDAY_UP_DEPS
SEAGAIA_HD_DOWN   = SEAGAIA_WD_DOWN
SEAGAIA_HD_UP     = SEAGAIA_WD_UP


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

    # にちりん通常
    emit('NICHIRIN', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'にちりん{n}号', trains, sched_wd, 1)
    emit('NICHIRIN', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'にちりん{n}号', trains, sched_wd, 2)
    emit_schedule_only('NICHIRIN', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('NICHIRIN', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

    # にちりんシーガイア
    emit('NICHIRIN_S', SEAGAIA_WD_DOWN, STOPS_S_DOWN, 'down', 'にちりんシーガイア{n}号', trains, sched_wd, 1)
    emit('NICHIRIN_S', SEAGAIA_WD_UP,   STOPS_S_UP,   'up',   'にちりんシーガイア{n}号', trains, sched_wd, 2)
    emit_schedule_only('NICHIRIN_S', SEAGAIA_HD_DOWN, STOPS_S_DOWN, sched_hd, 1)
    emit_schedule_only('NICHIRIN_S', SEAGAIA_HD_UP,   STOPS_S_UP,   sched_hd, 2)

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

    n_n = sum(1 for t in trains if t[0].startswith('NICHIRIN_') and t[0].split('_')[1].isdigit())
    n_s = sum(1 for t in trains if t[0].startswith('NICHIRIN_S_'))
    print(f'NICHIRIN trains.csv: {len(trains)}本')
    print(f'  にちりん {n_n} + にちりんシーガイア {n_s}')


if __name__ == '__main__':
    main()
