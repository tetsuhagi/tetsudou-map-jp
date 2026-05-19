const V = '?v=98';

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length === 0) return [];
  const header = lines[0].split(',');
  return lines.slice(1).map(line => {
    const cells = line.split(',');
    const row = {};
    header.forEach((key, i) => { row[key] = cells[i] ?? ''; });
    return row;
  });
}

async function fetchCSV(path) {
  const res = await fetch(path + V);
  if (!res.ok) throw new Error(`failed to load ${path}: ${res.status}`);
  return parseCSV(await res.text());
}

async function fetchCSVOptional(path) {
  try {
    const res = await fetch(path + V);
    if (!res.ok) return null;
    return parseCSV(await res.text());
  } catch {
    return null;
  }
}

async function fetchJSONOptional(path) {
  try {
    const res = await fetch(path + V);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// 'weekday' or 'holiday' based on the given date (defaults to now).
// Saturday/Sunday → holiday; weekday otherwise. Japanese public holidays are not
// automatically detected — override `dayType` in loadAllData() if needed.
export function getDayType(date = new Date()) {
  const d = date.getDay();
  return (d === 0 || d === 6) ? 'holiday' : 'weekday';
}

async function loadTimetableForRoute(routeId, dayType) {
  const baseDir = `data/timetables/${routeId}`;
  const trainsRaw = await fetchCSVOptional(`${baseDir}/trains.csv`);
  if (!trainsRaw || trainsRaw.length === 0) return { trains: [], schedule: [] };

  // Prefer day-type-specific schedule; fall back to weekday.csv
  let schedule = null;
  if (dayType === 'holiday') {
    schedule = await fetchCSVOptional(`${baseDir}/holiday.csv`);
  }
  if (!schedule) {
    schedule = await fetchCSVOptional(`${baseDir}/weekday.csv`);
  }
  return { trains: trainsRaw, schedule: schedule || [] };
}

export async function loadAllData({ dayType } = {}) {
  if (!dayType) dayType = getDayType();

  const [stationsRaw, routesRaw] = await Promise.all([
    fetchCSV('data/stations.csv'),
    fetchCSV('data/routes.csv'),
  ]);

  const stations = {};
  for (const s of stationsRaw) {
    if (!s.station_id) continue;
    stations[s.station_id] = {
      id: s.station_id,
      name: s.name,
      lat: parseFloat(s.lat),
      lon: parseFloat(s.lon),
    };
  }

  const routes = {};
  for (const r of routesRaw) {
    routes[r.route_id] = {
      id: r.route_id,
      name: r.name,
      color: r.color,
      display_id: r.display_id || '',
      icon: r.icon ? r.icon + V : '',
      stations: r.stations.split('|'),
      hide_when_idle: r.hide_when_idle === 'true' || r.hide_when_idle === '1',
    };
  }

  const trains = {};
  await Promise.all(Object.values(routes).map(async route => {
    // Geometry
    const geo = await fetchJSONOptional(`data/geometry/${route.id}.json`);
    if (geo && Array.isArray(geo.polyline) && geo.station_positions) {
      route.polyline = geo.polyline;
      route.stationPositions = geo.station_positions;
    } else {
      route.polyline = route.stations
        .filter(sid => stations[sid])
        .map(sid => [stations[sid].lat, stations[sid].lon]);
      route.stationPositions = {};
      let idx = 0;
      for (const sid of route.stations) {
        if (stations[sid]) {
          route.stationPositions[sid] = idx;
          idx++;
        }
      }
    }

    // Trains + schedule for this route
    const { trains: trainsRaw, schedule } = await loadTimetableForRoute(route.id, dayType);
    for (const t of trainsRaw) {
      trains[t.train_id] = {
        id: t.train_id,
        name: t.name,
        route_id: route.id,
        direction: t.direction,
        stops: [],
      };
    }
    for (const row of schedule) {
      const t = trains[row.train_id];
      if (!t) continue;
      t.stops.push({
        order: parseInt(row.stop_order, 10),
        station_id: row.station_id,
        arrival: row.arrival || null,
        departure: row.departure || null,
      });
    }
  }));

  for (const t of Object.values(trains)) {
    t.stops.sort((a, b) => a.order - b.order);
  }

  return { stations, routes, trains, dayType };
}
