#!/usr/bin/env python3
"""
Generate 九州新幹線 timetable (博多 ⇔ 鹿児島中央) — 実ダイヤ準拠版 + 列車種別拡充.

このスクリプトは gen_kyushu_mizuho_sakura.py を継承・拡張する。
みずほ・さくら統合 (KYUSHU_*) と つばめ博多-熊本 (TSUBAME_*) の発車時刻は
同スクリプトから引き継ぎ、つばめ全線 (TSUBAME_FULL_*) を追加で実装する。

つばめ全線追加の目的: 出水・新水俣の停車駅未カバー問題を解消する。
既存のみずほ・さくらは博多-鹿児島中央を5駅で走るため、出水/新水俣を通過していた。

1 route_id 複数列車種別パターン:
  ■ みずほ・さくら統合 (KYUSHU_*): 5駅停車 (博多・新鳥栖・久留米・熊本・鹿児島中央)、所要 90分
  ■ つばめ博多-熊本 (TSUBAME_*): 7駅停車、所要 50分 — 各駅停車シャトル便
  ■ つばめ全線 (TSUBAME_FULL_*): 全12駅停車、所要 125分 — 1日数本

参考: JR九州・JR西日本 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

注: 実在の特定列車番号と一致させる意図はない. みずほ・さくら・つばめ熊本止は
   実ダイヤの発車時刻、つばめ全線は出水/新水俣 station coverage のための補完便.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'KYUSHU_SHINKANSEN')


# === 停車駅パターン ===

# みずほ・さくら統合: 5駅 (博多・新鳥栖・久留米・熊本・鹿児島中央)
STOPS_DOWN = [
    ('HAKATA',         None,  0),
    ('SHIN_TOSU',      12,    13),
    ('KURUME',         18,    19),
    ('KUMAMOTO',       50,    52),
    ('KAGOSHIMA_CHUO', 90,    None),
]
STOPS_UP = [
    ('KAGOSHIMA_CHUO', None,  0),
    ('KUMAMOTO',       38,    40),
    ('KURUME',         71,    72),
    ('SHIN_TOSU',      77,    78),
    ('HAKATA',         90,    None),
]

# つばめ博多-熊本: 7駅 (各駅停車シャトル)
TSUBAME_STOPS_DOWN = [
    ('HAKATA',            None,  0),
    ('SHIN_TOSU',         12,    13),
    ('KURUME',            18,    19),
    ('CHIKUGO_FUNAGOYA',  25,    26),
    ('SHIN_OMUTA',        32,    33),
    ('SHIN_TAMANA',       40,    41),
    ('KUMAMOTO',          50,    None),
]
TSUBAME_STOPS_UP = [
    ('KUMAMOTO',          None,  0),
    ('SHIN_TAMANA',       9,     10),
    ('SHIN_OMUTA',        17,    18),
    ('CHIKUGO_FUNAGOYA',  24,    25),
    ('KURUME',            31,    32),
    ('SHIN_TOSU',         37,    38),
    ('HAKATA',            50,    None),
]

# つばめ全線 博多-鹿児島中央: 全12駅停車 (出水・新水俣カバー目的)
TSUBAME_FULL_STOPS_DOWN = [
    ('HAKATA',          None, 0),
    ('SHIN_TOSU',       13,   14),
    ('KURUME',          22,   23),
    ('CHIKUGO_FUNAGOYA',32,   33),
    ('SHIN_OMUTA',      42,   43),
    ('SHIN_TAMANA',     52,   53),
    ('KUMAMOTO',        62,   64),
    ('SHIN_YATSUSHIRO', 75,   76),
    ('SHIN_MINAMATA',   90,   91),
    ('IZUMI',           100,  101),
    ('SENDAI_KYUSHU',   112,  113),
    ('KAGOSHIMA_CHUO',  125,  None),
]
TSUBAME_FULL_STOPS_UP = [
    ('KAGOSHIMA_CHUO',  None, 0),
    ('SENDAI_KYUSHU',   12,   13),
    ('IZUMI',           24,   25),
    ('SHIN_MINAMATA',   34,   35),
    ('SHIN_YATSUSHIRO', 49,   50),
    ('KUMAMOTO',        61,   63),
    ('SHIN_TAMANA',     72,   73),
    ('SHIN_OMUTA',      82,   83),
    ('CHIKUGO_FUNAGOYA',92,   93),
    ('KURUME',          102,  103),
    ('SHIN_TOSU',       111,  112),
    ('HAKATA',          125,  None),
]


# === みずほ・さくら統合 発車時刻 (gen_kyushu_mizuho_sakura.py より継承) ===

WEEKDAY_DOWN_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30', '07:48',
    '08:13', '08:30',
    '09:00', '09:30',
    '10:00', '10:30', '10:48',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30', '13:48',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30', '16:48',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30', '19:48',
    '20:00', '20:30',
    '21:00', '21:30', '21:55',
]
WEEKDAY_UP_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:00', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:00',
]
HOLIDAY_DOWN_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30',
    '08:13', '08:30',
    '09:00', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:00', '21:30',
]
HOLIDAY_UP_DEPS = [
    '06:00', '06:32',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:00', '09:30',
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00',
]


# === つばめ博多-熊本 発車時刻 (gen_kyushu_mizuho_sakura.py より継承) ===

TSUBAME_WEEKDAY_DOWN = [
    '06:36', '07:36', '08:00', '08:36',
    '09:36', '10:36', '11:36', '12:36',
    '13:36', '14:36', '15:36',
    '17:00', '18:30', '20:00',
]
TSUBAME_WEEKDAY_UP = [
    '06:48', '07:36', '08:24', '09:30',
    '10:30', '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30', '17:30',
    '18:30', '19:30',
]
TSUBAME_HOLIDAY_DOWN = [
    '06:36', '07:36', '08:36',
    '09:36', '10:36', '11:36', '12:36',
    '13:36', '14:36', '15:36',
    '17:00', '18:30', '20:00',
]
TSUBAME_HOLIDAY_UP = [
    '06:48', '07:36', '08:24',
    '10:30', '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30', '17:30',
    '18:30', '19:30',
]


# === つばめ全線 発車時刻 (NEW、1日数本のみ、出水/新水俣カバー目的) ===

TSUBAME_FULL_WD_DOWN = [
    '07:48',
    '11:54',
    '15:54',
    '19:54',
]
TSUBAME_FULL_WD_UP = [
    '06:30',
    '10:30',
    '14:30',
    '18:30',
]
TSUBAME_FULL_HD_DOWN = TSUBAME_FULL_WD_DOWN
TSUBAME_FULL_HD_UP   = TSUBAME_FULL_WD_UP


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

    # みずほ・さくら統合 (KYUSHU prefix)
    emit('KYUSHU', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'みずほ/さくら{n}', trains, sched_wd, 1)
    emit('KYUSHU', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'みずほ/さくら{n}', trains, sched_wd, 2)
    emit_schedule_only('KYUSHU', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('KYUSHU', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

    # つばめ博多-熊本 (TSUBAME prefix)
    emit('TSUBAME', TSUBAME_WEEKDAY_DOWN, TSUBAME_STOPS_DOWN, 'down', 'つばめ{n}', trains, sched_wd, 1)
    emit('TSUBAME', TSUBAME_WEEKDAY_UP,   TSUBAME_STOPS_UP,   'up',   'つばめ{n}', trains, sched_wd, 2)
    emit_schedule_only('TSUBAME', TSUBAME_HOLIDAY_DOWN, TSUBAME_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TSUBAME', TSUBAME_HOLIDAY_UP,   TSUBAME_STOPS_UP,   sched_hd, 2)

    # つばめ全線 (TSUBAME_FULL prefix) — NEW
    emit('TSUBAME_FULL', TSUBAME_FULL_WD_DOWN, TSUBAME_FULL_STOPS_DOWN, 'down', 'つばめ{n}', trains, sched_wd, 1)
    emit('TSUBAME_FULL', TSUBAME_FULL_WD_UP,   TSUBAME_FULL_STOPS_UP,   'up',   'つばめ{n}', trains, sched_wd, 2)
    emit_schedule_only('TSUBAME_FULL', TSUBAME_FULL_HD_DOWN, TSUBAME_FULL_STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TSUBAME_FULL', TSUBAME_FULL_HD_UP,   TSUBAME_FULL_STOPS_UP,   sched_hd, 2)

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

    n_ky = sum(1 for t in trains if t[0].startswith('KYUSHU'))
    n_ts = sum(1 for t in trains if t[0].startswith('TSUBAME') and not t[0].startswith('TSUBAME_FULL'))
    n_tf = sum(1 for t in trains if t[0].startswith('TSUBAME_FULL'))
    wd = len(set(row[0] for row in sched_wd))
    hd = len(set(row[0] for row in sched_hd))
    print(f'KYUSHU_SHINKANSEN trains.csv: {len(trains)}本')
    print(f'  みずほ/さくら {n_ky} + つばめ熊本止 {n_ts} + つばめ全線 {n_tf}')
    print(f'  平日運行: {wd}本 / 土休日運行: {hd}本')


if __name__ == '__main__':
    main()
