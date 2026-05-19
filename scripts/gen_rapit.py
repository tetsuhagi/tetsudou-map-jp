#!/usr/bin/env python3
"""
Generate ラピート timetable (難波 ⇔ 関西空港).

南海ラピートは α (速達) と β (停車型) の2パターンを30分交互で運行。
2026年5月時点の概略を簡略化:
  - α: 4駅停車 (難波 - 新今宮 - 天下茶屋 - 関西空港) 約34分
  - β: 7駅停車 (難波 - 新今宮 - 天下茶屋 - 堺 - 岸和田 - 泉佐野 - 関西空港) 約40分

ダイヤパターン:
  - 平日/休日とも 30分間隔 で α と β を交互運行
  - α は 毎時 :00 発、β は 毎時 :30 発 と仮定
  - 始発(下り): 難波 6:00 (α), 6:30 (β)
  - 終発(下り): 難波 22:00 (α), 22:30 (β)
  - 始発(上り): 関空 7:00 (α), 7:30 (β)
  - 終発(上り): 関空 23:00 (α), 23:30 (β)
  - 合計: 各方向 34本/日 (α17 + β17)、全日 68本

実ダイヤとは細部が異なる (早朝/深夜の本数、α/β偏在など) が、シミュレーション
表示用の代表ダイヤとして簡略化している。

Stop intervals from 難波:
  α (4駅):
    NAMBA            +0:00 dep
    SHIN_IMAMIYA     +0:03 arr / +0:04 dep
    TENGACHAYA       +0:06 arr / +0:07 dep
    KANSAI_AIRPORT   +0:34 arr
  β (7駅):
    NAMBA            +0:00 dep
    SHIN_IMAMIYA     +0:03 arr / +0:04 dep
    TENGACHAYA       +0:06 arr / +0:07 dep
    SAKAI            +0:14 arr / +0:15 dep
    KISHIWADA        +0:24 arr / +0:25 dep
    IZUMISANO        +0:33 arr / +0:34 dep
    KANSAI_AIRPORT   +0:40 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'RAPIT')

# (station_id, arrival_offset_min, departure_offset_min)
ALPHA_DOWN = [
    ('NAMBA',          None, 0),
    ('SHIN_IMAMIYA',   3,    4),
    ('TENGACHAYA',     6,    7),
    ('KANSAI_AIRPORT', 34,   None),
]
ALPHA_UP = [
    ('KANSAI_AIRPORT', None, 0),
    ('TENGACHAYA',     27,   28),
    ('SHIN_IMAMIYA',   30,   31),
    ('NAMBA',          34,   None),
]
BETA_DOWN = [
    ('NAMBA',          None, 0),
    ('SHIN_IMAMIYA',   3,    4),
    ('TENGACHAYA',     6,    7),
    ('SAKAI',          14,   15),
    ('KISHIWADA',      24,   25),
    ('IZUMISANO',      33,   34),
    ('KANSAI_AIRPORT', 40,   None),
]
BETA_UP = [
    ('KANSAI_AIRPORT', None, 0),
    ('IZUMISANO',      6,    7),
    ('KISHIWADA',      15,   16),
    ('SAKAI',          25,   26),
    ('TENGACHAYA',     33,   34),
    ('SHIN_IMAMIYA',   36,   37),
    ('NAMBA',          40,   None),
]


def gen_hourly(start_h, end_h, minute=0):
    """:MM 発を毎時 start_h..end_h で生成"""
    return [f'{h:02d}:{minute:02d}' for h in range(start_h, end_h + 1)]


# 平日/休日同一の代表ダイヤ
WEEKDAY_ALPHA_DOWN = gen_hourly(6, 22, minute=0)    # 17本
WEEKDAY_BETA_DOWN  = gen_hourly(6, 22, minute=30)   # 17本
WEEKDAY_ALPHA_UP   = gen_hourly(7, 23, minute=0)    # 17本
WEEKDAY_BETA_UP    = gen_hourly(7, 23, minute=30)   # 17本


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
    """trains[] と schedule[] に追記。train_id は {prefix}_{N} で N は 2ずつ進める"""
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

    # α 系 (高速便) → train_id prefix = RAPIT_A
    emit('RAPIT_A', WEEKDAY_ALPHA_DOWN, ALPHA_DOWN, 'down', 'ラピートα{n}', trains, sched_wd, 1)
    emit('RAPIT_A', WEEKDAY_ALPHA_UP,   ALPHA_UP,   'up',   'ラピートα{n}', trains, sched_wd, 2)
    emit_schedule_only('RAPIT_A', WEEKDAY_ALPHA_DOWN, ALPHA_DOWN, sched_hd, 1)
    emit_schedule_only('RAPIT_A', WEEKDAY_ALPHA_UP,   ALPHA_UP,   sched_hd, 2)

    # β 系 (停車型) → train_id prefix = RAPIT_B
    emit('RAPIT_B', WEEKDAY_BETA_DOWN, BETA_DOWN, 'down', 'ラピートβ{n}', trains, sched_wd, 1)
    emit('RAPIT_B', WEEKDAY_BETA_UP,   BETA_UP,   'up',   'ラピートβ{n}', trains, sched_wd, 2)
    emit_schedule_only('RAPIT_B', WEEKDAY_BETA_DOWN, BETA_DOWN, sched_hd, 1)
    emit_schedule_only('RAPIT_B', WEEKDAY_BETA_UP,   BETA_UP,   sched_hd, 2)

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

    alpha = sum(1 for tid, _, _ in trains if tid.startswith('RAPIT_A'))
    beta  = sum(1 for tid, _, _ in trains if tid.startswith('RAPIT_B'))
    down = sum(1 for _, _, d in trains if d == 'down')
    up = sum(1 for _, _, d in trains if d == 'up')
    print(f'trains.csv: {len(trains)}本 (α {alpha} + β {beta}, 下り {down} / 上り {up})')
    print(f'weekday: α下 {len(WEEKDAY_ALPHA_DOWN)} + α上 {len(WEEKDAY_ALPHA_UP)} + β下 {len(WEEKDAY_BETA_DOWN)} + β上 {len(WEEKDAY_BETA_UP)} = {len(trains)}本')


if __name__ == '__main__':
    main()
