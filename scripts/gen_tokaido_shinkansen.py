#!/usr/bin/env python3
"""
Generate 東海道新幹線 timetable (東京 ⇔ 新大阪) — 実ダイヤ準拠版 + 列車種別拡充.

このスクリプトは gen_tokaido_nozomi.py を継承・拡張する。
NOZOMI の発車時刻は同スクリプトから引き継ぎ、HIKARI / KODAMA を追加で実装する。

1 route_id 複数列車種別パターン:
  ■ のぞみ (NOZOMI_*): 6駅停車 (東京・品川・新横浜・名古屋・京都・新大阪)、所要 144分
  ■ ひかり (HIKARI_*): 8駅停車 (静岡・浜松停車型代表)、所要 約3時間
  ■ こだま (KODAMA_*): 全17駅停車、所要 約4時間

参考: JR東海 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

注: 実在の特定列車番号と一致させる意図はない. のぞみは実ダイヤの発車時刻、
   ひかり・こだまは「だいたい合っている」レベルの代表ダイヤ.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TOKAIDO_SHINKANSEN')


# === 停車駅パターン (offset from base departure, in minutes) ===

NOZOMI_STOPS_DOWN = [
    ('TOKYO',         None, 0),
    ('SHINAGAWA',     7,    8),
    ('SHIN_YOKOHAMA', 18,   19),
    ('NAGOYA',        96,   97),
    ('KYOTO',         130,  131),
    ('SHIN_OSAKA',    144,  None),
]
NOZOMI_STOPS_UP = [
    ('SHIN_OSAKA',    None, 0),
    ('KYOTO',         13,   14),
    ('NAGOYA',        47,   48),
    ('SHIN_YOKOHAMA', 125,  126),
    ('SHINAGAWA',     136,  137),
    ('TOKYO',         144,  None),
]

HIKARI_STOPS_DOWN = [
    ('TOKYO',         None, 0),
    ('SHINAGAWA',     7,    8),
    ('SHIN_YOKOHAMA', 18,   19),
    ('SHIZUOKA',      79,   81),
    ('HAMAMATSU',     104,  106),
    ('NAGOYA',        130,  132),
    ('KYOTO',         167,  169),
    ('SHIN_OSAKA',    180,  None),
]
HIKARI_STOPS_UP = [
    ('SHIN_OSAKA',    None, 0),
    ('KYOTO',         13,   14),
    ('NAGOYA',        49,   51),
    ('HAMAMATSU',     75,   77),
    ('SHIZUOKA',      100,  102),
    ('SHIN_YOKOHAMA', 162,  163),
    ('SHINAGAWA',     173,  174),
    ('TOKYO',         180,  None),
]

KODAMA_STOPS_DOWN = [
    ('TOKYO',         None, 0),
    ('SHINAGAWA',     7,    8),
    ('SHIN_YOKOHAMA', 18,   19),
    ('ODAWARA',       33,   35),
    ('ATAMI',         44,   45),
    ('MISHIMA',       52,   53),
    ('SHIN_FUJI',     64,   65),
    ('SHIZUOKA',      75,   77),
    ('KAKEGAWA',      92,   94),
    ('HAMAMATSU',     103,  105),
    ('TOYOHASHI',     124,  126),
    ('MIKAWA_ANJO',   145,  147),
    ('NAGOYA',        159,  161),
    ('GIFU_HASHIMA',  180,  181),
    ('MAIBARA',       198,  200),
    ('KYOTO',         226,  227),
    ('SHIN_OSAKA',    240,  None),
]
KODAMA_STOPS_UP = [
    ('SHIN_OSAKA',    None, 0),
    ('KYOTO',         13,   14),
    ('MAIBARA',       41,   43),
    ('GIFU_HASHIMA',  60,   62),
    ('NAGOYA',        80,   82),
    ('MIKAWA_ANJO',   95,   97),
    ('TOYOHASHI',     115,  117),
    ('HAMAMATSU',     136,  138),
    ('KAKEGAWA',      147,  149),
    ('SHIZUOKA',      165,  167),
    ('SHIN_FUJI',     176,  178),
    ('MISHIMA',       188,  189),
    ('ATAMI',         196,  197),
    ('ODAWARA',       206,  208),
    ('SHIN_YOKOHAMA', 222,  223),
    ('SHINAGAWA',     233,  234),
    ('TOKYO',         240,  None),
]


# === のぞみ 発車時刻 (実ダイヤ準拠、gen_tokaido_nozomi.py より継承) ===

NOZOMI_WD_DOWN = [
    '06:00', '06:21', '06:33', '06:50', '06:57',
    '07:00', '07:03', '07:09', '07:21', '07:30', '07:33', '07:42', '07:48', '07:51', '07:57',
    '08:00', '08:09', '08:21', '08:30', '08:33', '08:42', '08:51', '08:54', '08:57',
    '09:00', '09:09', '09:21', '09:30', '09:33', '09:42', '09:51',
    '10:00', '10:09', '10:21', '10:30', '10:42', '10:51',
    '11:00', '11:09', '11:21', '11:30', '11:42', '11:51',
    '12:00', '12:09', '12:21', '12:30', '12:42', '12:51',
    '13:00', '13:09', '13:21', '13:30', '13:42', '13:51',
    '14:00', '14:09', '14:21', '14:30', '14:42', '14:51',
    '15:00', '15:09', '15:21', '15:30', '15:42', '15:51',
    '16:00', '16:09', '16:21', '16:30', '16:42', '16:51',
    '17:00', '17:09', '17:21', '17:30', '17:42', '17:51',
    '18:00', '18:09', '18:21', '18:30', '18:42', '18:51',
    '19:00', '19:09', '19:21', '19:30', '19:42', '19:51',
    '20:00', '20:09', '20:21', '20:30', '20:42', '20:51',
    '21:00', '21:09', '21:23',
]
NOZOMI_WD_UP = [
    '06:00', '06:13', '06:23', '06:37', '06:50', '06:56',
    '07:00', '07:13', '07:23', '07:33', '07:43', '07:50', '07:53',
    '08:00', '08:13', '08:23', '08:30', '08:42', '08:50', '08:53',
    '09:00', '09:13', '09:23', '09:30', '09:42', '09:50',
    '10:00', '10:13', '10:23', '10:30', '10:42', '10:50',
    '11:00', '11:13', '11:23', '11:30', '11:42', '11:50',
    '12:00', '12:13', '12:23', '12:30', '12:42', '12:50',
    '13:00', '13:13', '13:23', '13:30', '13:42', '13:50',
    '14:00', '14:13', '14:23', '14:30', '14:42', '14:50',
    '15:00', '15:13', '15:23', '15:30', '15:42', '15:50',
    '16:00', '16:13', '16:23', '16:30', '16:42', '16:50',
    '17:00', '17:13', '17:23', '17:30', '17:42', '17:50',
    '18:00', '18:13', '18:23', '18:30', '18:42', '18:50',
    '19:00', '19:13', '19:23', '19:30', '19:42', '19:50',
    '20:00', '20:13', '20:23', '20:30', '20:42', '20:50',
    '21:00', '21:13', '21:24',
]
NOZOMI_HD_DOWN = [
    '06:00', '06:21', '06:33', '06:50',
    '07:00', '07:09', '07:21', '07:30', '07:42', '07:51',
    '08:00', '08:09', '08:21', '08:30', '08:42', '08:51',
    '09:00', '09:09', '09:21', '09:30', '09:42', '09:51',
    '10:00', '10:09', '10:21', '10:30', '10:42', '10:51',
    '11:00', '11:09', '11:21', '11:30', '11:42', '11:51',
    '12:00', '12:09', '12:21', '12:30', '12:42', '12:51',
    '13:00', '13:09', '13:21', '13:30', '13:42', '13:51',
    '14:00', '14:09', '14:21', '14:30', '14:42', '14:51',
    '15:00', '15:09', '15:21', '15:30', '15:42', '15:51',
    '16:00', '16:09', '16:21', '16:30', '16:42', '16:51',
    '17:00', '17:09', '17:21', '17:30', '17:42', '17:51',
    '18:00', '18:09', '18:21', '18:30', '18:42', '18:51',
    '19:00', '19:09', '19:21', '19:30', '19:42', '19:51',
    '20:00', '20:09', '20:21', '20:30', '20:42',
    '21:00', '21:23',
]
NOZOMI_HD_UP = [
    '06:00', '06:23', '06:37', '06:50',
    '07:00', '07:13', '07:23', '07:33', '07:43', '07:53',
    '08:00', '08:13', '08:23', '08:30', '08:42', '08:53',
    '09:00', '09:13', '09:23', '09:30', '09:42', '09:50',
    '10:00', '10:13', '10:23', '10:30', '10:42', '10:50',
    '11:00', '11:13', '11:23', '11:30', '11:42', '11:50',
    '12:00', '12:13', '12:23', '12:30', '12:42', '12:50',
    '13:00', '13:13', '13:23', '13:30', '13:42', '13:50',
    '14:00', '14:13', '14:23', '14:30', '14:42', '14:50',
    '15:00', '15:13', '15:23', '15:30', '15:42', '15:50',
    '16:00', '16:13', '16:23', '16:30', '16:42', '16:50',
    '17:00', '17:13', '17:23', '17:30', '17:42', '17:50',
    '18:00', '18:13', '18:23', '18:30', '18:42', '18:50',
    '19:00', '19:13', '19:23', '19:30', '19:42', '19:50',
    '20:00', '20:13', '20:23', '20:30', '20:42',
    '21:00', '21:24',
]


# === ひかり 発車時刻 (代表パターン. 毎時33分東京発が主、夜間は減便) ===

HIKARI_WD_DOWN = [
    '06:33', '07:33', '08:33', '09:33', '10:33',
    '11:33', '12:33', '13:33', '14:33', '15:33',
    '16:33', '17:33', '18:33', '19:33', '20:33',
]
HIKARI_WD_UP = [
    '06:30', '07:30', '08:30', '09:30', '10:30',
    '11:30', '12:30', '13:30', '14:30', '15:30',
    '16:30', '17:30', '18:30', '19:30', '20:30',
]
HIKARI_HD_DOWN = HIKARI_WD_DOWN
HIKARI_HD_UP   = HIKARI_WD_UP


# === こだま 発車時刻 (代表パターン. ~30分毎) ===

KODAMA_WD_DOWN = [
    '06:26', '06:56',
    '07:26', '07:56',
    '08:26', '08:56',
    '09:26', '09:56',
    '10:26', '10:56',
    '11:26', '11:56',
    '12:26', '12:56',
    '13:26', '13:56',
    '14:26', '14:56',
    '15:26', '15:56',
    '16:26', '16:56',
    '17:26', '17:56',
    '18:26', '18:56',
    '19:26', '19:56',
]
KODAMA_WD_UP = [
    '06:18', '06:48',
    '07:18', '07:48',
    '08:18', '08:48',
    '09:18', '09:48',
    '10:18', '10:48',
    '11:18', '11:48',
    '12:18', '12:48',
    '13:18', '13:48',
    '14:18', '14:48',
    '15:18', '15:48',
    '16:18', '16:48',
    '17:18', '17:48',
    '18:18', '18:48',
    '19:18', '19:48',
]
KODAMA_HD_DOWN = KODAMA_WD_DOWN
KODAMA_HD_UP   = KODAMA_WD_UP


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
    """Register trains in trains.csv list + write their schedule rows."""
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

    # 平日 (down: 奇数番、up: 偶数番)
    emit_trains_and_schedule('NOZOMI', NOZOMI_WD_DOWN, NOZOMI_STOPS_DOWN, 'down', 'のぞみ{n}号', trains, sched_wd, 1,   all_train_ids)
    emit_trains_and_schedule('NOZOMI', NOZOMI_WD_UP,   NOZOMI_STOPS_UP,   'up',   'のぞみ{n}号', trains, sched_wd, 2,   all_train_ids)
    emit_trains_and_schedule('HIKARI', HIKARI_WD_DOWN, HIKARI_STOPS_DOWN, 'down', 'ひかり{n}号', trains, sched_wd, 501, all_train_ids)
    emit_trains_and_schedule('HIKARI', HIKARI_WD_UP,   HIKARI_STOPS_UP,   'up',   'ひかり{n}号', trains, sched_wd, 502, all_train_ids)
    emit_trains_and_schedule('KODAMA', KODAMA_WD_DOWN, KODAMA_STOPS_DOWN, 'down', 'こだま{n}号', trains, sched_wd, 701, all_train_ids)
    emit_trains_and_schedule('KODAMA', KODAMA_WD_UP,   KODAMA_STOPS_UP,   'up',   'こだま{n}号', trains, sched_wd, 702, all_train_ids)

    # 土休日
    emit_trains_and_schedule('NOZOMI', NOZOMI_HD_DOWN, NOZOMI_STOPS_DOWN, 'down', 'のぞみ{n}号', trains, sched_hd, 1,   all_train_ids)
    emit_trains_and_schedule('NOZOMI', NOZOMI_HD_UP,   NOZOMI_STOPS_UP,   'up',   'のぞみ{n}号', trains, sched_hd, 2,   all_train_ids)
    emit_trains_and_schedule('HIKARI', HIKARI_HD_DOWN, HIKARI_STOPS_DOWN, 'down', 'ひかり{n}号', trains, sched_hd, 501, all_train_ids)
    emit_trains_and_schedule('HIKARI', HIKARI_HD_UP,   HIKARI_STOPS_UP,   'up',   'ひかり{n}号', trains, sched_hd, 502, all_train_ids)
    emit_trains_and_schedule('KODAMA', KODAMA_HD_DOWN, KODAMA_STOPS_DOWN, 'down', 'こだま{n}号', trains, sched_hd, 701, all_train_ids)
    emit_trains_and_schedule('KODAMA', KODAMA_HD_UP,   KODAMA_STOPS_UP,   'up',   'こだま{n}号', trains, sched_hd, 702, all_train_ids)

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

    n_n = sum(1 for t in trains if t[0].startswith('NOZOMI'))
    n_h = sum(1 for t in trains if t[0].startswith('HIKARI'))
    n_k = sum(1 for t in trains if t[0].startswith('KODAMA'))
    wd = len(set(row[0] for row in sched_wd))
    hd = len(set(row[0] for row in sched_hd))
    print(f'TOKAIDO_SHINKANSEN trains.csv: {len(trains)}本 (のぞみ {n_n} + ひかり {n_h} + こだま {n_k})')
    print(f'  平日運行: {wd}本 / 土休日運行: {hd}本')


if __name__ == '__main__':
    main()
