"""Estilo de matplotlib que coincide con el mazo (colores, tipografía, grilla).

Uso típico, en un script figuras/generar.py:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    import estilo_graficos as eg
    import numpy as np

    eg.aplicar()
    d = np.genfromtxt("datos.dat", names=True)
    fig, ax = eg.figura(8.6, 5.2)             # pulgadas; 1 in = 100 px del lienzo
    ax.plot(d["x"], d["a"], color=eg.AZUL, label="Caso A")
    ax.plot(d["x"], d["b"], color=eg.NARANJA, label="Caso B")
    ax.set_xlabel("x [V]"); ax.set_ylabel("y [mV]")
    eg.coma(ax)                                # coma decimal en los ejes
    ax.legend()
    eg.guardar(fig, "figuras/nombre.svg")

Las figuras se guardan en SVG con el texto convertido a trazos, así se ven
igual en cualquier máquina. Tamaño: pensar en px del lienzo de 1920x1080
(una figura de 8.6 x 5.2 in ocupa 860 x 520 px a tamaño natural).
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker

AQUI = pathlib.Path(__file__).resolve().parent

MARINO = "#13213a"
CREMA = "#f6f4ef"
TARJETA = "#fffdf9"
LINEA = "#dcd6ca"
CUERPO = "#3d4a5c"
TENUE = "#5e6675"
AZUL = "#1f5fbf"
NARANJA = "#d9640f"
VERDE = "#0b6b5d"
GRIS = "#8a8f98"          # curvas de referencia ("sin compensar", límites)
AZUL_CLARO = "#6a8dcc"    # sobre fondo marino
NARANJA_CLARO = "#f08a3c"


def aplicar(fondo=CREMA):
    """Registra las tipografías del mazo y fija los rcParams. fondo=TARJETA
    si la figura va dentro de un <figure class="marco">."""
    for ttf in (AQUI / "assets" / "fonts").glob("IBMPlex*.ttf"):
        font_manager.fontManager.addfont(str(ttf))
    plt.rcParams.update({
        "font.family": "IBM Plex Sans",
        "font.size": 15,
        "axes.labelsize": 16,
        "axes.titlesize": 16,
        "xtick.labelsize": 14.5,
        "ytick.labelsize": 14.5,
        "legend.fontsize": 14,
        "text.color": MARINO,
        "axes.labelcolor": MARINO,
        "axes.edgecolor": CUERPO,
        "axes.linewidth": 1.1,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": fondo,
        "figure.facecolor": fondo,
        "savefig.facecolor": fondo,
        "xtick.color": CUERPO,
        "ytick.color": CUERPO,
        "axes.grid": True,
        "axes.grid.which": "both",
        "grid.color": "#e4dfd5",
        "grid.linewidth": 0.8,
        "lines.linewidth": 2.6,
        "lines.solid_capstyle": "round",
        "legend.frameon": True,
        "legend.facecolor": TARJETA,
        "legend.edgecolor": LINEA,
        "legend.framealpha": 1.0,
        "legend.fancybox": False,
        "axes.prop_cycle": matplotlib.cycler(color=[AZUL, NARANJA, MARINO, VERDE, GRIS]),
        "svg.fonttype": "path",
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "mathtext.fontset": "cm",
        "axes.unicode_minus": True,
    })


def figura(ancho=8.6, alto=5.2, **kw):
    """fig, ax con layout ajustado. Acepta nrows/ncols/sharex/etc. de subplots."""
    kw.setdefault("constrained_layout", True)
    return plt.subplots(figsize=(ancho, alto), **kw)


def _fmt_coma(decimales=None):
    def f(x, _pos):
        s = f"{x:.{decimales}f}" if decimales is not None else f"{x:g}"
        return s.replace("-", "−").replace(".", ",")
    return ticker.FuncFormatter(f)


def coma(ax, eje="ambos", decimales=None):
    """Pone coma decimal (y signo menos tipográfico) en los ejes lineales."""
    if eje in ("x", "ambos") and ax.get_xscale() == "linear":
        ax.xaxis.set_major_formatter(_fmt_coma(decimales))
    if eje in ("y", "ambos") and ax.get_yscale() == "linear":
        ax.yaxis.set_major_formatter(_fmt_coma(decimales))


def log_plano(ax, eje="x"):
    """Eje logarítmico con números planos (10, 100, 1000) en vez de 10^n."""
    def f(x, _pos):
        if x >= 10000:
            return f"{x:,.0f}".replace(",", " ")
        return f"{x:g}".replace(".", ",")
    fmt = ticker.FuncFormatter(f)
    (ax.xaxis if eje == "x" else ax.yaxis).set_major_formatter(fmt)
    ax.grid(True, which="minor", color="#ece8df", linewidth=0.6)


def anotar(ax, texto, xy, xytext, color=MARINO, **kw):
    """Rótulo con línea fina hacia el punto (como en los Bode de la referencia)."""
    return ax.annotate(texto, xy=xy, xytext=xytext, color=color, fontsize=kw.pop("fontsize", 14.5),
                       arrowprops=dict(arrowstyle="-", color=color, linewidth=1.0), **kw)


def guardar(fig, ruta):
    ruta = pathlib.Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta)
    plt.close(fig)
    print("figura ->", ruta)
