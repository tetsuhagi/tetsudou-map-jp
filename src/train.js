// "HH:MM" → minutes since 00:00
function toMinutes(hhmm) {
  if (!hhmm) return null;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

function interpolate(a, b, t) {
  return {
    lat: a.lat + (b.lat - a.lat) * t,
    lon: a.lon + (b.lon - a.lon) * t,
  };
}

// Approximate planar distance — good enough for interpolation proportions within Japan.
// Scale longitude by cos(lat) so x/y are roughly km-comparable.
function planarDist(a, b) {
  const meanLat = (a.lat + b.lat) / 2;
  const k = Math.cos(meanLat * Math.PI / 180);
  const dy = b.lat - a.lat;
  const dx = (b.lon - a.lon) * k;
  return Math.sqrt(dx * dx + dy * dy);
}

// Walk along a poly-path of stations and return the point at fraction `t` (0..1) of total distance.
function interpolateAlongPath(pathStations, t) {
  if (pathStations.length < 2) return null;
  if (t <= 0) return { lat: pathStations[0].lat, lon: pathStations[0].lon };

  const segLens = [];
  let total = 0;
  for (let i = 1; i < pathStations.length; i++) {
    const d = planarDist(pathStations[i - 1], pathStations[i]);
    segLens.push(d);
    total += d;
  }
  if (total === 0) return { lat: pathStations[0].lat, lon: pathStations[0].lon };
  if (t >= 1) {
    const last = pathStations[pathStations.length - 1];
    return { lat: last.lat, lon: last.lon };
  }

  let target = total * t;
  for (let i = 0; i < segLens.length; i++) {
    if (target <= segLens[i]) {
      const localT = segLens[i] > 0 ? target / segLens[i] : 0;
      return interpolate(pathStations[i], pathStations[i + 1], localT);
    }
    target -= segLens[i];
  }
  const last = pathStations[pathStations.length - 1];
  return { lat: last.lat, lon: last.lon };
}

// Build the chain of route stations between two train stops, in travel order.
function buildSegmentPath(routeStations, fromId, toId, stations) {
  const fromIdx = routeStations.indexOf(fromId);
  const toIdx = routeStations.indexOf(toId);
  if (fromIdx < 0 || toIdx < 0 || fromIdx === toIdx) return null;
  const ids = fromIdx < toIdx
    ? routeStations.slice(fromIdx, toIdx + 1)
    : routeStations.slice(toIdx, fromIdx + 1).reverse();
  return ids.map(id => stations[id]).filter(Boolean);
}

/**
 * Compute the current position of a train at `nowMin` (minutes since 00:00).
 *   status: 'waiting' (before first dep), 'finished', 'stopped', 'moving'
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
  const routeStations = route?.stations || null;

  for (let i = 0; i < stops.length - 1; i++) {
    const cur = stops[i];
    const next = stops[i + 1];
    const curDep = toMinutes(cur.departure);
    const nextArr = toMinutes(next.arrival);
    const curArr = toMinutes(cur.arrival);

    if (i > 0 && curArr != null && curDep != null && nowMin >= curArr && nowMin < curDep) {
      const st = stations[cur.station_id];
      return { status: 'stopped', lat: st.lat, lon: st.lon, atStation: st.name };
    }

    if (curDep != null && nextArr != null && nowMin >= curDep && nowMin < nextArr) {
      const span = nextArr - curDep;
      const t = span > 0 ? (nowMin - curDep) / span : 0;
      const from = stations[cur.station_id];
      const to = stations[next.station_id];

      let p = null;
      if (routeStations) {
        const path = buildSegmentPath(routeStations, cur.station_id, next.station_id, stations);
        if (path && path.length >= 2) p = interpolateAlongPath(path, t);
      }
      if (!p) p = interpolate(from, to, t);

      return {
        status: 'moving',
        lat: p.lat,
        lon: p.lon,
        fromStation: from.name,
        toStation: to.name,
        progress: t,
      };
    }
  }
  return null;
}

export function currentTimeMinutes(date = new Date()) {
  return date.getHours() * 60 + date.getMinutes() + date.getSeconds() / 60;
}
