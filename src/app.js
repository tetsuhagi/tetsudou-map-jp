import { loadAllData } from './data.js';
import { computeTrainPosition, currentTimeMinutes } from './train.js';

const TICK_MS = 1000;

const clockEl = document.getElementById('clock');
const statusEl = document.getElementById('status');

// Center on Japan, zoom out enough to see the whole archipelago
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

    // Station dots
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

function updateTrains(data) {
  const now = new Date();
  clockEl.textContent = formatClock(now);
  const nowMin = currentTimeMinutes(now);

  let runningCount = 0;
  for (const train of Object.values(data.trains)) {
    const pos = computeTrainPosition(train, data.stations, nowMin);
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
    const tooltip = pos.status === 'stopped'
      ? `${train.name}（${pos.atStation}停車中）`
      : `${train.name}（${pos.fromStation}→${pos.toStation}）`;

    if (!marker) {
      const icon = L.divIcon({
        className: `train-marker ${train.direction}`,
        html: train.name,
        iconSize: null,
        iconAnchor: [30, 10],
      });
      trainMarkers[train.id] = L.marker(latlng, { icon }).addTo(map)
        .bindTooltip(tooltip, { direction: 'top', offset: [0, -10] });
    } else {
      marker.setLatLng(latlng);
      marker.setTooltipContent(tooltip);
    }
  }
  statusEl.textContent = `運行中: ${runningCount}本`;
}

(async () => {
  try {
    const data = await loadAllData();
    drawRoutes(data);
    updateTrains(data);
    setInterval(() => updateTrains(data), TICK_MS);
  } catch (err) {
    console.error(err);
    statusEl.textContent = `エラー: ${err.message}`;
  }
})();
