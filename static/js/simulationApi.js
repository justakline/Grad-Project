// simulationApi.js - backend interaction and simulation loop

let pollingMs = 50;

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
    const res = await fetch(`/api/init?${params.toString()}`);
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

function startSimulation() {
  if (isRunning) return;
  runId += 1;
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

  if (stepAbortController) {
    stepAbortController.abort();
  }
  const controller = new AbortController();
  stepAbortController = controller;

  const myRunId = runId;
  try {
    const res = await fetch("/api/step", { signal: controller.signal });
    if (!isRunning || myRunId !== runId) return;
    const data = await res.json();
    if (data.status === "success") {
      lastAgents = data.agents;
      redraw();
      stepCountSpan.textContent = data.step;
      agentCountSpan.textContent = data.agents.length;
      let aggData = "";
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
    if (stepAbortController === controller) {
      stepAbortController = null;
    }
  }
}
