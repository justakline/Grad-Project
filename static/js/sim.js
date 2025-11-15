// Grab elements
const canvas = document.getElementById("simulationCanvas");
const ctx = canvas.getContext("2d");
const statusDiv = document.getElementById("status");
const initBtn = document.getElementById("initBtn");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const stepCountSpan = document.getElementById("stepCount");
const agentCountSpan = document.getElementById("agentCount");
const aggregateData = document.getElementById("aggregateData");
const viewport = document.getElementById("viewport");
const vwInput = document.getElementById("vwInput");
const vhInput = document.getElementById("vhInput");
const applyViewportBtn = document.getElementById("applyViewport");

const zoomSlider = document.getElementById("zoomSlider");
const zoomInBtn = document.getElementById("zoomInBtn");
const zoomOutBtn = document.getElementById("zoomOutBtn");
const zoomLabel = document.getElementById("zoomLabel");
const resetViewBtn = document.getElementById("resetViewBtn");

const toggleSettingsBtn = document.getElementById("toggleSettingsBtn");
const settingsPanel = document.getElementById("settingsPanel");
const driverMix = document.getElementById("driverMix");
const driverMixValue = document.getElementById("driverMixValue");
const applySettingsBtn = document.getElementById("applySettingsBtn");

// Driver behavior inputs
const aggressiveInput = document.getElementById("aggressiveInput");
const defensiveInput = document.getElementById("defensiveInput");

// Vehicle mix inputs and sliders
// Vehicle ratio inputs (independent)
const truckRatio = document.getElementById("truckRatio");
const suvRatio = document.getElementById("suvRatio");
const motorcycleRatio = document.getElementById("motorcycleRatio");
const vehicleRatioRaw = document.getElementById("vehicleRatioRaw");
const vehicleRatioPercent = document.getElementById("vehicleRatioPercent");

// State
const driveStrategyColorMap = {
  brake: "#f77926",
  accelerate: "#22c55e",
  cruise: "#eab308",
};

let settings = {
  dt: 0,
  aggressivePct: 0,
  agentRate: 0,
  nAgents: 0,
  highwayLength: 0,
  laneNumber: 0,
  laneSize: 0,
  isLogging: true,
  logDt: 0,
  aggressivePct: 0,
  defensivePct: 0,
  truckRatio: 0,
  suv_ratio: 0,
  motorcycle_ratio: 0,
};

let isRunning = false,
  intervalId = null,
  simType = null;

// World extents (mm) from backend
let maxX = 1000,
  maxY = 1000;
// Highway info
let laneCount = 0,
  laneWidth = 0,
  laneCenters = [];

// View transform
let fitScale = 1,
  zoom = 1,
  s = 1,
  ox = 0,
  oy = 0;

// Panning
let isPanning = false,
  panStartX = 0,
  panStartY = 0,
  oxAtPan = 0,
  oyAtPan = 0;

let lastAgents = [];

let simReady = false;

let stepAbortController = null; // abort in-flight /api/step
let runId = 0; // drops late responses from older runs

// UI helpers
function setStatus(msg, active = false) {
  statusDiv.textContent = msg;
  statusDiv.className = active ? "status active" : "status";
}

// Resize + HiDPI
const ro = new ResizeObserver(() => layoutPreserveCenter());
ro.observe(viewport);

function layoutPreserveCenter() {
  const cssW = viewport.clientWidth,
    cssH = viewport.clientHeight;
  const centerBefore = screenToWorld(cssW / 2, cssH / 2);

  const dpr = window.devicePixelRatio || 1;
  canvas.style.width = `${cssW}px`;
  canvas.style.height = `${cssH}px`;
  canvas.width = Math.max(1, Math.round(cssW * dpr));
  canvas.height = Math.max(1, Math.round(cssH * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  fitScale = Math.min(cssW / maxX, cssH / maxY);
  s = fitScale * zoom;

  const [wx, wy] = centerBefore;
  ox = cssW / 2 - wx * s;
  oy = cssH / 2 - (maxY - wy) * s;

  redraw();
}

// Transforms
function screenToWorld(px, py) {
  return [(px - ox) / s, maxY - (py - oy) / s];
}
function worldToScreen(x, y) {
  return [ox + x * s, oy + (maxY - y) * s];
}

// Zoom
function setZoom(newZoom, ax = null, ay = null) {
  newZoom = Math.min(zoomSlider.max, Math.max(zoomSlider.min, newZoom));
  if (newZoom === zoom) return;
  const cssW = viewport.clientWidth,
    cssH = viewport.clientHeight;
  const px = ax ?? cssW / 2,
    py = ay ?? cssH / 2;
  const [wx, wy] = screenToWorld(px, py);
  zoom = newZoom;
  s = fitScale * zoom;
  ox = px - wx * s;
  oy = py - (maxY - wy) * s;
  zoomSlider.value = String(zoom);
  zoomLabel.textContent = `${Math.round(zoom * 100)}%`;
  redraw();
}
zoomSlider.addEventListener("input", (e) =>
  setZoom(parseFloat(e.target.value))
);
zoomInBtn.addEventListener("click", () => setZoom(zoom * 1.1));
zoomOutBtn.addEventListener("click", () => setZoom(zoom / 1.1));
resetViewBtn.addEventListener("click", resetView);

viewport.addEventListener(
  "wheel",
  (e) => {
    e.preventDefault();
    const r = viewport.getBoundingClientRect();
    const factor = e.deltaY > 0 ? 1 / 1.08 : 1.08;
    setZoom(zoom * factor, e.clientX - r.left, e.clientY - r.top);
  },
  { passive: false }
);

window.addEventListener("keydown", (e) => {
  if (e.key === "+" || e.key === "=") setZoom(zoom * 1.1);
  else if (e.key === "-" || e.key === "_") setZoom(zoom / 1.1);
  else if (e.key === "0") resetView();
});

function resetView() {
  zoom = 1;
  zoomSlider.value = "1";
  zoomLabel.textContent = "100%";
  const cssW = viewport.clientWidth,
    cssH = viewport.clientHeight;
  fitScale = Math.min(cssW / maxX, cssH / maxY);
  s = fitScale * zoom;
  const contentW = s * maxX,
    contentH = s * maxY;
  ox = (cssW - contentW) / 2;
  oy = (cssH - contentH) / 2;
  redraw();
}

// Panning
viewport.addEventListener("mousedown", (e) => {
  isPanning = true;
  viewport.classList.add("panning");
  panStartX = e.clientX;
  panStartY = e.clientY;
  oxAtPan = ox;
  oyAtPan = oy;
});
window.addEventListener("mousemove", (e) => {
  if (!isPanning) return;
  ox = oxAtPan + (e.clientX - panStartX);
  oy = oyAtPan + (e.clientY - panStartY);
  redraw();
});
window.addEventListener("mouseup", () => {
  isPanning = false;
  viewport.classList.remove("panning");
});

// Open/close on click
toggleSettingsBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  // ensure it is not display:none
  settingsPanel.classList.remove("hidden");
  // animate visible state
  settingsPanel.classList.toggle("active");
});

// Close when clicking outside
document.addEventListener("click", (e) => {
  if (!settingsPanel.classList.contains("active")) return;
  const clickedButton = e.target === toggleSettingsBtn;
  const clickedInsidePanel = settingsPanel.contains(e.target);
  if (!clickedButton && !clickedInsidePanel) {
    settingsPanel.classList.remove("active");
    // keep it present in DOM for animation; do not re-add 'hidden' here
  }
});

// ============ UI BINDING FIX ============

function pctInt(v) {
  v = Number(v);
  if (!Number.isFinite(v)) v = 0;
  if (v < 0) v = 0;
  if (v > 100) v = 100;
  return Math.round(v);
}

/* ---------------- Driver Behavior: Aggressive vs Defensive = 100 ---------------- */
function setAggressivePercent(aggr) {
  aggr = pctInt(aggr);
  const def = 100 - aggr;

  if (aggressiveInput) aggressiveInput.value = aggr;
  if (defensiveInput) defensiveInput.value = def;
  if (driverMix) driverMix.value = aggr;
  if (driverMixValue)
    driverMixValue.textContent = `${aggr}% Aggressive / ${def}% Defensive`;
}

function bindDriverBehavior() {
  // If nothing exists, skip silently
  if (!driverMix && !aggressiveInput) return;

  // Remove any prior listeners by setting new ones once
  if (driverMix && !driverMix._bound) {
    driverMix.addEventListener("input", (e) =>
      setAggressivePercent(e.target.value)
    );
    driverMix._bound = true;
  }
  if (aggressiveInput && !aggressiveInput._bound) {
    aggressiveInput.addEventListener("input", (e) =>
      setAggressivePercent(e.target.value)
    );
    aggressiveInput._bound = true;
  }
  if (defensiveInput && !defensiveInput._bound) {
    defensiveInput.addEventListener("input", (e) => {
      const def = Math.max(
        0,
        Math.min(100, parseInt(e.target.value || "0", 10))
      );
      setAggressivePercent(100 - def);
    });
    defensiveInput._bound = true;
  }
  // Initialize display
  const init = aggressiveInput?.value ?? driverMix?.value ?? 30;
  setAggressivePercent(init);
}
/* ---------------- Vehicle Mix Ratios (independent) ---------------- */
function nonNeg(n) {
  const v = parseFloat(n, 10);
  return Number.isFinite(v) && v >= 0 ? v : 0;
}

function updateVehicleRatioSummary() {
  if (
    !vehicleRatioRaw ||
    !vehicleRatioPercent ||
    !truckRatio ||
    !suvRatio ||
    !motorcycleRatio
  )
    return;
  const t = nonNeg(truckRatio.value);
  const s = nonNeg(suvRatio.value);
  const m = nonNeg(motorcycleRatio.value);
  const total = t + s + m;

  let pt = 0,
    ps = 0,
    pm = 0;
  if (total > 0) {
    pt = Math.round((t / total) * 100);
    ps = Math.round((s / total) * 100);
    pm = 100 - pt - ps; // exact sum
  } // else leaves 0/0/0

  vehicleRatioRaw.textContent = `Truck ${t} : SUV ${s} : Motorcycle ${m} `;

  vehicleRatioPercent.textContent = `(${pt}% / ${ps}% / ${pm}%)`;
}

function bindVehicleRatios() {
  if (truckRatio && !truckRatio._bound) {
    truckRatio.addEventListener("input", updateVehicleRatioSummary);
    truckRatio._bound = true;
  }
  if (suvRatio && !suvRatio._bound) {
    suvRatio.addEventListener("input", updateVehicleRatioSummary);
    suvRatio._bound = true;
  }
  if (motorcycleRatio && !motorcycleRatio._bound) {
    motorcycleRatio.addEventListener("input", updateVehicleRatioSummary);
    motorcycleRatio._bound = true;
  }

  // Initialize
  updateVehicleRatioSummary();
}

/* ---------------- Init bindings ---------------- */
function wireSlidersAndInputs() {
  bindDriverBehavior();
  bindVehicleRatios();
}

// Bind once DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", wireSlidersAndInputs);
} else {
  wireSlidersAndInputs();
}
// Also bind when settings panel is toggled open
if (toggleSettingsBtn) {
  toggleSettingsBtn.addEventListener("click", () => {
    setTimeout(wireSlidersAndInputs, 0);
  });
}

// ========== END UI BINDING FIX ==========

function setSettings() {
  settings.dt = parseInt(document.getElementById("dtInput").value, 10);

  // Read aggressive percentage from the linked control
  if (aggressiveInput) {
    settings.aggressivePct = parseInt(aggressiveInput.value, 10);
  }

  // Store raw ratios so backend can decide how to sample
  if (truckRatio && suvRatio && motorcycleRatio) {
    settings.suv_ratio = nonNeg(suvRatio.value);
    settings.truckRatio = nonNeg(truckRatio.value);
    settings.motorcycle_ratio = nonNeg(motorcycleRatio.value);
    // settings.vehicleRatios = {
    //   truck: nonNeg(truckRatio.value),
    //   suv: nonNeg(suvRatio.value),
    //   motorcycle: nonNeg(motorcycleRatio.value),
    // };
  }

  settings.agentRate = parseInt(document.getElementById("agentRate").value, 10);
  settings.nAgents = parseInt(document.getElementById("numAgents").value, 10);
  settings.highwayLength =
    parseInt(document.getElementById("highwayLength").value, 10) * 1000; // Conversion to mm
  settings.laneNumber = parseInt(
    document.getElementById("laneNumber").value,
    10
  );
  settings.laneSize =
    parseFloat(document.getElementById("laneSize").value) * 1000; // Conversion to mm
  settings.isLogging = document.getElementById("isLogging").checked;
  settings.logDt = parseInt(document.getElementById("logDt").value, 10);

  // close the card
  settingsPanel.classList.remove("active");
}

// Backend
async function initSimulation(type) {
  if (isRunning) {
    return;
  }
  try {
    setSettings();
    const params = new URLSearchParams({
      dt: settings.dt,
      aggressive_pct: settings.aggressivePct,
      agent_rate: settings.agentRate,
      n_agents: settings.nAgents,
      highway_length: settings.highwayLength,
      number_of_lanes: settings.laneNumber,
      size_of_lanes: settings.laneSize,
      is_logging_agents: settings.isLogging,
      logging_dt: settings.logDt,
      aggressive_pct: settings.aggressivePct,
      defensive_pct: settings.defensivePct,
      truck_ratio: settings.truckRatio,
      suv_ratio: settings.suv_ratio,
      motorcycle_ratio: settings.motorcycle_ratio,
    });
    const res = await fetch(`/api/init/${type}?${params.toString()}`);
    const data = await res.json();

    if (data.status === "success") {
      simType = type;
      maxX = data.x_max;
      maxY = data.y_max;
      laneCount = data.lane_count ?? 0;
      laneWidth = data.lane_width ?? 0;
      laneCenters = Array.isArray(data.lane_centers)
        ? data.lane_centers.slice().sort((a, b) => a - b)
        : [];
      simReady = true;
      resetView();
      setStatus(`${data.message}. Click Start to begin.`, true);
      startBtn.disabled = false;
      stopBtn.disabled = true;
      initBtn.disabled = true;
      lastAgents = [];
      redraw();
    } else setStatus(`Error: ${data.message}`);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}

let pollingMs = 50;
function startSimulation() {
  if (isRunning) return;
  runId += 1; // new run; older responses become stale
  isRunning = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;
  initBtn.disabled = true;
  setStatus("Simulation running...", true);
  intervalId = setInterval(stepSimulation, pollingMs);
}
function stopSimulation() {
  if (!isRunning) return;
  setStatus("Simulation paused");
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }

  // abort any in-flight fetch so it stops now
  if (stepAbortController) {
    stepAbortController.abort();
    stepAbortController = null;
  }
  isRunning = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  initBtn.disabled = true;
}
async function resetSimulation() {
  stopSimulation();
  try {
    const res = await fetch("/api/reset");
    const data = await res.json();
    if (data.status === "success") {
      simType = null;
      lastAgents = [];
      simReady = false;
      startBtn.disabled = true;
      stopBtn.disabled = true;
      initBtn.disabled = false;
      stepCountSpan.textContent = "0";
      agentCountSpan.textContent = "0";
      aggregateData.textContent = "0";
      clearCanvas();
      setStatus("Simulation reset. Initialize a new simulation.");
    }
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}
async function stepSimulation() {
  if (!isRunning) return;

  // abort any previous in-flight step, then start a fresh one
  if (stepAbortController) {
    stepAbortController.abort();
  }
  const controller = new AbortController();
  stepAbortController = controller;

  // capture current run; if Start/Stop cycles, late responses are ignored
  const myRunId = runId;
  try {
    const res = await fetch("/api/step", { signal: controller.signal });
    // if we stopped or restarted meanwhile, drop this response
    if (!isRunning || myRunId !== runId) return;
    const data = await res.json();
    if (data.status === "success") {
      lastAgents = data.agents;
      redraw();
      stepCountSpan.textContent = data.step;
      agentCountSpan.textContent = data.agents.length;
      var aggData = "";
      for (const d of data.aggregateData) {
        for (const key of Object.keys(d)) {
          aggData += "| " + key + ": " + d[key] + " ";
        }
      }
      aggregateData.textContent = aggData;
    } else {
      setStatus(`Error: ${data.message}`);
      stopSimulation();
    }
  } catch (err) {
    if (err && err.name === "AbortError") return;
    setStatus(`Error: ${err.message}`);
    stopSimulation();
  } finally {
    // clear controller if it is ours
    if (stepAbortController === controller) {
      stepAbortController = null;
    }
  }
}

// Drawing basics
function clearCanvas() {
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.restore();
  const dpr = window.devicePixelRatio || 1;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvas.width / dpr, canvas.height / dpr);
}

// Highway rect (SCREEN px)
function getHighwayRect() {
  const pTL = worldToScreen(0, maxY);
  const pBR = worldToScreen(maxX, 0);
  const x0 = Math.floor(Math.min(pTL[0], pBR[0]));
  const y0 = Math.floor(Math.min(pTL[1], pBR[1]));
  const x1 = Math.ceil(Math.max(pTL[0], pBR[0]));
  const y1 = Math.ceil(Math.max(pTL[1], pBR[1]));
  return { x0, y0, x1, y1, w: x1 - x0, h: y1 - y0 };
}

// Highway (lanes + shoulders)
function drawHighway() {
  if (!simReady) return;
  const R = getHighwayRect();

  // Base asphalt
  ctx.fillStyle = "#222";
  ctx.fillRect(R.x0, R.y0, R.w, R.h);

  if (!laneWidth || !laneCenters || laneCenters.length === 0) {
    drawHighwayBorders();
    return;
  }

  // Build lane bands in WORLD units
  const half = laneWidth / 2;
  const centers = laneCenters.slice().sort((a, b) => a - b);
  const laneBands = centers.map((c) => [
    Math.max(0, c - half),
    Math.min(maxX, c + half),
  ]);

  // Build WORLD edges: 0, each lane boundary, maxX (deduped)
  const edgesWorldRaw = [0, ...laneBands.flat(), maxX];
  const EPS = 1e-6;
  const edgesWorld = [];
  edgesWorldRaw
    .sort((a, b) => a - b)
    .forEach((x) => {
      if (
        edgesWorld.length === 0 ||
        Math.abs(x - edgesWorld[edgesWorld.length - 1]) > EPS
      ) {
        edgesWorld.push(x);
      }
    });

  // Map to SCREEN; pin ends to rect; round internals to px
  let edgesX = edgesWorld.map((x) => worldToScreen(x, 0)[0]);
  const R2 = getHighwayRect();
  edgesX[0] = R2.x0;
  edgesX[edgesX.length - 1] = R2.x1;
  for (let i = 1; i < edgesX.length - 1; i++) edgesX[i] = Math.round(edgesX[i]);

  // Helper: does strip [a,b] (WORLD) overlap any lane band by >0?
  const overlapsLane = (a, b) => {
    for (const [L, Rw] of laneBands) {
      const overlap = Math.min(b, Rw) - Math.max(a, L);
      if (overlap > 0) return true;
    }
    return false;
  };

  // Paint consecutive strips full height; last strip forced to right edge
  let sx = edgesX[0];
  for (let i = 0; i < edgesX.length - 1; i++) {
    const next = i < edgesX.length - 2 ? edgesX[i + 1] : R2.x1;
    const w = next - sx;
    const aW = edgesWorld[i];
    const bW = edgesWorld[i + 1];
    if (w > 0) {
      const isLane = overlapsLane(aW, bW);
      ctx.fillStyle = isLane ? (i % 2 ? "#343434" : "#2c2c2c") : "#151515";
      ctx.fillRect(sx, R2.y0, w, R2.h);
    }
    sx = next;
  }

  drawHighwayBorders();
}

function drawHighwayBorders() {
  if (!simReady) return;
  ctx.save();
  ctx.strokeStyle = "#f5f5f5";
  ctx.lineWidth = Math.max(2, 3 * (s / (fitScale || 1)));
  const tL = worldToScreen(0, maxY),
    tR = worldToScreen(maxX, maxY);
  const bL = worldToScreen(0, 0),
    bR = worldToScreen(maxX, 0);
  ctx.beginPath();
  ctx.moveTo(tL[0], tL[1]);
  ctx.lineTo(tR[0], tR[1]);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(bL[0], bL[1]);
  ctx.lineTo(bR[0], bR[1]);
  ctx.stroke();
  ctx.restore();
}

// Agents
function drawAgents() {
  if (!simReady) return;
  for (const a of lastAgents) {
    const [px, py] = worldToScreen(a.x, a.y);
    const halfL = Math.max(0.5, (a.length * s - 1) / 2);
    const halfW = (a.width * s) / 2;

    var color =
      {
        brake: "#f77926",
        accelerate: "#22c55e",
        cruise: "#eab308",
      }[a.drive_strategy] || "#ffffff";

    ctx.save();
    ctx.translate(px, py);
    const heading = simType === "traffic" ? -a.heading : a.heading;
    ctx.rotate(heading);
    ctx.fillStyle = color;
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 1;
    ctx.beginPath();

    ctx.rect(-halfL, -halfW, 2 * halfL, 2 * halfW);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(halfL, -halfW);
    ctx.lineTo(halfL, halfW);
    ctx.stroke();
    ctx.restore();
  }
}

// Paint black outside the highway instead of clipping
function maskOutsideHighway() {
  if (!simReady) return;
  const R = getHighwayRect();
  const W = canvas.width / (window.devicePixelRatio || 1);
  const H = canvas.height / (window.devicePixelRatio || 1);
  ctx.fillStyle = "#000";
  if (R.x0 > 0) ctx.fillRect(0, 0, R.x0, H);
  if (R.x1 < W) ctx.fillRect(R.x1, 0, W - R.x1, H);
  if (R.y0 > 0) ctx.fillRect(R.x0, 0, R.w, R.y0);
  if (R.y1 < H) ctx.fillRect(R.x0, R.y1, R.w, H - R.y1);
}

// Main redraw
function redraw() {
  clearCanvas();
  if (!simReady) return;
  drawHighway();
  drawAgents();
  maskOutsideHighway();
}

// Boot (blank on load)
layoutPreserveCenter();
