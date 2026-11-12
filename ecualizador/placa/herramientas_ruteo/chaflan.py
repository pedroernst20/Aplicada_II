"""Pasa a 45 grados las esquinas de 90 (dos pistas de la misma red y capa que se juntan en angulo recto, sin pad ni via
en el vertice) y los empalmes en T a 90 (la rama entra a 45). Tambien pone gotas en pads y vias.
Correr con el python de KiCad. Uso: chaflan.py entrada.kicad_pcb salida.kicad_pcb [tope_mm] [evitar.json]
evitar.json: lista de vertices [x, y] (mm, coordenadas de la placa) donde usar un chaflan mas chico."""
import json
import math
import sys
from collections import defaultdict

import pcbnew

ENT, SAL = sys.argv[1], sys.argv[2]
TOPE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.9
EVITAR = {}
if len(sys.argv) > 4:
    for x, y, c in json.load(open(sys.argv[4])):
        EVITAR[(round(x, 2), round(y, 2))] = c
b = pcbnew.LoadBoard(ENT)
mm = pcbnew.FromMM
OX = OY = 40.0


def clave(p, t):
    return (t.GetNetCode(), t.GetLayer(), p.x, p.y)


def pistas():
    return [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLength() > 0]


# puntos con pad o via (ahi no se toca: la pista tiene que salir recta del pad)
fijos = set()
for fp in b.GetFootprints():
    for p in fp.Pads():
        for ly in (pcbnew.F_Cu, pcbnew.B_Cu):
            if p.IsOnLayer(ly):
                fijos.add((p.GetNetCode(), ly, p.GetPosition().x, p.GetPosition().y))
for v in b.GetTracks():
    if v.Type() == pcbnew.PCB_VIA_T:
        for ly in (pcbnew.F_Cu, pcbnew.B_Cu):
            fijos.add((v.GetNetCode(), ly, v.GetPosition().x, v.GetPosition().y))


def otro(t, p):
    return t.GetEnd() if t.GetStart() == p else t.GetStart()


def unit(a, b_):
    dx, dy = b_.x - a.x, b_.y - a.y
    L = math.hypot(dx, dy)
    return (dx / L, dy / L), L


def corre(t, p, nuevo):
    if t.GetStart() == p:
        t.SetStart(nuevo)
    else:
        t.SetEnd(nuevo)


esquinas = tes = 0
for vuelta in range(3):                       # varias vueltas: un chaflan puede dejar otra esquina
    ext = defaultdict(list)
    for t in pistas():
        for p in (t.GetStart(), t.GetEnd()):
            ext[clave(p, t)].append(t)
    hecho = False
    for k, ts in ext.items():
        if k in fijos:
            continue
        net, ly, x, y = k
        P = pcbnew.VECTOR2I(x, y)
        if any(t.GetStart() == t.GetEnd() for t in ts):
            continue
        dirs = [unit(P, otro(t, P)) for t in ts]
        tope = mm(EVITAR.get((round(pcbnew.ToMM(x) - OX, 2), round(pcbnew.ToMM(y) - OY, 2)), TOPE))
        if len(ts) == 2:
            (ua, La), (ub, Lb) = dirs
            if abs(ua[0] * ub[0] + ua[1] * ub[1]) > 0.05:
                continue
            c = min(tope, 0.45 * La, 0.45 * Lb)
            if c < mm(0.3):
                continue
            A = pcbnew.VECTOR2I(int(x + c * ua[0]), int(y + c * ua[1]))
            B = pcbnew.VECTOR2I(int(x + c * ub[0]), int(y + c * ub[1]))
            ta, tb = ts
            corre(ta, P, A)
            corre(tb, P, B)
            n = pcbnew.PCB_TRACK(b)
            n.SetStart(A); n.SetEnd(B)
            n.SetWidth(min(ta.GetWidth(), tb.GetWidth())); n.SetLayer(ly); n.SetNet(ta.GetNet())
            b.Add(n)
            esquinas += 1
            hecho = True
        elif len(ts) == 3:
            # T: dos colineales (principal) y una perpendicular (rama)
            for i in range(3):
                j, k2 = [m for m in range(3) if m != i]
                uj, uk, ui = dirs[j][0], dirs[k2][0], dirs[i][0]
                if abs(uj[0] * uk[0] + uj[1] * uk[1] + 1) < 0.05 and abs(ui[0] * uj[0] + ui[1] * uj[1]) < 0.05:
                    Li = dirs[i][1]
                    # la rama entra a 45 hacia el lado del principal que sea mas largo
                    lado, Lm = (j, dirs[j][1]) if dirs[j][1] >= dirs[k2][1] else (k2, dirs[k2][1])
                    um = dirs[lado][0]
                    c = min(tope, 0.45 * Li, 0.45 * Lm)
                    if c < mm(0.3):
                        break
                    R = pcbnew.VECTOR2I(int(x + c * ui[0]), int(y + c * ui[1]))
                    Q = pcbnew.VECTOR2I(int(x + c * um[0]), int(y + c * um[1]))
                    corre(ts[i], P, R)
                    n = pcbnew.PCB_TRACK(b)
                    n.SetStart(R); n.SetEnd(Q)
                    n.SetWidth(ts[i].GetWidth()); n.SetLayer(ly); n.SetNet(ts[i].GetNet())
                    b.Add(n)
                    # el principal se parte en Q para que la rama quede unida en un extremo
                    tm = ts[lado]
                    far = otro(tm, P)
                    m2 = pcbnew.PCB_TRACK(b)
                    m2.SetStart(Q); m2.SetEnd(far)
                    m2.SetWidth(tm.GetWidth()); m2.SetLayer(ly); m2.SetNet(tm.GetNet())
                    b.Add(m2)
                    corre(tm, far, Q)
                    tes += 1
                    hecho = True
                    break
    if not hecho:
        break

pcbnew.SaveBoard(SAL, b, True)   # True: no pisar el .kicad_pro
print("esquinas:", esquinas, "| empalmes en T:", tes)
