/* Dibuja el árbol sintáctico ({etiqueta, hijos}) como SVG. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const ALTO_NIVEL = 56, ANCHO_HOJA = 92;

  function medir(n) {
    n.hojas = n.hijos.length ? n.hijos.reduce((s, h) => s + medir(h), 0) : 1;
    return n.hojas;
  }
  function colocar(n, izq, nivel) {
    n.x = (izq + n.hojas / 2) * ANCHO_HOJA;
    n.y = nivel * ALTO_NIVEL + 24;
    let cursor = izq;
    n.hijos.forEach(h => { colocar(h, cursor, nivel + 1); cursor += h.hojas; });
  }
  function profundidad(n) { return 1 + Math.max(0, ...n.hijos.map(profundidad)); }

  window.dibujarArbol = function (contenedor, raiz) {
    contenedor.textContent = "";
    if (!raiz) {
      contenedor.innerHTML = '<p class="vacio">Compila un programa sin errores léxicos ni sintácticos para ver su árbol.</p>';
      return;
    }
    medir(raiz); colocar(raiz, 0, 0);
    const w = raiz.hojas * ANCHO_HOJA + 20, h = profundidad(raiz) * ALTO_NIVEL + 20;
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("width", w); svg.setAttribute("height", h);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    (function pintar(n) {
      n.hijos.forEach(c => {
        const p = document.createElementNS(NS, "path");
        const my = (n.y + c.y) / 2;
        p.setAttribute("d", `M ${n.x} ${n.y + 11} C ${n.x} ${my}, ${c.x} ${my}, ${c.x} ${c.y - 11}`);
        svg.appendChild(p);
        pintar(c);
      });
    })(raiz);
    (function nodos(n) {
      const g = document.createElementNS(NS, "g");
      if (!n.hijos.length) g.setAttribute("class", "hoja");
      const txt = n.etiqueta.length > 15 ? n.etiqueta.slice(0, 14) + "…" : n.etiqueta;
      const ancho = Math.max(34, txt.length * 6.6 + 14);
      const r = document.createElementNS(NS, "rect");
      r.setAttribute("x", n.x - ancho / 2); r.setAttribute("y", n.y - 11);
      r.setAttribute("width", ancho); r.setAttribute("height", 22); r.setAttribute("rx", 7);
      const t = document.createElementNS(NS, "text");
      t.setAttribute("x", n.x); t.setAttribute("y", n.y + 4); t.textContent = txt;
      const tit = document.createElementNS(NS, "title"); tit.textContent = n.etiqueta;
      g.append(r, t, tit); svg.appendChild(g);
      n.hijos.forEach(nodos);
    })(raiz);
    contenedor.appendChild(svg);
    contenedor.scrollLeft = (contenedor.scrollWidth - contenedor.clientWidth) / 2;
  };
})();
