#!/usr/bin/env python3
"""
Build a high-precision route geometry from MLIT (国土数値情報) railway data.

MLIT provides government-surveyed railway data with much better tunnel-section
geometry than OSM. The script:
  1. Downloads the latest N02 (railways) GeoJSON if not cached
  2. Filters features by line name (N02_003)
  3. Builds a graph and runs Dijkstra from the start station to the end station
  4. Saves the resulting polyline + station_positions mapping to
     data/geometry/<route_id>.json

License: MLIT 国土数値情報 (free for any use including commercial, with attribution)

Usage:
  python3 scripts/build_geometry.py <route_id> <mlit_line_names> <start_station_id> <end_station_id>

  <mlit_line_names> is one or more MLIT line names (N02_003), comma-separated.
  For routes that traverse multiple lines (e.g., 在来線特急), pass all the
  underlying lines so the graph spans the full journey.

Example:
  python3 scripts/build_geometry.py TOKAIDO_SHINKANSEN 東海道新幹線 TOKYO SHIN_OSAKA
  python3 scripts/build_geometry.py THUNDERBIRD "東海道本線,湖西線,北陸本線" OSAKA TSURUGA
"""
import csv
import heapq
import json
import os
import sys
import urllib.request
import zipfile
from collections import defaultdict
from math import cos, radians, sqrt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT, '.cache')
MLIT_VERSION = 'N02-24'  # bump when MLIT releases a newer fiscal-year dataset
MLIT_URL = f'https://nlftp.mlit.go.jp/ksj/gml/data/N02/{MLIT_VERSION}/{MLIT_VERSION}_GML.zip'
MLIT_ZIP = os.path.join(CACHE_DIR, f'{MLIT_VERSION}_GML.zip')
MLIT_GEOJSON = os.path.join(CACHE_DIR, f'{MLIT_VERSION}_RailroadSection.geojson')


def ensure_mlit_data():
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(MLIT_GEOJSON):
        return
    if not os.path.exists(MLIT_ZIP):
        print(f'downloading MLIT N02 (railways)... ', end='', flush=True)
        urllib.request.urlretrieve(MLIT_URL, MLIT_ZIP)
        print(f'{os.path.getsize(MLIT_ZIP) // 1024 // 1024}MB')
    print('extracting GeoJSON...')
    target_section = f'UTF-8/{MLIT_VERSION}_RailroadSection.geojson'
    target_station = f'UTF-8/{MLIT_VERSION}_Station.geojson'
    station_geojson = os.path.join(CACHE_DIR, f'{MLIT_VERSION}_Station.geojson')
    with zipfile.ZipFile(MLIT_ZIP) as z:
        section_found = False
        station_found = False
        for name in z.namelist():
            if name.endswith(target_section):
                with z.open(name) as src, open(MLIT_GEOJSON, 'wb') as dst:
                    dst.write(src.read())
                section_found = True
            elif name.endswith(target_station):
                with z.open(name) as src, open(station_geojson, 'wb') as dst:
                    dst.write(src.read())
                station_found = True
        if not section_found:
            raise RuntimeError(f'Could not find {target_section} in MLIT archive')


def load_stations():
    stations = {}
    with open(os.path.join(ROOT, 'data', 'stations.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not row['station_id'] or row['station_id'].startswith('WP_'):
                continue
            stations[row['station_id']] = (float(row['lat']), float(row['lon']))
    return stations


def planar_dist(a, b):
    lat_mean = (a[0] + b[0]) / 2
    k = cos(radians(lat_mean))
    dy = b[0] - a[0]
    dx = (b[1] - a[1]) * k
    return sqrt(dx * dx + dy * dy)


def node_id(lat, lon):
    return (round(lat, 6), round(lon, 6))


def build_graph(features):
    adj = defaultdict(set)
    for f in features:
        coords = f['geometry']['coordinates']
        for i in range(len(coords) - 1):
            a = node_id(coords[i][1], coords[i][0])
            b = node_id(coords[i + 1][1], coords[i + 1][0])
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
    return adj


def dijkstra(adj, start, end):
    dist = {start: 0.0}
    prev = {}
    heap = [(0.0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == end:
            break
        if d > dist.get(u, float('inf')):
            continue
        for v in adj[u]:
            nd = d + planar_dist(u, v)
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    if end not in dist:
        return None
    path = [end]
    while path[-1] in prev:
        path.append(prev[path[-1]])
    path.reverse()
    return path


def find_station_indices(polyline, stations, station_ids_on_route):
    result = {}
    for sid in station_ids_on_route:
        if sid not in stations:
            continue
        target = stations[sid]
        best_i, best_d = 0, float('inf')
        for i, p in enumerate(polyline):
            d = planar_dist(p, target)
            if d < best_d:
                best_d = d
                best_i = i
        result[sid] = best_i
        print(f'  {sid:>15} -> idx {best_i:>5}  ({best_d * 111000:.0f}m from station)')
    return result


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    route_id, mlit_names_arg, start_sid, end_sid = sys.argv[1:5]
    mlit_names = [n.strip() for n in mlit_names_arg.split(',') if n.strip()]

    stations = load_stations()
    if start_sid not in stations or end_sid not in stations:
        print(f'ERROR: start/end station not found in stations.csv')
        sys.exit(1)

    # Read which stations belong to this route from routes.csv (in route order)
    station_ids = []
    with open(os.path.join(ROOT, 'data', 'routes.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['route_id'] == route_id:
                station_ids = [s for s in row['stations'].split('|') if not s.startswith('WP_')]
                break
    if not station_ids:
        print(f'ERROR: route {route_id} not found in routes.csv')
        sys.exit(1)

    ensure_mlit_data()
    print(f'loading MLIT data...')
    with open(MLIT_GEOJSON, encoding='utf-8') as f:
        data = json.load(f)
    name_set = set(mlit_names)
    features = [x for x in data['features'] if x['properties'].get('N02_003') in name_set]
    if not features:
        print(f'ERROR: no features matching any of {mlit_names!r}')
        sys.exit(1)
    counts = {n: sum(1 for x in features if x['properties'].get('N02_003') == n) for n in mlit_names}
    for n in mlit_names:
        print(f'  features={counts[n]} for "{n}"')

    adj = build_graph(features)
    print(f'  graph nodes={len(adj)}')

    nodes = list(adj.keys())
    start_node = min(nodes, key=lambda n: planar_dist(n, stations[start_sid]))
    end_node = min(nodes, key=lambda n: planar_dist(n, stations[end_sid]))
    print(f'  start: {planar_dist(start_node, stations[start_sid])*111000:.0f}m from {start_sid}')
    print(f'  end:   {planar_dist(end_node, stations[end_sid])*111000:.0f}m from {end_sid}')

    print('running dijkstra...')
    path = dijkstra(adj, start_node, end_node)
    if not path:
        print('ERROR: no path found')
        sys.exit(1)

    polyline = [[lat, lon] for (lat, lon) in path]
    total = sum(planar_dist(path[i], path[i + 1]) for i in range(len(path) - 1))
    seg_lens = [planar_dist(path[i], path[i + 1]) * 111000 for i in range(len(path) - 1)]
    print(f'  polyline points={len(polyline)}, total length={total * 111000 / 1000:.1f}km')
    print(f'  max segment={max(seg_lens):.0f}m, segments>500m={sum(1 for s in seg_lens if s>500)}')

    print('mapping stations to polyline indices...')
    station_positions = find_station_indices(path, stations, station_ids)

    out_dir = os.path.join(ROOT, 'data', 'geometry')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{route_id}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'polyline': polyline,
            'station_positions': station_positions,
        }, f, ensure_ascii=False, separators=(',', ':'))
    size_kb = os.path.getsize(out_path) / 1024
    print(f'saved: {out_path} ({size_kb:.0f}KB)')


if __name__ == '__main__':
    main()
