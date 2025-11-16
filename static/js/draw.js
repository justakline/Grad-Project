// drawing.js - drawing logic

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

  ctx.fillStyle = "#222";
  ctx.fillRect(R.x0, R.y0, R.w, R.h);

  if (!laneWidth || !laneCenters || laneCenters.length === 0) {
    drawHighwayBorders();
    return;
  }

  const half = laneWidth / 2;
  const centers = laneCenters.slice().sort((a, b) => a - b);
  const laneBands = centers.map((c) => [
    Math.max(0, c - half),
    Math.min(maxX, c + half),
  ]);

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

  let edgesX = edgesWorld.map((x) => worldToScreen(x, 0)[0]);
  const R2 = getHighwayRect();
  edgesX[0] = R2.x0;
  edgesX[edgesX.length - 1] = R2.x1;
  for (let i = 1; i < edgesX.length - 1; i++) edgesX[i] = Math.round(edgesX[i]);

  const overlapsLane = (a, b) => {
    for (const [L, Rw] of laneBands) {
      const overlap = Math.min(b, Rw) - Math.max(a, L);
      if (overlap > 0) return true;
    }
    return false;
  };

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

    const color =
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
