// Grab elements
const canvas = document.getElementById("simulationCanvas");
const ctx = canvas.getContext("2d");
const statusDiv = document.getElementById("status");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const stepCountSpan = document.getElementById("stepCount");
const agentCountSpan = document.getElementById("agentCount");
const viewport = document.getElementById("viewport");
const vwInput = document.getElementById("vwInput");
const vhInput = document.getElementById("vhInput");
const applyViewportBtn = document.getElementById("applyViewport");
const toggleSenseBtn = document.getElementById("toggleSense");

const zoomSlider = document.getElementById("zoomSlider");
const zoomInBtn = document.getElementById("zoomInBtn");
const zoomOutBtn = document.getElementById("zoomOutBtn");
const zoomLabel = document.getElementById("zoomLabel");
const resetViewBtn = document.getElementById("resetViewBtn");

// State
const driveStrategyColorMap = {
  hard_brake: "#ef4444",
  brake: "#f77926",
  accelerate: "#22c55e",
  cruise: "#eab308",
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

let showSensing = true;
let lastAgents = [];

// NEW: gate drawing until initialized
let simReady = false;

// UI helpers
function setStatus(msg, active = false) {
  statusDiv.textContent = msg;
  statusDiv.className = active ? "status active" : "status";
}

toggleSenseBtn.addEventListener("click", () => {
  showSensing = !showSensing;
  toggleSenseBtn.textContent = showSensing ? "Sensing: On" : "Sensing: Off";
  redraw();
});

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
  newZoom = Math.min(4, Math.max(0.25, newZoom));
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

// Backend
async function initSimulation(type) {
  try {
    const res = await fetch(`/api/init/${type}`);
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
      simReady = true; // <— now we can draw
      resetView();
      setStatus(`${data.message}. Click Start to begin.`, true);
      startBtn.disabled = false;
      stopBtn.disabled = true;
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
  isRunning = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;
  setStatus("Simulation running...", true);
  intervalId = setInterval(stepSimulation, pollingMs);
}
function stopSimulation() {
  if (!isRunning) return;
  isRunning = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  setStatus("Simulation paused");
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}
async function resetSimulation() {
  stopSimulation();
  try {
    const res = await fetch("/api/reset");
    const data = await res.json();
    if (data.status === "success") {
      simType = null;
      lastAgents = [];
      simReady = false; // <— back to blank
      startBtn.disabled = true;
      stopBtn.disabled = true;
      stepCountSpan.textContent = "0";
      agentCountSpan.textContent = "0";
      clearCanvas(); // <— ensure blank immediately
      setStatus("Simulation reset. Initialize a new simulation.");
    }
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}
async function stepSimulation() {
  try {
    const res = await fetch("/api/step");
    const data = await res.json();
    if (data.status === "success") {
      lastAgents = data.agents;
      redraw();
      stepCountSpan.textContent = data.step;
      agentCountSpan.textContent = data.agents.length;
    } else {
      setStatus(`Error: ${data.message}`);
      stopSimulation();
    }
  } catch (err) {
    setStatus(`Error: ${err.message}`);
    stopSimulation();
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
  ctx.fillStyle = "#000"; // blank black background
  ctx.fillRect(0, 0, canvas.width / dpr, canvas.height / dpr);
}

// Highway rect (SCREEN px)
function getHighwayRect() {
  const pTL = worldToScreen(0, maxY); // top-left
  const pBR = worldToScreen(maxX, 0); // bottom-right
  const x0 = Math.floor(Math.min(pTL[0], pBR[0]));
  const y0 = Math.floor(Math.min(pTL[1], pBR[1]));
  const x1 = Math.ceil(Math.max(pTL[0], pBR[0]));
  const y1 = Math.ceil(Math.max(pTL[1], pBR[1]));
  return { x0, y0, x1, y1, w: x1 - x0, h: y1 - y0 };
}

// Highway (lanes + shoulders)
function drawHighway() {
  if (!simReady) return; // <— do not draw before init
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
  const R2 = getHighwayRect(); // recompute after transforms (safe)
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

    if (showSensing && Number.isFinite(a.sensing_distance)) {
      const r = a.sensing_distance * s;
      ctx.save();
      ctx.beginPath();
      ctx.arc(px, py, r, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(33,150,243,0.12)";
      ctx.strokeStyle = "rgba(33,150,243,0.35)";
      ctx.lineWidth = 1;
      ctx.setLineDash([6, 6]);
      ctx.fill();
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();
    }

    var color =
      {
        hard_brake: "#ef4444",
        brake: "#f77926",
        accelerate: "#22c55e",
        cruise: "#eab308",
      }[a.drive_strategy] || "#ffffff";

      if(a.id == 4){
        color = '#1703fc'
      }
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
  if (!simReady) return; // blank means no masking either
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
  if (!simReady) return; // keep it blank until init succeeds
  drawHighway();
  drawAgents();
  maskOutsideHighway();
}

// Boot (blank on load)
layoutPreserveCenter();
