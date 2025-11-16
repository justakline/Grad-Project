// settingsPanel.js - settings UI, sliders, and settings collection

// Open or close the settings panel
if (toggleSettingsBtn && settingsPanel) {
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
      // do not readd "hidden" here so animation still works
    }
  });
}

// Percent helper
function pctInt(v) {
  v = Number(v);
  if (!Number.isFinite(v)) v = 0;
  if (v < 0) v = 0;
  if (v > 100) v = 100;
  return Math.round(v);
}

/* ------------ Driver Behavior: Aggressive vs Defensive = 100 ------------ */

function setAggressivePercent(aggr) {
  aggr = pctInt(aggr);
  const def = 100 - aggr;

  if (aggressiveInput) aggressiveInput.value = aggr;
  if (defensiveInput) defensiveInput.value = def;
  if (driverMix) driverMix.value = aggr;
  if (driverMixValue) {
    driverMixValue.textContent = `${aggr}% Aggressive / ${def}% Defensive`;
  }
}

function bindDriverBehavior() {
  // If nothing exists, skip silently
  if (!driverMix && !aggressiveInput) return;

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

/* ------------ Vehicle Mix Ratios (independent) ------------ */

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
  ) {
    return;
  }

  const t = nonNeg(truckRatio.value);
  const sVal = nonNeg(suvRatio.value);
  const m = nonNeg(motorcycleRatio.value);
  const total = t + sVal + m;

  let pt = 0;
  let ps = 0;
  let pm = 0;
  if (total > 0) {
    pt = Math.round((t / total) * 100);
    ps = Math.round((sVal / total) * 100);
    pm = 100 - pt - ps; // exact sum
  }

  vehicleRatioRaw.textContent = `Truck ${t} : SUV ${sVal} : Motorcycle ${m} `;
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

/* ------------ Init bindings ------------ */

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

/* ------------ Collect settings for backend ------------ */

function setSettings() {
  settings.dt = parseInt(document.getElementById("dtInput").value, 10);

  // Aggressive percent from linked control
  if (aggressiveInput) {
    settings.aggressivePct = parseInt(aggressiveInput.value, 10);
  }

  // Store raw ratios so backend can decide how to sample
  if (truckRatio && suvRatio && motorcycleRatio) {
    settings.suv_ratio = nonNeg(suvRatio.value);
    settings.truckRatio = nonNeg(truckRatio.value);
    settings.motorcycle_ratio = nonNeg(motorcycleRatio.value);
  }

  settings.agentRate = parseInt(document.getElementById("agentRate").value, 10);
  settings.nAgents = parseInt(document.getElementById("numAgents").value, 10);
  settings.highwayLength =
    parseInt(document.getElementById("highwayLength").value, 10) * 1000; // m to mm
  settings.laneNumber = parseInt(
    document.getElementById("laneNumber").value,
    10
  );
  settings.laneSize =
    parseFloat(document.getElementById("laneSize").value) * 1000; // m to mm
  settings.isLogging = document.getElementById("isLogging").checked;
  settings.logDt = parseInt(document.getElementById("logDt").value, 10);

  // Close the card
  if (settingsPanel) {
    settingsPanel.classList.remove("active");
  }
}
