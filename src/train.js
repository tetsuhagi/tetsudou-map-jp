// "HH:MM" → minutes since 00:00
function toMinutes(hhmm) {
  if (!hhmm) return null;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

// linear interpolation between two stations
function interpolate(a, b, t) {
  return {
    lat: a.lat + (b.lat - a.lat) * t,
    lon: a.lon + (b.lon - a.lon) * t,
  };
}

/**
 * Compute the current position of a train at `nowMin` (minutes since 00:00).
 * Returns { lat, lon, status, fromStation, toStation } or null if not running.
 *   status: 'waiting' (before first dep), 'finished', 'stopped' (at a station), 'moving'
 */
export function computeTrainPosition(train, stations, nowMin) {
  const stops = train.stops;
  if (stops.length < 2) return null;

  const firstDep = toMinutes(stops[0].departure);
  const lastArr = toMinutes(stops[stops.length - 1].arrival);
  if (firstDep == null || lastArr == null) return null;

  if (nowMin < firstDep) return { status: 'waiting' };
  if (nowMin >= lastArr) return { status: 'finished' };

  for (let i = 0; i < stops.length - 1; i++) {
    const cur = stops[i];
    const next = stops[i + 1];
    const curDep = toMinutes(cur.departure);
    const nextArr = toMinutes(next.arrival);
    const curArr = toMinutes(cur.arrival);

    // currently stopped at `cur` station (between arrival and departure)
    if (i > 0 && curArr != null && curDep != null && nowMin >= curArr && nowMin < curDep) {
      const st = stations[cur.station_id];
      return {
        status: 'stopped',
        lat: st.lat,
        lon: st.lon,
        atStation: st.name,
      };
    }

    // currently between `cur` (departure) and `next` (arrival)
    if (curDep != null && nextArr != null && nowMin >= curDep && nowMin < nextArr) {
      const span = nextArr - curDep;
      const t = span > 0 ? (nowMin - curDep) / span : 0;
      const from = stations[cur.station_id];
      const to = stations[next.station_id];
      const p = interpolate(from, to, t);
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
