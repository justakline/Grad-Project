// viewport.js - layout, transforms, zoom and pan

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
