/* Partículas conectadas que reaccionan al cursor + blob "líquido" que cambia de forma. */
(function () {
  const lienzo = document.getElementById("particulas");
  const ctx = lienzo.getContext("2d");
  let ancho, alto, puntos = [];
  const raton = { x: -999, y: -999 };
  const colores = ["76,201,240", "123,97,255", "255,122,182"];

  function medir() {
    const d = window.devicePixelRatio || 1;
    ancho = lienzo.width = innerWidth * d;
    alto = lienzo.height = innerHeight * d;
    lienzo.style.width = innerWidth + "px";
    lienzo.style.height = innerHeight + "px";
    const n = Math.min(90, Math.floor(innerWidth / 16));
    puntos = Array.from({ length: n }, () => ({
      x: Math.random() * ancho, y: Math.random() * alto,
      vx: (Math.random() - .5) * .35 * d, vy: (Math.random() - .5) * .35 * d,
      r: (Math.random() * 1.6 + .6) * d, c: colores[(Math.random() * 3) | 0],
    }));
  }
  addEventListener("resize", medir);
  addEventListener("pointermove", e => {
    const d = window.devicePixelRatio || 1;
    raton.x = e.clientX * d; raton.y = e.clientY * d;
  });

  function dibujar() {
    ctx.clearRect(0, 0, ancho, alto);
    const d = window.devicePixelRatio || 1, radio = 140 * d;
    for (let i = 0; i < puntos.length; i++) {
      const p = puntos[i];
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > ancho) p.vx *= -1;
      if (p.y < 0 || p.y > alto) p.vy *= -1;
      const dx = p.x - raton.x, dy = p.y - raton.y, dist = Math.hypot(dx, dy);
      if (dist < radio) { p.x += dx / dist * 1.2; p.y += dy / dist * 1.2; }
      ctx.fillStyle = `rgba(${p.c},.8)`;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
      for (let j = i + 1; j < puntos.length; j++) {
        const q = puntos[j], l = Math.hypot(p.x - q.x, p.y - q.y);
        if (l < 110 * d) {
          ctx.strokeStyle = `rgba(${p.c},${(1 - l / (110 * d)) * .28})`;
          ctx.lineWidth = d * .7;
          ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
        }
      }
    }
    requestAnimationFrame(dibujar);
  }
  medir(); dibujar();

  /* ---- blob líquido: 8 puntos con ruido suave unidos con curvas ---- */
  const path = document.getElementById("blobPath");
  const N = 8, fases = Array.from({ length: N }, () => Math.random() * 6.28);
  function blob(t) {
    const pts = fases.map((f, i) => {
      const a = (i / N) * 6.283;
      const r = 120 + 34 * Math.sin(t * .0008 + f) + 16 * Math.sin(t * .0017 + f * 2);
      return [Math.cos(a) * r, Math.sin(a) * r];
    });
    // Catmull-Rom cerrado -> Bézier
    let d = `M ${pts[0][0]} ${pts[0][1]}`;
    for (let i = 0; i < N; i++) {
      const p0 = pts[(i - 1 + N) % N], p1 = pts[i], p2 = pts[(i + 1) % N], p3 = pts[(i + 2) % N];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C ${c1[0]} ${c1[1]}, ${c2[0]} ${c2[1]}, ${p2[0]} ${p2[1]}`;
    }
    path.setAttribute("d", d + " Z");
    requestAnimationFrame(blob);
  }
  requestAnimationFrame(blob);
})();
