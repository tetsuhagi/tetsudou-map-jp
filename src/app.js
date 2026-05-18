import { loadAllData } from './data.js?v=56';
import { computeTrainPosition, currentTimeMinutes } from './train.js?v=56';

const TICK_MS = 1000;
const ICON_SIZE = 24;

const clockEl = document.getElementById('clock');
const statusEl = document.getElementById('status');

const map = L.map('map', {
  center: [36.5, 137.5],
  zoom: 6,
  minZoom: 4,
  maxZoom: 12,
  // Canvas renderer makes polylines and circleMarkers draw to a single <canvas>
  // instead of one <svg> element per shape — critical for the 47 routes + ~300
  // station markers we draw simultaneously. Train icons (L.marker with image)
  // are unaffected and remain as DOM elements.
  preferCanvas: true,
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19,
}).addTo(map);

const trainMarkers = {};

// Map tint color stops keyed by hour-of-day. Color is interpolated between
// neighboring stops so the sky color shifts continuously through the day.
const COLOR_STOPS = [
  { h:  0,    rgba: [15, 25, 65, 0.55] },     // 深夜
  { h:  4.5,  rgba: [15, 25, 65, 0.55] },     // 夜終わり
  { h:  5.5,  rgba: [180, 100, 120, 0.30] },  // 夜明け
  { h:  6.5,  rgba: [255, 200, 170, 0.18] },  // 朝焼け
  { h:  8,    rgba: [0, 0, 0, 0] },           // 朝（クリア）
  { h: 15,    rgba: [0, 0, 0, 0] },           // 昼（クリア）
  { h: 16.5,  rgba: [255, 180, 100, 0.15] },  // 夕方
  { h: 17.5,  rgba: [255, 130, 60, 0.28] },   // 夕焼けピーク
  { h: 18.5,  rgba: [100, 80, 140, 0.40] },   // 黄昏
  { h: 19.5,  rgba: [15, 25, 65, 0.55] },     // 夜入り
  { h: 24,    rgba: [15, 25, 65, 0.55] },     // 翌深夜
];

// Tint layer sits in its own Leaflet pane between the polyline pane (400) and
// the marker pane (600) so train icons stay crisp at night while everything
// below — tiles, route lines, station dots — gets the time-of-day color wash.
map.createPane('mapTint');
const tintPane = map.getPane('mapTint');
tintPane.style.zIndex = 550;
tintPane.style.pointerEvents = 'none';
const tintRect = L.rectangle([[-90, -180], [90, 180]], {
  pane: 'mapTint',
  stroke: false,
  fillColor: '#000',
  fillOpacity: 0,
  interactive: false,
}).addTo(map);

function getTintColor(date) {
  const h = date.getHours() + date.getMinutes() / 60 + date.getSeconds() / 3600;
  let lo = COLOR_STOPS[0];
  let hi = COLOR_STOPS[COLOR_STOPS.length - 1];
  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    if (COLOR_STOPS[i].h <= h && h < COLOR_STOPS[i + 1].h) {
      lo = COLOR_STOPS[i];
      hi = COLOR_STOPS[i + 1];
      break;
    }
  }
  const t = hi.h === lo.h ? 0 : (h - lo.h) / (hi.h - lo.h);
  const lerp = (a, b) => a + (b - a) * t;
  return {
    r: Math.round(lerp(lo.rgba[0], hi.rgba[0])),
    g: Math.round(lerp(lo.rgba[1], hi.rgba[1])),
    b: Math.round(lerp(lo.rgba[2], hi.rgba[2])),
    a: lerp(lo.rgba[3], hi.rgba[3]),
  };
}

function phaseLabel(date) {
  const h = date.getHours() + date.getMinutes() / 60;
  if (h < 4.5 || h >= 19.5) return '夜';
  if (h < 6.5) return '夜明け';
  if (h < 8) return '朝';
  if (h < 15) return '昼';
  if (h < 17) return '夕方';
  if (h < 18.5) return '夕焼け';
  return '黄昏';
}

// Night mode toggle. Defaults to off — the tint is only applied while enabled.
// Persisted to localStorage so the user's preference survives reloads.
let nightModeOn = localStorage.getItem('nightMode') === '1';
const nightToggleEl = document.getElementById('night-toggle');

function setNightMode(on) {
  nightModeOn = on;
  nightToggleEl.classList.toggle('on', on);
  nightToggleEl.setAttribute('aria-pressed', on ? 'true' : 'false');
  localStorage.setItem('nightMode', on ? '1' : '0');
  updateTint(new Date());
}
nightToggleEl.addEventListener('click', () => setNightMode(!nightModeOn));
setNightMode(nightModeOn);

function updateTint(now) {
  if (!nightModeOn) {
    tintRect.setStyle({ fillOpacity: 0 });
    document.body.classList.remove('theme-dark');
    return;
  }
  const c = getTintColor(now);
  tintRect.setStyle({
    fillColor: `rgb(${c.r}, ${c.g}, ${c.b})`,
    fillOpacity: c.a,
  });
  // Switch the UI panels to dark theme once the overlay gets meaningfully dim.
  const dark = c.a >= 0.32;
  document.body.classList.toggle('theme-dark', dark);
}

const stationMarkers = [];

// Station dot styling per zoom level. At national zoom (z<=6) the dots are
// dense and visually noisy; scale them down so they recede into the map.
function stationStyleForZoom(z) {
  if (z <= 5) return { radius: 0.6, weight: 0, opacity: 0, fillOpacity: 0.5 };
  if (z === 6) return { radius: 1.2, weight: 0, opacity: 0, fillOpacity: 0.75 };
  if (z === 7) return { radius: 2,   weight: 0.4, opacity: 0.5, fillOpacity: 0.9 };
  return { radius: 3, weight: 1, opacity: 1, fillOpacity: 1 };
}

function applyStationZoomStyle() {
  const style = stationStyleForZoom(map.getZoom());
  for (const m of stationMarkers) {
    m.setRadius(style.radius);
    m.setStyle({ weight: style.weight, opacity: style.opacity, fillOpacity: style.fillOpacity });
  }
}

const routePolylines = {};

function drawRoutes(data) {
  const drawnStations = new Set();
  for (const route of Object.values(data.routes)) {
    const polyline = L.polyline(route.polyline, {
      color: route.color || '#888',
      weight: 3,
      opacity: 0.7,
    });
    // hide_when_idle routes (e.g., overnight sleepers) start hidden;
    // they're attached/removed each tick based on whether any train is running.
    if (!route.hide_when_idle) polyline.addTo(map);
    routePolylines[route.id] = polyline;

    for (const sid of route.stations) {
      if (sid.startsWith('WP_')) continue;
      if (drawnStations.has(sid)) continue;  // dedupe across routes
      drawnStations.add(sid);
      const s = data.stations[sid];
      if (!s) continue;
      const m = L.circleMarker([s.lat, s.lon], {
        color: '#333',
        fillColor: '#fff',
      }).addTo(map).bindTooltip(s.name, { permanent: false, direction: 'top' });
      stationMarkers.push(m);
    }
  }
  applyStationZoomStyle();
  map.on('zoomend', applyStationZoomStyle);
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
  updateTint(now);
  const nowMin = currentTimeMinutes(now);

  let runningCount = 0;
  const runningPerRoute = {};
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
    runningPerRoute[train.route_id] = (runningPerRoute[train.route_id] || 0) + 1;

    const latlng = [pos.lat, pos.lon];
    const route = data.routes[train.route_id];
    const tooltipText = route?.display_id || '?';
    const opacity = pos.opacity ?? 1;

    let m = marker;
    if (!m) {
      m = createMarkerForTrain(train, route, latlng)
        .addTo(map)
        .bindTooltip(tooltipText, { direction: 'top', offset: [0, -ICON_SIZE / 2] });
      trainMarkers[train.id] = m;
    } else {
      m.setLatLng(latlng);
    }
    setMarkerOpacity(m, opacity);
  }

  // hide_when_idle routes: attach polyline only while a train is running on it.
  for (const route of Object.values(data.routes)) {
    if (!route.hide_when_idle) continue;
    const pl = routePolylines[route.id];
    if (!pl) continue;
    const shouldShow = (runningPerRoute[route.id] || 0) > 0;
    if (shouldShow && !map.hasLayer(pl)) pl.addTo(map);
    else if (!shouldShow && map.hasLayer(pl)) map.removeLayer(pl);
  }

  const dayLabel = data.dayType === 'holiday' ? '土日祝' : '平日';
  const phaseSuffix = nightModeOn ? ` / ${phaseLabel(now)}` : '';
  statusEl.textContent = `運行中: ${runningCount}本 / ダイヤ: ${dayLabel}${phaseSuffix}`;
}

function setMarkerOpacity(marker, opacity) {
  if (typeof marker.setOpacity === 'function') {
    marker.setOpacity(opacity);
  } else if (typeof marker.setStyle === 'function') {
    marker.setStyle({ opacity, fillOpacity: opacity });
  }
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
