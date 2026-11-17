#!/usr/bin/env python3
"""Compila un dibujo TikZ / circuitikz / pgfplots a SVG para usarlo en el mazo.

Uso:  python3 tex2svg.py figuras/circuito.tex [figuras/otro.tex ...]

Cada .tex contiene SOLO el cuerpo del dibujo (el \\begin{circuitikz} ...
\\end{circuitikz} o \\begin{tikzpicture} ...), sin preámbulo. El script lo
envuelve en un documento standalone con los colores del mazo ya definidos:

    marino, crema, tarjeta, cuerpo, tenue, azul, naranja, verde

y deja figuras/circuito.svg (fondo transparente, texto convertido a trazos).
Si el .tex ya trae \\documentclass se compila tal cual.

Convención de la referencia: símbolos y cables en `marino`, valores de los
componentes en el color de la serie a la que pertenecen (azul o naranja),
por ejemplo  to[R, l=$R_d$, a={\\color{azul}9{,}1\\,k$\\Omega$}].
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

PREAMBULO = r"""\documentclass[border=4pt]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{siunitx}
\sisetup{output-decimal-marker={,}, group-digits=none, per-mode=symbol}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{fillbetween,groupplots}
\usepackage[siunitx,RPvoltages]{circuitikz}
\usetikzlibrary{calc,arrows.meta,positioning,shapes.geometric,plotmarks}
\definecolor{marino}{HTML}{13213A}
\definecolor{crema}{HTML}{F6F4EF}
\definecolor{tarjeta}{HTML}{FFFDF9}
\definecolor{cuerpo}{HTML}{3D4A5C}
\definecolor{tenue}{HTML}{5E6675}
\definecolor{azul}{HTML}{1F5FBF}
\definecolor{naranja}{HTML}{D9640F}
\definecolor{verde}{HTML}{0B6B5D}
\ctikzset{bipoles/thickness=1.4}
\tikzset{every picture/.append style={color=marino, line width=0.9pt}}
\begin{document}
%CUERPO%
\end{document}
"""


def compilar(tex: pathlib.Path) -> bool:
    fuente = tex.read_text(encoding="utf-8")
    doc = fuente if r"\documentclass" in fuente else PREAMBULO.replace("%CUERPO%", fuente)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "f.tex").write_text(doc, encoding="utf-8")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "f.tex"],
                           cwd=tmp, capture_output=True, text=True, errors="replace",
                           env=None)
        if r.returncode != 0 or not (tmp / "f.pdf").exists():
            lineas = [l for l in r.stdout.splitlines() if l.startswith("!") or l.startswith("l.")]
            print(f"ERROR en {tex}:\n  " + "\n  ".join(lineas[:12] or r.stdout.splitlines()[-15:]))
            return False
        svg = tex.with_suffix(".svg")
        subprocess.run(["pdftocairo", "-svg", "f.pdf", "f.svg"], cwd=tmp, check=True)
        shutil.copy(tmp / "f.svg", svg)
        print("figura ->", svg)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ok = all([compilar(pathlib.Path(a).resolve()) for a in sys.argv[1:]])
    sys.exit(0 if ok else 1)
