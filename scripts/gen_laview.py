#!/usr/bin/env python3
"""
Generate 西武ラビュー timetable (池袋 ⇔ 西武秩父 / 飯能) — 実ダイヤ準拠版.

西武鉄道001系「Laview」の特急ちちぶ・むさし系統の現行ダイヤを反映。
西武公式 PDF 時刻表 (2025年3月15日改正) を元に構築。

経由路線:
  - 西武鉄道 池袋線 (池袋〜飯能)
  - 西武鉄道 西武秩父線 (飯能〜西武秩父)

2系統 (ASHIZURI 方式の1 route_id 複数終点パターン):
  ■ ちちぶ (LAVIEW_*_C): 西武秩父まで全6駅停車、所要 77分
  ■ むさし (LAVIEW_*_M): 飯能止、4駅停車 (横瀬・西武秩父はカット)
                          所要 38分
  ※ ドーム (西武球場前行) は別路線のため本テンプレート対象外

代表ダイヤ (実ダイヤ準拠):

  平日 下り (池袋発):
    ちちぶ 18本: 06:50, 07:30, 08:30〜15:30 毎時:30,
                 16:30, 17:08, 17:30, 18:30, 19:30, 20:30, 21:30
    むさし 8本: 06:30, 16:00, 17:00, 18:00, 20:00, 21:00, 22:00, 23:30
    計 26本

  平日 上り:
    ちちぶ 16本 (西武秩父発): 06:08, 08:26, 09:24〜21:24 毎時:24, 22:47
    むさし 8本 (飯能発): 05:39, 05:57, 06:20, 06:34, 06:49, 16:34, 17:35, 19:37
    計 24本

  土休日: 平日とほぼ同等の本数として簡略化 (実態は朝早朝便が少なく、
         観光客向け日中便が増える微差あり)

注: 平日と休日で train_id を分離 (LAVIEW_W_C/M, LAVIEW_H_C/M)、
   時刻も別ダイヤとして管理。

Stop intervals from 池袋 (ちちぶ):
  IKEBUKURO       +0:00 dep
  TOKOROZAWA      +0:21 arr / +0:22 dep
  IRUMASHI        +0:39 arr / +0:40 dep
  HANNO           +0:47 arr / +0:49 dep   (スイッチバックで2分停車)
  YOKOZE          +1:13 arr / +1:14 dep
  SEIBU_CHICHIBU  +1:17 arr

Stop intervals from 池袋 (むさし、飯能止):
  IKEBUKURO       +0:00 dep
  TOKOROZAWA      +0:21 arr / +0:22 dep
  IRUMASHI        +0:32 arr / +0:33 dep
  HANNO           +0:38 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'LAVIEW')

# === ちちぶ (西武秩父まで全6駅) ===
STOPS_C_DOWN = [
    ('IKEBUKURO',      None, 0),
    ('TOKOROZAWA',     21,   22),
    ('IRUMASHI',       39,   40),
    ('HANNO',          47,   49),
    ('YOKOZE',         73,   74),
    ('SEIBU_CHICHIBU', 77,   None),
]
STOPS_C_UP = [
    ('SEIBU_CHICHIBU', None, 0),
    ('YOKOZE',         3,    4),
    ('HANNO',          28,   30),
    ('IRUMASHI',       37,   38),
    ('TOKOROZAWA',     55,   56),
    ('IKEBUKURO',      77,   None),
]

# === むさし (飯能止、4駅) ===
STOPS_M_DOWN = [
    ('IKEBUKURO',  None, 0),
    ('TOKOROZAWA', 21,   22),
    ('IRUMASHI',   32,   33),
    ('HANNO',      38,   None),
]
STOPS_M_UP = [
    ('HANNO',      None, 0),
    ('IRUMASHI',   5,    6),
    ('TOKOROZAWA', 16,   17),
    ('IKEBUKURO',  38,   None),
]

# === 平日 ダイヤ (PDF 西武公式 2025-03-15改正準拠) ===

# ちちぶ 平日下り 18本
WEEKDAY_C_DOWN = [
    '06:50', '07:30', '08:30', '09:30', '10:30',
    '11:30', '12:30', '13:30', '14:30', '15:30',
    '16:30', '17:08', '17:30', '18:30', '19:30',
    '20:30', '21:30', '22:30',
]
# ちちぶ 平日上り 16本 (西武秩父発)
WEEKDAY_C_UP = [
    '06:08', '08:26', '09:24', '10:24', '11:24',
    '12:24', '13:24', '14:24', '15:24', '16:24',
    '17:24', '18:24', '19:24', '20:24', '21:24',
    '22:47',
]

# むさし 平日下り 8本 (飯能止)
WEEKDAY_M_DOWN = [
    '06:30', '16:00', '17:00', '18:00',
    '20:00', '21:00', '22:00', '23:30',
]
# むさし 平日上り 8本 (飯能発)
WEEKDAY_M_UP = [
    '05:39', '05:57', '06:20', '06:34', '06:49',
    '16:34', '17:35', '19:37',
]

# === 土休日 (実態は微差、本テンプレートでは平日と同等で簡略化) ===
HOLIDAY_C_DOWN = WEEKDAY_C_DOWN
HOLIDAY_C_UP   = WEEKDAY_C_UP
HOLIDAY_M_DOWN = WEEKDAY_M_DOWN
HOLIDAY_M_UP   = WEEKDAY_M_UP


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

    # 平日 ちちぶ / むさし
    emit('LAVIEW_W_C', WEEKDAY_C_DOWN, STOPS_C_DOWN, 'down', 'ちちぶ{n}号', trains, sched_wd, 1)
    emit('LAVIEW_W_C', WEEKDAY_C_UP,   STOPS_C_UP,   'up',   'ちちぶ{n}号', trains, sched_wd, 2)
    emit('LAVIEW_W_M', WEEKDAY_M_DOWN, STOPS_M_DOWN, 'down', 'むさし{n}号', trains, sched_wd, 1)
    emit('LAVIEW_W_M', WEEKDAY_M_UP,   STOPS_M_UP,   'up',   'むさし{n}号', trains, sched_wd, 2)

    # 土休日 ちちぶ / むさし
    emit('LAVIEW_H_C', HOLIDAY_C_DOWN, STOPS_C_DOWN, 'down', 'ちちぶ{n}号', trains, sched_hd, 1)
    emit('LAVIEW_H_C', HOLIDAY_C_UP,   STOPS_C_UP,   'up',   'ちちぶ{n}号', trains, sched_hd, 2)
    emit('LAVIEW_H_M', HOLIDAY_M_DOWN, STOPS_M_DOWN, 'down', 'むさし{n}号', trains, sched_hd, 1)
    emit('LAVIEW_H_M', HOLIDAY_M_UP,   STOPS_M_UP,   'up',   'むさし{n}号', trains, sched_hd, 2)

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

    print(f'trains.csv: {len(trains)}本')
    print(f'  平日: ちちぶ {len(WEEKDAY_C_DOWN)+len(WEEKDAY_C_UP)}本 + むさし {len(WEEKDAY_M_DOWN)+len(WEEKDAY_M_UP)}本 = {len(WEEKDAY_C_DOWN)+len(WEEKDAY_C_UP)+len(WEEKDAY_M_DOWN)+len(WEEKDAY_M_UP)}本')
    print(f'  休日: ちちぶ {len(HOLIDAY_C_DOWN)+len(HOLIDAY_C_UP)}本 + むさし {len(HOLIDAY_M_DOWN)+len(HOLIDAY_M_UP)}本 = {len(HOLIDAY_C_DOWN)+len(HOLIDAY_C_UP)+len(HOLIDAY_M_DOWN)+len(HOLIDAY_M_UP)}本')


if __name__ == '__main__':
    main()
