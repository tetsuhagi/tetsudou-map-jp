#!/usr/bin/env python3
"""
Generate サンライズ瀬戸・サンライズ出雲 timetable — 実ダイヤ準拠版.

JR西日本・JR東海・JR四国「サンライズ瀬戸」(285系3000番台)、
JR西日本・JR東海・JR東日本「サンライズ出雲」(285系0番台)。
2024年現在、日本で唯一の定期運用寝台特急 (1日1往復ずつ).

経路:
  ■ サンライズ瀬戸 (SUNRISE_SETO): 東京⇔高松
  ■ サンライズ出雲 (SUNRISE_IZUMO): 東京⇔出雲市

特徴:
  - 東京-岡山 区間は併結運転 (両列車を連結して走行)、岡山で分割
  - 下り (東京発): 大阪・三ノ宮は通過扱い (運転停車のみ、客扱いなし)
  - 上り (高松/出雲市発): 大阪・三ノ宮で客扱い停車
  - 時刻は HH:MM 表記で 24:00 以降の表記も使用 (29:25 = 翌朝 5:25)

参考: JR西日本 公式時刻表 / NAVITIME / 駅探 2025年3月15日改正

注: 平日・土休日同一ダイヤ (寝台特急は両日とも運行).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# サンライズ瀬戸 下り (東京 21:26 → 高松 翌 7:27)
# 下り: 大阪・三ノ宮は通過 (客扱いなし)
# ============================================================
SETO_DOWN = [
    ('TOKYO',     None, 0),       # 21:26 発
    ('YOKOHAMA',  24,   25),
    ('ATAMI',     83,   84),
    ('NUMAZU',    99,   100),
    ('FUJI',      113,  114),
    ('SHIZUOKA',  140,  141),
    ('HAMAMATSU', 191,  192),
    ('HIMEJI',    479,  480),
    ('OKAYAMA',   541,  545),     # 翌 06:27 着 / 06:31 発 (分割後 高松行)
    ('KOJIMA',    565,  566),
    ('SAKAIDE',   583,  584),
    ('TAKAMATSU', 601,  None),    # 翌 07:27 着
]


# ============================================================
# サンライズ瀬戸 上り (高松 21:26 → 東京 翌 7:08)
# 上り: 大阪・三ノ宮で客扱い停車
# ============================================================
SETO_UP = [
    ('TAKAMATSU', None, 0),       # 21:26 発
    ('SAKAIDE',   11,   12),
    ('KOJIMA',    29,   30),
    ('OKAYAMA',   57,   68),      # 22:23 着 / 22:34 発 (出雲と併結)
    ('HIMEJI',    127,  128),
    ('SANNOMIYA', 165,  166),
    ('OSAKA',     187,  188),
    ('HAMAMATSU', 432,  433),
    ('SHIZUOKA',  490,  491),
    ('FUJI',      514,  515),
    ('NUMAZU',    528,  529),
    ('ATAMI',     546,  547),
    ('YOKOHAMA',  565,  566),
    ('TOKYO',     582,  None),
]


# ============================================================
# サンライズ出雲 下り (東京 21:26 → 出雲市 翌 9:58)
# 東京-岡山は瀬戸と共通だが、岡山で分割 → 出雲市行は 6:34発
# ============================================================
IZUMO_DOWN = [
    ('TOKYO',             None, 0),       # 21:26 発
    ('YOKOHAMA',          24,   25),
    ('ATAMI',             83,   84),
    ('NUMAZU',            99,   100),
    ('FUJI',              113,  114),
    ('SHIZUOKA',          140,  141),
    ('HAMAMATSU',         191,  192),
    ('HIMEJI',            479,  480),
    ('OKAYAMA',           541,  548),     # 翌 06:27 着 / 06:34 発
    ('KURASHIKI',         557,  558),
    ('BITCHU_TAKAHASHI',  578,  579),
    ('NIIMI',             616,  618),
    ('YONAGO',            699,  700),
    ('YASUGI',            709,  710),
    ('MATSUE',            725,  726),
    ('TAMATSUKURI_ONSEN', 735,  736),
    ('IZUMOSHI',          752,  None),    # 翌 09:58 着
]


# ============================================================
# サンライズ出雲 上り (出雲市 18:57 → 東京 翌 7:08)
# 岡山で瀬戸と併結 (OKAYAMA 22:31 着 / 22:34 発)
# ============================================================
IZUMO_UP = [
    ('IZUMOSHI',          None, 0),     # 18:57 発
    ('TAMATSUKURI_ONSEN', 9,    10),
    ('MATSUE',            20,   21),
    ('YASUGI',            28,   29),
    ('YONAGO',            43,   44),
    ('NIIMI',             123,  125),
    ('BITCHU_TAKAHASHI',  155,  156),
    ('KURASHIKI',         179,  180),
    ('OKAYAMA',           214,  217),   # 22:31 着 / 22:34 発 (瀬戸と併結)
    ('HIMEJI',            276,  277),
    ('SANNOMIYA',         314,  315),
    ('OSAKA',             336,  337),
    ('HAMAMATSU',         581,  582),
    ('SHIZUOKA',          639,  640),
    ('FUJI',              663,  664),
    ('NUMAZU',            677,  678),
    ('ATAMI',             695,  696),
    ('YOKOHAMA',          714,  715),
    ('TOKYO',             731,  None),
]


# 発車基準時刻 (始発駅)
SETO_DOWN_BASE  = '21:26'
SETO_UP_BASE    = '21:26'
IZUMO_DOWN_BASE = '21:26'
IZUMO_UP_BASE   = '18:57'


def parse_hhmm(s):
    h, m = s.split(':')
    return int(h) * 60 + int(m)


def fmt_hhmm(mins):
    """Format minutes-from-00:00 as HH:MM. Allows hours >= 24 (e.g. 29:25)."""
    h = mins // 60
    m = mins % 60
    return f'{h:02d}:{m:02d}'


def build_stops(base_dep_min, stops_def):
    rows = []
    for sid, arr_off, dep_off in stops_def:
        arr = fmt_hhmm(base_dep_min + arr_off) if arr_off is not None else ''
        dep = fmt_hhmm(base_dep_min + dep_off) if dep_off is not None else ''
        rows.append((sid, arr, dep))
    return rows


def write_route(route_id, trains_data):
    out_dir = os.path.join(ROOT, 'data', 'timetables', route_id)
    os.makedirs(out_dir, exist_ok=True)

    trains = []
    schedule = []
    for tid, name, direction, base_dep, stops_def in trains_data:
        trains.append((tid, name, direction))
        for order, (sid, arr, dp) in enumerate(build_stops(parse_hhmm(base_dep), stops_def), 1):
            schedule.append((tid, order, sid, arr, dp))

    with open(os.path.join(out_dir, 'trains.csv'), 'w', encoding='utf-8') as f:
        f.write('train_id,name,direction\n')
        for tid, name, direction in trains:
            f.write(f'{tid},{name},{direction}\n')

    # 平日・土休日同一ダイヤ
    for fname in ('weekday.csv', 'holiday.csv'):
        with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
            f.write('train_id,stop_order,station_id,arrival,departure\n')
            for row in schedule:
                f.write(','.join(map(str, row)) + '\n')

    print(f'{route_id}: {len(trains)}本')


def main():
    write_route('SUNRISE_SETO', [
        ('SUNRISE_SETO_D1', 'サンライズ瀬戸 下り', 'down', SETO_DOWN_BASE,  SETO_DOWN),
        ('SUNRISE_SETO_U1', 'サンライズ瀬戸 上り', 'up',   SETO_UP_BASE,    SETO_UP),
    ])
    write_route('SUNRISE_IZUMO', [
        ('SUNRISE_IZUMO_D1', 'サンライズ出雲 下り', 'down', IZUMO_DOWN_BASE, IZUMO_DOWN),
        ('SUNRISE_IZUMO_U1', 'サンライズ出雲 上り', 'up',   IZUMO_UP_BASE,   IZUMO_UP),
    ])


if __name__ == '__main__':
    main()
