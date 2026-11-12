"""Mapa de soldadura de la placa doble faz sin metalizar y lista de montaje.

Dos pasos (el python de KiCad no trae matplotlib):
  1) con el python de KiCad:  mapa_soldadura.py datos  placa.kicad_pcb  datos.json
  2) con el python comun:     mapa_soldadura.py dibujo  datos.json  mapa.png  montaje.md
"""
import json
import sys

OX = OY = 40.0   # origen de la placa en la hoja de KiCad


def datos(pcb, salida):
    import pcbnew
    b = pcbnew.LoadBoard(pcb)
    mm = pcbnew.ToMM
    P = lambda v: (round(mm(v.x) - OX, 3), round(mm(v.y) - OY, 3))
    pistas, vias = [], []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            vias.append({"p": P(t.GetPosition()), "red": t.GetNetname()})
        elif t.Type() == pcbnew.PCB_TRACE_T:
            pistas.append({"a": P(t.GetStart()), "b": P(t.GetEnd()), "arriba": t.GetLayer() == pcbnew.F_Cu})
    arriba = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == pcbnew.F_Cu]
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            sold = p.IsOnLayer(pcbnew.F_Cu) and any(
                t.GetNetCode() == p.GetNetCode() and (p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd())) for t in arriba)
            pads.append({"ref": fp.GetReference(), "n": p.GetNumber(), "p": P(p.GetPosition()), "arriba": sold})
    refs = {fp.GetReference(): P(fp.GetPosition()) for fp in b.GetFootprints()}
    bb = b.GetBoardEdgesBoundingBox()
    json.dump({"pistas": pistas, "vias": vias, "pads": pads, "refs": refs,
               "borde": [mm(bb.GetWidth()), mm(bb.GetHeight())]}, open(salida, "w"))


def dibujo(entrada, png, md):
    import re
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    D = json.load(open(entrada))
    W, H = D["borde"]
    vias = sorted(D["vias"], key=lambda v: (v["p"][0], v["p"][1]))
    sold = [p for p in D["pads"] if p["arriba"]]
    fig, ax = plt.subplots(figsize=(W / 11, H / 11 + 0.8))
    ax.add_patch(Rectangle((0, 0), W, H, fc="#f3f0e8", ec="#222", lw=1.2))
    for t in D["pistas"]:
        if not t["arriba"]:
            ax.plot([t["a"][0], t["b"][0]], [t["a"][1], t["b"][1]], color="#a9c1e0", lw=1.6, solid_capstyle="round")
    for t in D["pistas"]:
        if t["arriba"]:
            ax.plot([t["a"][0], t["b"][0]], [t["a"][1], t["b"][1]], color="#d24130", lw=2.4, solid_capstyle="round")
    for p in D["pads"]:
        if not p["arriba"]:
            ax.plot(*p["p"], "o", color="#7c7c7c", ms=6)
    for p in sold:
        ax.plot(*p["p"], "o", mfc="#ffd400", mec="#b08f00", ms=14)
    for i, v in enumerate(vias, 1):
        ax.plot(*v["p"], "o", mfc="#111", mec="#ffd400", mew=2, ms=13)
        ax.annotate(f"V{i}", v["p"], xytext=(9, 3), textcoords="offset points", fontsize=10, weight="bold")
    for r, (x, y) in D["refs"].items():
        cerca = [p["p"] for p in D["pads"] if p["ref"] == r]
        ytop = min(q[1] for q in cerca) if cerca else y
        ax.text(x, ytop - 2.2, r, fontsize=6, ha="center", color="#333")
    ax.set_xlim(-1, W + 1)
    ax.set_ylim(H + 1, -1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Visto desde arriba (lado de los componentes). Rojo: pistas de arriba. Celeste: pistas de abajo.\n"
                 f"Amarillo: pads que se sueldan TAMBIEN arriba ({len(sold)}). "
                 f"Negro con aro amarillo: vias, alambre soldado de los dos lados ({len(vias)}).", fontsize=11)
    fig.tight_layout()
    fig.savefig(png, dpi=110)

    clave = lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0))
    por_ref = {}
    for p in sold:
        por_ref.setdefault(p["ref"], []).append(p["n"])
    L = ["# Placa doble faz: montaje", "",
         "Agujeros sin metalizar: cada via y cada pad con pista de arriba se suelda tambien del lado de los componentes.",
         "Mapa: `imagenes/doble_faz_como_se_suelda.png` (lo generan `herramientas_ruteo/mapa_soldadura.py`).", "",
         f"## Vias ({len(vias)}): alambre pasante soldado de los dos lados", "",
         "| Via | x (mm) | y (mm) | red |", "|---|---|---|---|"]
    L += [f"| V{i} | {v['p'][0]:.2f} | {v['p'][1]:.2f} | {v['red']} |" for i, v in enumerate(vias, 1)]
    L += ["", f"## Pads que llevan soldadura arriba ({len(sold)})", "",
          "Soldar estas piezas un poco levantadas (1 o 2 mm) para llegar con el soldador al pad de arriba.", ""]
    L += [f"- **{r}**: pata {', '.join(sorted(ns))}" for r, ns in sorted(por_ref.items(), key=lambda kv: clave(kv[0]))]
    L += ["", "Orden: primero las vias, despues las piezas bajas con soldadura arriba y al final las que van solo abajo.",
          "Solo abajo: zocalos, tiras de pines, potes, jack, pulsador, LED, electroliticos, capacitores de caja y pads de",
          "cocodrilo (el ruteo nunca les lleva pistas por arriba).", ""]
    open(md, "w", newline="\r\n").write("\n".join(L))


if __name__ == "__main__":
    {"datos": datos, "dibujo": dibujo}[sys.argv[1]](*sys.argv[2:])
