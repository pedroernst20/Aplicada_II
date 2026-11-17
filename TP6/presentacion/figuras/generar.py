"""Genera todos los gráficos del mazo a partir de los datos del informe.

Uso (desde presentacion/):  python3 figuras/generar.py
Lee ../informe/datos/*.dat y resultados.json; escribe figuras/*.svg.
Color: azul = fuente con etapa prereguladora, naranja = LM7805 directo a la
primaria. Las magnitudes internas van en marino, gris o verde.
"""
import json
import pathlib
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
import estilo_graficos as eg  # noqa: E402

DATOS = AQUI.parent.parent / "informe" / "datos"
R = json.loads((DATOS / "resultados.json").read_text())


def dat(nombre):
    return np.genfromtxt(DATOS / f"{nombre}.dat", names=True)


def c(x, dec):
    """Número con coma decimal y signo menos tipográfico."""
    return f"{x:.{dec}f}".replace(".", ",").replace("-", "−")


VERDE_TINTE = "#e3f1ee"


# ------------------------------------------------------------------ portada
def portada():
    eg.aplicar()
    d = dat("linea")
    fig = plt.figure(figsize=(19.2, 2.9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    for y in (8, 12):
        ax.axhline(y, color="#5a6885", lw=1.5, ls=(0, (6, 6)))
    m = d["vp"] >= 0
    ax.plot(d["vp"][m], d["vp"][m], color=eg.NARANJA_CLARO, lw=4)
    v = np.clip(d["vireg"], 0, None)
    ax.plot(d["vp"], v, color=eg.AZUL_CLARO, lw=4)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 31)
    fig.savefig(AQUI / "portada_fondo.svg", transparent=True)
    plt.close(fig)
    print("figura ->", AQUI / "portada_fondo.svg")


# ---------------------------------------------------- ventana de 8 a 12 V
def _ventana(ax, filas):
    ax.add_patch(Rectangle((8, -0.6), 4, len(filas) + 0.2, color=VERDE_TINTE, zorder=0))
    for x in (8, 12):
        ax.axvline(x, color=eg.VERDE, lw=1.6, ls="--", zorder=1)
    ax.text(10, len(filas) - 0.45, "Ventana del LM7805: 8 a 12 V", color=eg.VERDE,
            ha="center", va="bottom", fontsize=15, fontweight="medium")
    ax.set_xlim(7.5, 12.5)
    ax.set_ylim(-0.6, len(filas) - 0.1)
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels([f[0] for f in reversed(filas)], fontsize=15.5)
    ax.tick_params(axis="y", length=0)
    ax.grid(False)
    ax.grid(True, axis="x", color="#e4dfd5")
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("$V_{i,\\mathrm{reg}}$ [V]")
    eg.coma(ax, "x", 1)


def ventana_calculo():
    eg.aplicar()
    fig, ax = eg.figura(10.8, 3.9)
    filas = [("1N4741A · 11 V", None), ("1N4740A · 10 V", None)]
    _ventana(ax, filas)
    y = 1
    ax.plot([8.85, 10.35], [y, y], color=eg.AZUL, lw=9, solid_capstyle="butt", alpha=0.35)
    ax.plot(9.6, y, "o", color=eg.AZUL, ms=13, zorder=5)
    ax.text(9.6, y + 0.28, "≈ 9,6 V", color=eg.AZUL, ha="center", fontsize=15)
    ax.text(8.85, y - 0.3, "8,85", color=eg.AZUL, ha="center", va="top", fontsize=14.5)
    ax.text(10.35, y - 0.3, "10,35", color=eg.AZUL, ha="center", va="top", fontsize=14.5)
    y = 0
    ax.plot(8.6, y, "o", color=eg.GRIS, ms=13, zorder=5)
    ax.text(8.6, y + 0.28, "≈ 8,6 V", color=eg.TENUE, ha="center", fontsize=15)
    eg.guardar(fig, AQUI / "ventana_calculo.svg")


def ventana_tolerancia():
    eg.aplicar()
    fig, ax = eg.figura(10.8, 3.9)
    filas = [("Cálculo · peor caso", None), ("Simulación · $V_Z$ ±5 %", None)]
    _ventana(ax, filas)
    y = 1
    ax.plot([8.85, 10.35], [y, y], color=eg.AZUL, lw=9, solid_capstyle="butt", alpha=0.35)
    ax.text(8.85, y - 0.3, "8,85", color=eg.AZUL, ha="center", va="top", fontsize=14.5)
    ax.text(10.35, y - 0.3, "10,35", color=eg.AZUL, ha="center", va="top", fontsize=14.5)
    y = 0
    vals = [R["ViregTolBajo"], R["ViregTolNom"], R["ViregTolAlto"]]
    ax.plot(vals, [y] * 3, color=eg.AZUL, lw=1.4, zorder=4)
    for v, rot in zip(vals, ("−5 %", "nom.", "+5 %")):
        ax.plot(v, y, "o", color=eg.AZUL, ms=13, zorder=5)
        ax.text(v, y + 0.27, c(v, 2), color=eg.AZUL, ha="center", fontsize=15)
        ax.text(v, y - 0.3, rot, color=eg.TENUE, ha="center", va="top", fontsize=14)
    eg.guardar(fig, AQUI / "ventana_tolerancia.svg")


# ---------------------------------------------------------------------- SOA
def soa():
    eg.aplicar()
    fig, ax = eg.figura(9.0, 6.3)
    x1 = np.linspace(13, 20.2, 30)
    x2 = np.linspace(20.2, 100, 60)
    xs = np.concatenate([[1, 13], x1, x2, [100, 100]])
    ys = np.concatenate([[5, 5], 65 / x1, 3.1 * (20.2 / x2) ** 1.58, [0.247, 0.05]])
    ax.fill_between(xs, 0.05, ys, color="#ece8df", zorder=0)
    ax.plot(xs, ys, color=eg.MARINO, lw=3, label="SOA en continua, $T_C$ = 25 °C")
    x3 = np.linspace(7.28, 51.6, 40)
    ax.plot(np.concatenate([[1, 7.28], x3]), np.concatenate([[5, 5], 36.4 / x3]), color=eg.GRIS,
            lw=2.2, ls="--", label="Límite térmico, $T_C$ = 80 °C")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1, 150); ax.set_ylim(0.05, 10)
    ax.plot(R["VceVeinticinco"], 0.505, "o", color=eg.AZUL, ms=12, zorder=5)
    ax.plot(18.65, 0.508, "o", mfc=eg.CREMA, mec=eg.AZUL, mew=2.4, ms=12, zorder=5)
    ax.plot(R["VceCorto"], R["IscCorto"], "s", color=eg.MARINO, ms=11, zorder=5)
    eg.anotar(ax, "$Q_\\mathrm{nom}$  15,36 V · 7,76 W", (R["VceVeinticinco"], 0.505), (2.2, 0.32), color=eg.AZUL)
    eg.anotar(ax, "$Q_\\mathrm{máx}$  18,65 V · 9,5 W", (18.65, 0.508), (2.2, 0.17), color=eg.AZUL)
    eg.anotar(ax, "$Q_{cc}$  " + c(R["IscCorto"], 2) + " A", (R["VceCorto"], R["IscCorto"]), (3.0, 1.75), color=eg.MARINO)
    ax.text(30, 2.4, "2.ª ruptura", color=eg.MARINO, fontsize=14.5)
    ax.set_xlabel("$V_{CE}$ [V]"); ax.set_ylabel("$I_C$ [A]")
    eg.log_plano(ax, "x"); eg.log_plano(ax, "y")
    ax.legend(loc="lower left")
    eg.guardar(fig, AQUI / "soa.svg")


# ------------------------------------------------------------ línea: barrido
def linea():
    eg.aplicar()
    d = dat("linea")
    fig, ax = eg.figura(9.4, 6.4)
    ax.axhspan(8, 12, color=VERDE_TINTE, zorder=0)
    ax.text(0.6, 12.25, "Ventana de 8 a 12 V", color=eg.VERDE, fontsize=15)
    ax.plot(d["vp"], d["vb"], color=eg.GRIS, lw=2.2, ls="--", label="Base de $Q_1$")
    ax.plot(d["vp"], d["vireg"], color=eg.MARINO, lw=3, label="Entrada del LM7805, $V_{i,\\mathrm{reg}}$")
    ax.plot(d["vp"], d["vo"], color=eg.AZUL, lw=3, label="Salida $V_O$")
    for vp, v in ((10, R["ViregDiez"]), (25, R["ViregVeinticinco"])):
        ax.plot(vp, v, "o", color=eg.MARINO, ms=11, zorder=5)
    eg.anotar(ax, c(R["ViregVeinticinco"], 2) + " V con $V_P$ = 25 V", (25, R["ViregVeinticinco"]), (18.2, 6.2))
    eg.anotar(ax, c(R["ViregDiez"], 2) + " V con $V_P$ = 10 V", (10, R["ViregDiez"]), (10.8, 5.6))
    ax.set_xlim(0, 30); ax.set_ylim(0, 14)
    ax.set_xlabel("Fuente primaria $V_P$ [V]"); ax.set_ylabel("Tensión [V]")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86))
    eg.coma(ax)
    eg.guardar(fig, AQUI / "linea.svg")


def linea_detalle():
    eg.aplicar()
    d = dat("linea_detalle")
    fig, ax = eg.figura(9.4, 6.2)
    ax.axvspan(22.5, 27.5, color="#ece8df", zorder=0)
    ax.text(25, 0.78, "$V_P$ ± 10 %", ha="center", color=eg.CUERPO, fontsize=15)
    ax.axhline(0, color=eg.CUERPO, lw=1)
    ax.plot(d["vp"], d["dvosin"], color=eg.NARANJA, lw=3, label="LM7805 directo a $V_P$")
    ax.plot(d["vp"], d["dvocon"], color=eg.AZUL, lw=3, label="Con etapa prereguladora")
    ax.set_xlim(9, 29); ax.set_ylim(-3, 1)
    ax.set_xlabel("Fuente primaria $V_P$ [V]"); ax.set_ylabel("$\\Delta V_O$ respecto de $V_P$ = 25 V [mV]")
    ax.legend(loc="lower right")
    eg.coma(ax)
    eg.guardar(fig, AQUI / "linea_detalle.svg")


def otra_lectura():
    eg.aplicar()
    d = dat("linea")
    fig, ax = eg.figura(9.0, 6.0)
    ax.axhspan(8, 12, color=VERDE_TINTE, zorder=0)
    ax.text(29.6, 12.15, "Ventana de 8 a 12 V", color=eg.VERDE, fontsize=15, ha="right")
    ax.plot(d["vp"], d["vp"], color=eg.GRIS, lw=1.6, ls=":", label="$V_{i,\\mathrm{reg}} = V_P$")
    ax.plot(d["vp"], d["vireg"], color=eg.MARINO, lw=3, label="$V_{i,\\mathrm{reg}}$ con etapa")
    ax.axvline(11, color=eg.TENUE, lw=1.2, ls="--")
    ax.text(11.3, 13.1, "$V_P$ = 11 V: el Zener deja de conducir", color=eg.TENUE, fontsize=14.5)
    ax.plot(R["VpVentana"], 8, "o", mfc=eg.CREMA, mec=eg.MARINO, mew=2.2, ms=11, zorder=5)
    ax.plot(10, R["ViregDiez"], "o", color=eg.MARINO, ms=11, zorder=5)
    eg.anotar(ax, c(R["VpVentana"], 2) + " V: límite de la ventana", (R["VpVentana"], 8), (13.5, 3.6))
    eg.anotar(ax, c(R["ViregDiez"], 2) + " V con $V_P$ = 10 V", (10, R["ViregDiez"]), (13.5, 2.0))
    ax.set_xlim(5, 30); ax.set_ylim(0, 14)
    ax.set_xlabel("Fuente primaria $V_P$ [V]"); ax.set_ylabel("Tensión [V]")
    ax.legend(loc="upper left")
    eg.coma(ax)
    eg.guardar(fig, AQUI / "otra_lectura.svg")


# -------------------------------------------------------------------- carga
def carga():
    eg.aplicar()
    d = dat("carga")
    fig, ax = eg.figura(9.4, 6.0)
    dv = (d["vo"] - R["VoVacio"]) * 1000
    ax.axvline(0.5, color=eg.TENUE, lw=1.2, ls="--")
    ax.text(0.52, 0.25, "$I_{L,\\mathrm{máx}}$ = 0,5 A", color=eg.TENUE, fontsize=15)
    ax.plot(d["il"], dv, color=eg.AZUL, lw=3)
    k = np.argmin(abs(d["il"] - 0.5))
    ax.plot(0.5, dv[k], "o", color=eg.AZUL, ms=11, zorder=5)
    eg.anotar(ax, "4,9645 V → 4,9634 V", (0.5, dv[k]), (0.62, -0.55), color=eg.AZUL)
    ax.set_xlim(0, 1.5); ax.set_ylim(-3, 0.5)
    ax.set_xlabel("Corriente de carga $I_L$ [A]"); ax.set_ylabel("$V_O - V_{O(I_L=0)}$ [mV]")
    eg.coma(ax)
    eg.guardar(fig, AQUI / "carga.svg")


# ------------------------------------------------------------------- rizado
def rizado():
    eg.aplicar()
    d = dat("rizado")
    m = d["t"] <= 20
    t = d["t"][m]
    fig, axs = eg.figura(9.8, 6.6, nrows=2, ncols=2, sharex=True)
    paneles = [
        (axs[0, 0], d["vp"][m], eg.MARINO, "Fuente primaria · V", (-1.25, 1.25)),
        (axs[0, 1], d["vireg"][m], eg.MARINO, "Entrada del LM7805 · mV", (-15, 15)),
        (axs[1, 0], d["vosin"][m], eg.NARANJA, "Salida, LM7805 directo · µV", (-200, 200)),
        (axs[1, 1], d["vo"][m], eg.AZUL, "Salida, con etapa · µV", (-3, 3)),
    ]
    for ax, y, col, tit, lim in paneles:
        ax.plot(t, y, color=col, lw=2.6)
        ax.set_title(tit, loc="left", color=col if col != eg.MARINO else eg.MARINO, fontsize=16, fontweight="medium")
        ax.set_ylim(*lim); ax.set_xlim(0, 20)
        eg.coma(ax)
    for ax in axs[1]:
        ax.set_xlabel("t [ms]")
    eg.guardar(fig, AQUI / "rizado.svg")


# -------------------------------------------------------------- temperatura
def temperatura():
    eg.aplicar()
    d = dat("temperatura")
    fig, ax = eg.figura(9.4, 6.0)
    ax.plot(d["t"], d["vosin"], color=eg.NARANJA, lw=3, label="LM7805 directo a $V_P$")
    ax.plot(d["t"], d["vo"], color=eg.AZUL, lw=3, label="Con etapa prereguladora")
    ax.set_xlim(0, 55)
    ax.set_xlabel("Temperatura [°C]"); ax.set_ylabel("$V_O$ [V]")
    ax.legend(loc="upper right")
    eg.coma(ax, "x"); eg.coma(ax, "y", 3)
    eg.guardar(fig, AQUI / "temperatura.svg")


# ---------------------------------------------------------------- potencias
def potencias():
    eg.aplicar()
    fig, ax = eg.figura(10.0, 5.0)
    ax.set_axisbelow(True)
    pl = R["PlVeinticinco"]
    pl_sin = R["VoSinVeinticinco"] * 0.5
    resto = R["PinVeinticinco"] - pl - R["PregVeinticinco"] - R["PqVeinticinco"]
    filas = [
        (1, [("Carga", pl, "#0b6b5d"), ("TIP122", R["PqVeinticinco"], eg.GRIS),
             ("LM7805", R["PregVeinticinco"], eg.MARINO), ("", resto, "#c9c3b6")]),
        (0, [("Carga", pl_sin, "#0b6b5d"), ("LM7805", R["PregSinVeinticinco"], eg.MARINO)]),
    ]
    for y, segs in filas:
        x = 0
        for nombre, w, col in segs:
            ax.barh(y, w, left=x, height=0.66, color=col, edgecolor=eg.CREMA, linewidth=2)
            if nombre:
                ax.text(x + w / 2, y + 0.02, f"{nombre}\n{c(w, 2)} W", ha="center", va="center",
                        color="white", fontsize=17, fontweight="medium", linespacing=1.15)
            x += w
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["Con etapa", "LM7805 directo"], fontsize=16, fontweight="medium")
    for lab, col in zip(ax.get_yticklabels(), (eg.AZUL, eg.NARANJA)):
        lab.set_color(col)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.grid(False); ax.grid(True, axis="x", color="#e4dfd5")
    ax.set_xlim(0, 14); ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel("Potencia [W] · $V_P$ = 25 V, $I_L$ = 0,5 A")
    eg.coma(ax, "x")
    eg.guardar(fig, AQUI / "potencias.svg")


# ---------------------------------------------------------------- VBE TIP122
def vbe():
    eg.aplicar()
    d = dat("vbe_tip122")
    h = dat("vbe_hoja")
    fig, ax = eg.figura(9.2, 6.0)
    ax.plot(d["ic"], d["vbeorig"], color=eg.GRIS, lw=2.6, ls="--", label="Modelo de onsemi")
    ax.plot(d["ic"], d["vbeaj"], color=eg.VERDE, lw=3, label="Modelo ajustado TIP122_AJ")
    ax.plot(h["ic"], h["vbe"], "o", color=eg.MARINO, ms=9, zorder=5, label="Hoja de datos (Fig. 11, típica)")
    ax.set_xscale("log")
    ax.set_xlim(0.01, 6); ax.set_ylim(0.5, 2.1)
    ax.set_xlabel("$I_C$ [A]"); ax.set_ylabel("$V_{BE}$ [V]")
    eg.log_plano(ax, "x"); eg.coma(ax, "y", 1)
    ax.legend(loc="upper left")
    eg.guardar(fig, AQUI / "vbe.svg")


if __name__ == "__main__":
    portada()
    ventana_calculo()
    ventana_tolerancia()
    soa()
    linea()
    linea_detalle()
    otra_lectura()
    carga()
    rizado()
    temperatura()
    potencias()
    vbe()
