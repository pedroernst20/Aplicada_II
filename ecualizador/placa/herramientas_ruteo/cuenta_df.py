"""Cuenta, en una placa doble faz sin metalizar: vias, pads que hay que soldar arriba y redes sin conectar."""
import sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
arriba = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == pcbnew.F_Cu]
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
pads_arriba = set()
for fp in b.GetFootprints():
    for p in fp.Pads():
        if not p.IsOnLayer(pcbnew.F_Cu):
            continue
        for t in arriba:
            if t.GetNetCode() == p.GetNetCode() and (p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd())):
                pads_arriba.add(f"{fp.GetReference()}.{p.GetNumber()}")
                break
print("vias:", len(vias), "| pads a soldar arriba:", len(pads_arriba), "| pistas arriba (mm):",
      round(sum(pcbnew.ToMM(t.GetLength()) for t in arriba), 1))
print(" ", " ".join(sorted(pads_arriba)))
