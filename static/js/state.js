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
