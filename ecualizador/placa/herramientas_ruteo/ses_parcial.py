"""Agrega a una placa solo las pistas y vias de ciertas redes de un .ses de Freerouting (el resto no se toca).
Uso: ses_parcial.py placa.kicad_pcb ruteo.ses red1,red2,..."""
import re, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ses = open(sys.argv[2]).read(); redes = sys.argv[3].split(",")
U = lambda v: int(round(float(v) * 100))          # 0,1 um -> nm
nv = nt = 0
for red in redes:
    i = ses.index(f'(net "{red}"'); j = ses.find("\n      (net ", i + 5); bloque = ses[i:j if j > 0 else None]
    net = b.FindNet(red)
    for m in re.finditer(r"\(path (\S+) (\d+)\s+([-\d\s]+)\)", bloque):
        ly = b.GetLayerID(m.group(1)); w = U(m.group(2)); c = m.group(3).split()
        pts = [pcbnew.VECTOR2I(U(c[k]), -U(c[k + 1])) for k in range(0, len(c), 2)]
        for a, z in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(z); t.SetWidth(w); t.SetLayer(ly); t.SetNet(net); b.Add(t); nt += 1
    for m in re.finditer(r'\(via "[^"]+" (-?\d+) (-?\d+)', bloque):
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(U(m.group(1)), -U(m.group(2))))
        v.SetWidth(pcbnew.FromMM(2.0)); v.SetDrill(pcbnew.FromMM(0.9)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net); b.Add(v); nv += 1
pcbnew.SaveBoard(sys.argv[1], b, True)
print("tramos:", nt, "| vias:", nv)
