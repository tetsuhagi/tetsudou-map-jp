#!/usr/bin/env python3
"""
Generate 山形つばさ timetable (東京 ⇔ 新庄 / 東京 ⇔ 山形) — 実ダイヤ準拠版.

JR東日本 山形新幹線「つばさ」。E3系2000番台 と E8系 (2024年導入) が
運用される **ミニ新幹線**。本マップで初の在来線改軌型新幹線。

経路の特徴:
  - 東京〜福島: 東北新幹線、E5系「やまびこ」と併結運転 (連結状態)
  - 福島駅で切り離し、つばさは奥羽線 (山形新幹線区間) へ転線
  - 福島〜新庄: 旧奥羽本線を狭軌→標準軌に改軌した在来線

1 route_id 複数終点パターン:
  ■ つばさ新庄行 (TSUBASA_*): 9駅停車 (東京-...-新庄)、所要 210分
    主流: 1日15往復/方向
  ■ つばさ山形止 (TSUBASA_Y_*): 8駅停車 (東京-...-山形)、所要 161分
    1日1-2往復/方向 (限定運用)

参考: JR東日本 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

Stop intervals from 東京:
  TOKYO        +0:00 dep
  UENO         +0:05 arr / +0:06 dep
  OMIYA        +0:30 arr / +0:31 dep
  UTSUNOMIYA   +1:00 arr / +1:01 dep
  KORIYAMA     +1:30 arr / +1:31 dep
  FUKUSHIMA    +1:45 arr / +1:50 dep   (やまびこと切り離し、5分停車)
  YONEZAWA     +2:15 arr / +2:16 dep
  YAMAGATA     +2:40 arr / +2:41 dep   (山形止: ここで終端)
  SHINJO       +3:30 arr               (新庄行)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TSUBASA')


# === 停車駅パターン ===

STOPS_DOWN = [
    ('TOKYO',      None, 0),
    ('UENO',       5,    6),
    ('OMIYA',      30,   31),
    ('UTSUNOMIYA', 60,   61),
    ('KORIYAMA',   90,   91),
    ('FUKUSHIMA',  105,  110),
    ('YONEZAWA',   135,  136),
    ('YAMAGATA',   160,  161),
    ('SHINJO',     210,  None),
]
STOPS_UP = [
    ('SHINJO',     None, 0),
    ('YAMAGATA',   49,   50),
    ('YONEZAWA',   74,   75),
    ('FUKUSHIMA',  100,  105),
    ('KORIYAMA',   119,  120),
    ('UTSUNOMIYA', 149,  150),
    ('OMIYA',      179,  180),
    ('UENO',       204,  205),
    ('TOKYO',      210,  None),
]

# 山形止 (8駅、新庄区間カット)
STOPS_Y_DOWN = [
    ('TOKYO',      None, 0),
    ('UENO',       5,    6),
    ('OMIYA',      30,   31),
    ('UTSUNOMIYA', 60,   61),
    ('KORIYAMA',   90,   91),
    ('FUKUSHIMA',  105,  110),
    ('YONEZAWA',   135,  136),
    ('YAMAGATA',   160,  None),
]
STOPS_Y_UP = [
    ('YAMAGATA',   None, 0),
    ('YONEZAWA',   25,   26),
    ('FUKUSHIMA',  51,   56),
    ('KORIYAMA',   70,   71),
    ('UTSUNOMIYA', 100,  101),
    ('OMIYA',      130,  131),
    ('UENO',       155,  156),
    ('TOKYO',      161,  None),
]


# === 発車時刻 (実2024ダイヤ準拠) ===

# 新庄行 (主流) - 平日15本/方向
TSUBASA_WD_DOWN = [
    '06:12', '06:48',
    '07:08', '08:12',
    '09:00', '10:00',
    '11:00', '12:00',
    '13:00', '14:00',
    '15:00', '16:00',
    '17:08', '18:00',
    '19:48',
]
TSUBASA_WD_UP = [
    '06:01', '07:00',
    '08:14', '09:11',
    '10:14', '11:14',
    '12:14', '13:14',
    '14:14', '15:14',
    '16:14', '17:14',
    '18:14', '19:14',
    '20:14',
]

# 山形止 - 平日2本/方向 (深夜便など)
TSUBASA_Y_WD_DOWN = [
    '21:12',
    '22:00',
]
TSUBASA_Y_WD_UP = [
    '06:48',
    '21:18',
]

# 土休日: 平日とほぼ同じ
TSUBASA_HD_DOWN   = TSUBASA_WD_DOWN
TSUBASA_HD_UP     = TSUBASA_WD_UP
TSUBASA_Y_HD_DOWN = TSUBASA_Y_WD_DOWN
TSUBASA_Y_HD_UP   = TSUBASA_Y_WD_UP


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

    # 新庄行
    emit('TSUBASA', TSUBASA_WD_DOWN, STOPS_DOWN, 'down', 'つばさ{n}号', trains, sched_wd, 1)
    emit('TSUBASA', TSUBASA_WD_UP,   STOPS_UP,   'up',   'つばさ{n}号', trains, sched_wd, 2)
    emit_schedule_only('TSUBASA', TSUBASA_HD_DOWN, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TSUBASA', TSUBASA_HD_UP,   STOPS_UP,   sched_hd, 2)

    # 山形止
    emit('TSUBASA_Y', TSUBASA_Y_WD_DOWN, STOPS_Y_DOWN, 'down', 'つばさ{n}号', trains, sched_wd, 1)
    emit('TSUBASA_Y', TSUBASA_Y_WD_UP,   STOPS_Y_UP,   'up',   'つばさ{n}号', trains, sched_wd, 2)
    emit_schedule_only('TSUBASA_Y', TSUBASA_Y_HD_DOWN, STOPS_Y_DOWN, sched_hd, 1)
    emit_schedule_only('TSUBASA_Y', TSUBASA_Y_HD_UP,   STOPS_Y_UP,   sched_hd, 2)

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

    n_s = sum(1 for t in trains if t[0].startswith('TSUBASA_') and t[0].split('_')[1].isdigit())
    n_y = sum(1 for t in trains if t[0].startswith('TSUBASA_Y_'))
    print(f'TSUBASA trains.csv: {len(trains)}本')
    print(f'  つばさ新庄行 {n_s} + つばさ山形止 {n_y}')


if __name__ == '__main__':
    main()
