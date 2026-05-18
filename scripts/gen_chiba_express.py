#!/usr/bin/env python3
"""
Generate しおさい・わかしお・さざなみ (千葉方面3兄弟) timetables.

Real 2024 dia:
- しおさい (東京-銚子): ~8往復/方向 (~2h)
- わかしお (東京-安房鴨川): ~10往復/方向 (~2h)
- さざなみ (東京-君津): ~6往復/方向 (~1h10, 平日中心)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# しおさい: 東京-千葉-佐倉-八日市場-旭-銚子
SHIOSAI_DOWN = [
    ('TOKYO',      None,  0),
    ('CHIBA',      40,    41),
    ('SAKURA',     56,    57),
    ('YOKAICHIBA', 85,    86),
    ('ASAHI',      95,    96),
    ('CHOSHI',     120,   None),
]
SHIOSAI_UP = [
    ('CHOSHI',     None,  0),
    ('ASAHI',      24,    25),
    ('YOKAICHIBA', 34,    35),
    ('SAKURA',     63,    64),
    ('CHIBA',      79,    80),
    ('TOKYO',      120,   None),
]

# わかしお: 東京-蘇我-大網-茂原-大原-勝浦-安房鴨川
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

# さざなみ: 東京-蘇我-五井-木更津-君津
SAZANAMI_DOWN = [
    ('TOKYO',    None,  0),
    ('SOGA',     40,    41),
    ('GOI',      48,    49),
    ('KISARAZU', 60,    61),
    ('KIMITSU',  70,    None),
]
SAZANAMI_UP = [
    ('KIMITSU',  None,  0),
    ('KISARAZU', 9,     10),
    ('GOI',      21,    22),
    ('SOGA',     29,    30),
    ('TOKYO',    70,    None),
]

SHIOSAI_WEEKDAY_DOWN = ['07:38', '09:08', '11:08', '13:08', '15:38', '17:23', '18:23', '20:23']
SHIOSAI_WEEKDAY_UP   = ['05:08', '06:23', '08:23', '10:23', '13:23', '15:23', '17:23', '19:43']

WAKASHIO_WEEKDAY_DOWN = ['07:00', '08:50', '09:50', '10:50', '11:50', '13:50', '15:50', '17:50', '18:50', '20:00']
WAKASHIO_WEEKDAY_UP   = ['05:48', '07:09', '08:38', '09:38', '11:38', '13:38', '15:38', '17:01', '18:38', '20:01']

SAZANAMI_WEEKDAY_DOWN = ['07:48', '17:00', '17:30', '18:00', '18:30', '19:00']
SAZANAMI_WEEKDAY_UP   = ['06:18', '06:45', '07:15', '07:43', '08:15', '17:18']
SAZANAMI_HOLIDAY_DOWN = ['07:48', '17:30', '18:30']
SAZANAMI_HOLIDAY_UP   = ['06:45', '07:43', '17:18']


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


def write_route(route_id, prefix, name_jp, deps_down, stops_down, deps_up, stops_up,
                deps_hol_down=None, deps_hol_up=None):
    out_dir = os.path.join(ROOT, 'data', 'timetables', route_id)
    os.makedirs(out_dir, exist_ok=True)
    trains = []
    sched_wd = []
    sched_hd = []

    n = 1
    for dep in deps_down:
        tid = f'{prefix}_{n}'
        trains.append((tid, f'{name_jp}{n}', 'down'))
        for order, (sid, a, d) in enumerate(build_stops(parse_hhmm(dep), stops_down), 1):
            sched_wd.append((tid, order, sid, a, d))
        n += 2
    n = 2
    for dep in deps_up:
        tid = f'{prefix}_{n}'
        trains.append((tid, f'{name_jp}{n}', 'up'))
        for order, (sid, a, d) in enumerate(build_stops(parse_hhmm(dep), stops_up), 1):
            sched_wd.append((tid, order, sid, a, d))
        n += 2

    h_down = deps_hol_down if deps_hol_down is not None else deps_down
    h_up = deps_hol_up if deps_hol_up is not None else deps_up
    n = 1
    for dep in h_down:
        tid = f'{prefix}_{n}'
        for order, (sid, a, d) in enumerate(build_stops(parse_hhmm(dep), stops_down), 1):
            sched_hd.append((tid, order, sid, a, d))
        n += 2
    n = 2
    for dep in h_up:
        tid = f'{prefix}_{n}'
        for order, (sid, a, d) in enumerate(build_stops(parse_hhmm(dep), stops_up), 1):
            sched_hd.append((tid, order, sid, a, d))
        n += 2

    with open(os.path.join(out_dir, 'trains.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,name,direction\n')
        for tid, name, direction in trains:
            f.write(f'{tid},{name},{direction}\n')
    with open(os.path.join(out_dir, 'weekday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched_wd:
            f.write(','.join(map(str, row)) + '\n')
    with open(os.path.join(out_dir, 'holiday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched_hd:
            f.write(','.join(map(str, row)) + '\n')

    print(f'{route_id}: {len(trains)}本')


def main():
    write_route('SHIOSAI', 'SHIOSAI', 'しおさい',
                SHIOSAI_WEEKDAY_DOWN, SHIOSAI_DOWN,
                SHIOSAI_WEEKDAY_UP,   SHIOSAI_UP)
    write_route('WAKASHIO', 'WAKASHIO', 'わかしお',
                WAKASHIO_WEEKDAY_DOWN, WAKASHIO_DOWN,
                WAKASHIO_WEEKDAY_UP,   WAKASHIO_UP)
    write_route('SAZANAMI', 'SAZANAMI', 'さざなみ',
                SAZANAMI_WEEKDAY_DOWN, SAZANAMI_DOWN,
                SAZANAMI_WEEKDAY_UP,   SAZANAMI_UP,
                SAZANAMI_HOLIDAY_DOWN, SAZANAMI_HOLIDAY_UP)


if __name__ == '__main__':
    main()
