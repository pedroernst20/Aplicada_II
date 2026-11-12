"""Compara el esquematico de KiCad con el circuito simulado en LTspice, pin por pin.

Uso (desde esta carpeta):  python paridad_kicad_ltspice.py

Exporta el netlist de ../placa/ecualizador.kicad_sch con kicad-cli, lee eq_audio.inc y
eq_detectores.inc, y verifica que cada nodo de LTspice corresponda a una sola red de KiCad
(y al reves). Las piezas que solo existen en la simulacion (fuentes, carga del TP4) se ignoran.
"""
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.normpath(os.path.join(AQUI, "..", "placa", "ecualizador.kicad_sch"))
KICAD_CLI = r"C:\Users\valen\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# nombre en LTspice -> (referencia en KiCad, pines de KiCad en el orden de los nodos de LTspice, polarizado)
# Operacionales: (+, -, V+, V-, salida). Diodos: (anodo, catodo). Pote: dos mitades con el cursor en el pin 2.
OPA = lambda ref, mas, menos, sal, vp=4, vn=11: (ref, [mas, menos, vp, vn, sal], True)
MAPA = {
    "RINL": ("R1", [1, 2], False), "RINR": ("R2", [1, 2], False), "CIN": ("C3", [1, 2], False), "RBIAS": ("R3", [1, 2], False),
    "XU1A": OPA("U1", 5, 6, 7),
    "RG1": ("R4", [1, 2], False), "RG2": ("R5", [1, 2], False), "CG1": ("C4", [1, 2], False), "CG2": ("C5", [1, 2], False),
    "XU1B": OPA("U1", 10, 9, 8),
    "CA1": ("C6", [1, 2], False), "CA2": ("C7", [1, 2], False), "RA1": ("R6", [1, 2], False), "RA2": ("R7", [1, 2], False),
    "XU1C": OPA("U3", 3, 2, 1),
    "CM1": ("C8", [1, 2], False), "CM2": ("C9", [1, 2], False), "RM1": ("R8", [1, 2], False), "RM2": ("R9", [1, 2], False),
    "XU1D": OPA("U1", 3, 2, 1),
    "RM3": ("R10", [1, 2], False), "RM4": ("R11", [1, 2], False), "RM5": ("R12", [1, 2], False),
    "CM3": ("C10", [1, 2], False), "CM4": ("C11", [1, 2], False), "XU2A": OPA("U1", 12, 13, 14),
    "RB1": ("R13", [1, 2], False), "RVB1": ("RV1", [3, 2], True), "RVB2": ("RV1", [2, 1], True), "RB2": ("R14", [1, 2], False),
    "XU2B": OPA("U2", 10, 9, 8),
    "RMM1": ("R15", [1, 2], False), "RVM1": ("RV2", [3, 2], True), "RVM2": ("RV2", [2, 1], True), "RMM2": ("R16", [1, 2], False),
    "XU2C": OPA("U3", 10, 9, 8),
    "RT1": ("R17", [1, 2], False), "RVT1": ("RV3", [3, 2], True), "RVT2": ("RV3", [2, 1], True), "RT2": ("R18", [1, 2], False),
    "XU2D": OPA("U4", 10, 9, 8),
    "RS1": ("R19", [1, 2], False), "RS2": ("R20", [1, 2], False), "RS3": ("R21", [1, 2], False), "RSF": ("R22", [1, 2], False),
    "XU3A": OPA("U3", 5, 6, 7), "ROUT": ("R23", [1, 2], False),
    # detectores de banda
    "XU3B": OPA("U2", 12, 13, 14), "DPB": ("D3", [2, 1], True), "CPB": ("C18", [1, 2], False), "RPB1": ("R24", [1, 2], False),
    "RPB2": ("R25", [1, 2], False), "RADB": ("R26", [1, 2], False), "XDCB": ("D4", [2, 1], True), "CADB": ("C19", [1, 2], False),
    "XU3C": OPA("U3", 12, 13, 14), "DPM": ("D5", [2, 1], True), "CPM": ("C20", [1, 2], False), "RPM1": ("R27", [1, 2], False),
    "RPM2": ("R28", [1, 2], False), "RADM": ("R29", [1, 2], False), "XDCM": ("D6", [2, 1], True), "CADM": ("C21", [1, 2], False),
    "XU3D": OPA("U4", 12, 13, 14), "DPT": ("D7", [2, 1], True), "CPT": ("C22", [1, 2], False), "RPT1": ("R30", [1, 2], False),
    "RPT2": ("R31", [1, 2], False), "RADT": ("R32", [1, 2], False), "XDCT": ("D8", [2, 1], True), "CADT": ("C23", [1, 2], False),
    # recorte
    "XU4A": OPA("U4", 5, 6, 7), "DPC": ("D9", [2, 1], True), "CPC": ("C24", [1, 2], False), "RPC": ("R33", [1, 2], False),
    "XU4B": OPA("U4", 3, 2, 1), "RR1": ("R34", [1, 2], False), "RR2": ("R35", [1, 2], False), "RRH": ("R36", [1, 2], False),
    "DQ": ("D10", [2, 1], True), "RQB": ("R37", [1, 2], False), "RQBE": ("R38", [1, 2], False),
    "Q1": ("Q1", [1, 2, 3], True), "RPU": ("R39", [1, 2], False),
    "DLED": ("D11", [2, 1], True), "RLED": ("R40", [1, 2], False), "DL2": ("D12", [2, 1], True),
}
SOLO_SIMULACION = {"VCC", "VEE", "V33", "V33A", "CL", "RL"}


def netlist_kicad():
    out = os.path.join(AQUI, "_corridas", "ecualizador_kicad.net")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, SCH],
                   check=True, capture_output=True)
    t = open(out, encoding="utf-8").read()
    pin_red = {}
    for blk in re.split(r"\(net\s*\(code", t[t.find("(nets"):])[1:]:
        red = re.search(r'\(name "([^"]*)"\)', blk).group(1)
        for ref, pin in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
            pin_red[(ref, pin)] = red
    return pin_red


def elementos_ltspice():
    elems = []
    for f in ("eq_audio.inc", "eq_detectores.inc"):
        for linea in open(os.path.join(AQUI, f), encoding="utf-8"):
            linea = linea.strip()
            if not linea or linea[0] in "*.":
                continue
            partes = linea.split()
            nombre = partes[0].upper()
            if nombre in SOLO_SIMULACION:
                continue
            if nombre[0] == "X":
                nodos = partes[1:-1]   # todo menos el nombre del subcircuito
            elif nombre[0] == "Q":
                nodos = partes[1:4]
            else:
                nodos = partes[1:3]
            elems.append((nombre, [n.upper() for n in nodos]))
    return elems


def main():
    pin_red = netlist_kicad()
    elems = elementos_ltspice()
    faltan = [n for n, _ in elems if n not in MAPA]
    if faltan:
        sys.exit(f"Elementos de LTspice sin correspondencia en el mapa: {faltan}")
    lt_a_kicad, kicad_a_lt, errores = {}, {}, []

    def unir(nodo, red, quien):
        if lt_a_kicad.setdefault(nodo, red) != red:
            errores.append(f"{quien}: el nodo {nodo} cae en {red} y tambien en {lt_a_kicad[nodo]}")
        if kicad_a_lt.setdefault(red, nodo) != nodo:
            errores.append(f"{quien}: la red {red} junta los nodos {nodo} y {kicad_a_lt[red]}")

    pendientes = []
    for nombre, nodos in elems:
        ref, pines, polar = MAPA[nombre]
        redes = [pin_red.get((ref, str(p))) for p in pines]
        if None in redes:
            errores.append(f"{nombre} -> {ref}: pin sin red en KiCad ({pines})")
            continue
        if polar:
            for n, r in zip(nodos, redes):
                unir(n, r, f"{nombre}->{ref}")
        else:
            pendientes.append((nombre, ref, nodos, redes))
    # pasivos sin polaridad: se acepta cualquiera de los dos sentidos, el que coincida con lo ya unido
    for _ in range(3):
        resto = []
        for nombre, ref, nodos, redes in pendientes:
            directo = all(lt_a_kicad.get(n, r) == r for n, r in zip(nodos, redes))
            cruzado = all(lt_a_kicad.get(n, r) == r for n, r in zip(nodos, redes[::-1]))
            conocido = any(n in lt_a_kicad for n in nodos)
            if not conocido:
                resto.append((nombre, ref, nodos, redes))
                continue
            if directo:
                orden = redes
            elif cruzado:
                orden = redes[::-1]
            else:
                errores.append(f"{nombre}->{ref}: nodos {nodos} contra redes {redes}")
                continue
            for n, r in zip(nodos, orden):
                unir(n, r, f"{nombre}->{ref}")
        pendientes = resto
    for nombre, ref, nodos, redes in pendientes:
        errores.append(f"{nombre}->{ref}: no se pudo ubicar ({nodos})")

    print(f"Elementos comparados: {len(elems)}  |  nodos de LTspice: {len(lt_a_kicad)}")
    for n in sorted(lt_a_kicad):
        print(f"  {n:7s} -> {lt_a_kicad[n]}")
    if errores:
        print("\nDIFERENCIAS:")
        for e in errores:
            print("  " + e)
        sys.exit(1)
    print("\nOK: cada nodo de LTspice es una sola red de KiCad y cada red de KiCad es un solo nodo.")


if __name__ == "__main__":
    main()
