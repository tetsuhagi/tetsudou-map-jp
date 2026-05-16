function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = lines[0].split(',');
  return lines.slice(1).map(line => {
    const cells = line.split(',');
    const row = {};
    header.forEach((key, i) => { row[key] = cells[i] ?? ''; });
    return row;
  });
}

async function fetchCSV(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`failed to load ${path}: ${res.status}`);
  return parseCSV(await res.text());
}

async function fetchJSONOptional(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function loadAllData() {
  const [stationsRaw, routesRaw, trainsRaw, scheduleRaw] = await Promise.all([
    fetchCSV('data/stations.csv'),
    fetchCSV('data/routes.csv'),
    fetchCSV('data/trains.csv'),
    fetchCSV('data/schedule.csv'),
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
      icon: r.icon || '',
      stations: r.stations.split('|'),
    };
  }

  const trains = {};
  for (const t of trainsRaw) {
    trains[t.train_id] = {
      id: t.train_id,
      name: t.name,
      route_id: t.route_id,
      direction: t.direction,
      stops: [],
    };
  }

  for (const row of scheduleRaw) {
    const t = trains[row.train_id];
    if (!t) continue;
    t.stops.push({
      order: parseInt(row.stop_order, 10),
      station_id: row.station_id,
      arrival: row.arrival || null,
      departure: row.departure || null,
    });
  }
  for (const t of Object.values(trains)) {
    t.stops.sort((a, b) => a.order - b.order);
  }

  // Load high-resolution geometry per route. Fall back to station-coord polyline
  // when no geometry file exists.
  await Promise.all(Object.values(routes).map(async route => {
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
  }));

  return { stations, routes, trains };
}
