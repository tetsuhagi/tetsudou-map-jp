#!/usr/bin/env python3
"""
Generate きのさき・はしだて・まいづる timetables (京都発北近畿3兄弟).

Real 2024 dia:
- きのさき: ~6往復/方向 (京都→城崎温泉 ~2h25)
- はしだて: ~3-4往復/方向 (京都→天橋立 ~2h05)
- まいづる: ~5往復/方向 (京都→東舞鶴 ~1h35)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# きのさき (京都-城崎温泉)
KINOSAKI_DOWN = [
    ('KYOTO',          None,  0),
    ('SONOBE',         35,    36),
    ('AYABE',          68,    69),
    ('FUKUCHIYAMA',    80,    82),
    ('WADAYAMA',       105,   106),
    ('YOKA',           120,   121),
    ('TOYOOKA',        133,   134),
    ('KINOSAKI_ONSEN', 145,   None),
]
KINOSAKI_UP = [
    ('KINOSAKI_ONSEN', None,  0),
    ('TOYOOKA',        11,    12),
    ('YOKA',           24,    25),
    ('WADAYAMA',       39,    40),
    ('FUKUCHIYAMA',    63,    65),
    ('AYABE',          76,    77),
    ('SONOBE',         109,   110),
    ('KYOTO',          145,   None),
]

# はしだて (京都-天橋立)
HASHIDATE_DOWN = [
    ('KYOTO',          None,  0),
    ('SONOBE',         35,    36),
    ('AYABE',          68,    69),
    ('FUKUCHIYAMA',    80,    82),
    ('MIYAZU',         115,   116),
    ('AMANOHASHIDATE', 125,   None),
]
HASHIDATE_UP = [
    ('AMANOHASHIDATE', None,  0),
    ('MIYAZU',         10,    11),
    ('FUKUCHIYAMA',    43,    45),
    ('AYABE',          56,    57),
    ('SONOBE',         89,    90),
    ('KYOTO',          125,   None),
]

# まいづる (京都-東舞鶴)
MAIZURU_DOWN = [
    ('KYOTO',         None,  0),
    ('SONOBE',        35,    36),
    ('AYABE',         68,    69),
    ('NISHI_MAIZURU', 85,    86),
    ('HIGASHI_MAIZURU', 95,  None),
]
MAIZURU_UP = [
    ('HIGASHI_MAIZURU', None,  0),
    ('NISHI_MAIZURU',   10,    11),
    ('AYABE',           26,    27),
    ('SONOBE',          60,    61),
    ('KYOTO',           95,    None),
]

KINOSAKI_WEEKDAY_DOWN = ['07:34', '09:34', '11:34', '13:34', '15:34', '17:34']
KINOSAKI_WEEKDAY_UP   = ['06:00', '08:00', '10:00', '14:00', '16:00', '18:00']

HASHIDATE_WEEKDAY_DOWN = ['08:34', '10:34', '14:34', '17:34']
HASHIDATE_WEEKDAY_UP   = ['07:00', '11:00', '15:00', '17:00']

MAIZURU_WEEKDAY_DOWN = ['07:08', '09:08', '11:08', '13:08', '17:08', '19:08']
MAIZURU_WEEKDAY_UP   = ['06:30', '08:30', '12:30', '14:30', '16:30', '18:30']


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


def write_route(route_id, prefix, name_jp, deps_down, stops_down, deps_up, stops_up):
    out_dir = os.path.join(ROOT, 'data', 'timetables', route_id)
    os.makedirs(out_dir, exist_ok=True)
    trains = []
    sched = []
    n = 1
    for dep in deps_down:
        tid = f'{prefix}_{n}'
        trains.append((tid, f'{name_jp}{n}', 'down'))
        for order, (sid, a, d) in enumerate(build_stops(parse_hhmm(dep), stops_down), 1):
            sched.append((tid, order, sid, a, d))
        n += 2
    n = 2
    for dep in deps_up:
        tid = f'{prefix}_{n}'
        trains.append((tid, f'{name_jp}{n}', 'up'))
        for order, (sid, a, d) in enumerate(build_stops(parse_hhmm(dep), stops_up), 1):
            sched.append((tid, order, sid, a, d))
        n += 2

    with open(os.path.join(out_dir, 'trains.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,name,direction\n')
        for tid, name, direction in trains:
            f.write(f'{tid},{name},{direction}\n')
    with open(os.path.join(out_dir, 'weekday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched:
            f.write(','.join(map(str, row)) + '\n')
    # holiday = weekday for these routes
    with open(os.path.join(out_dir, 'holiday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched:
            f.write(','.join(map(str, row)) + '\n')

    print(f'{route_id}: {len(trains)}本')


def main():
    write_route('KINOSAKI', 'KINOSAKI', 'きのさき',
                KINOSAKI_WEEKDAY_DOWN, KINOSAKI_DOWN,
                KINOSAKI_WEEKDAY_UP,   KINOSAKI_UP)
    write_route('HASHIDATE', 'HASHIDATE', 'はしだて',
                HASHIDATE_WEEKDAY_DOWN, HASHIDATE_DOWN,
                HASHIDATE_WEEKDAY_UP,   HASHIDATE_UP)
    write_route('MAIZURU', 'MAIZURU', 'まいづる',
                MAIZURU_WEEKDAY_DOWN, MAIZURU_DOWN,
                MAIZURU_WEEKDAY_UP,   MAIZURU_UP)


if __name__ == '__main__':
    main()
