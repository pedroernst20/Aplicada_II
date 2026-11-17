#!/usr/bin/env python3
"""Exporta el mazo HTML a PDF y lo revisa.

Uso:  python3 exportar.py [deck.html] [-o salida.pdf] [--sin-png]

Genera:
  - <salida>.pdf            PDF vectorial, una página de 1920x1080 px por diapositiva
  - _revision/NN.png        captura de cada diapositiva (para mirarlas con Read)
  - _revision/hoja_N.png    hojas de contacto de 12 diapositivas
Y controla, diapositiva por diapositiva:
  - contenido que se sale del lienzo o pisa el pie
  - texto cortado dentro de su caja (overflow)
  - imágenes que no cargaron y fórmulas KaTeX con error
Termina con código 1 si encontró problemas.

Necesita playwright (python) y un Chromium del sistema.
"""
import argparse
import pathlib
import shutil
import sys

from playwright.sync_api import sync_playwright

CONTROL_JS = r"""
() => {
  const problemas = [];
  const slides = Array.from(document.querySelectorAll('.slide'));
  slides.forEach((s, i) => {
    const n = i + 1;
    const sr = s.getBoundingClientRect();
    const pie = s.querySelector('.pie');
    const limite = pie ? pie.getBoundingClientRect().top : sr.bottom;
    const vistos = new Set();
    s.querySelectorAll('*').forEach((el) => {
      if (el.closest('.pie') || el.closest('.katex') || el.closest('svg') && el.tagName !== 'svg') return;
      if (el.classList.contains('fondo') || el.closest('.fondo')) return;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;
      const nombre = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
      const txt = (el.textContent || '').trim().slice(0, 40);
      const clave = nombre + '|' + txt;
      if (r.right > sr.right - 60 + 1 || r.left < sr.left + 60 - 1 || r.top < sr.top - 1) {
        if (!vistos.has('m' + clave)) { vistos.add('m' + clave); problemas.push(`dia ${n}: <${nombre}> invade el margen lateral/superior ("${txt}")`); }
      }
      const fijo = getComputedStyle(el).position === 'absolute';
      if (!fijo && r.bottom > limite + 1 && el.children.length === 0) {
        if (!vistos.has('p' + clave)) { vistos.add('p' + clave); problemas.push(`dia ${n}: <${nombre}> pisa el pie o se sale por abajo (${Math.round(r.bottom - limite)} px) ("${txt}")`); }
      }
      if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflowX !== 'visible' && el !== s) {
        problemas.push(`dia ${n}: <${nombre}> tiene contenido cortado a lo ancho ("${txt}")`);
      }
    });
    s.querySelectorAll('img').forEach((img) => {
      if (!img.complete || img.naturalWidth === 0) problemas.push(`dia ${n}: no cargó la imagen ${img.getAttribute('src')}`);
    });
    s.querySelectorAll('.katex-error').forEach((e) => problemas.push(`dia ${n}: fórmula con error: ${e.textContent.slice(0, 60)}`));
    if (/\$[^$]+\$/.test(s.innerText)) problemas.push(`dia ${n}: quedó una fórmula sin renderizar (signos $ visibles)`);
  });
  return { cantidad: slides.length, problemas };
}
"""


def chromium():
    for nombre in ("chromium", "chromium-browser", "google-chrome-stable", "google-chrome"):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", nargs="?", default="deck.html")
    ap.add_argument("-o", "--salida", default=None)
    ap.add_argument("--sin-png", action="store_true", help="no generar capturas ni hojas de contacto")
    a = ap.parse_args()

    html = pathlib.Path(a.html).resolve()
    if not html.exists():
        sys.exit(f"No existe {html}")
    salida = pathlib.Path(a.salida).resolve() if a.salida else html.with_suffix(".pdf")
    rev = html.parent / "_revision"

    with sync_playwright() as p:
        exe = chromium()
        nav = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1920, "height": 1080})
        errores_consola = []
        pag.on("pageerror", lambda e: errores_consola.append(str(e)))
        pag.on("requestfailed", lambda r: errores_consola.append("no cargó " + r.url))
        pag.goto(html.as_uri() + "?todas")
        pag.wait_for_load_state("networkidle")
        pag.evaluate("document.fonts.ready")
        pag.wait_for_timeout(300)

        res = pag.evaluate(CONTROL_JS)
        n = res["cantidad"]

        pag.emulate_media(media="print")
        pag.pdf(path=str(salida), width="1920px", height="1080px", print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}, prefer_css_page_size=True)
        pag.emulate_media(media="screen")

        if not a.sin_png:
            if rev.exists():
                shutil.rmtree(rev)
            rev.mkdir()
            for i, s in enumerate(pag.query_selector_all(".slide"), 1):
                s.screenshot(path=str(rev / f"{i:02d}.png"))
        nav.close()

    if not a.sin_png:
        try:
            from PIL import Image
            archivos = sorted(rev.glob("[0-9][0-9].png"))
            for h in range(0, len(archivos), 12):
                grupo = archivos[h:h + 12]
                w, hh, m = 800, 450, 8
                filas = (len(grupo) + 2) // 3
                hoja = Image.new("RGB", (3 * w + 4 * m, filas * hh + (filas + 1) * m), "#888888")
                for k, f in enumerate(grupo):
                    im = Image.open(f).resize((w, hh), Image.LANCZOS)
                    hoja.paste(im, (m + (k % 3) * (w + m), m + (k // 3) * (hh + m)))
                hoja.save(rev / f"hoja_{h // 12 + 1}.png")
        except ImportError:
            print("(sin Pillow: no se generan hojas de contacto)")

    print(f"{n} diapositivas -> {salida}")
    if not a.sin_png:
        print(f"capturas en {rev}/ (NN.png y hoja_N.png)")
    problemas = res["problemas"] + errores_consola
    if problemas:
        print(f"\n{len(problemas)} PROBLEMA(S):")
        for x in problemas:
            print("  -", x)
        sys.exit(1)
    print("control automático: sin problemas (igual hay que mirar las capturas)")


if __name__ == "__main__":
    main()
