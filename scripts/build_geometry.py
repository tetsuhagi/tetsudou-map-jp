#!/usr/bin/env python3
"""
Fetch railway geometry from OpenStreetMap (Overpass API) and convert it into
a route polyline that the app can use for high-precision rendering and
position interpolation.

Output: data/geometry/<route_id>.json
  {
    "polyline": [[lat, lon], ...],         # ordered points along the track
    "station_positions": { station_id: idx } # nearest polyline index per station
  }

Usage:
  python3 scripts/build_geometry.py <route_id> <osm_name> <start_station_id> <end_station_id>

Example:
  python3 scripts/build_geometry.py TOKAIDO_SHINKANSEN 東海道新幹線 TOKYO SHIN_OSAKA
"""
import csv
import heapq
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from math import cos, radians, sqrt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_stations():
    stations = {}
    with open(os.path.join(ROOT, 'data', 'stations.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not row['station_id'] or row['station_id'].startswith('WP_'):
                continue
            stations[row['station_id']] = (float(row['lat']), float(row['lon']))
    return stations


def fetch_ways(osm_name):
    query = f'[out:json][timeout:180];(way["name"="{osm_name}"]["railway"="rail"];);out geom;'
    req = urllib.request.Request(
        'https://overpass-api.de/api/interpreter',
        data=query.encode('utf-8'),
        headers={'User-Agent': 'tetsudou-now/1.0', 'Accept': 'application/json'},
    )
    print(f'fetching geometry for "{osm_name}"...')
    with urllib.request.urlopen(req, timeout=240) as resp:
        return json.loads(resp.read())


def planar_dist(a, b):
    lat_mean = (a[0] + b[0]) / 2
    k = cos(radians(lat_mean))
    dy = b[0] - a[0]
    dx = (b[1] - a[1]) * k
    return sqrt(dx * dx + dy * dy)


def build_graph(data):
    def node_id(lat, lon):
        return (round(lat, 6), round(lon, 6))

    adj = defaultdict(set)
    for el in data['elements']:
        if el['type'] != 'way' or 'geometry' not in el:
            continue
        geom = el['geometry']
        for i in range(len(geom) - 1):
            a = node_id(geom[i]['lat'], geom[i]['lon'])
            b = node_id(geom[i + 1]['lat'], geom[i + 1]['lon'])
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
    return adj


def nearest_node(nodes, target):
    return min(nodes, key=lambda n: planar_dist(n, target))


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
    """For each station, find the nearest index on the polyline.
    Returns dict: station_id -> index."""
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
    route_id, osm_name, start_sid, end_sid = sys.argv[1:5]

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

    data = fetch_ways(osm_name)
    ways = [e for e in data['elements'] if e['type'] == 'way' and 'geometry' in e]
    print(f'  ways={len(ways)}')

    adj = build_graph(data)
    print(f'  graph nodes={len(adj)}')

    nodes = list(adj.keys())
    start_node = nearest_node(nodes, stations[start_sid])
    end_node = nearest_node(nodes, stations[end_sid])

    print('running dijkstra...')
    path = dijkstra(adj, start_node, end_node)
    if not path:
        print('ERROR: no path found')
        sys.exit(1)

    polyline = [[lat, lon] for (lat, lon) in path]
    total = sum(planar_dist(path[i], path[i + 1]) for i in range(len(path) - 1))
    print(f'  polyline points={len(polyline)}, total length={total * 111000 / 1000:.1f}km')

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
