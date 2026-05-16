// Simple CSV parser (assumes no quoted commas in our data)
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

export async function loadAllData() {
  const [stationsRaw, routesRaw, trainsRaw, scheduleRaw] = await Promise.all([
    fetchCSV('data/stations.csv'),
    fetchCSV('data/routes.csv'),
    fetchCSV('data/trains.csv'),
    fetchCSV('data/schedule.csv'),
  ]);

  const stations = {};
  for (const s of stationsRaw) {
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

  return { stations, routes, trains };
}
