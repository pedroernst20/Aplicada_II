"""Espeja un Gerber de KiCad de izquierda a derecha (cara de abajo vista desde abajo, para el que fresa).
El eje es vertical, en x = eje_mm (coordenadas del Gerber); con el centro de la placa, el contorno queda en su lugar.
Sirve para los Gerbers de cobre de KiCad sin arcos: espeja las coordenadas X y las esquinas de las aperturas
RoundRect; las aperturas C, R y O son simetricas. Si encuentra arcos o aperturas que no conoce, corta con error.
Uso: python espejar_gerber.py entrada.gbl salida.gbl eje_mm"""
import re
import sys

ENT, SAL, EJE = sys.argv[1], sys.argv[2], float(sys.argv[3])
t = open(ENT, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"

fs = re.search(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%", t)
if not fs or "%MOMM*%" not in t:
    sys.exit("formato no soportado (se espera FSLAX..Y.. en mm)")
dec = int(fs.group(2))
eje = round(EJE * 10 ** dec)
if re.search(r"^G0?[23]\b|^G7[45]\*", t, re.M) or re.search(r"[IJ]-?\d+D0", t):
    sys.exit("el archivo tiene arcos: este script no los espeja")

for m in re.finditer(r"^%ADD\d+([A-Za-z_]+)", t, re.M):
    if m.group(1) not in ("C", "R", "O", "RoundRect"):
        sys.exit(f"apertura no soportada: {m.group(1)}")


def roundrect(m):
    # radio, x1, y1, x2, y2, x3, y3, x4, y4, rotacion -> se niegan las x
    p = m.group(2).split("X")
    if len(p) != 10 or float(p[9]) != 0:
        sys.exit("RoundRect con rotacion o formato inesperado")
    for k in (1, 3, 5, 7):
        v = -float(p[k])
        p[k] = f"{v:.6f}" if v != 0 else "0.000000"
    return f"{m.group(1)}{'X'.join(p)}*%"


t = re.sub(r"^(%ADD\d+RoundRect,)([^*]+)\*%", roundrect, t, flags=re.M)
n = 0


def coord(m):
    global n
    n += 1
    return f"X{eje * 2 - int(m.group(1))}"


lineas = []
for ln in t.split(nl):
    if ln.startswith(("X", "Y", "G01X", "G01Y")) and ln.endswith("*") and not ln.startswith("%"):
        ln = re.sub(r"X(-?\d+)", coord, ln)
    lineas.append(ln)
t = nl.join(lineas)
t = t.replace("%TF.FileFunction,", f"G04 ESPEJADO de izquierda a derecha (visto desde abajo), eje x = {EJE} mm*{nl}%TF.FileFunction,", 1)
open(SAL, "w", encoding="utf-8", newline="").write(t)
print("coordenadas espejadas:", n)
