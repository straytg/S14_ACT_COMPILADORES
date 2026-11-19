/* Tipografía ASCII cinética + pipeline isométrico de las 4 etapas. */
(function () {
  const ARTE = [
    " ██████╗██████╗ ███████╗██████╗ ██╗██╗  ██╗",
    "██╔════╝██╔══██╗██╔════╝██╔══██╗██║╚██╗██╔╝",
    "██║     ██████╔╝█████╗  ██║  ██║██║ ╚███╔╝ ",
    "██║     ██╔══██╗██╔══╝  ██║  ██║██║ ██╔██╗ ",
    "╚██████╗██║  ██║███████╗██████╔╝██║██╔╝ ██╗",
    " ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝",
  ];
  const RAMPA = " .:-=+*#%@";
  const pre = document.getElementById("ascii");
  const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let empuje = 0; // el cursor encima acelera la onda

  pre.addEventListener("pointerenter", () => (empuje = 1));
  pre.addEventListener("pointerleave", () => (empuje = 0));

  function cuadro(t) {
    const v = t * (.0016 + empuje * .004);
    pre.textContent = ARTE.map((fila, y) =>
      [...fila].map((c, x) => {
        if (c === " ") return c;
        const onda = Math.sin(v - x * .14 + y * .35);
        if (onda > -.82) return c;                       // letra formada
        const k = Math.floor(((onda + 1) / .18) * (RAMPA.length - 1));
        return RAMPA[Math.max(1, Math.min(RAMPA.length - 1, k))]; // se deshace en puntos
      }).join("")
    ).join("\n");
    if (!reducido) requestAnimationFrame(cuadro);
  }
  requestAnimationFrame(cuadro);

  /* ---------- pipeline isométrico ---------- */
  const NS = "http://www.w3.org/2000/svg";
  const iso = document.getElementById("iso");
  const ETAPAS = [
    { id: "lexico", n: "1", etq: "léxico", color: "#4cc9f0" },
    { id: "sintactico", n: "2", etq: "sintáctico", color: "#7b61ff" },
    { id: "semantico", n: "3", etq: "semántico", color: "#ff7ab6" },
    { id: "generacion", n: "4", etq: "generación", color: "#ffc857" },
  ];
  const A = 52, H = 36; // semiancho y alto del cubo
  const piezas = {};

  function el(tag, attrs, padre) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    (padre || iso).appendChild(e);
    return e;
  }

  // línea guía (flujo) entre cubos
  el("path", { d: "M 70 170 L 570 70", stroke: "rgba(120,180,255,.35)", "stroke-dasharray": "4 6", fill: "none" });

  ETAPAS.forEach((e, i) => {
    const cx = 86 + i * 156, cy = 150 - i * 32;
    const g = el("g", { transform: `translate(${cx} ${cy})` });
    const inner = el("g", { class: "pieza" }, g);
    // sombra
    el("ellipse", { cx: 0, cy: A * .55 + H * .55, rx: A * 1.05, ry: A * .38, fill: "rgba(0,0,0,.35)" }, inner);
    // cara izquierda, derecha y superior (proyección isométrica)
    el("polygon", { points: `${-A},0 0,${A * .58} 0,${A * .58 + H} ${-A},${H}`, fill: "rgba(255,255,255,.07)", stroke: e.color, "stroke-opacity": .6 }, inner);
    el("polygon", { points: `0,${A * .58} ${A},0 ${A},${H} 0,${A * .58 + H}`, fill: "rgba(255,255,255,.13)", stroke: e.color, "stroke-opacity": .6 }, inner);
    const sup = el("polygon", { class: "cara-sup", points: `0,${-A * .58} ${A},0 0,${A * .58} ${-A},0`, fill: "rgba(255,255,255,.18)", stroke: e.color }, inner);
    el("text", { class: "num", x: 0, y: 5 }, inner).textContent = e.n;
    el("text", { class: "etq", x: 0, y: A * .58 + H + 22 }, inner).textContent = e.etq;
    piezas[e.id] = { g: inner, sup, color: e.color };
  });

  window.marcarEtapas = function (etapas) {
    for (const id in piezas) {
      const estado = (etapas && etapas[id]) || "pendiente";
      const p = piezas[id];
      p.g.setAttribute("class", "pieza " + (estado === "ok" || estado === "error" ? estado : ""));
      p.sup.setAttribute("fill", estado === "ok" ? p.color : estado === "error" ? "#ff6b81" : "rgba(255,255,255,.18)");
      p.sup.style.filter = estado === "pendiente" ? "none" : `drop-shadow(0 0 10px ${estado === "error" ? "#ff6b81" : p.color})`;
    }
  };
  window.marcarEtapas(null);
})();
