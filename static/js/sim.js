// dom.js - grab all DOM elements

// Canvas and status
const canvas = document.getElementById("simulationCanvas");
const ctx = canvas.getContext("2d");
const statusDiv = document.getElementById("status");

// Control buttons and labels
const initBtn = document.getElementById("initBtn");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const stepCountSpan = document.getElementById("stepCount");
const agentCountSpan = document.getElementById("agentCount");
const aggregateData = document.getElementById("aggregateData");

// Viewport and zoom controls
const viewport = document.getElementById("viewport");
const vwInput = document.getElementById("vwInput");
const vhInput = document.getElementById("vhInput");
const applyViewportBtn = document.getElementById("applyViewport");

const zoomSlider = document.getElementById("zoomSlider");
const zoomInBtn = document.getElementById("zoomInBtn");
const zoomOutBtn = document.getElementById("zoomOutBtn");
const zoomLabel = document.getElementById("zoomLabel");
const resetViewBtn = document.getElementById("resetViewBtn");

// Settings panel
const toggleSettingsBtn = document.getElementById("toggleSettingsBtn");
const settingsPanel = document.getElementById("settingsPanel");
const driverMix = document.getElementById("driverMix");
const driverMixValue = document.getElementById("driverMixValue");
const applySettingsBtn = document.getElementById("applySettingsBtn");

// Driver behavior inputs
const aggressiveInput = document.getElementById("aggressiveInput");
const defensiveInput = document.getElementById("defensiveInput");

// Vehicle mix inputs and summary
const truckRatio = document.getElementById("truckRatio");
const suvRatio = document.getElementById("suvRatio");
const motorcycleRatio = document.getElementById("motorcycleRatio");
const vehicleRatioRaw = document.getElementById("vehicleRatioRaw");
const vehicleRatioPercent = document.getElementById("vehicleRatioPercent");

// Boot the front end once everything is ready
function boot() {
  // Center the canvas based on current viewport size
  if (typeof layoutPreserveCenter === "function") {
    layoutPreserveCenter();
  }

  // Hook up simulation controls
  if (initBtn) {
    // adjust "traffic" if you have multiple sim types
    initBtn.addEventListener("click", () => initSimulation("traffic"));
  }
  if (startBtn) {
    startBtn.addEventListener("click", startSimulation);
  }
  if (stopBtn) {
    stopBtn.addEventListener("click", stopSimulation);
  }
  const resetBtn = document.getElementById("resetBtn");
  if (resetBtn) {
    resetBtn.addEventListener("click", resetSimulation);
  }

  // Optional: viewport size apply button
  if (applyViewportBtn && viewport && vwInput && vhInput) {
    applyViewportBtn.addEventListener("click", () => {
      const w = parseInt(vwInput.value, 10) || viewport.clientWidth;
      const h = parseInt(vhInput.value, 10) || viewport.clientHeight;
      viewport.style.width = `${w}px`;
      viewport.style.height = `${h}px`;
      if (typeof layoutPreserveCenter === "function") {
        layoutPreserveCenter();
      }
    });
  }
}

// Wait for DOM ready so that viewport.js and simulationApi.js are loaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
