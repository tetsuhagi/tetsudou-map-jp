#!/usr/bin/env python3
"""
Generate 北陸新幹線 timetable (高崎 ⇔ 敦賀) — 実ダイヤ準拠版 + 列車種別拡充.

このスクリプトは gen_hokuriku.py を継承・拡張する。
かがやき・はくたかの発車時刻は同スクリプトから引き継ぎ、
つるぎ (TSURUGI_*) と あさま (ASAMA_*) を追加で実装する。

本マップでは 高崎-敦賀 区間のみ扱う (東京-高崎 は実車では同一だが、マップ上で
は別レイヤ扱い).

1 route_id 複数列車種別パターン:
  ■ かがやき (KAGAYAKI_*): 6駅停車 (高崎・長野・富山・金沢・福井・敦賀)、所要 200分
  ■ はくたか (HAKUTAKA_*): 14駅停車 (各駅停車に近い)、所要 225分
  ■ つるぎ (TSURUGI_*): 富山-敦賀シャトル、所要 90分
  ■ あさま (ASAMA_*): 高崎-長野シャトル、所要 55分

参考: JR西日本・JR東日本 公式時刻表 / NAVITIME / 駅探 2024年3月16日改正

注: 実在の特定列車番号と一致させる意図はない. かがやき・はくたかは実ダイヤの
   発車時刻、つるぎ・あさまは「だいたい合っている」レベルの代表ダイヤ.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'HOKURIKU_SHINKANSEN')


# === 停車駅パターン ===

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

# つるぎ: 富山-敦賀シャトル
TSURUGI_STOPS_DOWN = [
    ('TOYAMA',         None, 0),
    ('SHIN_TAKAOKA',   12,   13),
    ('KANAZAWA',       28,   30),
    ('KOMATSU',        42,   43),
    ('KAGA_ONSEN',     52,   53),
    ('AWARA_ONSEN',    60,   61),
    ('FUKUI',          68,   70),
    ('ECHIZEN_TAKEFU', 78,   79),
    ('TSURUGA',        90,   None),
]
TSURUGI_STOPS_UP = [
    ('TSURUGA',        None, 0),
    ('ECHIZEN_TAKEFU', 10,   11),
    ('FUKUI',          18,   20),
    ('AWARA_ONSEN',    27,   28),
    ('KAGA_ONSEN',     35,   36),
    ('KOMATSU',        45,   46),
    ('KANAZAWA',       59,   61),
    ('SHIN_TAKAOKA',   76,   77),
    ('TOYAMA',         90,   None),
]

# あさま: 高崎-長野シャトル
ASAMA_STOPS_DOWN = [
    ('TAKASAKI',     None, 0),
    ('ANNAKA_HARUNA',8,    9),
    ('KARUIZAWA',    20,   22),
    ('SAKUDAIRA',    30,   31),
    ('UEDA',         40,   41),
    ('NAGANO',       55,   None),
]
ASAMA_STOPS_UP = [
    ('NAGANO',       None, 0),
    ('UEDA',         15,   16),
    ('SAKUDAIRA',    25,   26),
    ('KARUIZAWA',    35,   37),
    ('ANNAKA_HARUNA',47,   48),
    ('TAKASAKI',     55,   None),
]


# === かがやき 発車時刻 (gen_hokuriku.py より継承) ===

KAGAYAKI_WD_DOWN = [
    '07:06', '07:46', '08:14', '10:14',
    '15:14', '17:14', '19:14', '20:14', '20:54', '21:54',
]
KAGAYAKI_WD_UP = [
    '06:11', '07:00', '08:00', '10:00',
    '12:25', '14:25', '16:25', '18:25', '19:00', '20:11',
]
KAGAYAKI_HD_DOWN = [
    '07:06', '07:46', '08:14', '10:14',
    '15:14', '17:14', '19:14', '20:14', '20:54',
]
KAGAYAKI_HD_UP = [
    '06:11', '07:00', '08:00', '10:00',
    '14:25', '16:25', '18:25', '19:00', '20:11',
]


# === はくたか 発車時刻 (gen_hokuriku.py より継承) ===

HAKUTAKA_WD_DOWN = [
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
HAKUTAKA_WD_UP = [
    '06:45', '07:30', '08:30', '09:30', '10:30', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '16:00',
    '17:30', '18:30', '19:30', '20:30', '21:30',
    '22:00',
]
HAKUTAKA_HD_DOWN = [
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
HAKUTAKA_HD_UP = [
    '06:45', '07:30', '08:30', '09:30', '10:30', '11:30',
    '12:00',
    '13:00', '13:30',
    '14:00',
    '15:00', '16:00',
    '17:30', '18:30', '19:30', '20:30', '21:30',
]


# === つるぎ 発車時刻 (NEW、代表ダイヤ。朝夕集中、毎時1〜2本) ===

TSURUGI_WD_DOWN = [
    '06:00', '06:30',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:30',
    '10:30',
    '11:30',
    '12:30',
    '13:30',
    '14:30',
    '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:30',
]
TSURUGI_WD_UP = [
    '06:00', '06:30',
    '07:00', '07:30',
    '08:00', '08:30',
    '09:30',
    '10:30',
    '11:30',
    '12:30',
    '13:30',
    '14:30',
    '15:30',
    '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:30',
]
TSURUGI_HD_DOWN = [
    '07:00', '08:00', '09:00', '10:00',
    '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00',
    '19:00', '20:00', '21:00',
]
TSURUGI_HD_UP = [
    '07:00', '08:00', '09:00', '10:00',
    '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00',
    '19:00', '20:00', '21:00',
]


# === あさま 発車時刻 (NEW、代表ダイヤ。朝夕集中) ===

ASAMA_WD_DOWN = [
    '06:00', '06:30',
    '07:00', '07:30',
    '08:30', '09:30', '10:30',
    '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30',
    '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30',
    '21:30',
]
ASAMA_WD_UP = [
    '06:00', '07:00',
    '07:30', '08:30', '09:30', '10:30',
    '11:30', '12:30', '13:30',
    '14:30', '15:30', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:30',
    '21:30',
]
ASAMA_HD_DOWN = [
    '07:00', '08:00', '09:00', '10:00',
    '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00',
    '19:00', '20:00',
]
ASAMA_HD_UP = [
    '07:00', '08:00', '09:00', '10:00',
    '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00',
    '19:00', '20:00',
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


def emit_trains_and_schedule(prefix, deps, stops_def, direction, name_template, trains, schedule, start_n, all_train_ids):
    n = start_n
    for dep in deps:
        tid = f'{prefix}_{n}'
        if tid not in all_train_ids:
            trains.append((tid, name_template.format(n=n), direction))
            all_train_ids.add(tid)
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(dep), stops_def), 1):
            schedule.append((tid, order, sid, arr, dp))
        n += 2


def main():
    trains = []
    sched_wd = []
    sched_hd = []
    all_train_ids = set()

    # 平日
    emit_trains_and_schedule('KAGAYAKI', KAGAYAKI_WD_DOWN, KAGAYAKI_STOPS_DOWN, 'down', 'かがやき{n}号', trains, sched_wd, 1, all_train_ids)
    emit_trains_and_schedule('KAGAYAKI', KAGAYAKI_WD_UP,   KAGAYAKI_STOPS_UP,   'up',   'かがやき{n}号', trains, sched_wd, 2, all_train_ids)
    emit_trains_and_schedule('HAKUTAKA', HAKUTAKA_WD_DOWN, HAKUTAKA_STOPS_DOWN, 'down', 'はくたか{n}号', trains, sched_wd, 1, all_train_ids)
    emit_trains_and_schedule('HAKUTAKA', HAKUTAKA_WD_UP,   HAKUTAKA_STOPS_UP,   'up',   'はくたか{n}号', trains, sched_wd, 2, all_train_ids)
    emit_trains_and_schedule('TSURUGI',  TSURUGI_WD_DOWN,  TSURUGI_STOPS_DOWN,  'down', 'つるぎ{n}号',   trains, sched_wd, 1, all_train_ids)
    emit_trains_and_schedule('TSURUGI',  TSURUGI_WD_UP,    TSURUGI_STOPS_UP,    'up',   'つるぎ{n}号',   trains, sched_wd, 2, all_train_ids)
    emit_trains_and_schedule('ASAMA',    ASAMA_WD_DOWN,    ASAMA_STOPS_DOWN,    'down', 'あさま{n}号',   trains, sched_wd, 1, all_train_ids)
    emit_trains_and_schedule('ASAMA',    ASAMA_WD_UP,      ASAMA_STOPS_UP,      'up',   'あさま{n}号',   trains, sched_wd, 2, all_train_ids)

    # 土休日
    emit_trains_and_schedule('KAGAYAKI', KAGAYAKI_HD_DOWN, KAGAYAKI_STOPS_DOWN, 'down', 'かがやき{n}号', trains, sched_hd, 1, all_train_ids)
    emit_trains_and_schedule('KAGAYAKI', KAGAYAKI_HD_UP,   KAGAYAKI_STOPS_UP,   'up',   'かがやき{n}号', trains, sched_hd, 2, all_train_ids)
    emit_trains_and_schedule('HAKUTAKA', HAKUTAKA_HD_DOWN, HAKUTAKA_STOPS_DOWN, 'down', 'はくたか{n}号', trains, sched_hd, 1, all_train_ids)
    emit_trains_and_schedule('HAKUTAKA', HAKUTAKA_HD_UP,   HAKUTAKA_STOPS_UP,   'up',   'はくたか{n}号', trains, sched_hd, 2, all_train_ids)
    emit_trains_and_schedule('TSURUGI',  TSURUGI_HD_DOWN,  TSURUGI_STOPS_DOWN,  'down', 'つるぎ{n}号',   trains, sched_hd, 1, all_train_ids)
    emit_trains_and_schedule('TSURUGI',  TSURUGI_HD_UP,    TSURUGI_STOPS_UP,    'up',   'つるぎ{n}号',   trains, sched_hd, 2, all_train_ids)
    emit_trains_and_schedule('ASAMA',    ASAMA_HD_DOWN,    ASAMA_STOPS_DOWN,    'down', 'あさま{n}号',   trains, sched_hd, 1, all_train_ids)
    emit_trains_and_schedule('ASAMA',    ASAMA_HD_UP,      ASAMA_STOPS_UP,      'up',   'あさま{n}号',   trains, sched_hd, 2, all_train_ids)

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

    n_kg = sum(1 for t in trains if t[0].startswith('KAGAYAKI'))
    n_hk = sum(1 for t in trains if t[0].startswith('HAKUTAKA'))
    n_ts = sum(1 for t in trains if t[0].startswith('TSURUGI'))
    n_as = sum(1 for t in trains if t[0].startswith('ASAMA'))
    wd = len(set(row[0] for row in sched_wd))
    hd = len(set(row[0] for row in sched_hd))
    print(f'HOKURIKU_SHINKANSEN trains.csv: {len(trains)}本')
    print(f'  かがやき {n_kg} + はくたか {n_hk} + つるぎ {n_ts} + あさま {n_as}')
    print(f'  平日運行: {wd}本 / 土休日運行: {hd}本')


if __name__ == '__main__':
    main()
