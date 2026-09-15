#!/usr/bin/env python3
"""
Build route geometry from hand-placed waypoints (for lines absent from MLIT N02).

build_geometry.py は国土数値情報 N02 の線形をたどるが、未開業路線（リニア中央
新幹線など）は N02 に収録されていない。本スクリプトは scripts/waypoints/<route_id>.json
に並べた経由点（駅 + 公表施設の位置）を centripetal Catmull-Rom で補間し、
build_geometry.py と同じ形式の data/geometry/<route_id>.json を出力する。

  - 駅の経由点は {"station_id": ...} で書き、座標は data/stations.csv から引く
  - 補間後も駅の点はそのまま残るので station_positions は正確に対応する
  - centripetal (alpha=0.5) は経由点の間隔が不揃いでもループや行き過ぎが出にくい

Usage:
  python3 scripts/build_geometry_waypoints.py <route_id>

Example:
  python3 scripts/build_geometry_waypoints.py LINEAR_CHUO
"""
import csv
import json
import os
import sys
from math import cos, radians, sqrt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP_KM = 0.5    # 補間後の点の間隔の目安
ALPHA = 0.5      # centripetal Catmull-Rom


def load_stations():
    with open(os.path.join(ROOT, 'data', 'stations.csv'), encoding='utf-8') as f:
        return {r['station_id']: (float(r['lat']), float(r['lon'])) for r in csv.DictReader(f)}


def dist_km(a, b):
    k = cos(radians((a[0] + b[0]) / 2))
    dy = (b[0] - a[0]) * 111.0
    dx = (b[1] - a[1]) * 111.0 * k
    return sqrt(dx * dx + dy * dy)


def catmull_rom(p0, p1, p2, p3, n):
    """p1→p2 の区間を n 分割した点列（p1 を含み p2 を含まない）を返す。"""
    def tj(ti, pi, pj):
        return ti + max(dist_km(pi, pj), 1e-6) ** ALPHA
    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    out = []
    for i in range(n):
        t = t1 + (t2 - t1) * i / n
        def lerp(pa, pb, ta, tb):
            if tb == ta:
                return pa
            wa, wb = (tb - t) / (tb - ta), (t - ta) / (tb - ta)
            return (pa[0] * wa + pb[0] * wb, pa[1] * wa + pb[1] * wb)
        a1 = lerp(p0, p1, t0, t1); a2 = lerp(p1, p2, t1, t2); a3 = lerp(p2, p3, t2, t3)
        b1 = lerp(a1, a2, t0, t2); b2 = lerp(a2, a3, t1, t3)
        out.append(lerp(b1, b2, t1, t2))
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    route_id = sys.argv[1]
    src = os.path.join(ROOT, 'scripts', 'waypoints', f'{route_id}.json')
    with open(src, encoding='utf-8') as f:
        spec = json.load(f)
    stations = load_stations()

    pts, station_at = [], {}
    for p in spec['points']:
        if 'station_id' in p:
            sid = p['station_id']
            if sid not in stations:
                sys.exit(f'ERROR: {sid} が data/stations.csv にありません')
            station_at[len(pts)] = sid
            pts.append(stations[sid])
        else:
            pts.append((p['lat'], p['lon']))

    polyline, station_positions = [], {}
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        n = max(1, round(dist_km(pts[i], pts[i + 1]) / STEP_KM))
        if i in station_at:
            station_positions[station_at[i]] = len(polyline)
        polyline.extend(catmull_rom(p0, pts[i], pts[i + 1], p3, n))
    last = len(pts) - 1
    if last in station_at:
        station_positions[station_at[last]] = len(polyline)
    polyline.append(pts[last])

    polyline = [[round(lat, 6), round(lon, 6)] for lat, lon in polyline]
    out = os.path.join(ROOT, 'data', 'geometry', f'{route_id}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'polyline': polyline, 'station_positions': station_positions}, f,
                  ensure_ascii=False, separators=(',', ':'))

    # 駅間距離のレポート（営業キロとの突き合わせ用）
    cum, total = [0.0], 0.0
    for a, b in zip(polyline, polyline[1:]):
        total += dist_km(a, b)
        cum.append(total)
    print(f'wrote {out}  points={len(polyline)}  length={total:.1f}km')
    for sid, idx in station_positions.items():
        print(f'  {sid:<18} idx={idx:<5} {cum[idx]:6.1f}km')


if __name__ == '__main__':
    main()
