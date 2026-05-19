#!/usr/bin/env python3
"""
Generate 小田急ロマンスカー timetable (はこね系統: 新宿 ⇔ 箱根湯本).

小田急ロマンスカーは多系統あるが、ここでは代表系統「はこね」のみを
収録する。他系統（ふじさん／えのしま／メトロはこね 等）は将来別の
route_id で追加する設計：
  - ROMANCECAR_FUJISAN: 新宿 ⇔ 御殿場 (JR御殿場線直通、MSE使用)
  - ROMANCECAR_ENOSHIMA: 新宿 ⇔ 片瀬江ノ島 (江ノ島線)

2026年5月時点で運用中の主な車両:
  - GSE (70000形): 現フラッグシップ、赤＋白
  - MSE (60000形): 千代田線・御殿場線直通可、青
  - EXE / EXEα (30000形): リニューアル車、シャインオレンジ
  - VSE (50000形) は 2023年12月で運用終了

代表ダイヤ (はこね):
  - 30分間隔 (毎時 :00 / :30)
  - 始発: 新宿 7:00 / 箱根湯本 8:30
  - 終発: 新宿 21:30 / 箱根湯本 23:00
  - 所要時間 85分 (はこね代表値、スーパーはこねは75分ほど)
  - 1日 60本 (各方向 30本)

実ダイヤでは:
  - 時間帯により本数変動 (朝・夕は多め、昼間は1時間に1本程度の時間帯あり)
  - 停車パターンも多様 (スーパーはこね / はこね / ホームウェイ など)
本テンプレートでは全便を「はこね」として停車駅・所要時間を統一。

Stop intervals from 新宿:
  SHINJUKU       +0:00 dep
  MACHIDA        +0:35 arr / +0:36 dep
  EBINA          +0:44 arr / +0:45 dep
  HONATSUGI      +0:49 arr / +0:50 dep
  HADANO         +1:02 arr / +1:03 dep
  ODAWARA        +1:15 arr / +1:17 dep   (箱根登山線への切替で2分停車)
  HAKONEYUMOTO   +1:25 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'ROMANCECAR')

STOPS_DOWN = [
    ('SHINJUKU',     None, 0),
    ('MACHIDA',      35,   36),
    ('EBINA',        44,   45),
    ('HONATSUGI',    49,   50),
    ('HADANO',       62,   63),
    ('ODAWARA',      75,   77),
    ('HAKONEYUMOTO', 85,   None),
]
STOPS_UP = [
    ('HAKONEYUMOTO', None, 0),
    ('ODAWARA',      8,    10),
    ('HADANO',       22,   23),
    ('HONATSUGI',    35,   36),
    ('EBINA',        40,   41),
    ('MACHIDA',      49,   50),
    ('SHINJUKU',     85,   None),
]


def gen_half_hourly(start_h, start_m, end_h, end_m):
    times = []
    h, m = start_h, start_m
    while (h, m) <= (end_h, end_m):
        times.append(f'{h:02d}:{m:02d}')
        if m == 0:
            m = 30
        else:
            m = 0
            h += 1
    return times


WEEKDAY_DOWN_DEPS = gen_half_hourly(7, 0,  21, 30)   # 30本
WEEKDAY_UP_DEPS   = gen_half_hourly(8, 30, 23, 0)    # 30本
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

    emit('ROMANCECAR', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'はこね{n}', trains, sched_wd, 1)
    emit('ROMANCECAR', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'はこね{n}', trains, sched_wd, 2)
    emit_schedule_only('ROMANCECAR', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('ROMANCECAR', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
    print(f'weekday: 下 {len(WEEKDAY_DOWN_DEPS)} + 上 {len(WEEKDAY_UP_DEPS)} = {len(WEEKDAY_DOWN_DEPS) + len(WEEKDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
