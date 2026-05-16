#!/usr/bin/env python3
"""
Generate realistic-ish weekday schedules for all Shinkansen lines.

Approach: per-line config defines stop pattern (with relative timing) and
hourly intervals. Peak hours get shorter intervals; off-peak / late night
get longer intervals. Approximates real-world frequency without scraping.

Run:
  python3 scripts/build_shinkansen_schedules.py

Overwrites data/timetables/<route_id>/trains.csv and weekday.csv.
"""
import os
import csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_intervals(*ranges):
    """Build hour -> interval dict. ranges = list of (hour_range, interval).
    e.g., make_intervals((range(7,10), 10), (range(10,17), 15))
    """
    d = {}
    for hours, interval in ranges:
        for h in hours:
            d[h] = interval
    return d


LINES = {
    'TOKAIDO_SHINKANSEN': {
        'id_prefix': 'NOZOMI',
        'name_prefix': 'のぞみ',
        'down_stops': [
            ('TOKYO', None, 0),
            ('SHINAGAWA', 7, 8),
            ('SHIN_YOKOHAMA', 18, 19),
            ('NAGOYA', 94, 96),
            ('KYOTO', 131, 133),
            ('SHIN_OSAKA', 143, None),
        ],
        'up_stops': [
            ('SHIN_OSAKA', None, 0),
            ('KYOTO', 13, 14),
            ('NAGOYA', 50, 52),
            ('SHIN_YOKOHAMA', 129, 130),
            ('SHINAGAWA', 141, 142),
            ('TOKYO', 150, None),
        ],
        # Real のぞみ: ~6/hour normal, up to 10-12/hour peak
        'intervals': make_intervals(
            (range(6, 7), 20),
            (range(7, 10), 10),    # morning peak
            (range(10, 17), 15),   # normal day
            (range(17, 20), 10),   # evening peak
            (range(20, 22), 20),
        ),
    },
    'SANYO_SHINKANSEN': {
        'id_prefix': 'SANYO',
        'name_prefix': '山陽',
        'down_stops': [
            ('SHIN_OSAKA', None, 0),
            ('SHIN_KOBE', 13, 14),
            ('OKAYAMA', 46, 47),
            ('HIROSHIMA', 84, 85),
            ('KOKURA', 129, 130),
            ('HAKATA', 145, None),
        ],
        'up_stops': [
            ('HAKATA', None, 0),
            ('KOKURA', 15, 16),
            ('HIROSHIMA', 59, 60),
            ('OKAYAMA', 97, 98),
            ('SHIN_KOBE', 130, 131),
            ('SHIN_OSAKA', 145, None),
        ],
        # Real 山陽のぞみ: ~3-4/hour
        'intervals': make_intervals(
            (range(6, 7), 30),
            (range(7, 10), 15),
            (range(10, 17), 20),
            (range(17, 20), 15),
            (range(20, 22), 30),
        ),
    },
    'KYUSHU_SHINKANSEN': {
        'id_prefix': 'KYUSHU',
        'name_prefix': '九州',
        'down_stops': [
            ('HAKATA', None, 0),
            ('KURUME', 17, 18),
            ('KUMAMOTO', 48, 49),
            ('KAGOSHIMA_CHUO', 80, None),
        ],
        'up_stops': [
            ('KAGOSHIMA_CHUO', None, 0),
            ('KUMAMOTO', 31, 32),
            ('KURUME', 62, 63),
            ('HAKATA', 80, None),
        ],
        # Real みずほ・さくら速達: 1-2/hour
        'intervals': make_intervals(
            (range(6, 7), 60),
            (range(7, 10), 30),
            (range(10, 17), 30),
            (range(17, 20), 30),
            (range(20, 22), 60),
        ),
    },
    'NISHI_KYUSHU_SHINKANSEN': {
        'id_prefix': 'NK',
        'name_prefix': '西九州',
        'down_stops': [
            ('TAKEO_ONSEN', None, 0),
            ('URESHINO_ONSEN', 6, 7),
            ('SHIN_OMURA', 15, 16),
            ('ISAHAYA', 22, 23),
            ('NAGASAKI', 30, None),
        ],
        'up_stops': [
            ('NAGASAKI', None, 0),
            ('ISAHAYA', 7, 8),
            ('SHIN_OMURA', 14, 15),
            ('URESHINO_ONSEN', 23, 24),
            ('TAKEO_ONSEN', 30, None),
        ],
        # Real かもめ: ~2/hour at peak, hourly off-peak
        'intervals': make_intervals(
            (range(6, 7), 60),
            (range(7, 10), 30),
            (range(10, 17), 45),
            (range(17, 20), 30),
            (range(20, 22), 60),
        ),
    },
    'TOHOKU_SHINKANSEN': {
        'id_prefix': 'TOHOKU',
        'name_prefix': '東北',
        'down_stops': [
            ('TOKYO', None, 0),
            ('UENO', 5, 6),
            ('OMIYA', 25, 26),
            ('SENDAI', 95, 96),
            ('MORIOKA', 135, 136),
            ('SHIN_AOMORI', 185, None),
        ],
        'up_stops': [
            ('SHIN_AOMORI', None, 0),
            ('MORIOKA', 50, 51),
            ('SENDAI', 90, 91),
            ('OMIYA', 160, 161),
            ('UENO', 179, 180),
            ('TOKYO', 185, None),
        ],
        # Real はやぶさ(新青森行): ~1-2/hour
        # Last down departure must arrive within day: 185min = 3h5m
        'intervals': make_intervals(
            (range(6, 7), 60),
            (range(7, 10), 30),
            (range(10, 17), 45),
            (range(17, 19), 30),
            (range(19, 21), 60),  # latest dep at 20:30 → arrive 23:35
        ),
    },
    'HOKKAIDO_SHINKANSEN': {
        'id_prefix': 'HOKKAIDO',
        'name_prefix': '北海道',
        'down_stops': [
            ('SHIN_AOMORI', None, 0),
            ('OKUTSUGARU_IMABETSU', 30, 31),
            ('KIKONAI', 56, 57),
            ('SHIN_HAKODATE_HOKUTO', 75, None),
        ],
        'up_stops': [
            ('SHIN_HAKODATE_HOKUTO', None, 0),
            ('KIKONAI', 18, 19),
            ('OKUTSUGARU_IMABETSU', 44, 45),
            ('SHIN_AOMORI', 75, None),
        ],
        # Real はやぶさ(新函館北斗): ~10/day each way → roughly hourly
        'intervals': make_intervals(
            (range(6, 22), 60),
        ),
    },
    'JOETSU_SHINKANSEN': {
        'id_prefix': 'JOETSU',
        'name_prefix': '上越',
        'down_stops': [
            ('OMIYA', None, 0),
            ('TAKASAKI', 25, 26),
            ('ECHIGO_YUZAWA', 55, 56),
            ('NAGAOKA', 82, 83),
            ('NIIGATA', 95, None),
        ],
        'up_stops': [
            ('NIIGATA', None, 0),
            ('NAGAOKA', 13, 14),
            ('ECHIGO_YUZAWA', 40, 41),
            ('TAKASAKI', 70, 71),
            ('OMIYA', 95, None),
        ],
        # Real とき: ~1-2/hour
        'intervals': make_intervals(
            (range(6, 7), 60),
            (range(7, 10), 30),
            (range(10, 17), 60),
            (range(17, 20), 30),
            (range(20, 22), 60),
        ),
    },
    'HOKURIKU_SHINKANSEN': {
        'id_prefix': 'HOKURIKU',
        'name_prefix': '北陸',
        'down_stops': [
            ('TAKASAKI', None, 0),
            ('NAGANO', 40, 41),
            ('TOYAMA', 95, 96),
            ('KANAZAWA', 116, 117),
            ('FUKUI', 147, 148),
            ('TSURUGA', 168, None),
        ],
        'up_stops': [
            ('TSURUGA', None, 0),
            ('FUKUI', 20, 21),
            ('KANAZAWA', 51, 52),
            ('TOYAMA', 72, 73),
            ('NAGANO', 127, 128),
            ('TAKASAKI', 168, None),
        ],
        # Real かがやき(敦賀): ~14/day each way
        'intervals': make_intervals(
            (range(6, 7), 60),
            (range(7, 10), 60),
            (range(10, 17), 90),
            (range(17, 20), 60),
            (range(20, 21), 60),
        ),
    },
}


def hhmm(m):
    if m is None:
        return ''
    return f"{m // 60:02d}:{m % 60:02d}"


def generate_departure_times(intervals):
    """Return sorted list of departure base-minutes from 00:00."""
    times = []
    for hour in sorted(intervals):
        interval = intervals[hour]
        for m in range(0, 60, interval):
            times.append(hour * 60 + m)
    return sorted(set(times))


def build_route(route_id, cfg):
    """Generate (trains_rows, schedule_rows) for one route."""
    dep_times = generate_departure_times(cfg['intervals'])

    trains_rows = []
    schedule_rows = []

    # Down: odd IDs (1, 3, 5, ...)
    n = 1
    for base in dep_times:
        # Skip if last arrival would exceed 23:59
        last_arr = base + cfg['down_stops'][-1][1]
        if last_arr is None or last_arr > 23 * 60 + 59:
            continue
        tid = f"{cfg['id_prefix']}_{n}"
        trains_rows.append({'train_id': tid, 'name': f"{cfg['name_prefix']}{n}", 'direction': 'down'})
        for i, (sid, arr_off, dep_off) in enumerate(cfg['down_stops'], 1):
            arr = base + arr_off if arr_off is not None else None
            dep = base + dep_off if dep_off is not None else None
            schedule_rows.append({
                'train_id': tid, 'stop_order': i,
                'station_id': sid, 'arrival': hhmm(arr), 'departure': hhmm(dep),
            })
        n += 2

    # Up: even IDs (2, 4, 6, ...)
    n = 2
    for base in dep_times:
        last_arr = base + cfg['up_stops'][-1][1]
        if last_arr is None or last_arr > 23 * 60 + 59:
            continue
        tid = f"{cfg['id_prefix']}_{n}"
        trains_rows.append({'train_id': tid, 'name': f"{cfg['name_prefix']}{n}", 'direction': 'up'})
        for i, (sid, arr_off, dep_off) in enumerate(cfg['up_stops'], 1):
            arr = base + arr_off if arr_off is not None else None
            dep = base + dep_off if dep_off is not None else None
            schedule_rows.append({
                'train_id': tid, 'stop_order': i,
                'station_id': sid, 'arrival': hhmm(arr), 'departure': hhmm(dep),
            })
        n += 2

    return trains_rows, schedule_rows


def write_route(route_id, trains_rows, schedule_rows):
    route_dir = os.path.join(ROOT, 'data', 'timetables', route_id)
    os.makedirs(route_dir, exist_ok=True)
    with open(os.path.join(route_dir, 'trains.csv'), 'w', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['train_id', 'name', 'direction'])
        w.writeheader()
        w.writerows(trains_rows)
    with open(os.path.join(route_dir, 'weekday.csv'), 'w', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['train_id', 'stop_order', 'station_id', 'arrival', 'departure'])
        w.writeheader()
        w.writerows(schedule_rows)


def main():
    total_trains = 0
    for route_id, cfg in LINES.items():
        trains_rows, schedule_rows = build_route(route_id, cfg)
        write_route(route_id, trains_rows, schedule_rows)
        down = sum(1 for t in trains_rows if t['direction'] == 'down')
        up = sum(1 for t in trains_rows if t['direction'] == 'up')
        total_trains += len(trains_rows)
        print(f"  {route_id:>25}: {down:>3} down + {up:>3} up = {len(trains_rows):>3} trains")
    print(f"\nTotal Shinkansen trains: {total_trains}")


if __name__ == '__main__':
    main()
