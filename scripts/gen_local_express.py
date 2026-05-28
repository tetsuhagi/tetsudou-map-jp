#!/usr/bin/env python3
"""
Generate timetables for remaining local express trains:
- 南紀 (名古屋-紀伊勝浦)
- ふじかわ (静岡-甲府)
- 伊那路 (豊橋-飯田)
- うずしお (岡山-徳島)
- しまんと (高松-高知)

スーパーはくとは 2026-05 で複数終点パターン化のため gen_super_hakuto.py
に分離 (倉吉行 + 鳥取止 variant).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


# 南紀 (名古屋→紀伊勝浦 ~3h30, ~4往復)
NANKI_DOWN = [
    ('NAGOYA',       None,  0),
    ('KUWANA',       30,    31),
    ('YOKKAICHI',    45,    46),
    ('TSU',          80,    81),
    ('MATSUSAKA',    100,   101),
    ('OWASE',        165,   166),
    ('KUMANOSHI',    200,   201),
    ('SHINGU',       220,   221),
    ('KII_KATSUURA', 240,   None),
]
NANKI_UP = [
    ('KII_KATSUURA', None,  0),
    ('SHINGU',       19,    20),
    ('KUMANOSHI',    39,    40),
    ('OWASE',        74,    75),
    ('MATSUSAKA',    139,   140),
    ('TSU',          159,   160),
    ('YOKKAICHI',    194,   195),
    ('KUWANA',       209,   210),
    ('NAGOYA',       240,   None),
]
NANKI_DEPS_DOWN = ['08:02', '10:01', '12:38', '17:32']
NANKI_DEPS_UP   = ['07:30', '13:10', '15:36', '17:13']

# ふじかわ (静岡→甲府 ~2h, ~7往復)
FUJIKAWA_DOWN = [
    ('SHIZUOKA',       None,  0),
    ('FUJI',           20,    21),
    ('FUJINOMIYA',     35,    36),
    ('MINOBU',         85,    86),
    ('KAJIKAZAWAGUCHI', 110, 111),
    ('KOFU',           130,   None),
]
FUJIKAWA_UP = [
    ('KOFU',           None,  0),
    ('KAJIKAZAWAGUCHI', 19,   20),
    ('MINOBU',         44,    45),
    ('FUJINOMIYA',     94,    95),
    ('FUJI',           109,   110),
    ('SHIZUOKA',       130,   None),
]
FUJIKAWA_DEPS_DOWN = ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00']
FUJIKAWA_DEPS_UP   = ['07:00', '09:00', '11:00', '13:00', '15:00', '17:00', '19:00']

# 伊那路 (豊橋→飯田 ~2h30, ~3往復)
INAJI_DOWN = [
    ('TOYOHASHI',  None,  0),
    ('SHINSHIRO',  35,    36),
    ('TENRYUKYO',  130,   131),
    ('IIDA',       150,   None),
]
INAJI_UP = [
    ('IIDA',       None,  0),
    ('TENRYUKYO',  19,    20),
    ('SHINSHIRO',  114,   115),
    ('TOYOHASHI',  150,   None),
]
INAJI_DEPS_DOWN = ['09:30', '13:30', '17:30']
INAJI_DEPS_UP   = ['07:00', '11:00', '15:00']

# NOTE: スーパーはくと は scripts/gen_super_hakuto.py に分離。

# うずしお (岡山→徳島 or 高松→徳島, ~16往復)
UZUSHIO_DOWN = [
    ('OKAYAMA',    None,  0),
    ('KOJIMA',     18,    19),
    ('UTAZU',      28,    29),
    ('TAKAMATSU',  60,    61),
    ('TOKUSHIMA',  130,   None),
]
UZUSHIO_UP = [
    ('TOKUSHIMA',  None,  0),
    ('TAKAMATSU',  69,    70),
    ('UTAZU',      101,   102),
    ('KOJIMA',     111,   112),
    ('OKAYAMA',    130,   None),
]
UZUSHIO_DEPS_DOWN = ['06:30', '07:30', '08:30', '09:30', '10:30', '11:30',
                     '12:30', '13:30', '14:30', '15:30', '16:30', '17:30',
                     '18:30', '19:30', '20:30', '21:30']
UZUSHIO_DEPS_UP   = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                     '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                     '18:00', '19:00', '20:00', '21:00']

# しまんと (高松→高知 ~2h30, ~3往復)
SHIMANTO_DOWN = [
    ('TAKAMATSU',   None,  0),
    ('TADOTSU',     32,    33),
    ('KOTOHIRA',    51,    52),
    ('AWA_IKEDA',   76,    77),
    ('TOSA_YAMADA', 129,   130),
    ('KOCHI',       152,   None),
]
SHIMANTO_UP = [
    ('KOCHI',       None,  0),
    ('TOSA_YAMADA', 22,    23),
    ('AWA_IKEDA',   75,    76),
    ('KOTOHIRA',    100,   101),
    ('TADOTSU',     119,   120),
    ('TAKAMATSU',   152,   None),
]
SHIMANTO_DEPS_DOWN = ['08:00', '13:00', '18:00']
SHIMANTO_DEPS_UP   = ['06:00', '11:00', '16:00']


def main():
    write_route('NANKI', 'NANKI', '南紀', NANKI_DEPS_DOWN, NANKI_DOWN, NANKI_DEPS_UP, NANKI_UP)
    write_route('FUJIKAWA', 'FUJIKAWA', 'ふじかわ', FUJIKAWA_DEPS_DOWN, FUJIKAWA_DOWN, FUJIKAWA_DEPS_UP, FUJIKAWA_UP)
    write_route('INAJI', 'INAJI', '伊那路', INAJI_DEPS_DOWN, INAJI_DOWN, INAJI_DEPS_UP, INAJI_UP)
    write_route('UZUSHIO', 'UZUSHIO', 'うずしお', UZUSHIO_DEPS_DOWN, UZUSHIO_DOWN, UZUSHIO_DEPS_UP, UZUSHIO_UP)
    write_route('SHIMANTO', 'SHIMANTO', 'しまんと', SHIMANTO_DEPS_DOWN, SHIMANTO_DOWN, SHIMANTO_DEPS_UP, SHIMANTO_UP)


if __name__ == '__main__':
    main()
