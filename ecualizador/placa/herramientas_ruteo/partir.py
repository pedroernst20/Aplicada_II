"""Parte una pista donde otra de la misma red y capa termina en su interior (T), para que chaflan.py la vea.
Tambien saca tramos de largo cero."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
todo = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
cero = [t for t in todo if t.GetStart() == t.GetEnd()]
ts = [t for t in todo if t.GetStart() != t.GetEnd()]
def interior(p, t):
    a, c = t.GetStart(), t.GetEnd(); L = t.GetLength()
    if (p - a).EuclideanNorm() < 1000 or (p - c).EuclideanNorm() < 1000: return False
    cr = (c.x-a.x)*(p.y-a.y)-(c.y-a.y)*(p.x-a.x)
    if abs(cr) / L > 1000: return False
    d = (p.x-a.x)*(c.x-a.x)+(p.y-a.y)*(c.y-a.y)
    return 0 < d < L*L
quitar, nuevos = [], []
for i, t in enumerate(ts):
    ps = set()
    for j, o in enumerate(ts):
        if i == j or o.GetNetCode() != t.GetNetCode() or o.GetLayer() != t.GetLayer(): continue
        for p in (o.GetStart(), o.GetEnd()):
            if interior(p, t): ps.add((p.x, p.y))
    if not ps: continue
    a, c = t.GetStart(), t.GetEnd()
    cad = [a] + [pcbnew.VECTOR2I(x, y) for x, y in sorted(ps, key=lambda q: (q[0]-a.x)**2 + (q[1]-a.y)**2)] + [c]
    for p, q in zip(cad, cad[1:]):
        nuevos.append((p, q, t.GetWidth(), t.GetLayer(), t.GetNet()))
    quitar.append(t)
    print("parto", t.GetNetname(), [(round(pcbnew.ToMM(x)-40, 2), round(pcbnew.ToMM(y)-40, 2)) for x, y in sorted(ps)])
for p, q, w, ly, net in nuevos:
    nt = pcbnew.PCB_TRACK(b); nt.SetStart(p); nt.SetEnd(q); nt.SetWidth(w); nt.SetLayer(ly); nt.SetNet(net); b.Add(nt)
for t in quitar + cero:
    b.Remove(t)
pcbnew.SaveBoard(sys.argv[1], b, True)
print("pistas partidas:", len(quitar), "| tramos de largo cero:", len(cero))
