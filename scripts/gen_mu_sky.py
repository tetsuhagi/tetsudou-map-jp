#!/usr/bin/env python3
"""
Generate ミュースカイ timetable (名鉄岐阜・名鉄名古屋 ⇔ 中部国際空港).

名鉄2000系「ミュースカイ」の現行ダイヤを正確に反映。実態調査
(名鉄公式/NAVITIME 平日時刻表) によると、ミュースカイは大半が
**名鉄名古屋発着** で、名鉄岐阜発着は1日数本のみという運行形態。

経由路線:
  - 名古屋鉄道 名古屋本線 (名鉄岐阜〜名鉄名古屋〜神宮前)
  - 名古屋鉄道 常滑線 (神宮前〜常滑)
  - 名古屋鉄道 空港線 (常滑〜中部国際空港)

2系統:
  ■ 名鉄岐阜発着系 (MU_SKY_G、6駅停車): 朝・夜の数本のみ
      所要63分 (名鉄岐阜⇔中部国際空港)
  ■ 名鉄名古屋発着系 (MU_SKY_N、4駅停車): 主流系統
      所要39分 (名鉄名古屋⇔中部国際空港)

設計のキモ「1 route_id 複数始終点」:
  ASOBOY と同じパターン。routes.csv の stations 列は全駅含むが、
  train ごとに停車駅 (stop_order) を変えて分岐表現。

代表ダイヤ (平日、実ダイヤ準拠):
  下り (空港行)
    岐阜発: 5:55 (始発), 9:21, 19:21, 20:21 → 4本
    名古屋発: 6:02, 6:29, 6:52, 7:19, 7:49, ..., 21:19 → 32本
    計 36本

  上り (空港発)
    岐阜行: 8:00, 9:07, 18:06, 19:06, 20:07, 21:07 → 6本
    名古屋行: 9:37, 10:07, 10:37, ..., 16:37, 17:06, 22:07 → 17本
    計 23本

  合計 59本/日

  ※ 新鵜沼発着系 (犬山線経由) は本route_id では扱わず、将来
    MU_SKY_INUYAMA として別途実装予定 (約8本/方向)

Stop intervals 岐阜便 (下り):
  MEITETSU_GIFU         +0:00 dep
  MEITETSU_ICHINOMIYA   +0:09 arr / +0:10 dep
  MEITETSU_NAGOYA       +0:23 arr / +0:24 dep
  KANAYAMA              +0:28 arr / +0:29 dep
  JINGUMAE              +0:32 arr / +0:33 dep
  CENTRAIR              +1:03 arr

Stop intervals 名古屋便 (下り):
  MEITETSU_NAGOYA       +0:00 dep
  KANAYAMA              +0:04 arr / +0:05 dep
  JINGUMAE              +0:08 arr / +0:09 dep
  CENTRAIR              +0:39 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'MU_SKY')

# === 岐阜発着系 (6駅停車、63分) ===
STOPS_G_DOWN = [
    ('MEITETSU_GIFU',        None, 0),
    ('MEITETSU_ICHINOMIYA',  9,    10),
    ('MEITETSU_NAGOYA',      23,   24),
    ('KANAYAMA',             28,   29),
    ('JINGUMAE',             32,   33),
    ('CENTRAIR',             63,   None),
]
STOPS_G_UP = [
    ('CENTRAIR',             None, 0),
    ('JINGUMAE',             30,   31),
    ('KANAYAMA',             34,   35),
    ('MEITETSU_NAGOYA',      39,   40),
    ('MEITETSU_ICHINOMIYA',  53,   54),
    ('MEITETSU_GIFU',        63,   None),
]

# === 名古屋発着系 (4駅停車、39分) ===
STOPS_N_DOWN = [
    ('MEITETSU_NAGOYA', None, 0),
    ('KANAYAMA',        4,    5),
    ('JINGUMAE',        8,    9),
    ('CENTRAIR',        39,   None),
]
STOPS_N_UP = [
    ('CENTRAIR',        None, 0),
    ('JINGUMAE',        30,   31),
    ('KANAYAMA',        34,   35),
    ('MEITETSU_NAGOYA', 39,   None),
]

# === 平日ダイヤ (実ダイヤ準拠) ===

# 岐阜発着: 下り4本、上り6本
WEEKDAY_G_DOWN = ['05:55', '09:21', '19:21', '20:21']
WEEKDAY_G_UP   = ['08:00', '09:07', '18:06', '19:06', '20:07', '21:07']

# 名古屋発着: 下り32本、上り17本
WEEKDAY_N_DOWN = [
    '06:02', '06:29', '06:52',
    '07:19', '07:49',
    '08:19', '08:49',
    '09:19', '09:49',
    '10:19', '10:49',
    '11:19', '11:49',
    '12:19', '12:49',
    '13:19', '13:49',
    '14:19', '14:49',
    '15:19', '15:49',
    '16:19', '16:49',
    '17:19', '17:49',
    '18:19', '18:49',
    '19:19', '19:49',
    '20:19', '20:49',
    '21:19',
]
WEEKDAY_N_UP = [
    '09:37',
    '10:07', '10:37',
    '11:07', '11:37',
    '12:07', '12:37',
    '13:07', '13:37',
    '14:07', '14:37',
    '15:07', '15:37',
    '16:07', '16:37',
    '17:06',
    '22:07',
]

# 休日も平日とほぼ同等として簡略化
HOLIDAY_G_DOWN = WEEKDAY_G_DOWN
HOLIDAY_G_UP   = WEEKDAY_G_UP
HOLIDAY_N_DOWN = WEEKDAY_N_DOWN
HOLIDAY_N_UP   = WEEKDAY_N_UP


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

    # 岐阜発着系 (G)
    emit('MU_SKY_G', WEEKDAY_G_DOWN, STOPS_G_DOWN, 'down', 'ミュースカイ{n}', trains, sched_wd, 1)
    emit('MU_SKY_G', WEEKDAY_G_UP,   STOPS_G_UP,   'up',   'ミュースカイ{n}', trains, sched_wd, 2)
    emit_schedule_only('MU_SKY_G', HOLIDAY_G_DOWN, STOPS_G_DOWN, sched_hd, 1)
    emit_schedule_only('MU_SKY_G', HOLIDAY_G_UP,   STOPS_G_UP,   sched_hd, 2)

    # 名古屋発着系 (N)
    emit('MU_SKY_N', WEEKDAY_N_DOWN, STOPS_N_DOWN, 'down', 'ミュースカイ{n}', trains, sched_wd, 1)
    emit('MU_SKY_N', WEEKDAY_N_UP,   STOPS_N_UP,   'up',   'ミュースカイ{n}', trains, sched_wd, 2)
    emit_schedule_only('MU_SKY_N', HOLIDAY_N_DOWN, STOPS_N_DOWN, sched_hd, 1)
    emit_schedule_only('MU_SKY_N', HOLIDAY_N_UP,   STOPS_N_UP,   sched_hd, 2)

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

    gifu = sum(1 for tid, _, _ in trains if tid.startswith('MU_SKY_G'))
    nagoya = sum(1 for tid, _, _ in trains if tid.startswith('MU_SKY_N'))
    print(f'trains.csv: {len(trains)}本 (岐阜発着 {gifu}, 名古屋発着 {nagoya})')


if __name__ == '__main__':
    main()
