/* Controlador de la interfaz: solo llama a la API y pinta; no contiene reglas de negocio. */
(function () {
  const $ = id => document.getElementById(id);
  const fuente = $("fuente"), numeros = $("numeros"), estado = $("estado"), btn = $("btnCompilar");
  const soles = n => "S/ " + Number(n).toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  /* ---------- editor ---------- */
  function actualizarNumeros() {
    const n = fuente.value.split("\n").length;
    numeros.textContent = Array.from({ length: n }, (_, i) => i + 1).join("\n");
    numeros.scrollTop = fuente.scrollTop;
  }
  fuente.addEventListener("input", actualizarNumeros);
  fuente.addEventListener("scroll", () => (numeros.scrollTop = fuente.scrollTop));
  fuente.addEventListener("keydown", e => {
    if (e.key === "Tab") {
      e.preventDefault();
      const s = fuente.selectionStart;
      fuente.setRangeText("    ", s, fuente.selectionEnd, "end");
      actualizarNumeros();
    }
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") compilar();
  });

  function saltarALinea(linea, columna) {
    const lineas = fuente.value.split("\n");
    let pos = 0;
    for (let i = 0; i < linea - 1 && i < lineas.length; i++) pos += lineas[i].length + 1;
    const fin = pos + (lineas[linea - 1] || "").length;
    fuente.focus();
    fuente.setSelectionRange(pos + Math.max(0, columna - 1), fin);
    fuente.scrollTop = Math.max(0, (linea - 4) * 20);
  }

  /* ---------- pestañas ---------- */
  function irA(tab) {
    document.querySelectorAll(".pestanas button").forEach(b => b.classList.toggle("activa", b.dataset.tab === tab));
    document.querySelectorAll(".vista").forEach(v => v.classList.toggle("activa", v.id === "vista-" + tab));
  }
  document.querySelectorAll(".pestanas button").forEach(b => b.addEventListener("click", () => irA(b.dataset.tab)));

  /* ---------- pintar resultados ---------- */
  function pintarResultados(lista) {
    const cont = $("vista-resultados");
    if (!lista.length) {
      cont.innerHTML = '<p class="vacio">Sin evaluaciones todavía.<br>Compila un programa con sentencias <b>evaluar</b>.</p>';
      return;
    }
    cont.innerHTML = lista.map((r, i) => {
      const ok = r.decision === "APROBADO";
      const reglas = r.reglas.map(x =>
        `<li><span class="${x.cumple ? "si" : "no"}">${x.cumple ? "✔" : "✘"}</span>
           <span>${esc(x.regla)} <small style="color:var(--tenue)">(${x.izquierda} vs ${x.derecha})</small></span></li>`).join("");
      const motivos = r.motivos.length
        ? `<p style="color:var(--mal);font-size:.8rem;margin:6px 0">${r.motivos.map(esc).join("<br>")}</p>` : "";
      const cron = r.cronograma.length ? `
        <details><summary>Cronograma de pagos (${r.cronograma.length} cuotas)</summary>
        <table><thead><tr><th>N°</th><th>Cuota</th><th>Interés</th><th>Capital</th><th>Saldo</th></tr></thead><tbody>
        ${r.cronograma.map(f => `<tr><td>${f.n}</td><td>${f.cuota.toFixed(2)}</td><td>${f.interes.toFixed(2)}</td>
          <td>${f.capital.toFixed(2)}</td><td>${f.saldo.toFixed(2)}</td></tr>`).join("")}
        </tbody></table></details>` : "";
      return `<article class="tarjeta" style="animation-delay:${i * 90}ms">
        <header><h4>${esc(r.solicitud)}</h4><span class="cli">${esc(r.cliente)} · política ${esc(r.politica)}</span>
        <span class="sello ${ok ? "ok" : "mal"}">${r.decision}</span></header>
        <div class="metricas">
          <div><small>Monto</small><strong>${soles(r.monto)}</strong></div>
          <div><small>Plazo</small><strong>${r.plazo} m</strong></div>
          <div><small>Cuota</small><strong>${soles(r.cuota)}</strong></div>
          <div><small>Endeudamiento</small><strong>${(r.endeudamiento * 100).toFixed(1)}%</strong></div>
          ${ok ? `<div><small>Intereses</small><strong>${soles(r.total_intereses)}</strong></div>` : ""}
        </div>
        <ul class="reglas">${reglas}</ul>${motivos}${cron}</article>`;
    }).join("");
  }

  function pintarErrores(errores, avisos) {
    const todos = errores.concat(avisos);
    const cont = $("vista-errores"), em = $("contErr");
    em.textContent = todos.length;
    em.classList.toggle("hay", errores.length > 0);
    if (!todos.length) {
      cont.innerHTML = '<p class="vacio">Sin errores ni advertencias ✔</p>';
      return;
    }
    cont.innerHTML = todos.map((e, i) => `
      <div class="error-item ${e.gravedad}" data-l="${e.linea}" data-c="${e.columna}" style="animation-delay:${i * 60}ms">
        <code>${esc(e.codigo)}</code>
        <div>${esc(e.mensaje)}<small>${esc(e.etapa)}${e.linea ? " · línea " + e.linea + ":" + e.columna : ""}</small></div>
      </div>`).join("");
    cont.querySelectorAll(".error-item").forEach(d =>
      d.addEventListener("click", () => d.dataset.l > 0 && saltarALinea(+d.dataset.l, +d.dataset.c)));
  }

  function pintarTokens(tokens) {
    $("vista-tokens").innerHTML = tokens.length
      ? `<div class="tokens">${tokens.map(t => `<span class="token"><b>${esc(t.tipo)}</b>${esc(t.valor)}</span>`).join("")}</div>`
      : '<p class="vacio">Sin tokens.</p>';
  }

  /* ---------- compilar ---------- */
  async function compilar() {
    btn.classList.add("cargando");
    estado.textContent = "Compilando…";
    try {
      const resp = await fetch("/api/compilar", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fuente: fuente.value }),
      });
      const r = await resp.json();
      window.marcarEtapas(r.etapas);
      pintarResultados(r.resultados || []);
      pintarErrores(r.errores || [], r.advertencias || []);
      pintarTokens(r.tokens || []);
      window.dibujarArbol($("vista-arbol"), r.arbol);
      $("codigoPy").textContent = r.codigo_python || "# El código Python se genera cuando el programa no tiene errores.";
      if (r.ok) { estado.textContent = `✔ Compilado: ${r.resultados.length} evaluación(es).`; irA("resultados"); }
      else { estado.textContent = `✘ ${r.errores.length} error(es) encontrados.`; irA("errores"); }
    } catch (e) {
      estado.textContent = "No se pudo conectar con el backend (¿está corriendo app.py?).";
    } finally {
      btn.classList.remove("cargando");
    }
  }
  btn.addEventListener("click", compilar);

  /* ---------- ejemplos y gramática ---------- */
  async function cargarEjemplo(nombre) {
    const r = await (await fetch("/api/ejemplos/" + nombre)).json();
    fuente.value = r.fuente;
    actualizarNumeros();
  }
  async function iniciar() {
    const lista = await (await fetch("/api/ejemplos")).json();
    const sel = $("ejemplos");
    sel.innerHTML = lista.map(n => `<option>${esc(n)}</option>`).join("");
    sel.addEventListener("change", () => cargarEjemplo(sel.value));
    if (lista.length) { sel.value = lista.includes("credito_pyme") ? "credito_pyme" : lista[0]; await cargarEjemplo(sel.value); }
    compilar();
  }
  $("btnGramatica").addEventListener("click", async () => {
    $("txtGramatica").textContent = (await (await fetch("/api/gramatica")).json()).gramatica;
    $("dlgGramatica").showModal();
  });
  pintarErrores([], []);
  iniciar().catch(() => (estado.textContent = "Inicia el backend: python backend/app.py"));
})();
