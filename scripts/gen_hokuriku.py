#!/usr/bin/env python3
"""
Generate 北陸新幹線 timetable (かがやき + はくたか).

Real 2024 dia (敦賀延伸後):
- かがやき (最速): 約10-12本/方向/日, 高崎-長野-富山-金沢-福井-敦賀
- はくたか (標準): 約14-15本/方向/日, 停車駅多め
- つるぎ (富山-金沢シャトル) は本実装では割愛

かがやき stop intervals from 高崎:
  TAKASAKI  +0:00 dep
  NAGANO    +0:47 arr / +0:49 dep
  TOYAMA    +1:46 arr / +1:48 dep
  KANAZAWA  +2:11 arr / +2:13 dep
  FUKUI     +2:58 arr / +3:00 dep
  TSURUGA   +3:20 arr

はくたか stop intervals from 高崎 (14駅停車):
  TAKASAKI       +0:00 dep
  KARUIZAWA      +0:25 arr / +0:26 dep
  UEDA           +0:45 arr / +0:46 dep
  NAGANO         +1:00 arr / +1:02 dep
  JOETSU_MYOKO   +1:22 arr / +1:23 dep
  TOYAMA         +2:17 arr / +2:19 dep
  SHIN_TAKAOKA   +2:26 arr / +2:27 dep
  KANAZAWA       +2:39 arr / +2:41 dep
  KOMATSU        +2:53 arr / +2:54 dep
  KAGA_ONSEN     +3:01 arr / +3:02 dep
  AWARA_ONSEN    +3:12 arr / +3:13 dep
  FUKUI          +3:22 arr / +3:24 dep
  ECHIZEN_TAKEFU +3:35 arr / +3:36 dep
  TSURUGA        +3:45 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HOKURIKU_SHINKANSEN')

KAGAYAKI_STOPS_DOWN = [
    ('TAKASAKI', None,  0),
    ('NAGANO',   47,    49),
    ('TOYAMA',   106,   108),
    ('KANAZAWA', 131,   133),
    ('FUKUI',    178,   180),
    ('TSURUGA',  200,   None),
]

KAGAYAKI_STOPS_UP = [
    ('TSURUGA',  None,  0),
    ('FUKUI',    20,    22),
    ('KANAZAWA', 67,    69),
    ('TOYAMA',   92,    94),
    ('NAGANO',   151,   153),
    ('TAKASAKI', 200,   None),
]

HAKUTAKA_STOPS_DOWN = [
    ('TAKASAKI',       None,  0),
    ('KARUIZAWA',      25,    26),
    ('UEDA',           45,    46),
    ('NAGANO',         60,    62),
    ('JOETSU_MYOKO',   82,    83),
    ('TOYAMA',         137,   139),
    ('SHIN_TAKAOKA',   146,   147),
    ('KANAZAWA',       159,   161),
    ('KOMATSU',        173,   174),
    ('KAGA_ONSEN',     181,   182),
    ('AWARA_ONSEN',    192,   193),
    ('FUKUI',          202,   204),
    ('ECHIZEN_TAKEFU', 215,   216),
    ('TSURUGA',        225,   None),
]

HAKUTAKA_STOPS_UP = [
    ('TSURUGA',        None,  0),
    ('ECHIZEN_TAKEFU', 9,     10),
    ('FUKUI',          21,    23),
    ('AWARA_ONSEN',    32,    33),
    ('KAGA_ONSEN',     43,    44),
    ('KOMATSU',        51,    52),
    ('KANAZAWA',       64,    66),
    ('SHIN_TAKAOKA',   78,    79),
    ('TOYAMA',         86,    88),
    ('JOETSU_MYOKO',   142,   143),
    ('NAGANO',         163,   165),
    ('UEDA',           179,   180),
    ('KARUIZAWA',      199,   200),
    ('TAKASAKI',       225,   None),
]

# かがやき: 高崎発下り (平日)
KAGAYAKI_WEEKDAY_DOWN = [
    '07:06', '07:46', '08:14', '10:14',
    '15:14', '17:14', '19:14', '20:14', '20:54', '21:54',
]
KAGAYAKI_WEEKDAY_UP = [
    '06:11', '07:00', '08:00', '10:00',
    '12:25', '14:25', '16:25', '18:25', '19:00', '20:11',
]
KAGAYAKI_HOLIDAY_DOWN = [
    '07:06', '07:46', '08:14', '10:14',
    '15:14', '17:14', '19:14', '20:14', '20:54',
]
KAGAYAKI_HOLIDAY_UP = [
    '06:11', '07:00', '08:00', '10:00',
    '14:25', '16:25', '18:25', '19:00', '20:11',
]

# はくたか: 高崎発下り (平日)
HAKUTAKA_WEEKDAY_DOWN = [
    '07:18', '08:18',
    '09:18',
    '10:13', '10:48',
    '11:13', '11:48',
    '12:13', '12:48',
    '13:13', '13:48',
    '14:13', '14:48',
    '15:48',
    '16:48',
    '17:48',
    '18:48',
    '19:48',
    '20:48',
    '22:13',
]
HAKUTAKA_WEEKDAY_UP = [
    '06:45',
    '07:30',
    '08:30',
    '09:30',
    '10:30',
    '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00',
    '16:00',
    '17:30',
    '18:30',
    '19:30',
    '20:30',
    '21:30',
    '22:00',
]

HAKUTAKA_HOLIDAY_DOWN = [
    '07:18', '08:18',
    '09:18',
    '10:13', '10:48',
    '11:13', '11:48',
    '12:13', '12:48',
    '13:13', '13:48',
    '14:13',
    '15:48',
    '16:48',
    '17:48',
    '18:48',
    '19:48',
    '20:48',
]
HAKUTAKA_HOLIDAY_UP = [
    '06:45',
    '07:30',
    '08:30',
    '09:30',
    '10:30',
    '11:30',
    '12:00',
    '13:00', '13:30',
    '14:00',
    '15:00',
    '16:00',
    '17:30',
    '18:30',
    '19:30',
    '20:30',
    '21:30',
]


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


def emit(prefix, deps, stops_def, direction, name_template,
         trains, schedule, start_n):
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

    # かがやき
    emit('KAGAYAKI', KAGAYAKI_WEEKDAY_DOWN, KAGAYAKI_STOPS_DOWN, 'down', 'かがやき{n}', trains, sched_wd, 1)
    emit('KAGAYAKI', KAGAYAKI_WEEKDAY_UP,   KAGAYAKI_STOPS_UP,   'up',   'かがやき{n}', trains, sched_wd, 2)
    emit_schedule_only('KAGAYAKI', KAGAYAKI_HOLIDAY_DOWN, KAGAYAKI_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('KAGAYAKI', KAGAYAKI_HOLIDAY_UP,   KAGAYAKI_STOPS_UP,   sched_hd, 2)

    # はくたか
    emit('HAKUTAKA', HAKUTAKA_WEEKDAY_DOWN, HAKUTAKA_STOPS_DOWN, 'down', 'はくたか{n}', trains, sched_wd, 1)
    emit('HAKUTAKA', HAKUTAKA_WEEKDAY_UP,   HAKUTAKA_STOPS_UP,   'up',   'はくたか{n}', trains, sched_wd, 2)
    emit_schedule_only('HAKUTAKA', HAKUTAKA_HOLIDAY_DOWN, HAKUTAKA_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('HAKUTAKA', HAKUTAKA_HOLIDAY_UP,   HAKUTAKA_STOPS_UP,   sched_hd, 2)

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
    wd_d = len(KAGAYAKI_WEEKDAY_DOWN) + len(HAKUTAKA_WEEKDAY_DOWN)
    wd_u = len(KAGAYAKI_WEEKDAY_UP) + len(HAKUTAKA_WEEKDAY_UP)
    hd_d = len(KAGAYAKI_HOLIDAY_DOWN) + len(HAKUTAKA_HOLIDAY_DOWN)
    hd_u = len(KAGAYAKI_HOLIDAY_UP) + len(HAKUTAKA_HOLIDAY_UP)
    print(f'weekday: 下 {wd_d} + 上 {wd_u} = {wd_d + wd_u}本')
    print(f'holiday: 下 {hd_d} + 上 {hd_u} = {hd_d + hd_u}本')


if __name__ == '__main__':
    main()
