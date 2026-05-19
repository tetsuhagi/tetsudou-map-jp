#!/usr/bin/env python3
"""
Generate ミュースカイ timetable (名鉄岐阜 ⇔ 中部国際空港).

代表ダイヤ（2026年5月時点の概略を簡略化）:
- ほぼ30分間隔で1日約30本/方向
- 名鉄岐阜 → 中部国際空港 約65分
- 始発(下り): 名鉄岐阜 7:30 発
- 終発(下り): 名鉄岐阜 21:30 発
- 始発(上り): 中部国際空港 8:30 発
- 終発(上り): 中部国際空港 22:30 発

実ダイヤでは:
- 名鉄一宮を通過するミュースカイあり (一部は停車)
- 神宮前を通過するミュースカイあり (一部は停車)
本テンプレートでは "全停車版" の代表ダイヤとして簡略化。
将来的に通過パターンを反映する場合は STOPS_DOWN / STOPS_UP を分岐させる。

Stop intervals from 名鉄岐阜 (代表値):
  MEITETSU_GIFU         +0:00 dep
  MEITETSU_ICHINOMIYA   +0:09 arr / +0:10 dep
  MEITETSU_NAGOYA       +0:23 arr / +0:24 dep
  KANAYAMA              +0:28 arr / +0:29 dep
  JINGUMAE              +0:32 arr / +0:33 dep
  CENTRAIR              +1:05 arr
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', 'MU_SKY')

# (station_id, arrival_offset_min, departure_offset_min)
STOPS_DOWN = [
    ('MEITETSU_GIFU',        None, 0),
    ('MEITETSU_ICHINOMIYA',  9,    10),
    ('MEITETSU_NAGOYA',      23,   24),
    ('KANAYAMA',             28,   29),
    ('JINGUMAE',             32,   33),
    ('CENTRAIR',             65,   None),
]
STOPS_UP = [
    ('CENTRAIR',             None, 0),
    ('JINGUMAE',             32,   33),
    ('KANAYAMA',             36,   37),
    ('MEITETSU_NAGOYA',      41,   42),
    ('MEITETSU_ICHINOMIYA',  55,   56),
    ('MEITETSU_GIFU',        65,   None),
]


def gen_half_hourly(start_h, start_m, end_h, end_m):
    """Generate departures at :00 and :30 from start to end (inclusive)."""
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


# Half-hourly base. Holiday is same — Centrair patronage is similar 7 days a week.
WEEKDAY_DOWN_DEPS = gen_half_hourly(7, 30, 21, 30)
WEEKDAY_UP_DEPS   = gen_half_hourly(8, 30, 22, 30)
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

    emit('MU_SKY', WEEKDAY_DOWN_DEPS, STOPS_DOWN, 'down', 'ミュースカイ{n}', trains, sched_wd, 1)
    emit('MU_SKY', WEEKDAY_UP_DEPS,   STOPS_UP,   'up',   'ミュースカイ{n}', trains, sched_wd, 2)
    emit_schedule_only('MU_SKY', HOLIDAY_DOWN_DEPS, STOPS_DOWN, sched_hd, 1)
    emit_schedule_only('MU_SKY', HOLIDAY_UP_DEPS,   STOPS_UP,   sched_hd, 2)

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
    print(f'holiday: 下 {len(HOLIDAY_DOWN_DEPS)} + 上 {len(HOLIDAY_UP_DEPS)} = {len(HOLIDAY_DOWN_DEPS) + len(HOLIDAY_UP_DEPS)}本')


if __name__ == '__main__':
    main()
