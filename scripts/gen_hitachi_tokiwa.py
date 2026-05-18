#!/usr/bin/env python3
"""
Generate ひたち・ときわ timetable.

Real 2024 dia:
- ひたち仙台行き: ~3本/方向/日 (品川-仙台 ~4h40)
- ひたちいわき行き: ~15本/方向/日 (品川-いわき ~2h25)
- ときわ勝田行き (折り返し): ~20本/方向/日 (品川-勝田 ~1h22)

Stop intervals from 品川:
  SHINAGAWA   +0:00 dep
  UENO        +0:11 arr / +0:12 dep
  MITO        +1:15 arr / +1:17 dep
  KATSUTA     +1:20 arr / +1:21 dep
  HITACHI     +1:35 arr / +1:36 dep
  TAKAHAGI    +1:49 arr / +1:50 dep
  IWAKI       +2:20 arr / +2:22 dep
  HARANOMACHI +3:35 arr / +3:37 dep
  SENDAI      +4:40 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HITACHI_TOKIWA')

HITACHI_SENDAI_DOWN = [
    ('SHINAGAWA',   None,  0),
    ('UENO',        11,    12),
    ('MITO',        75,    77),
    ('KATSUTA',     80,    81),
    ('HITACHI',     95,    96),
    ('TAKAHAGI',    109,   110),
    ('IWAKI',       140,   142),
    ('HARANOMACHI', 215,   217),
    ('SENDAI',      280,   None),
]
HITACHI_SENDAI_UP = [
    ('SENDAI',      None,  0),
    ('HARANOMACHI', 63,    65),
    ('IWAKI',       138,   140),
    ('TAKAHAGI',    170,   171),
    ('HITACHI',     184,   185),
    ('KATSUTA',     199,   200),
    ('MITO',        203,   205),
    ('UENO',        268,   269),
    ('SHINAGAWA',   280,   None),
]

HITACHI_IWAKI_DOWN = [
    ('SHINAGAWA', None,  0),
    ('UENO',      11,    12),
    ('MITO',      75,    77),
    ('KATSUTA',   80,    81),
    ('HITACHI',   95,    96),
    ('TAKAHAGI',  109,   110),
    ('IWAKI',     145,   None),
]
HITACHI_IWAKI_UP = [
    ('IWAKI',     None,  0),
    ('TAKAHAGI',  35,    36),
    ('HITACHI',   49,    50),
    ('KATSUTA',   64,    65),
    ('MITO',      68,    70),
    ('UENO',      133,   134),
    ('SHINAGAWA', 145,   None),
]

TOKIWA_KATSUTA_DOWN = [
    ('SHINAGAWA', None,  0),
    ('UENO',      11,    12),
    ('MITO',      78,    80),
    ('KATSUTA',   85,    None),
]
TOKIWA_KATSUTA_UP = [
    ('KATSUTA',   None,  0),
    ('MITO',      5,     7),
    ('UENO',      73,    74),
    ('SHINAGAWA', 85,    None),
]

HITACHI_SENDAI_WEEKDAY_DOWN = ['09:45', '13:45', '16:45']
HITACHI_SENDAI_WEEKDAY_UP   = ['06:14', '11:30', '15:30']
HITACHI_SENDAI_HOLIDAY_DOWN = ['09:45', '13:45', '16:45']
HITACHI_SENDAI_HOLIDAY_UP   = ['06:14', '11:30', '15:30']

HITACHI_IWAKI_WEEKDAY_DOWN = [
    '06:45', '07:00', '08:00',
    '10:00', '11:00', '12:00',
    '14:00', '15:00', '15:45',
    '17:45', '18:00', '19:00', '20:00',
    '21:00', '22:00',
]
HITACHI_IWAKI_WEEKDAY_UP = [
    '06:50', '08:00', '09:00',
    '10:00', '11:00', '12:00',
    '13:00', '14:00',
    '16:00', '17:00', '18:00', '19:00',
    '20:00', '21:00', '22:00',
]
HITACHI_IWAKI_HOLIDAY_DOWN = [
    '06:45', '07:00', '08:00',
    '10:00', '11:00', '12:00',
    '14:00', '15:00',
    '17:45', '18:00', '19:00', '20:00',
    '21:00',
]
HITACHI_IWAKI_HOLIDAY_UP = [
    '06:50', '08:00', '09:00',
    '10:00', '11:00', '12:00',
    '13:00', '14:00',
    '16:00', '17:00', '18:00', '19:00',
    '21:00',
]

TOKIWA_KATSUTA_WEEKDAY_DOWN = [
    '06:30', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:00', '16:30',
    '17:00', '17:30', '18:30',
    '19:30', '20:30',
    '21:30', '22:30',
    '23:00',
]
TOKIWA_KATSUTA_WEEKDAY_UP = [
    '05:30', '06:30',
    '07:00', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30', '21:30',
    '22:30', '23:00',
]
TOKIWA_KATSUTA_HOLIDAY_DOWN = [
    '06:30', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30', '21:30',
    '22:30',
]
TOKIWA_KATSUTA_HOLIDAY_UP = [
    '06:30', '07:30',
    '08:30', '09:30',
    '10:30', '11:30',
    '12:30', '13:30',
    '14:30', '15:30',
    '16:30', '17:30',
    '18:30', '19:30',
    '20:30', '21:30',
    '22:30',
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

    emit('HITACHI_S', HITACHI_SENDAI_WEEKDAY_DOWN, HITACHI_SENDAI_DOWN, 'down', 'ひたち(仙台){n}', trains, sched_wd, 1)
    emit('HITACHI_S', HITACHI_SENDAI_WEEKDAY_UP,   HITACHI_SENDAI_UP,   'up',   'ひたち(仙台){n}', trains, sched_wd, 2)
    emit_schedule_only('HITACHI_S', HITACHI_SENDAI_HOLIDAY_DOWN, HITACHI_SENDAI_DOWN, sched_hd, 1)
    emit_schedule_only('HITACHI_S', HITACHI_SENDAI_HOLIDAY_UP,   HITACHI_SENDAI_UP,   sched_hd, 2)

    emit('HITACHI_I', HITACHI_IWAKI_WEEKDAY_DOWN, HITACHI_IWAKI_DOWN, 'down', 'ひたち(いわき){n}', trains, sched_wd, 1)
    emit('HITACHI_I', HITACHI_IWAKI_WEEKDAY_UP,   HITACHI_IWAKI_UP,   'up',   'ひたち(いわき){n}', trains, sched_wd, 2)
    emit_schedule_only('HITACHI_I', HITACHI_IWAKI_HOLIDAY_DOWN, HITACHI_IWAKI_DOWN, sched_hd, 1)
    emit_schedule_only('HITACHI_I', HITACHI_IWAKI_HOLIDAY_UP,   HITACHI_IWAKI_UP,   sched_hd, 2)

    emit('TOKIWA', TOKIWA_KATSUTA_WEEKDAY_DOWN, TOKIWA_KATSUTA_DOWN, 'down', 'ときわ(勝田){n}', trains, sched_wd, 1)
    emit('TOKIWA', TOKIWA_KATSUTA_WEEKDAY_UP,   TOKIWA_KATSUTA_UP,   'up',   'ときわ(勝田){n}', trains, sched_wd, 2)
    emit_schedule_only('TOKIWA', TOKIWA_KATSUTA_HOLIDAY_DOWN, TOKIWA_KATSUTA_DOWN, sched_hd, 1)
    emit_schedule_only('TOKIWA', TOKIWA_KATSUTA_HOLIDAY_UP,   TOKIWA_KATSUTA_UP,   sched_hd, 2)

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
    wd_d = len(HITACHI_SENDAI_WEEKDAY_DOWN) + len(HITACHI_IWAKI_WEEKDAY_DOWN) + len(TOKIWA_KATSUTA_WEEKDAY_DOWN)
    wd_u = len(HITACHI_SENDAI_WEEKDAY_UP) + len(HITACHI_IWAKI_WEEKDAY_UP) + len(TOKIWA_KATSUTA_WEEKDAY_UP)
    hd_d = len(HITACHI_SENDAI_HOLIDAY_DOWN) + len(HITACHI_IWAKI_HOLIDAY_DOWN) + len(TOKIWA_KATSUTA_HOLIDAY_DOWN)
    hd_u = len(HITACHI_SENDAI_HOLIDAY_UP) + len(HITACHI_IWAKI_HOLIDAY_UP) + len(TOKIWA_KATSUTA_HOLIDAY_UP)
    print(f'weekday: 下 {wd_d} + 上 {wd_u} = {wd_d + wd_u}本')
    print(f'holiday: 下 {hd_d} + 上 {hd_u} = {hd_d + hd_u}本')


if __name__ == '__main__':
    main()
