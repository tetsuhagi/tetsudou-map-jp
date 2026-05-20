#!/usr/bin/env python3
"""
Generate 山形つばさ timetable (東京 ⇔ 新庄).

JR東日本 山形新幹線「つばさ」。E3系2000番台 と E8系 (2024年導入) が
運用される **ミニ新幹線**。本マップで初の在来線改軌型新幹線。

経路の特徴:
  - 東京〜福島: 東北新幹線、E5系「やまびこ」と併結運転 (連結状態)
  - 福島駅で切り離し、つばさは奥羽線 (山形新幹線区間) へ転線
  - 福島〜新庄: 旧奥羽本線を狭軌→標準軌に改軌した在来線
  - MLIT N02 では「山形新幹線」という独立路線名はなく、
    福島以北は「奥羽線」(275 features) として登録

代表ダイヤ:
  - 60分間隔 (毎時 :00 発)
  - 東京発・新庄発とも 6:00〜21:00 → 16本/方向
  - 1日 32本
  - 所要 210分 (3時間30分)

実ダイヤとの差:
  - 実本数は1日約15往復/方向。本テンプレートでは16本/方向で簡略化。
  - 一部の便はかみのやま温泉/天童/さくらんぼ東根に停車するが、
    本テンプレートでは代表停車駅版で省略。

Stop intervals from 東京:
  TOKYO        +0:00 dep
  UENO         +0:05 arr / +0:06 dep
  OMIYA        +0:30 arr / +0:31 dep
  UTSUNOMIYA   +1:00 arr / +1:01 dep
  KORIYAMA     +1:30 arr / +1:31 dep
  FUKUSHIMA    +1:45 arr / +1:50 dep   (やまびこと切り離し、5分停車)
  YONEZAWA     +2:15 arr / +2:16 dep
  YAMAGATA     +2:40 arr / +2:41 dep
  SHINJO       +3:30 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'TSUBASA')

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


def gen_hourly(start_h, end_h, minute=0):
    return [f'{h:02d}:{minute:02d}' for h in range(start_h, end_h + 1)]


# 60分間隔
WEEKDAY_DOWN_DEPS = gen_hourly(6, 21, minute=0)    # 16本
WEEKDAY_UP_DEPS   = gen_hourly(6, 21, minute=0)    # 16本
HOLIDAY_DOWN_DEPS = WEEKDAY_DOWN_DEPS
HOLIDAY_UP_DEPS   = WEEKDAY_UP_DEPS


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

    emit('TSUBASA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'つばさ{n}', trains, sched_wd, 1)
    emit('TSUBASA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'つばさ{n}', trains, sched_wd, 2)
    emit_schedule_only('TSUBASA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('TSUBASA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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


if __name__ == '__main__':
    main()
