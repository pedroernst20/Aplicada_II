"""Corre las simulaciones LTspice de la Consigna 6 y exporta los resultados.

Uso (desde esta carpeta, en Windows):  python correr_simulaciones.py

Para cada esquematico .asc genera el netlist con LTspice, lo simula en modo
batch con salida ASCII y procesa el .raw. Escribe en ../informe/datos/
(o en ../datos/ dentro del .zip de la entrega):
  - archivos .dat para las figuras (pgfplots)
  - resultados.tex con un \\newcommand por cada numero citado en el informe
  - resultados.json con los mismos valores
Las corridas se hacen en _corridas/ (no se versiona).
"""
import json
import math
import os
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
TRABAJO = os.path.join(AQUI, "_corridas")
# En el repositorio los datos van a ../informe/datos; en el .zip de la
# entrega el informe esta en la raiz y los datos en ../datos.
DATOS = os.path.normpath(os.path.join(AQUI, "..", "informe", "datos"))
if not os.path.isdir(os.path.join(AQUI, "..", "informe")) and \
        os.path.isdir(os.path.join(AQUI, "..", "datos")):
    DATOS = os.path.normpath(os.path.join(AQUI, "..", "datos"))
LTSPICE = [
    r"C:\Program Files\ADI\LTspice\LTspice.exe",
    r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe",
]


def ltspice():
    for p in LTSPICE:
        if os.path.exists(p):
            return p
    raise SystemExit("No se encontro LTspice")


def correr(asc):
    """Genera el netlist, simula y devuelve la lista de corridas (steps)."""
    exe = ltspice()
    ruta = os.path.join(TRABAJO, asc)
    carpeta, nombre = os.path.split(ruta)
    base = os.path.splitext(nombre)[0]
    subprocess.run([exe, "-netlist", nombre], cwd=carpeta, check=True)
    subprocess.run([exe, "-b", "-ascii", base + ".net"], cwd=carpeta,
                   check=True)
    log = decodificar(os.path.join(carpeta, base + ".log"))
    for mala in ("singular matrix", "Time step too small", "ERROR"):
        if mala.lower() in log.lower():
            raise SystemExit(f"{asc}: {mala}\n{log}")
    return leer_raw(os.path.join(carpeta, base + ".raw"))


def decodificar(ruta):
    """LTspice escribe .log y .raw en UTF-16 o en ASCII segun el archivo."""
    with open(ruta, "rb") as f:
        crudo = f.read()
    txt = crudo.decode("utf-16-le") if b"\x00" in crudo[:40] else \
        crudo.decode("latin-1")
    return txt.replace("\r\n", "\n")


def leer_raw(ruta):
    txt = decodificar(ruta)
    cab, valores = txt.split("Values:\n", 1)
    nombres = []
    en_vars = False
    for linea in cab.splitlines():
        if linea.startswith("Variables:"):
            en_vars = True
            continue
        if en_vars and linea.strip():
            nombres.append(linea.split("\t")[2])
    nv = len(nombres)
    numeros = []
    for linea in valores.splitlines():
        partes = linea.strip().split("\t")
        if not partes or partes == [""]:
            continue
        v = partes[-1]
        if "," in v:  # complejo
            re, im = v.split(",")
            numeros.append(complex(float(re), float(im)))
        else:
            numeros.append(float(v))
    puntos = [numeros[i:i + nv] for i in range(0, len(numeros), nv)]
    # separar corridas de un .step: la escala vuelve a empezar
    corridas, actual = [], []
    for p in puntos:
        if actual and p[0] == puntos[0][0] and len(actual) > 1:
            corridas.append(actual)
            actual = []
        actual.append(p)
    corridas.append(actual)
    return [{n: [p[k] for p in c] for k, n in enumerate(nombres)}
            for c in corridas]


def interp(xs, ys, x):
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        if (a - x) * (b - x) <= 0 and a != b:
            return ys[i] + (ys[i + 1] - ys[i]) * (x - a) / (b - a)
    raise ValueError(f"{x} fuera de rango")


def cruce(xs, ys, nivel):
    """Primer x en que ys cruza nivel."""
    for i in range(len(xs) - 1):
        if (ys[i] - nivel) * (ys[i + 1] - nivel) <= 0 and ys[i] != ys[i + 1]:
            return xs[i] + (xs[i + 1] - xs[i]) * (nivel - ys[i]) / \
                (ys[i + 1] - ys[i])
    raise ValueError("sin cruce")


def pp(ys):
    return max(ys) - min(ys)


def rms_ac(ts, ys):
    """Valor eficaz de la componente alterna (integracion trapecial)."""
    T = ts[-1] - ts[0]
    media = sum((ys[i] + ys[i + 1]) / 2 * (ts[i + 1] - ts[i])
                for i in range(len(ts) - 1)) / T
    cuad = sum((((ys[i] - media) ** 2 + (ys[i + 1] - media) ** 2) / 2)
               * (ts[i + 1] - ts[i]) for i in range(len(ts) - 1)) / T
    return math.sqrt(cuad)


def guardar_dat(nombre, columnas, filas, cada=1):
    with open(os.path.join(DATOS, nombre), "w", encoding="ascii") as f:
        f.write(" ".join(columnas) + "\n")
        for i, fila in enumerate(filas):
            if i % cada == 0 or i == len(filas) - 1:
                f.write(" ".join(f"{v:.6g}" for v in fila) + "\n")


R = {}  # resultados numericos


def main():
    if os.path.exists(TRABAJO):
        shutil.rmtree(TRABAJO)
    shutil.copytree(AQUI, TRABAJO, ignore=shutil.ignore_patterns(
        "_corridas", "*.py", "*.raw", "*.log", "*.net"))
    os.makedirs(DATOS, exist_ok=True)

    # ---------------- validacion del modelo LM7805 -----------------------
    v1 = correr(os.path.join("validacion_7805", "v1_linea.asc"))
    a, b = v1[0], v1[1]                      # IL = 0,5 A y 1 A
    vi, vo = a["V1"], a["V(vo)"]
    R["valVo"] = interp(vi, vo, 10)
    R["valLineaAmplia"] = (interp(vi, vo, 25) - interp(vi, vo, 7)) * 1e3
    R["valLineaCentral"] = (interp(vi, vo, 12) - interp(vi, vo, 8)) * 1e3
    R["valIq"] = (-interp(vi, a["I(V1)"], 10) - 0.5) * 1e3
    vnom1 = interp(b["V1"], b["V(vo)"], 10)
    vi_do = cruce(b["V1"], b["V(vo)"], vnom1 - 0.1)
    R["valDropout"] = vi_do - (vnom1 - 0.1)
    guardar_dat("val_linea.dat", ["vi", "vo05", "vo1"],
                list(zip(vi, vo, b["V(vo)"])), cada=10)

    v2 = correr(os.path.join("validacion_7805", "v2_carga.asc"))[0]
    il, vo = v2["IL1"], v2["V(vo)"]
    R["valCargaAmplia"] = (interp(il, vo, 0.005) - interp(il, vo, 1.5)) * 1e3
    R["valCargaCentral"] = (interp(il, vo, 0.25) - interp(il, vo, 0.75)) * 1e3

    v3 = correr(os.path.join("validacion_7805", "v3_rizado.asc"))[0]
    R["valRR"] = 20 * math.log10(pp(v3["V(vi)"]) / pp(v3["V(vo)"]))

    v4 = correr(os.path.join("validacion_7805", "v4_temperatura.asc"))[0]
    t, vo = v4["temperature"], v4["V(vo)"]
    R["valTempco"] = (interp(t, vo, 125) - interp(t, vo, 0)) / 125 * 1e3

    v5 = correr(os.path.join("validacion_7805", "v5_cortocircuito.asc"))[0]
    vi, isc = v5["V1"], v5["I(RL1)"]
    R["valIscDiez"] = interp(vi, isc, 10)
    R["valIscVeinticinco"] = interp(vi, isc, 25)
    R["valIscTreintaycinco"] = interp(vi, isc, 35)

    # ---------------- VBE del TIP122 contra la hoja de datos -------------
    # Curva "VBE @ VCE = 4,0 V" de la Fig. 11 de la hoja de datos TIP120/D
    # (TJ = 25 C), digitalizada de la imagen del PDF a 300 dpi.
    HOJA_VBE = [(0.12, 1.254), (0.2, 1.283), (0.3, 1.312), (0.5, 1.354),
                (0.8, 1.404), (1.0, 1.438), (1.5, 1.506), (2.0, 1.577),
                (3.0, 1.698), (5.0, 1.994)]
    B = correr(os.path.join("validacion_tip122", "vbe_tip122.asc"))[0]
    vb = B["VB"]
    ic_or = [-x for x in B["I(VC1)"]]
    ic_aj = [-x for x in B["I(VC2)"]]
    vbe_or = lambda i: interp(ic_or, vb, i)
    vbe_aj = lambda i: interp(ic_aj, vb, i)
    R["VbeHojaMedio"] = dict(HOJA_VBE)[0.5]
    R["VbeOrigMedio"] = vbe_or(0.5)
    R["VbeAjMedio"] = vbe_aj(0.5)
    R["VbeErrMaxAj"] = max(abs(vbe_aj(i) - v) for i, v in HOJA_VBE
                           if i <= 3) * 1e3
    R["VbeErrMaxOrig"] = max(abs(vbe_or(i) - v) for i, v in HOJA_VBE
                             if i <= 3) * 1e3
    corrientes = [0.01 * 10 ** (k / 40) for k in range(101)]   # 10 mA a 3 A
    corrientes = [i for i in corrientes if i <= 3.0]
    guardar_dat("vbe_tip122.dat", ["ic", "vbeorig", "vbeaj"],
                [(i, vbe_or(i), vbe_aj(i)) for i in corrientes])
    guardar_dat("vbe_hoja.dat", ["ic", "vbe"], HOJA_VBE)

    # ---------------- regulacion de linea --------------------------------
    L = correr("c6_linea.asc")[0]
    vp = L["V1"]
    f = {k: (lambda x, k=k: interp(vp, L[k], x)) for k in L}
    R["ViregVeinticinco"] = f["V(vireg)"](25)
    R["ViregDiez"] = f["V(vireg)"](10)
    R["ViregMin"] = f["V(vireg)"](22.5)
    R["ViregMax"] = f["V(vireg)"](27.5)
    R["VbVeinticinco"] = f["V(b)"](25)
    R["VbeVeinticinco"] = f["V(b)"](25) - f["V(vireg)"](25)
    R["VoVeinticinco"] = f["V(vo)"](25)
    R["VoSinVeinticinco"] = f["V(vo_sin)"](25)
    R["IzVeinticinco"] = -f["I(DZ)"](25) * 1e3
    R["IrzVeinticinco"] = f["I(RZ)"](25) * 1e3
    R["IbVeinticinco"] = f["Ix(q1:2)"](25) * 1e3
    R["VceVeinticinco"] = 25 - R["ViregVeinticinco"]
    # rango de Vp en que Vi,reg queda en la ventana 8-12 V
    R["VpVentana"] = cruce(vp, L["V(vireg)"], 8.0)
    # regulacion de red, Ec. 6-41 (variacion de +-10 % de la primaria)
    def rred(k, vmin, vmax):
        a, b = f[k](vmin), f[k](vmax)
        return (b - a) * 1e6, (b - a) / a * 100
    R["dVoCon"], R["RredCon"] = rred("V(vo)", 22.5, 27.5)
    R["dVoSin"], R["RredSin"] = rred("V(vo_sin)", 22.5, 27.5)
    R["dVoSinDiez"], R["RredSinDiez"] = rred("V(vo_sin)", 9.0, 11.0)
    R["dViregCon"] = (f["V(vireg)"](27.5) - f["V(vireg)"](22.5)) * 1e3
    R["MejoraLinea"] = R["dVoSin"] / R["dVoCon"]
    # excursion completa de la primaria 10 V -> 25 V
    R["dVoCompleta"] = (f["V(vo)"](25) - f["V(vo)"](10)) * 1e6
    R["dVoSinCompleta"] = (f["V(vo_sin)"](25) - f["V(vo_sin)"](10)) * 1e6
    # rendimiento (Ec. 6-68) en la condicion nominal
    pin = 25 * (f["I(RZ)"](25) + f["Ix(q1:1)"](25))
    pl = f["V(vo)"](25) * 0.5
    R["PinVeinticinco"] = pin
    R["PlVeinticinco"] = pl
    R["Rendimiento"] = pl / pin * 100
    R["RendimientoSin"] = (f["V(vo_sin)"](25) * 0.5
                           / (25 * f["Ix(u2:1)"](25)) * 100)
    R["PqVeinticinco"] = R["VceVeinticinco"] * f["Ix(q1:1)"](25)
    R["PregVeinticinco"] = (f["V(vireg)"](25) * f["Ix(u1:1)"](25)
                            - f["V(vo)"](25) * 0.5)
    R["PregSinVeinticinco"] = (25 * f["Ix(u2:1)"](25)
                               - f["V(vo_sin)"](25) * 0.5)
    guardar_dat("linea.dat", ["vp", "vb", "vireg", "vo", "vosin"],
                list(zip(vp, L["V(b)"], L["V(vireg)"], L["V(vo)"],
                         L["V(vo_sin)"])), cada=10)
    # detalle de la salida alrededor de 25 V y de 10 V (en mV respecto
    # del valor nominal de cada caso)
    filas = [(x, (f["V(vo)"](x) - R["VoVeinticinco"]) * 1e3,
              (f["V(vo_sin)"](x) - R["VoSinVeinticinco"]) * 1e3)
             for x in [9 + 0.1 * k for k in range(200)]]
    guardar_dat("linea_detalle.dat", ["vp", "dvocon", "dvosin"], filas)

    # ---------------- tolerancia del Zener -------------------------------
    T = correr("c6_tolerancia.asc")
    for nombre, c in zip(("Bajo", "Nom", "Alto"), T):
        R[f"ViregTol{nombre}"] = interp(c["V1"], c["V(vireg)"], 25)
        R[f"ViregTolDiez{nombre}"] = interp(c["V1"], c["V(vireg)"], 10)

    # ---------------- regulacion de carga --------------------------------
    C = correr("c6_carga.asc")[0]
    il = C["IL1"]
    g = {k: (lambda x, k=k: interp(il, C[k], x)) for k in C}
    R["VoVacio"] = g["V(vo)"](0)
    R["VoPlena"] = g["V(vo)"](0.5)
    R["dVoCarga"] = (R["VoVacio"] - R["VoPlena"]) * 1e3
    R["Rcar"] = (R["VoVacio"] - R["VoPlena"]) / R["VoPlena"] * 100
    R["Rsal"] = (R["VoVacio"] - R["VoPlena"]) / 0.5 * 1e3  # mOhm
    R["IzPlena"] = -g["I(DZ)"](0.5) * 1e3
    R["IzVacio"] = -g["I(DZ)"](0) * 1e3
    R["IbPlena"] = g["Ix(q1:2)"](0.5) * 1e3
    R["ViregVacio"] = g["V(vireg)"](0)
    R["ViregPlena"] = g["V(vireg)"](0.5)
    R["ViregUnAmper"] = g["V(vireg)"](1.0)
    R["VoUnAmper"] = g["V(vo)"](1.0)
    R["VoUnoCinco"] = g["V(vo)"](1.5)
    pq = [(25 - C["V(vireg)"][i]) * C["Ix(q1:1)"][i] for i in range(len(il))]
    preg = [C["V(vireg)"][i] * C["Ix(u1:1)"][i] - C["V(vo)"][i] * il[i]
            for i in range(len(il))]
    R["PqPlena"] = interp(il, pq, 0.5)
    R["PregPlena"] = interp(il, preg, 0.5)
    R["PqUnAmper"] = interp(il, pq, 1.0)
    R["PregUnAmper"] = interp(il, preg, 1.0)
    guardar_dat("carga.dat", ["il", "vo", "vireg", "pq", "preg"],
                list(zip(il, C["V(vo)"], C["V(vireg)"], pq, preg)), cada=10)

    # ---------------- rizado ---------------------------------------------
    Z = correr("c6_rizado.asc")[0]
    t = Z["time"]
    vr = {k: pp(Z[k]) for k in ("V(vp)", "V(vireg)", "V(vo)", "V(vo_sin)")}
    R["VrIn"] = vr["V(vp)"]
    R["VrVireg"] = vr["V(vireg)"] * 1e3
    R["VrOut"] = vr["V(vo)"] * 1e6
    R["VrOutSin"] = vr["V(vo_sin)"] * 1e6
    R["VefOut"] = rms_ac(t, Z["V(vo)"]) * 1e6
    R["VefOutSin"] = rms_ac(t, Z["V(vo_sin)"]) * 1e6
    R["RRPre"] = 20 * math.log10(vr["V(vp)"] / vr["V(vireg)"])
    R["RRReg"] = 20 * math.log10(vr["V(vireg)"] / vr["V(vo)"])
    R["RRTotal"] = 20 * math.log10(vr["V(vp)"] / vr["V(vo)"])
    R["RRSin"] = 20 * math.log10(vr["V(vp)"] / vr["V(vo_sin)"])
    R["FactorRizo"] = R["VefOut"] * 1e-6 / R["VoVeinticinco"] * 100
    t0 = t[0]
    m_vp = sum(Z["V(vp)"]) / len(t)
    m_vi = sum(Z["V(vireg)"]) / len(t)
    m_vo = sum(Z["V(vo)"]) / len(t)
    m_vs = sum(Z["V(vo_sin)"]) / len(t)
    filas = [((t[i] - t0) * 1e3, Z["V(vp)"][i] - m_vp,
              (Z["V(vireg)"][i] - m_vi) * 1e3, (Z["V(vo)"][i] - m_vo) * 1e6,
              (Z["V(vo_sin)"][i] - m_vs) * 1e6) for i in range(len(t))]
    guardar_dat("rizado.dat", ["t", "vp", "vireg", "vo", "vosin"], filas,
                cada=max(1, len(filas) // 800))

    # ---------------- temperatura ----------------------------------------
    Q = correr("c6_temperatura.asc")[0]
    tt = Q["temperature"]
    h = {k: (lambda x, k=k: interp(tt, Q[k], x)) for k in Q}
    for clave, nodo in (("Con", "V(vo)"), ("Sin", "V(vo_sin)")):
        v0, v55, v25 = h[nodo](0), h[nodo](55), h[nodo](25)
        R[f"CT{clave}"] = (v55 - v0) / (55 * v25) * 100        # %/C
        R[f"CTmV{clave}"] = (v55 - v0) / 55 * 1e3              # mV/C
    R["dViregTemp"] = (h["V(vireg)"](55) - h["V(vireg)"](0)) / 55 * 1e3
    guardar_dat("temperatura.dat", ["t", "vo", "vosin", "vireg"],
                list(zip(tt, Q["V(vo)"], Q["V(vo_sin)"], Q["V(vireg)"])),
                cada=2)

    # ---------------- cortocircuito --------------------------------------
    K = correr("c6_cortocircuito.asc")[0]
    R["IscCorto"] = K["I(RL1)"][0]
    R["ViregCorto"] = K["V(vireg)"][0]
    R["PqCorto"] = (25 - K["V(vireg)"][0]) * K["Ix(q1:1)"][0]
    R["PregCorto"] = K["V(vireg)"][0] * K["Ix(u1:1)"][0]
    R["VceCorto"] = 25 - K["V(vireg)"][0]

    # ---------------- temperatura de juntura del TIP122 ------------------
    # Ta = 40 C, R(j-mb) = 1,92 C/W, mica y grasa 1,3 C/W, ZD-28 2,9 C/W
    R["TjQNominal"] = 40 + R["PqVeinticinco"] * (1.92 + 1.3 + 2.9)

    # ---------------- exportar -------------------------------------------
    with open(os.path.join(DATOS, "resultados.json"), "w") as fj:
        json.dump(R, fj, indent=2, sort_keys=True)
    with open(os.path.join(DATOS, "resultados.tex"), "w",
              encoding="ascii") as ft:
        ft.write("% Generado por simulacion/correr_simulaciones.py\n")
        for k in sorted(R):
            ft.write(f"\\newcommand{{\\sim{k}}}{{{R[k]:.6g}}}\n")
    for k in sorted(R):
        print(f"{k:24s} {R[k]:.6g}")


if __name__ == "__main__":
    main()
