"""Doble faz: exporta el .kicad_pcb a DSN, le pone las preferencias de ruteo (cara de arriba cara, vias caras),
corre Freerouting y vuelve a importar el resultado. Correr con el python de KiCad.
Por defecto la masa no se rutea (va como plano en las dos caras y se cose con vias despues).
Uso: freeroute_df.py carpeta [pasadas]
FIJAR=1: lo ya ruteado queda fijo (para rutear solo lo que falta). Ojo: el .ses trae solo lo nuevo y al importarlo
se pierde el resto; en ese caso tomar las redes nuevas con ses_parcial.py sobre la placa original."""
import os
import re
import subprocess
import sys

import pcbnew

CARPETA = sys.argv[1]
PASADAS = sys.argv[2] if len(sys.argv) > 2 else "60"
JAR = r"C:\Users\valen\Documents\KiCad\freerouting\freerouting-1.9.0.jar"
PCB = os.path.join(CARPETA, "ecualizador.kicad_pcb")
DSN = os.path.join(CARPETA, "ecualizador.dsn")
SES = os.path.join(CARPETA, "ecualizador.ses")

board = pcbnew.LoadBoard(PCB)
# planos y mordidas afuera para el ruteador (las mordidas se verifican con el DRC)
zonas = list(board.Zones())
for z in zonas:
    board.Remove(z)
ok = pcbnew.ExportSpecctraDSN(board, DSN)
print("DSN:", ok)
t = open(DSN, encoding="utf-8").read()
ajustes = """    (autoroute_settings
      (fanout off) (autoroute on) (postroute on) (vias on)
      (via_costs 120) (plane_via_costs 5) (start_ripup_costs 100) (start_pass_no 1)
      (layer_rule F.Cu (active on) (preferred_direction vertical)
        (preferred_direction_trace_costs 6.0) (against_preferred_direction_trace_costs 8.0))
      (layer_rule B.Cu (active on) (preferred_direction horizontal)
        (preferred_direction_trace_costs 1.0) (against_preferred_direction_trace_costs 1.3))
    )
"""
if "autoroute_settings" not in t:
    i = t.index("(structure")
    j = t.index("    (via ", i)
    t = t[:j] + ajustes + t[j:]
if os.environ.get("SIN_GND", "1") == "1":
    t = re.sub(r"\n\s*\(net GND\s*\n\s*\(pins[^)]*\)\s*\)", "", t, count=1)
    t = re.sub(r"(\(class [^\n]*?) GND(?=[\s)])", r"\1", t)
    t = re.sub(r"\n\s*\(wire \(path [^\n]*\(net GND\)[^\n]*", "", t)
SOLO_ABAJO = ("DIP-", "PinSocket", "PinHeader", "KF2510", "Jack_", "Pote_", "CP_Radial", "C_Rect", "SW_PUSH", "LED_",
              "Pad_Cocodrilo")


def solo_abajo(t):
    """Huellas que no se sueldan arriba: pad solo en B.Cu y un obstaculo en F.Cu del tamano del pad + separacion."""
    pads = {}
    for m in re.finditer(r"\n    \(padstack (\S+)\n(.*?)\n    \)", t, re.S):
        pads[m.group(1)] = m.group(2)
    nuevos = {}

    def extension(cuerpo):
        mx = 0.0
        for s in re.finditer(r"\(shape \((\w+) F\.Cu ([^)]*)\)", cuerpo):
            nums = [float(v) for v in s.group(2).split()]
            if s.group(1) == "circle":
                mx = max(mx, nums[0])
            elif s.group(1) == "path":
                w, pts = nums[0], nums[1:]
                xs, ys = pts[0::2], pts[1::2]
                mx = max(mx, w + max(max(xs) - min(xs), max(ys) - min(ys)))
            else:                                   # rect / polygon: coordenadas
                pts = nums[1:] if s.group(1) == "polygon" else nums
                xs, ys = pts[0::2], pts[1::2]
                mx = max(mx, max(max(xs) - min(xs), max(ys) - min(ys)))
        return mx

    def img(m):
        crudo, cuerpo = m.group(1), m.group(2)
        nombre = crudo.strip('"')
        if not any(k in nombre for k in SOLO_ABAJO):
            return m.group(0)
        extra = []

        def pin(pm):
            ps, resto = pm.group(1), pm.group(2)
            if ps in pads:
                nb = ps + "_B"
                if nb not in nuevos:
                    # separar las expresiones de primer nivel (pueden ocupar varias lineas) y sacar las de F.Cu
                    cuerpo_ps, partes, nivel, ini = pads[ps], [], 0, None
                    for k, ch in enumerate(cuerpo_ps):
                        if ch == "(":
                            if nivel == 0:
                                ini = k
                            nivel += 1
                        elif ch == ")":
                            nivel -= 1
                            if nivel == 0:
                                partes.append(cuerpo_ps[ini:k + 1])
                    nuevos[nb] = "\n".join("      " + p for p in partes if "F.Cu" not in p)
                xy = re.findall(r"(-?[\d.]+) (-?[\d.]+)\)$", resto)
                if xy:
                    x, y = xy[0]
                    d = extension(pads[ps]) + 1300
                    extra.append(f'      (keepout "" (circle F.Cu {d:.0f} {x} {y}))')
                return f"(pin {nb} {resto}"
            return pm.group(0)

        cuerpo2 = re.sub(r"\(pin (\S+) ([^\n]*\))", pin, cuerpo)
        return f'(image {crudo}{cuerpo2}\n' + "\n".join(extra) + "\n    )"

    t = re.sub(r'\(image ("[^"]+"|[^\s()]+)(.*?)\n    \)', img, t, flags=re.S)
    defs = "".join(f"\n    (padstack {k}\n{v}\n    )" for k, v in nuevos.items())
    i = t.index("\n    (padstack ")
    return t[:i] + defs + t[i:]


if os.environ.get("SOLO_ABAJO", "1") == "1":
    t = solo_abajo(t)
if os.environ.get("FIJAR", "0") == "1":
    t = t.replace("(type route))", "(type fix))")
open(DSN, "w", encoding="utf-8").write(t)
if os.path.exists(SES):
    os.remove(SES)
r = subprocess.run(["java", "-jar", JAR, "-de", DSN, "-do", SES, "-mp", PASADAS, "-dct", "0"],
                   capture_output=True, text=True, timeout=3600)
print(r.stdout[-1200:], r.stderr[-1200:])
if not os.path.exists(SES):
    sys.exit("Freerouting no genero el .ses")
ok = pcbnew.ImportSpecctraSES(board, SES)
print("SES:", ok)
# patas repetidas del pulsador: la de masa no paso por el ruteador
sw = board.FindFootprintByReference("SW1")
if sw:
    por_num = {}
    for pad in sw.Pads():
        por_num.setdefault(pad.GetNumber(), []).append(pad)
    for num, pads in por_num.items():
        if len(pads) == 2 and pads[0].GetNetname() == "GND":
            tr = pcbnew.PCB_TRACK(board)
            tr.SetStart(pads[0].GetPosition())
            tr.SetEnd(pads[1].GetPosition())
            tr.SetWidth(pcbnew.FromMM(1.0))
            tr.SetLayer(pcbnew.B_Cu)
            tr.SetNet(pads[0].GetNet())
            board.Add(tr)
for z in zonas:
    board.Add(z)
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(PCB, board, True)
vias = [x for x in board.GetTracks() if x.Type() == pcbnew.PCB_VIA_T]
arriba = [x for x in board.GetTracks() if x.Type() == pcbnew.PCB_TRACE_T and x.GetLayer() == pcbnew.F_Cu]
print("vias:", len(vias), "| tramos arriba:", len(arriba),
      "| largo arriba (mm):", round(sum(pcbnew.ToMM(x.GetLength()) for x in arriba), 1))
