#!/usr/bin/env python3
"""
Generate 東北新幹線 timetable (東京 ⇔ 新青森) — 実ダイヤ準拠版 + 列車種別拡充.

このスクリプトは gen_tohoku.py を継承・拡張する。
はやぶさ・やまびこ仙台行・なすの の発車時刻は同スクリプトから引き継ぎ、
やまびこ盛岡行 (YAMABIKO_M_*) を追加で実装する。

1 route_id 複数列車種別パターン:
  ■ はやぶさ (HAYABUSA_*): 6駅停車 (東京・上野・大宮・仙台・盛岡・新青森)、所要 180分
  ■ やまびこ仙台行 (YAMABIKO_*): 7駅、所要 167分
  ■ やまびこ盛岡行 (YAMABIKO_M_*): 9駅、所要 約3時間
  ■ なすの (NASUNO_*): 6駅停車 (東京・上野・大宮・小山・宇都宮・那須塩原)、所要 88分

参考: JR東日本 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

注: 実在の特定列車番号と一致させる意図はない. はやぶさ・やまびこ仙台行・なすの
   は実ダイヤの発車時刻、やまびこ盛岡行は「だいたい合っている」レベルの代表ダイヤ.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TOHOKU_SHINKANSEN')


# === 停車駅パターン ===

HAYABUSA_STOPS_DOWN = [
    ('TOKYO',       None,  0),
    ('UENO',        6,     7),
    ('OMIYA',       25,    26),
    ('SENDAI',      88,    89),
    ('MORIOKA',     130,   132),
    ('SHIN_AOMORI', 180,   None),
]
HAYABUSA_STOPS_UP = [
    ('SHIN_AOMORI', None,  0),
    ('MORIOKA',     48,    50),
    ('SENDAI',      91,    92),
    ('OMIYA',       154,   155),
    ('UENO',        174,   175),
    ('TOKYO',       180,   None),
]

# やまびこ仙台行 (existing real-dia from gen_tohoku.py)
YAMABIKO_STOPS_DOWN = [
    ('TOKYO',      None,  0),
    ('UENO',       6,     7),
    ('OMIYA',      25,    26),
    ('UTSUNOMIYA', 67,    69),
    ('KORIYAMA',   110,   112),
    ('FUKUSHIMA',  132,   134),
    ('SENDAI',     167,   None),
]
YAMABIKO_STOPS_UP = [
    ('SENDAI',     None,  0),
    ('FUKUSHIMA',  33,    35),
    ('KORIYAMA',   55,    57),
    ('UTSUNOMIYA', 98,    100),
    ('OMIYA',      141,   142),
    ('UENO',       160,   161),
    ('TOKYO',      167,   None),
]

# やまびこ盛岡行 (NEW: 主要駅停車)
YAMABIKO_M_STOPS_DOWN = [
    ('TOKYO',         None, 0),
    ('UENO',          6,    7),
    ('OMIYA',         25,   26),
    ('UTSUNOMIYA',    67,   69),
    ('KORIYAMA',      110,  112),
    ('FUKUSHIMA',     132,  134),
    ('SENDAI',        167,  169),
    ('KITAKAMI',      200,  201),
    ('SHIN_HANAMAKI', 209,  210),
    ('MORIOKA',       220,  None),
]
YAMABIKO_M_STOPS_UP = [
    ('MORIOKA',       None, 0),
    ('SHIN_HANAMAKI', 10,   11),
    ('KITAKAMI',      19,   20),
    ('SENDAI',        51,   53),
    ('FUKUSHIMA',     86,   88),
    ('KORIYAMA',      108,  110),
    ('UTSUNOMIYA',    151,  153),
    ('OMIYA',         194,  195),
    ('UENO',          213,  214),
    ('TOKYO',         220,  None),
]

NASUNO_STOPS_DOWN = [
    ('TOKYO',         None,  0),
    ('UENO',          6,     7),
    ('OMIYA',         25,    26),
    ('OYAMA',         54,    55),
    ('UTSUNOMIYA',    71,    72),
    ('NASU_SHIOBARA', 88,    None),
]
NASUNO_STOPS_UP = [
    ('NASU_SHIOBARA', None,  0),
    ('UTSUNOMIYA',    17,    18),
    ('OYAMA',         34,    35),
    ('OMIYA',         62,    63),
    ('UENO',          81,    82),
    ('TOKYO',         88,    None),
]


# === はやぶさ 発車時刻 (gen_tohoku.py より継承) ===

HAYABUSA_WD_DOWN = [
    '06:32', '07:08', '07:20', '07:32',
    '08:08', '08:20', '08:32',
    '09:08', '09:36',
    '10:20', '10:36',
    '11:36', '12:36', '13:36', '14:36',
    '15:08', '15:36',
    '16:08', '16:36',
    '17:08', '17:36',
    '18:08', '18:36',
    '19:08', '19:36',
    '20:08', '20:36',
    '21:08', '21:20',
]
HAYABUSA_WD_UP = [
    '06:11', '07:00', '07:46',
    '08:30',
    '09:00', '09:34',
    '10:00', '10:36',
    '11:00', '11:36',
    '12:00', '12:36',
    '13:00', '13:36',
    '14:00', '14:36',
    '15:00', '15:36',
    '16:00', '16:36',
    '17:00', '17:36',
    '18:00',
    '19:09',
    '20:09',
    '21:00',
]
HAYABUSA_HD_DOWN = [
    '06:32', '07:08', '07:20', '07:32',
    '08:08', '08:32',
    '09:08', '09:36',
    '10:20', '10:36',
    '11:36', '12:36', '13:36', '14:36',
    '15:36',
    '16:08', '16:36',
    '17:08', '17:36',
    '18:08', '18:36',
    '19:08', '19:36',
    '20:08', '20:36',
    '21:08', '21:20',
]
HAYABUSA_HD_UP = [
    '06:11', '07:00', '07:46',
    '08:30',
    '09:00', '09:34',
    '10:00', '10:36',
    '11:00', '11:36',
    '12:00', '12:36',
    '13:00', '13:36',
    '14:00', '14:36',
    '15:00', '15:36',
    '16:00', '16:36',
    '17:00', '17:36',
    '18:00',
    '19:09',
    '20:09',
]


# === やまびこ仙台行 発車時刻 (gen_tohoku.py より継承) ===

YAMABIKO_WD_DOWN = [
    '06:08', '06:44',
    '07:44',
    '08:44',
    '09:44',
    '10:08', '10:44',
    '11:08', '11:44',
    '12:08', '12:44',
    '13:08', '13:44',
    '14:08', '14:44',
    '15:44',
    '16:44',
    '17:08', '17:44',
    '18:08', '18:44',
    '19:08', '19:44',
    '20:08', '20:44',
    '21:44',
]
YAMABIKO_WD_UP = [
    '06:14', '06:54',
    '07:51',
    '08:51',
    '09:51',
    '10:14', '10:51',
    '11:14', '11:51',
    '12:14', '12:51',
    '13:14', '13:51',
    '14:14', '14:51',
    '15:14', '15:51',
    '16:14', '16:51',
    '17:14',
    '18:14',
    '19:14',
    '20:11',
    '21:18',
]
YAMABIKO_HD_DOWN = [
    '06:08', '06:44',
    '07:44', '08:44', '09:44', '10:44',
    '11:44', '12:44', '13:44', '14:44',
    '15:44', '16:44',
    '17:08', '17:44',
    '18:08', '18:44',
    '19:08', '19:44',
    '20:08', '20:44',
    '21:44',
]
YAMABIKO_HD_UP = [
    '06:14', '06:54',
    '07:51', '08:51', '09:51',
    '10:51', '11:51', '12:51', '13:51', '14:51',
    '15:14', '15:51',
    '16:14', '16:51',
    '17:14',
    '18:14',
    '19:14',
    '20:11',
    '21:18',
]


# === やまびこ盛岡行 発車時刻 (NEW、代表ダイヤ。実際は数本) ===

YAMABIKO_M_WD_DOWN = [
    '06:08',
    '08:08',
    '12:08',
    '16:08',
    '19:00',
    '20:00',
]
YAMABIKO_M_WD_UP = [
    '06:30',
    '07:30',
    '10:30',
    '14:30',
    '18:30',
]
YAMABIKO_M_HD_DOWN = YAMABIKO_M_WD_DOWN
YAMABIKO_M_HD_UP   = YAMABIKO_M_WD_UP


# === なすの 発車時刻 (gen_tohoku.py より継承) ===

NASUNO_WD_DOWN = [
    '06:18',
    '08:28',
    '10:28', '12:28', '14:28', '16:28',
    '18:28',
    '19:28', '20:28', '21:28', '22:28',
]
NASUNO_WD_UP = [
    '06:34',
    '07:32',
    '08:32',
    '10:32', '12:32', '14:32',
    '16:32',
    '18:32', '20:32', '21:32',
]
NASUNO_HD_DOWN = [
    '06:18',
    '08:28', '10:28', '12:28', '14:28', '16:28',
    '18:28', '19:28', '20:28', '21:28',
]
NASUNO_HD_UP = [
    '06:34',
    '08:32',
    '10:32', '12:32', '14:32', '16:32',
    '18:32', '20:32',
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
    emit_trains_and_schedule('HAYABUSA',   HAYABUSA_WD_DOWN,   HAYABUSA_STOPS_DOWN,   'down', 'はやぶさ{n}号', trains, sched_wd, 1,   all_train_ids)
    emit_trains_and_schedule('HAYABUSA',   HAYABUSA_WD_UP,     HAYABUSA_STOPS_UP,     'up',   'はやぶさ{n}号', trains, sched_wd, 2,   all_train_ids)
    emit_trains_and_schedule('YAMABIKO',   YAMABIKO_WD_DOWN,   YAMABIKO_STOPS_DOWN,   'down', 'やまびこ{n}号', trains, sched_wd, 1,   all_train_ids)
    emit_trains_and_schedule('YAMABIKO',   YAMABIKO_WD_UP,     YAMABIKO_STOPS_UP,     'up',   'やまびこ{n}号', trains, sched_wd, 2,   all_train_ids)
    emit_trains_and_schedule('YAMABIKO_M', YAMABIKO_M_WD_DOWN, YAMABIKO_M_STOPS_DOWN, 'down', 'やまびこ{n}号', trains, sched_wd, 51,  all_train_ids)
    emit_trains_and_schedule('YAMABIKO_M', YAMABIKO_M_WD_UP,   YAMABIKO_M_STOPS_UP,   'up',   'やまびこ{n}号', trains, sched_wd, 52,  all_train_ids)
    emit_trains_and_schedule('NASUNO',     NASUNO_WD_DOWN,     NASUNO_STOPS_DOWN,     'down', 'なすの{n}号',   trains, sched_wd, 1,   all_train_ids)
    emit_trains_and_schedule('NASUNO',     NASUNO_WD_UP,       NASUNO_STOPS_UP,       'up',   'なすの{n}号',   trains, sched_wd, 2,   all_train_ids)

    # 土休日
    emit_trains_and_schedule('HAYABUSA',   HAYABUSA_HD_DOWN,   HAYABUSA_STOPS_DOWN,   'down', 'はやぶさ{n}号', trains, sched_hd, 1,   all_train_ids)
    emit_trains_and_schedule('HAYABUSA',   HAYABUSA_HD_UP,     HAYABUSA_STOPS_UP,     'up',   'はやぶさ{n}号', trains, sched_hd, 2,   all_train_ids)
    emit_trains_and_schedule('YAMABIKO',   YAMABIKO_HD_DOWN,   YAMABIKO_STOPS_DOWN,   'down', 'やまびこ{n}号', trains, sched_hd, 1,   all_train_ids)
    emit_trains_and_schedule('YAMABIKO',   YAMABIKO_HD_UP,     YAMABIKO_STOPS_UP,     'up',   'やまびこ{n}号', trains, sched_hd, 2,   all_train_ids)
    emit_trains_and_schedule('YAMABIKO_M', YAMABIKO_M_HD_DOWN, YAMABIKO_M_STOPS_DOWN, 'down', 'やまびこ{n}号', trains, sched_hd, 51,  all_train_ids)
    emit_trains_and_schedule('YAMABIKO_M', YAMABIKO_M_HD_UP,   YAMABIKO_M_STOPS_UP,   'up',   'やまびこ{n}号', trains, sched_hd, 52,  all_train_ids)
    emit_trains_and_schedule('NASUNO',     NASUNO_HD_DOWN,     NASUNO_STOPS_DOWN,     'down', 'なすの{n}号',   trains, sched_hd, 1,   all_train_ids)
    emit_trains_and_schedule('NASUNO',     NASUNO_HD_UP,       NASUNO_STOPS_UP,       'up',   'なすの{n}号',   trains, sched_hd, 2,   all_train_ids)

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

    n_hb = sum(1 for t in trains if t[0].startswith('HAYABUSA'))
    n_ym = sum(1 for t in trains if t[0].startswith('YAMABIKO_') and not t[0].startswith('YAMABIKO_M'))
    n_ymm = sum(1 for t in trains if t[0].startswith('YAMABIKO_M'))
    # YAMABIKO_M's count includes the YAMABIKO_M_* prefix. The above is correct since the
    # YAMABIKO_ prefix (without _M_) means YAMABIKO_<digit> (仙台行).
    n_ns = sum(1 for t in trains if t[0].startswith('NASUNO'))
    wd = len(set(row[0] for row in sched_wd))
    hd = len(set(row[0] for row in sched_hd))
    print(f'TOHOKU_SHINKANSEN trains.csv: {len(trains)}本')
    print(f'  はやぶさ {n_hb} + やまびこ仙台行 {n_ym} + やまびこ盛岡行 {n_ymm} + なすの {n_ns}')
    print(f'  平日運行: {wd}本 / 土休日運行: {hd}本')


if __name__ == '__main__':
    main()
