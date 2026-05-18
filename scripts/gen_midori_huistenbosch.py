#!/usr/bin/env python3
"""
Generate みどり・ハウステンボス timetables.

Real 2024 dia:
- みどり (博多-佐世保): ~18往復/方向 (~1h50)
- ハウステンボス (博多-HTB): ~10往復/方向 (~1h45)
- 実態では「みどり+ハウステンボス」併結運転が多いが、本実装では別列車扱い
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIDORI_DOWN = [
    ('HAKATA', None,  0),
    ('TOSU',   30,    31),
    ('SAGA',   50,    51),
    ('KOGI',   75,    76),
    ('SASEBO', 110,   None),
]
MIDORI_UP = [
    ('SASEBO', None,  0),
    ('KOGI',   34,    35),
    ('SAGA',   59,    60),
    ('TOSU',   79,    80),
    ('HAKATA', 110,   None),
]

HTB_DOWN = [
    ('HAKATA',         None,  0),
    ('TOSU',           30,    31),
    ('SAGA',           50,    51),
    ('KOGI',           75,    76),
    ('HAIKI',          100,   101),
    ('HUIS_TEN_BOSCH', 105,   None),
]
HTB_UP = [
    ('HUIS_TEN_BOSCH', None,  0),
    ('HAIKI',          4,     5),
    ('KOGI',           29,    30),
    ('SAGA',           54,    55),
    ('TOSU',           74,    75),
    ('HAKATA',         105,   None),
]


def gen_pattern(start_h, end_h, minute_marks):
    times = []
    for h in range(start_h, end_h + 1):
        for m in minute_marks:
            times.append(f'{h:02d}:{m:02d}')
    return times


MIDORI_WEEKDAY_DOWN = gen_pattern(6, 21, [10])
MIDORI_WEEKDAY_UP   = gen_pattern(6, 21, [40])
HTB_WEEKDAY_DOWN    = gen_pattern(7, 20, [40])
HTB_WEEKDAY_UP      = gen_pattern(7, 20, [15])


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
    with open(os.path.join(out_dir, 'holiday.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,stop_order,station_id,arrival,departure\n')
        for row in sched:
            f.write(','.join(map(str, row)) + '\n')

    print(f'{route_id}: {len(trains)}本')


def main():
    write_route('MIDORI', 'MIDORI', 'みどり',
                MIDORI_WEEKDAY_DOWN, MIDORI_DOWN,
                MIDORI_WEEKDAY_UP,   MIDORI_UP)
    write_route('HUISTENBOSCH', 'HTB', 'ハウステンボス',
                HTB_WEEKDAY_DOWN, HTB_DOWN,
                HTB_WEEKDAY_UP,   HTB_UP)


if __name__ == '__main__':
    main()
