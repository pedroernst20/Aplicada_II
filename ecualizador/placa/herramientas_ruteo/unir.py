"""Une tramos colineales consecutivos (punto con solo dos pistas, sin pad ni via) y arregla codos con una pata corta."""
import sys, math, pcbnew
from collections import defaultdict
b = pcbnew.LoadBoard(sys.argv[1])
fijos = set()
for fp in b.GetFootprints():
    for p in fp.Pads():
        fijos.add((p.GetPosition().x, p.GetPosition().y))
for v in b.GetTracks():
    if v.Type() == pcbnew.PCB_VIA_T: fijos.add((v.GetPosition().x, v.GetPosition().y))
ts = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
vivos = {i: t for i, t in enumerate(ts)}
def ext():
    E = defaultdict(list)
    for i, t in vivos.items():
        for p in (t.GetStart(), t.GetEnd()):
            E[(t.GetNetCode(), t.GetLayer(), p.x, p.y)].append(i)
    return E
def otro(t, x, y):
    s, e = t.GetStart(), t.GetEnd()
    return e if (s.x, s.y) == (x, y) else s
def u(dx, dy):
    L = math.hypot(dx, dy); return dx / L, dy / L
quitar = []; uniones = 0
cambio = True
while cambio:
    cambio = False
    for (net, ly, x, y), ids in ext().items():
        if len(ids) != 2 or (x, y) in fijos: continue
        a, c = vivos[ids[0]], vivos[ids[1]]
        if a.GetWidth() != c.GetWidth(): continue
        pa, pc = otro(a, x, y), otro(c, x, y)
        ua, uc = u(pa.x - x, pa.y - y), u(pc.x - x, pc.y - y)
        if ua[0] * uc[0] + ua[1] * uc[1] < -0.9995:
            a.SetStart(pa); a.SetEnd(pc); quitar.append(c); del vivos[ids[1]]; uniones += 1; cambio = True; break
print("tramos unidos:", uniones)
# codos a 90 con una pata corta (< 0.7 mm) que sigue en diagonal: se corre el codo
codos = 0
for (net, ly, x, y), ids in ext().items():
    if len(ids) != 2 or (x, y) in fijos: continue
    A, B = vivos[ids[0]], vivos[ids[1]]
    if A.GetLength() < B.GetLength(): A, B = B, A
    if B.GetLength() >= pcbnew.FromMM(0.7): continue
    pa, q = otro(A, x, y), otro(B, x, y)
    ua, ub = u(pa.x - x, pa.y - y), u(q.x - x, q.y - y)
    if abs(ua[0] * ub[0] + ua[1] * ub[1]) > 0.02: continue
    s = B.GetLength()
    n = pcbnew.VECTOR2I(int(x + s * ua[0]), int(y + s * ua[1]))
    if (A.GetStart().x, A.GetStart().y) == (x, y): A.SetStart(n)
    else: A.SetEnd(n)
    if (B.GetStart().x, B.GetStart().y) == (x, y): B.SetStart(n)
    else: B.SetEnd(n)
    codos += 1
    print("codo corto", b.GetNetName(net) if hasattr(b, "GetNetName") else net, round(pcbnew.ToMM(x) - 40, 2), round(pcbnew.ToMM(y) - 40, 2))
for t in quitar: b.Remove(t)
pcbnew.SaveBoard(sys.argv[1], b, True)
print("codos cortos corridos:", codos)
