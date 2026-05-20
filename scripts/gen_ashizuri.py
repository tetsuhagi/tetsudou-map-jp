#!/usr/bin/env python3
"""
Generate あしずり timetable (高知 ⇔ 中村 / 高知 ⇔ 宿毛).

JR四国 特急「あしずり」。2700系/N2000系で運用。土佐くろしお鉄道線
への直通運転が特徴で、中村行が主流、宿毛行は1日2本程度のレア運行。

経路:
  - JR四国 土讃線 (高知〜窪川)
  - 土佐くろしお鉄道 中村線 (窪川〜中村)
  - 土佐くろしお鉄道 宿毛線 (中村〜宿毛)

設計のキモ「1 route_id で複数終点」:
  routes.csv stations 列は宿毛まで全駅含む (KOCHI|SUSAKI|KUBOKAWA|
  NAKAMURA|SUKUMO) が、各 train の停車駅は train.csv で個別定義。
  - 中村行 train: stop_order [1〜4] で NAKAMURA まで
  - 宿毛行 train: stop_order [1〜5] で SUKUMO まで
  ジオメトリは宿毛まで生成、中村行は途中で「降りる」形になる。

代表ダイヤ:
  - 中村行: 1日 14本 (各方向7本) — 主流系統
  - 宿毛行: 1日 4本 (各方向2本)  — レア系統
  - 合計 18本/日

実ダイヤ:
  - 中村行は実際は約8往復/方向
  - 宿毛行は実際は1日1〜2本/方向程度
  - 簡略化のため本テンプレートでは7往復+2往復にして見栄えを確保

所要時間:
  - 高知→中村: 100分 (1時間40分)
  - 高知→宿毛: 130分 (2時間10分)

Stop intervals from 高知 (中村行):
  KOCHI       +0:00 dep
  SUSAKI      +0:35 arr / +0:36 dep
  KUBOKAWA    +1:10 arr / +1:11 dep
  NAKAMURA    +1:40 arr

Stop intervals from 高知 (宿毛行):
  KOCHI       +0:00 dep
  SUSAKI      +0:35 arr / +0:36 dep
  KUBOKAWA    +1:10 arr / +1:11 dep
  NAKAMURA    +1:40 arr / +1:42 dep   (運転士交代で2分停車)
  SUKUMO      +2:10 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ASHIZURI')

# 中村行 (主流系統)
STOPS_DOWN_NAKAMURA = [
    ('KOCHI',     None, 0),
    ('SUSAKI',    35,   36),
    ('KUBOKAWA',  70,   71),
    ('NAKAMURA',  100,  None),
]
STOPS_UP_NAKAMURA = [
    ('NAKAMURA',  None, 0),
    ('KUBOKAWA',  29,   30),
    ('SUSAKI',    64,   65),
    ('KOCHI',     100,  None),
]

# 宿毛行 (レア系統)
STOPS_DOWN_SUKUMO = [
    ('KOCHI',     None, 0),
    ('SUSAKI',    35,   36),
    ('KUBOKAWA',  70,   71),
    ('NAKAMURA',  100,  102),
    ('SUKUMO',    130,  None),
]
STOPS_UP_SUKUMO = [
    ('SUKUMO',    None, 0),
    ('NAKAMURA',  28,   30),
    ('KUBOKAWA',  59,   60),
    ('SUSAKI',    94,   95),
    ('KOCHI',     130,  None),
]

# 中村行: 60分間隔のうち7本ピックアップ (主要時間帯)
WEEKDAY_NAKAMURA_DOWN = ['06:00', '07:00', '08:00', '10:00', '12:00', '14:00', '18:00']
WEEKDAY_NAKAMURA_UP   = ['07:30', '08:30', '09:30', '11:30', '13:30', '15:30', '19:30']

# 宿毛行: 1日2本ずつ
WEEKDAY_SUKUMO_DOWN = ['09:00', '16:00']
WEEKDAY_SUKUMO_UP   = ['08:30', '17:30']

# 平日/休日同一
HOLIDAY_NAKAMURA_DOWN = WEEKDAY_NAKAMURA_DOWN
HOLIDAY_NAKAMURA_UP   = WEEKDAY_NAKAMURA_UP
HOLIDAY_SUKUMO_DOWN   = WEEKDAY_SUKUMO_DOWN
HOLIDAY_SUKUMO_UP     = WEEKDAY_SUKUMO_UP


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

    # 中村行 (主流) — ID は ASHIZURI_N_
    emit('ASHIZURI_N', WEEKDAY_NAKAMURA_DOWN, STOPS_DOWN_NAKAMURA, 'down', 'あしずり{n}号', trains, sched_wd, 1)
    emit('ASHIZURI_N', WEEKDAY_NAKAMURA_UP,   STOPS_UP_NAKAMURA,   'up',   'あしずり{n}号', trains, sched_wd, 2)
    emit_schedule_only('ASHIZURI_N', HOLIDAY_NAKAMURA_DOWN, STOPS_DOWN_NAKAMURA, sched_hd, 1)
    emit_schedule_only('ASHIZURI_N', HOLIDAY_NAKAMURA_UP,   STOPS_UP_NAKAMURA,   sched_hd, 2)

    # 宿毛行 (レア) — ID は ASHIZURI_S_
    emit('ASHIZURI_S', WEEKDAY_SUKUMO_DOWN, STOPS_DOWN_SUKUMO, 'down', 'あしずり{n}号 (宿毛行)', trains, sched_wd, 1)
    emit('ASHIZURI_S', WEEKDAY_SUKUMO_UP,   STOPS_UP_SUKUMO,   'up',   'あしずり{n}号 (宿毛発)', trains, sched_wd, 2)
    emit_schedule_only('ASHIZURI_S', HOLIDAY_SUKUMO_DOWN, STOPS_DOWN_SUKUMO, sched_hd, 1)
    emit_schedule_only('ASHIZURI_S', HOLIDAY_SUKUMO_UP,   STOPS_UP_SUKUMO,   sched_hd, 2)

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

    nakamura = sum(1 for tid, _, _ in trains if tid.startswith('ASHIZURI_N'))
    sukumo   = sum(1 for tid, _, _ in trains if tid.startswith('ASHIZURI_S'))
    print(f'trains.csv: {len(trains)}本 (中村行 {nakamura}, 宿毛行 {sukumo})')


if __name__ == '__main__':
    main()
