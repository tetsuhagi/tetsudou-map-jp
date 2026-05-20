#!/usr/bin/env python3
"""
Generate ミュースカイ新鵜沼系統 timetable (新鵜沼 ⇔ 中部国際空港).

ミュースカイの犬山線経由系統。本系統は **平日朝・夕の通勤時間帯のみ**
運行され、日中の運行はほぼなし (空港への通勤・出張需要に対応)。

経由路線:
  - 名古屋鉄道 犬山線 (新鵜沼〜枇杷島分岐点)
  - 名古屋鉄道 名古屋本線 (枇杷島分岐点〜名鉄名古屋〜神宮前)
  - 名古屋鉄道 常滑線 (神宮前〜常滑)
  - 名古屋鉄道 空港線 (常滑〜中部国際空港)

代表ダイヤ (平日、実ダイヤ準拠):
  下り (新鵜沼発):
    06:11, 06:38, 07:12, 07:46, 08:13, 08:44, 09:46 (朝7本)
    17:44, 18:44, 19:44, 20:44 (夕4本)
    計 11本
  上り (空港発):
    07:03, 07:26, 08:33 (朝3本)
    17:36, 18:36, 19:37, 20:37, 21:37 (夕5本)
    計 8本

  合計 19本/日

実態の特徴:
  - 日中 10時〜17時は運行なし (通勤特化型)
  - 平日のみ運行が中心、休日は本数減 (本テンプレートでは平日と同等で簡略化)

Stop intervals from 新鵜沼:
  SHIN_UNUMA          +0:00 dep
  INUYAMA             +0:03 arr / +0:04 dep
  MEITETSU_NAGOYA     +0:33 arr / +0:34 dep
  KANAYAMA            +0:38 arr / +0:39 dep
  JINGUMAE            +0:42 arr / +0:43 dep
  CENTRAIR            +1:03 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'MU_SKY_INUYAMA')

STOPS_DOWN = [
    ('SHIN_UNUMA',       None, 0),
    ('INUYAMA',          3,    4),
    ('MEITETSU_NAGOYA',  33,   34),
    ('KANAYAMA',         38,   39),
    ('JINGUMAE',         42,   43),
    ('CENTRAIR',         63,   None),
]
STOPS_UP = [
    ('CENTRAIR',         None, 0),
    ('JINGUMAE',         30,   31),
    ('KANAYAMA',         34,   35),
    ('MEITETSU_NAGOYA',  39,   40),
    ('INUYAMA',          59,   60),
    ('SHIN_UNUMA',       63,   None),
]

# 平日 (実ダイヤ準拠)
WEEKDAY_DOWN_DEPS = [
    '06:11', '06:38', '07:12', '07:46', '08:13', '08:44', '09:46',
    '17:44', '18:44', '19:44', '20:44',
]
WEEKDAY_UP_DEPS = [
    '07:03', '07:26', '08:33',
    '17:36', '18:36', '19:37', '20:37', '21:37',
]

# 休日は実態では本数減だが、本テンプレートでは平日と同等で簡略化
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

    emit('MU_SKY_INUYAMA', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ミュースカイ{n}', trains, sched_wd, 1)
    emit('MU_SKY_INUYAMA', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ミュースカイ{n}', trains, sched_wd, 2)
    emit_schedule_only('MU_SKY_INUYAMA', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('MU_SKY_INUYAMA', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
