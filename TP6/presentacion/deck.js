/* Comportamiento del mazo: pie automático, fórmulas KaTeX y navegación.
   - Pie izquierdo: atributo data-pie del <body>.
   - Pie derecho: "Expone: <data-expone> · NN". data-expone se hereda de la
     diapositiva anterior si no se repite. En las de respaldo se usa
     "Respaldo para preguntas". Con data-sin-pie no se dibuja pie.
   - Teclas: flechas / espacio / Re Pág / Av Pág, Inicio, Fin, F (pantalla completa).
   - ?todas en la URL (o impresión) muestra todas las diapositivas apiladas.   */
(function () {
  const slides = Array.from(document.querySelectorAll(".slide"));
  const pieIzq = document.body.dataset.pie || "";
  let expone = "";
  slides.forEach((s, i) => {
    if (s.dataset.expone) expone = s.dataset.expone;
    if (s.hasAttribute("data-sin-pie")) return;
    const n = String(i + 1).padStart(2, "0");
    const der = s.classList.contains("respaldo")
      ? "Respaldo para preguntas"
      : (expone ? "Expone: " + expone : "");
    const pie = document.createElement("div");
    pie.className = "pie";
    pie.innerHTML = "<span>" + pieIzq + "</span><span>" + der + (der ? " · " : "") + "<b>" + n + "</b></span>";
    s.appendChild(pie);
  });

  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
      throwOnError: false,
    });
  }

  const todas = new URLSearchParams(location.search).has("todas");
  if (todas) document.body.classList.add("todas");

  let actual = 0;
  function escalar() {
    const k = Math.min(innerWidth / 1920, innerHeight / 1080);
    slides.forEach((s) => (s.style.transform = "translate(-50%, -50%) scale(" + k + ")"));
  }
  function ir(n) {
    actual = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, i) => s.classList.toggle("activa", i === actual));
    history.replaceState(null, "", "#" + (actual + 1));
  }
  if (!todas) {
    escalar();
    addEventListener("resize", escalar);
    ir((parseInt(location.hash.slice(1), 10) || 1) - 1);
    addEventListener("keydown", (e) => {
      if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(e.key)) { ir(actual + 1); e.preventDefault(); }
      else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(e.key)) { ir(actual - 1); e.preventDefault(); }
      else if (e.key === "Home") ir(0);
      else if (e.key === "End") ir(slides.length - 1);
      else if (e.key === "f" || e.key === "F") document.documentElement.requestFullscreen();
    });
    addEventListener("click", (e) => { if (e.clientX > innerWidth / 2) ir(actual + 1); else ir(actual - 1); });
  }
})();
