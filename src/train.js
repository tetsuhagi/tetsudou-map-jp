function toMinutes(hhmm) {
  if (!hhmm) return null;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

// Approximate planar distance between two [lat, lon] points (degrees).
function planarDist(a, b) {
  const meanLat = (a[0] + b[0]) / 2;
  const k = Math.cos(meanLat * Math.PI / 180);
  const dy = b[0] - a[0];
  const dx = (b[1] - a[1]) * k;
  return Math.sqrt(dx * dx + dy * dy);
}

// Walk along a route polyline from index `fromIdx` to `toIdx` (in either direction)
// and return the position at fraction `t` (0..1) of the cumulative distance.
function interpolateAlongPolyline(polyline, fromIdx, toIdx, t) {
  if (fromIdx === toIdx) return polyline[fromIdx];
  if (t <= 0) return polyline[fromIdx];
  if (t >= 1) return polyline[toIdx];

  const step = fromIdx < toIdx ? 1 : -1;
  let total = 0;
  const lens = [];
  for (let i = fromIdx; i !== toIdx; i += step) {
    const d = planarDist(polyline[i], polyline[i + step]);
    lens.push(d);
    total += d;
  }
  if (total === 0) return polyline[fromIdx];

  let target = total * t;
  for (let k = 0, i = fromIdx; k < lens.length; k++, i += step) {
    if (target <= lens[k]) {
      const localT = lens[k] > 0 ? target / lens[k] : 0;
      const a = polyline[i];
      const b = polyline[i + step];
      return [
        a[0] + (b[0] - a[0]) * localT,
        a[1] + (b[1] - a[1]) * localT,
      ];
    }
    target -= lens[k];
  }
  return polyline[toIdx];
}

/**
 * Compute the current position of a train at `nowMin` (minutes since 00:00).
 *   status: 'waiting' | 'finished' | 'stopped' | 'moving'
 */
export function computeTrainPosition(train, stations, routes, nowMin) {
  const stops = train.stops;
  if (stops.length < 2) return null;

  const firstDep = toMinutes(stops[0].departure);
  const lastArr = toMinutes(stops[stops.length - 1].arrival);
  if (firstDep == null || lastArr == null) return null;

  if (nowMin < firstDep) return { status: 'waiting' };
  if (nowMin >= lastArr) return { status: 'finished' };

  const route = routes?.[train.route_id];
  if (!route || !route.polyline || !route.stationPositions) return null;

  for (let i = 0; i < stops.length - 1; i++) {
    const cur = stops[i];
    const next = stops[i + 1];
    const curDep = toMinutes(cur.departure);
    const nextArr = toMinutes(next.arrival);
    const curArr = toMinutes(cur.arrival);

    if (i > 0 && curArr != null && curDep != null && nowMin >= curArr && nowMin < curDep) {
      const st = stations[cur.station_id];
      const idx = route.stationPositions[cur.station_id];
      const [lat, lon] = (idx != null && route.polyline[idx]) ? route.polyline[idx] : [st.lat, st.lon];
      return { status: 'stopped', lat, lon, atStation: st.name };
    }

    if (curDep != null && nextArr != null && nowMin >= curDep && nowMin < nextArr) {
      const span = nextArr - curDep;
      const t = span > 0 ? (nowMin - curDep) / span : 0;
      const fromIdx = route.stationPositions[cur.station_id];
      const toIdx = route.stationPositions[next.station_id];
      if (fromIdx == null || toIdx == null) return null;
      const [lat, lon] = interpolateAlongPolyline(route.polyline, fromIdx, toIdx, t);
      return {
        status: 'moving',
        lat,
        lon,
        fromStation: stations[cur.station_id].name,
        toStation: stations[next.station_id].name,
        progress: t,
      };
    }
  }
  return null;
}

export function currentTimeMinutes(date = new Date()) {
  return date.getHours() * 60 + date.getMinutes() + date.getSeconds() / 60;
}
