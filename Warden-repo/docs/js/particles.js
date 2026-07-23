/**
 * particles.js — ambient embers drifting upward through the page.
 * Lightweight canvas loop; pauses entirely for prefers-reduced-motion
 * and when the tab isn't visible, to keep this cheap.
 */
(function () {
  const canvas = document.getElementById("ember-canvas");
  if (!canvas) return;

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;
  if (prefersReducedMotion) {
    canvas.remove();
    return;
  }

  const ctx = canvas.getContext("2d");
  let width, height, dpr;
  let embers = [];
  let running = true;
  let rafId = null;

  const COLORS = ["#C9A24B", "#E9C46A", "#B5232F"];

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const density = width < 720 ? 26 : 55;
    embers = Array.from({ length: density }, spawnEmber);
  }

  function spawnEmber(existing) {
    const e = existing || {};
    e.x = Math.random() * width;
    e.y = height + Math.random() * 100;
    e.r = 0.6 + Math.random() * 1.8;
    e.speed = 0.15 + Math.random() * 0.45;
    e.drift = (Math.random() - 0.5) * 0.4;
    e.alpha = 0.15 + Math.random() * 0.5;
    e.color = COLORS[Math.floor(Math.random() * COLORS.length)];
    e.flicker = Math.random() * Math.PI * 2;
    return e;
  }

  function tick() {
    if (!running) return;
    ctx.clearRect(0, 0, width, height);

    for (const e of embers) {
      e.y -= e.speed;
      e.x += e.drift;
      e.flicker += 0.05;

      if (e.y < -20) spawnEmber(e);

      const flicker = 0.6 + Math.sin(e.flicker) * 0.4;
      ctx.beginPath();
      ctx.arc(e.x, e.y, e.r, 0, Math.PI * 2);
      ctx.fillStyle = e.color;
      ctx.globalAlpha = e.alpha * flicker;
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    rafId = requestAnimationFrame(tick);
  }

  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) {
      rafId = requestAnimationFrame(tick);
    } else if (rafId) {
      cancelAnimationFrame(rafId);
    }
  });

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 150);
  });

  resize();
  rafId = requestAnimationFrame(tick);
})();
