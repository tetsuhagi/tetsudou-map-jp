#!/usr/bin/env python3
"""
Generate リニア中央新幹線（品川 ⇔ 名古屋）の「想定」ダイヤ.

⚠ 未開業路線。実在のダイヤではなく、公表情報をもとにした独自の想定。
   マップ上は layer=future（デフォルト非表示・メニューから表示）として扱う。

前提（出典）:
  - 毎時片道5本 = 速達4本 + 各駅停車1本
    （日経xTECH 2009-08-25「リニア新幹線運行ダイヤ」: JR東海資料と記者の試算）
  - 所要: 速達 40分（品川〜名古屋ノンストップ）/ 各停 約70分
  - 参考: 東京〜大阪 全線開業後は最大 片道8本/時（速達7+各停1, JR東海 FAQ）→ 今回は採用しない

パターン（上下とも同じ）:
  速達 毎時 :00 :15 :30 :45 発 / 各停 毎時 :08 発
  運行時間 6時台〜22時台の発車（片道 速達68本 + 各停17本 = 85本/日）

各停の組み立て:
  駅間の走行時間 = 速達の平均速度で走った時間 + 加減速ぶん（ACCEL_PENALTY_MIN）。
  各駅の発車は「次の駅に着くまでに後続の速達に追いつかれない」時刻まで待つ。
  → 追い越しは必ず各停が駅に停車している間に起きる（駅間で抜かれると
    地図上で不自然に見えるため）。最後に全列車でこの条件を検証する。

駅間距離は data/geometry/LINEAR_CHUO.json（build_geometry_waypoints.py の出力）から取る。
平日・土休日は同一ダイヤ。weekday.csv と同じ内容の holiday.csv も必ず出力する
（holiday.csv を置かないと、本番で存在しないファイルへの応答が 404 にならない場合に
 data.js のフォールバックが効かず、土休日に列車が消えるため）。
"""
import csv
import json
import math
import os
from math import cos, radians, sqrt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTE_ID = 'LINEAR_CHUO'
OUT_DIR = os.path.join(ROOT, 'data', 'timetables', ROUTE_ID)

STATIONS = ['SHINAGAWA', 'LINEAR_KANAGAWA', 'LINEAR_YAMANASHI',
            'LINEAR_NAGANO', 'LINEAR_GIFU', 'NAGOYA']
EXPRESS_MIN = 40
EXPRESS_OFFSETS = [0, 15, 30, 45]
LOCAL_OFFSET = 8
FIRST_HOUR, LAST_HOUR = 6, 22
ACCEL_PENALTY_MIN = 2.5   # 各停の駅間ごとの加減速ロス
MIN_DWELL = 2           # 各停の最短停車


def station_km():
    with open(os.path.join(ROOT, 'data', 'geometry', f'{ROUTE_ID}.json'), encoding='utf-8') as f:
        geo = json.load(f)
    pl, pos = geo['polyline'], geo['station_positions']
    cum = [0.0]
    for a, b in zip(pl, pl[1:]):
        k = cos(radians((a[0] + b[0]) / 2))
        cum.append(cum[-1] + sqrt(((b[0] - a[0]) * 111) ** 2 + ((b[1] - a[1]) * 111 * k) ** 2))
    return [cum[pos[s]] for s in STATIONS]


def hhmm(m):
    return f'{int(m) // 60:02d}:{int(m) % 60:02d}'


def build_direction(km):
    """km: 起点からの距離（進行方向順）。各列車を [(station_idx, arr, dep)] で返す。"""
    total = km[-1]
    frac = [k / total for k in km]
    n = len(km)

    expresses = []
    for h in range(FIRST_HOUR, LAST_HOUR + 1):
        for off in EXPRESS_OFFSETS:
            dep = h * 60 + off
            expresses.append(dep)
    # 速達が各駅を通過する時刻（小数分）
    def pass_time(dep, i):
        return dep + EXPRESS_MIN * frac[i]

    locals_ = []
    for h in range(FIRST_HOUR, LAST_HOUR + 1):
        stops = []
        dep = h * 60 + LOCAL_OFFSET
        arr = None
        for i in range(n - 1):
            run = math.ceil(EXPRESS_MIN * (frac[i + 1] - frac[i]) + ACCEL_PENALTY_MIN)
            if i > 0:
                dep = arr + MIN_DWELL
            # 後続の速達にこの駅間で追いつかれるなら、その速達が通過するまで待つ
            while True:
                catch = [e for e in expresses
                         if pass_time(e, i) > dep - 1 and pass_time(e, i + 1) < dep + run + 1]
                if not catch:
                    break
                dep = math.ceil(max(pass_time(e, i) for e in catch) + 1)
            stops.append((i, arr, dep))
            arr = dep + run
        stops.append((n - 1, arr, None))
        locals_.append(stops)

    express_stops = [[(0, None, e), (n - 1, e + EXPRESS_MIN, None)] for e in expresses]
    return express_stops, locals_, pass_time


def verify(express_deps, locals_, pass_time):
    """各停が駅間で速達に抜かれていないことを検証する。"""
    for stops in locals_:
        for (i, _, dep), (j, arr, _) in zip(stops, stops[1:]):
            for e in express_deps:
                ts, te = pass_time(e, i), pass_time(e, j)
                assert not (ts > dep and te < arr), \
                    f'駅間追い越し: 各停 {hhmm(stops[0][2])}発 区間{i}-{j} を 速達 {hhmm(e)}発 が追い越し'


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    km_down = station_km()
    km_up = [km_down[-1] - k for k in reversed(km_down)]

    trains, rows = [], []
    summary = {}
    for direction, km, order in (('down', km_down, STATIONS), ('up', km_up, list(reversed(STATIONS)))):
        express, locals_, pass_time = build_direction(km)
        verify([s[0][2] for s in express], locals_, pass_time)
        dir_label = '名古屋行き' if direction == 'down' else '品川行き'
        for kind, group in (('EXP', express), ('LOC', locals_)):
            for stops in group:
                start = stops[0][2]
                tid = f'LINEAR_{kind}_{direction[0].upper()}_{hhmm(start).replace(":", "")}'
                kind_label = '速達' if kind == 'EXP' else '各駅停車'
                trains.append((tid, f'リニア{kind_label}（想定）{hhmm(start)}発 {dir_label}', direction))
                for n, (i, arr, dep) in enumerate(stops, 1):
                    rows.append((tid, n, order[i],
                                 hhmm(arr) if arr is not None else '',
                                 hhmm(dep) if dep is not None else ''))
        loc_times = sorted({s[-1][1] - s[0][2] for s in locals_})
        summary[direction] = (len(express), len(locals_), loc_times,
                              [(order[i], hhmm(a) if a else '', hhmm(d) if d else '') for i, a, d in locals_[0]])

    with open(os.path.join(OUT_DIR, 'trains.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['train_id', 'name', 'direction'])
        w.writerows(trains)
    for day in ('weekday', 'holiday'):
        with open(os.path.join(OUT_DIR, f'{day}.csv'), 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['train_id', 'stop_order', 'station_id', 'arrival', 'departure'])
            w.writerows(rows)

    print('station km (down):', ' / '.join(f'{s}={k:.1f}' for s, k in zip(STATIONS, km_down)))
    for d, (ne, nl, lt, first) in summary.items():
        print(f'[{d}] 速達 {ne}本 / 各停 {nl}本 / 各停所要 {lt}分')
        print('   各停 初列車:', '  '.join(f'{s}({a}-{dp})' for s, a, dp in first))
    print(f'wrote {len(trains)} trains, {len(rows)} stop rows → {OUT_DIR}')


if __name__ == '__main__':
    main()
