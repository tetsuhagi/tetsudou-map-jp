import { loadAllData } from './data.js';
import { computeTrainPosition, currentTimeMinutes } from './train.js';

const TICK_MS = 1000;
const ICON_SIZE = 24;

const clockEl = document.getElementById('clock');
const statusEl = document.getElementById('status');

const map = L.map('map', {
  center: [36.5, 137.5],
  zoom: 6,
  minZoom: 4,
  maxZoom: 12,
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19,
}).addTo(map);

const trainMarkers = {};

function drawRoutes(data) {
  for (const route of Object.values(data.routes)) {
    const latlngs = route.stations.map(sid => {
      const s = data.stations[sid];
      return [s.lat, s.lon];
    });
    L.polyline(latlngs, {
      color: route.color || '#888',
      weight: 3,
      opacity: 0.7,
    }).addTo(map);

    for (const sid of route.stations) {
      const s = data.stations[sid];
      L.circleMarker([s.lat, s.lon], {
        radius: 3,
        color: '#333',
        fillColor: '#fff',
        fillOpacity: 1,
        weight: 1,
      }).addTo(map).bindTooltip(s.name, { permanent: false, direction: 'top' });
    }
  }
}

function formatClock(date) {
  const pad = n => String(n).padStart(2, '0');
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

// Preload route icon images; if a file is missing, mark it as unavailable so we
// can fall back to a colored circle marker.
function preloadIcons(routes) {
  return Promise.all(Object.values(routes).map(route => new Promise(resolve => {
    if (!route.icon) { route._iconLoaded = false; return resolve(); }
    const img = new Image();
    img.onload = () => { route._iconLoaded = true; resolve(); };
    img.onerror = () => { route._iconLoaded = false; resolve(); };
    img.src = route.icon;
  })));
}

function createMarkerForTrain(train, route, latlng) {
  if (route && route._iconLoaded) {
    const icon = L.icon({
      iconUrl: route.icon,
      iconSize: [ICON_SIZE, ICON_SIZE],
      iconAnchor: [ICON_SIZE / 2, ICON_SIZE / 2],
    });
    return L.marker(latlng, { icon });
  }
  // Fallback: circle marker in route color
  return L.circleMarker(latlng, {
    radius: 6,
    color: '#fff',
    fillColor: route?.color || '#888',
    fillOpacity: 1,
    weight: 2,
  });
}

function updateTrains(data) {
  const now = new Date();
  clockEl.textContent = formatClock(now);
  const nowMin = currentTimeMinutes(now);

  let runningCount = 0;
  for (const train of Object.values(data.trains)) {
    const pos = computeTrainPosition(train, data.stations, data.routes, nowMin);
    const marker = trainMarkers[train.id];

    if (!pos || pos.status === 'waiting' || pos.status === 'finished') {
      if (marker) {
        map.removeLayer(marker);
        delete trainMarkers[train.id];
      }
      continue;
    }
    runningCount++;

    const latlng = [pos.lat, pos.lon];
    const route = data.routes[train.route_id];
    const tooltipText = route?.display_id || '?';

    if (!marker) {
      trainMarkers[train.id] = createMarkerForTrain(train, route, latlng)
        .addTo(map)
        .bindTooltip(tooltipText, { direction: 'top', offset: [0, -ICON_SIZE / 2] });
    } else {
      marker.setLatLng(latlng);
    }
  }
  statusEl.textContent = `運行中: ${runningCount}本`;
}

(async () => {
  try {
    const data = await loadAllData();
    await preloadIcons(data.routes);
    drawRoutes(data);
    updateTrains(data);
    setInterval(() => updateTrains(data), TICK_MS);
  } catch (err) {
    console.error(err);
    statusEl.textContent = `エラー: ${err.message}`;
  }
})();
