"""Corre las simulaciones del TP2 con ngspice y exporta los resultados.

Uso (desde esta carpeta):  python3 correr_simulaciones.py

El circuito completo esta en tp2_circuito.cir (se abre tal cual en LTspice).
Este script arma, para cada analisis, un netlist en _corridas/ con el
circuito (cambiando los .param que hagan falta) y el bloque .control de
ngspice, lo simula y procesa los resultados. Escribe en ../informe/datos/:
  - archivos .dat para las figuras (pgfplots)
  - resultados.tex con un \\newcommand por cada numero citado en el informe
  - resultados.json con los mismos valores
"""
import json
import math
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
TRABAJO = os.path.join(AQUI, "_corridas")
DATOS = os.path.normpath(os.path.join(AQUI, "..", "informe", "datos"))
MEDICIONES = os.path.normpath(os.path.join(AQUI, "..", "mediciones"))

F0 = 4300.0          # frecuencia de diseno [Hz]
T0 = 1.0 / F0        # periodo de diseno [s]
RES = {}             # resultados numericos -> resultados.tex


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def circuito(diodo="D1N4004", **params):
    """Texto del circuito completo con los .param cambiados."""
    with open(os.path.join(AQUI, "tp2_circuito.cir"), encoding="utf-8") as f:
        txt = f.read()
    txt = txt.replace(".include modelos_tp2.lib", ".include ../modelos_tp2.lib")
    for k, v in params.items():
        txt, n = re.subn(r"(\.param[^\n]*\b%s=)(\S+)" % k, r"\g<1>%s" % v, txt)
        if n != 1:
            raise SystemExit(f"parametro {k} no encontrado")
    txt = txt.replace("D1N4004", diodo)
    return "\n".join(l for l in txt.splitlines() if l.strip() != ".end")


def correr(nombre, cuerpo, control):
    """Escribe _corridas/<nombre>.cir, lo simula y devuelve el log."""
    ruta = os.path.join(TRABAJO, nombre + ".cir")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"* {nombre}\n{cuerpo}\n.control\n{control}\n.endc\n.end\n")
    p = subprocess.run(["ngspice", "-b", nombre + ".cir"], cwd=TRABAJO,
                       capture_output=True, text=True)
    log = p.stdout + p.stderr
    for mala in ("Timestep too small", "singular matrix", "aborted",
                 "doAnalyses: TRAN:  Timestep", "ERROR:", "Error on line"):
        if mala.lower() in log.lower():
            raise SystemExit(f"{nombre}: {mala}\n{log[-3000:]}")
    return log


def leer(nombre):
    """Lee un archivo de wrdata: devuelve (x, [y1, y2, ...])."""
    d = np.atleast_2d(np.loadtxt(os.path.join(TRABAJO, nombre)))
    x = d[:, 0]
    return x, [d[:, 2 * i + 1] for i in range(d.shape[1] // 2)]


def guardar(nombre, cabecera, columnas, fmt="%.6g"):
    np.savetxt(os.path.join(DATOS, nombre), np.column_stack(columnas),
               header=cabecera, comments="", fmt=fmt)


def ultimos_periodos(t, vs, n=2, f=F0, fase=0.0):
    """Recorta los ultimos n periodos. fase: corrimiento en segundos."""
    t_ini = t[-1] - n / f
    m = t >= t_ini
    return t[m] - t_ini + fase, [v[m] for v in vs]


def remuestrear(t, vs, dt):
    tn = np.arange(t[0], t[-1], dt)
    return tn, [np.interp(tn, t, v) for v in vs]


def meseta(t, v, t0, t1):
    """Mediana de v en [t0, t1]."""
    m = (t >= t0) & (t <= t1)
    return float(np.median(v[m]))


def cruce(t, v, nivel, subida=True, desde=0.0):
    """Primer instante (interpolado) en que v cruza nivel despues de 'desde'."""
    m = t >= desde
    tt, vv = t[m], v[m]
    s = (vv >= nivel) if subida else (vv <= nivel)
    i = np.argmax(s[1:] & ~s[:-1]) + 1
    if i == 1 and not (s[1] and not s[0]):
        return float("nan")
    return float(tt[i - 1] + (nivel - vv[i - 1]) * (tt[i] - tt[i - 1]) /
                 (vv[i] - vv[i - 1]))


# ---------------------------------------------------------------------------
# A. Simulacion nominal del circuito completo
# ---------------------------------------------------------------------------
TRAN_LARGO = "tran 50n 60m 58.8m 0.1u uic"
VEC_TODOS = "v(in) v(s1) v(int) v(s2) v(der) v(s3) v(vp) v(va) v(s4) v(vref1) v(vref2)"


def nominal():
    # Paso 1: con P3 en 3,8 kOhm se mide el pico de la senal 4.
    rp3 = 3.8e3
    for paso in (1, 2):
        cuerpo = circuito(RP3=f"{rp3:.1f}")
        correr("nominal", cuerpo,
               f"{TRAN_LARGO}\nwrdata nominal.txt {VEC_TODOS}")
        t, v = leer("nominal.txt")
        tt, vv = ultimos_periodos(t, v, 3)
        pico = vv[8].max()
        if paso == 1:
            # La ganancia del sumador es (10k + P3)/20k: se escala P3.
            rp3 = (10e3 + rp3) * 1.0 / pico - 10e3
    RES["simPtres"] = rp3 / 1e3
    nombres = ["in", "s1", "int", "s2", "der", "s3", "vp", "va", "s4",
               "vref1", "vref2"]
    S = dict(zip(nombres, vv))
    # Origen de tiempo: flanco de subida de la senal 1 (cruce de 0,25 V)
    tf = cruce(tt, S["s1"], 0.25, True, 0.25 * T0)
    tr = tt - tf
    # Se guardan dos periodos completos desde t = -T/4
    m = (tr >= -0.25 * T0) & (tr <= 1.75 * T0)
    tg, vg = remuestrear(tr[m], [S[k][m] for k in ("in", "s1", "s2", "s3",
                                                   "s4", "der", "vp", "va",
                                                   "int")], 0.1e-6)
    guardar("nominal.dat", "t in s1 s2 s3 s4 der vp va int",
            [tg * 1e6] + vg)

    s1, s2, s3, s4 = S["s1"], S["s2"], S["s3"], S["s4"]
    # Senal 1: mesetas
    RES["simSunoAlto"] = meseta(tr, s1, 0.2 * T0, 0.45 * T0)
    RES["simSunoBajo"] = meseta(tr, s1, 0.7 * T0, 0.95 * T0)
    RES["simVrefUno"] = float(np.mean(S["vref1"]))
    RES["simVrefDos"] = float(np.mean(S["vref2"]))
    # Senal 2
    RES["simSdosMax"] = float(s2.max())
    RES["simSdosMin"] = float(s2.min())
    RES["simSdosMed"] = float(np.mean(s2))
    RES["simSdosVpp"] = float(s2.max() - s2.min())
    # Linealidad de la rampa ascendente (entre 10 % y 90 % del semiperiodo)
    mr = (tr > 0.05 * T0) & (tr < 0.45 * T0)
    p = np.polyfit(tr[mr], s2[mr], 1)
    RES["simPendSubida"] = p[0] / 1e3          # V/ms
    RES["simNoLinSdos"] = float(np.max(np.abs(s2[mr] - np.polyval(p, tr[mr])))
                                / RES["simSdosVpp"] * 100)
    mb = (tr > 0.55 * T0) & (tr < 0.95 * T0)
    pb = np.polyfit(tr[mb], s2[mb], 1)
    RES["simPendBajada"] = pb[0] / 1e3
    # Minimo de la triangular respecto del flanco de la senal 1
    i0 = np.argmin(np.where((tr > -0.2 * T0) & (tr < 0.2 * T0), s2, 1e9))
    RES["simRetMinTri"] = float(tr[i0] * 1e6)
    # Senal 3
    RES["simStresAlto"] = meseta(tr, s3, 0.25 * T0, 0.45 * T0)
    RES["simStresBajo"] = meseta(tr, s3, 0.75 * T0, 0.95 * T0)
    h, l = RES["simStresAlto"], RES["simStresBajo"]
    t10 = cruce(tr, s3, l + 0.1 * (h - l), True, -0.2 * T0)
    t90 = cruce(tr, s3, l + 0.9 * (h - l), True, -0.2 * T0)
    t50 = cruce(tr, s3, l + 0.5 * (h - l), True, -0.2 * T0)
    RES["simStresSubida"] = (t90 - t10) * 1e6
    RES["simStresRetardo"] = t50 * 1e6
    RES["simStresSobrepico"] = (s3[(tr > 0) & (tr < 0.25 * T0)].max() - h) / (h - l) * 100
    f10 = cruce(tr, s3, l + 0.9 * (h - l), False, 0.3 * T0)
    f90 = cruce(tr, s3, l + 0.1 * (h - l), False, 0.3 * T0)
    RES["simStresBajadaT"] = (f90 - f10) * 1e6
    # Inclinacion de la meseta (caida de la parte alta)
    RES["simStresInclin"] = (meseta(tr, s3, 0.15 * T0, 0.2 * T0) -
                             meseta(tr, s3, 0.45 * T0, 0.49 * T0)) * 1e3
    # Senal 4: picos en flanco de subida y de bajada de la senal 3
    w1 = (tr > -0.1 * T0) & (tr < 0.3 * T0)
    w2 = (tr > 0.4 * T0) & (tr < 0.8 * T0)
    RES["simScuatroPicoSub"] = float(s4[w1].max())
    RES["simScuatroPicoBaj"] = float(s4[w2].max())
    # Constante de caida: desde el pico hasta 1/e
    for nom, w in (("simScuatroTauSub", w1), ("simScuatroTauBaj", w2)):
        tw, vw = tr[w], s4[w]
        ip = np.argmax(vw)
        pk = vw[ip]
        j = ip + np.argmax(vw[ip:] < pk / math.e)
        RES[nom] = (tw[j] - tw[ip]) * 1e6
        # ancho a media altura
        a = tw[np.argmax(vw > pk / 2)]
        b = tw[ip + np.argmax(vw[ip:] < pk / 2)]
        RES[nom.replace("Tau", "Ancho")] = (b - a) * 1e6
    RES["simScuatroMin"] = float(s4.min())
    RES["simScuatroResid"] = float(np.median(s4[(tr > 0.25 * T0) & (tr < 0.45 * T0)]))
    # Frecuencia y pendiente teorica
    RES["simFrec"] = F0


# ---------------------------------------------------------------------------
# B. Circuito con la entrada y el ajuste de P2 que se midieron en la placa
# ---------------------------------------------------------------------------
def medida(med):
    vbajo, valto, fmed = med["inBajo"], med["inAlto"], med["frec"]
    # P2 ajustado para que la senal 1 reproduzca la meseta baja medida
    vref1 = vbajo - med["s1Bajo"]
    vz = RES["simVz"]
    alfa2 = vref1 / vz
    RES["simAjVrefUno"] = vref1
    # Condiciones iniciales de regimen para CC y C1
    media_s1 = (vbajo + valto) / 2 - vref1
    vpp = (valto - vbajo) / 2 * (0.5 / fmed) / (5.6e3 * 4.7e-9)
    cuerpo = circuito(VALTO=f"{valto - vbajo:.4f}", FREQ=f"{fmed:.1f}",
                      ALFA2=f"{alfa2:.5f}", RP3=f"{RES['simPtres'] * 1e3:.1f}",
                      VCCI=f"{media_s1 - 1.25:.4f}", VC1I=f"{-vpp / 2:.4f}")
    cuerpo = cuerpo.replace("VGEN in 0 PULSE(0 {VALTO}",
                            f"VGEN in 0 PULSE({vbajo} {{{vbajo}+VALTO}}")
    correr("medida", cuerpo, f"{TRAN_LARGO}\nwrdata medida.txt v(in) v(s1) v(s2) v(s3) v(s4)")
    t, v = leer("medida.txt")
    T = 1 / fmed
    tt, vv = ultimos_periodos(t, v, 4, fmed)
    S = dict(zip(["in", "s1", "s2", "s3", "s4"], vv))
    RES["simMedSunoAlto"] = float(np.percentile(S["s1"], 95))
    RES["simMedSunoBajo"] = float(np.percentile(S["s1"], 5))
    RES["simMedSdosMax"] = float(S["s2"].max())
    RES["simMedSdosMin"] = float(S["s2"].min())
    RES["simMedSdosVpp"] = RES["simMedSdosMax"] - RES["simMedSdosMin"]
    RES["simMedSdosMed"] = float(np.mean(S["s2"][tt > tt[-1] - 2 * T]))
    return tt, S


# ---------------------------------------------------------------------------
# C. Integrador: tres variantes, y sensibilidad a un error en el valor medio
# ---------------------------------------------------------------------------
INTEG = """.include ../modelos_tp2.lib
VCCP vcc 0 12
VCCN 0 vee 12
VREF vref2 0 1.25
VM vm 0 0.25
VS1 s1 0 PULSE({lo} {hi} 0 50n 50n {pw} {per})
{red}
R6 int n3 10k
R7 n3 s2 10k
XU2 vref2 n3 vcc vee s2 TL084
"""
RED_CC = """CC s1 ci 1u IC={vcc}
RI ci n2 5.6k
C1 n2 int 4.7n IC=-2.75
RF n2 int 1Meg
XU1 vref2 n2 vcc vee int TL084"""
# Acoplamiento en continua: la entrada (+) se lleva al valor medio de la
# senal 1 (0,25 V) y la salida se corre a 1,25 V con el inversor.
RED_DC = """RI s1 n2 5.6k
C1 n2 int 4.7n IC={c1ic}
RF n2 int {rf}
XU1 vm n2 vcc vee int TL084"""


def integrador():
    per = T0
    pw = 0.5 * per - 50e-9
    casos = {
        "dc10": RED_DC.format(rf="56k", c1ic="-2.75"),
        "dc100": RED_DC.format(rf="560k", c1ic="-2.75"),
        "ac": RED_CC.format(vcc="-1.0"),
    }
    trabajos = []
    for nom, red in casos.items():
        for err in (0.0, 0.05):
            lo, hi = -1.0 + err, 1.5 + err
            cuerpo = INTEG.format(lo=lo, hi=hi, pw=pw, per=per, red=red)
            if nom.startswith("dc"):
                # El inversor de salida se referencia a 0,25 V para que la
                # triangular quede centrada en 1,25 V: s2 = 2*0,75 - int
                cuerpo = cuerpo.replace("XU2 vref2 n3", "XU2 v075 n3")
                cuerpo += "VB v075 0 0.75\n"
            else:
                cuerpo = cuerpo.replace("IC=-1.0", f"IC={-1.0 + err:.3f}")
            trabajos.append((f"integ_{nom}_{int(err * 1000)}", cuerpo))
    ctrl = "tran 20n 60m 0 0.2u uic\nwrdata {n}.txt v(s1) v(s2)"
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda tr: correr(tr[0], tr[1], ctrl.format(n=tr[0])),
                    trabajos))
    curvas = []
    for nom in casos:
        for err in (0, 50):
            t, (s1, s2) = leer(f"integ_{nom}_{err}.txt")
            tt, (a, b) = ultimos_periodos(t, [s1, s2], 1)
            vpp = b.max() - b.min()
            med = (b.max() + b.min()) / 2
            # no linealidad de la rampa de subida (s1 en alto)
            alto = a > 0.25 + err / 1000
            ts, bs = tt[alto], b[alto]
            q = (ts > ts[0] + 0.05 * T0) & (ts < ts[-1] - 0.05 * T0)
            p = np.polyfit(ts[q], bs[q], 1)
            nl = np.max(np.abs(bs[q] - np.polyval(p, ts[q]))) / vpp * 100
            # pendiente al principio y al final de la rampa
            k = len(ts)
            p1 = np.polyfit(ts[q][:k // 6], bs[q][:k // 6], 1)[0]
            p2 = np.polyfit(ts[q][-k // 6:], bs[q][-k // 6:], 1)[0]
            clave = {"dc10": "DcDiez", "dc100": "DcCien", "ac": "Ac"}[nom]
            suf = "" if err == 0 else "Err"
            RES[f"simInt{clave}Vpp{suf}"] = vpp
            RES[f"simInt{clave}Centro{suf}"] = med
            RES[f"simInt{clave}Max{suf}"] = float(b.max())
            RES[f"simInt{clave}Min{suf}"] = float(b.min())
            if err == 0:
                RES[f"simInt{clave}NoLin"] = nl
                RES[f"simInt{clave}Pend"] = p2 / p1
            # curva para la figura: un periodo desde el flanco de subida de s1
            umbral = 0.25 + err / 1000
            i0 = np.argmax((a[1:] > umbral) & (a[:-1] <= umbral)) + 1
            tq = np.r_[tt[i0:] - tt[i0], tt[:i0] + tt[-1] - tt[i0]]
            bq = np.r_[b[i0:], b[:i0]]
            o = np.argsort(tq)
            tg, (bg,) = remuestrear(tq[o], [bq[o]], 0.5e-6)
            curvas.append(bg)
    n = min(len(c) for c in curvas)
    guardar("integrador.dat", "t dc10 dc10e dc100 dc100e ac ace",
            [tg[:n] * 1e6] + [c[:n] for c in curvas])
    for clave in ("DcDiez", "DcCien", "Ac"):
        RES[f"simInt{clave}Corr"] = (RES[f"simInt{clave}CentroErr"] -
                                     RES[f"simInt{clave}Centro"])


# ---------------------------------------------------------------------------
# D. Derivador: respuesta en frecuencia y respuesta al vertice de la triangular
# ---------------------------------------------------------------------------
DERIV = """.include ../modelos_tp2.lib
VCCP vcc 0 12
VCCN 0 vee 12
VT s2 0 DC 0 AC 1 PULSE(-1.5 4 0 116.28u 116.28u 10n 232.57u)
RS s2 cd {rs}
CD cd n4 1n
RD n4 der 31.6k
CF n4 der {cf}
XU 0 n4 vcc vee der TL084
"""


def derivador():
    casos = {"sin": ("1m", "1f"), "rs": ("1k", "1f"), "con": ("1k", "56p")}
    trabajos = []
    for nom, (rs, cf) in casos.items():
        cuerpo = DERIV.format(rs=rs, cf=cf)
        trabajos.append((f"der_{nom}", cuerpo,
                         "ac dec 100 100 10Meg\nlet m=db(v(der))\n"
                         f"wrdata der_ac_{nom}.txt m\n"
                         "tran 5n 700u 400u 20n\n"
                         f"wrdata der_tr_{nom}.txt v(der)"))
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(lambda tr: correr(*tr), trabajos))
    acs, trs = [], []
    for nom in casos:
        f, (m,) = leer(f"der_ac_{nom}.txt")
        acs.append(m)
        t, (v,) = leer(f"der_tr_{nom}.txt")
        # vertice superior de la triangular en t = 4 * 116,28 us
        tv = 2 * 232.57e-6
        tq = t - tv
        trs.append((tq, v))
        clave = {"sin": "Sin", "rs": "Rs", "con": "Con"}[nom]
        i = np.argmax(m)
        RES[f"simDer{clave}Fpico"] = f[i] / 1e3
        RES[f"simDer{clave}Pico"] = float(m[i])
        RES[f"simDer{clave}Ganancia"] = float(np.interp(F0, f, m))
        # respuesta al vertice: sobrepico y tiempo de transicion
        hi = np.median(v[(tq > 60e-6) & (tq < 100e-6)])
        lo = np.median(v[(tq > -60e-6) & (tq < -20e-6)])
        w = (tq > 0) & (tq < 60e-6)
        RES[f"simDer{clave}Sobrepico"] = (hi - v[w].min()) / (lo - hi) * 100
        a = cruce(tq, v, lo - 0.1 * (lo - hi), False, -5e-6)
        b = cruce(tq, v, lo - 0.9 * (lo - hi), False, -5e-6)
        RES[f"simDer{clave}Transicion"] = (b - a) * 1e6
        # frecuencia de la oscilacion: cruces por el valor final
        z = v[w] - hi
        tz = tq[w]
        cr = tz[1:][(z[1:] > 0) & (z[:-1] <= 0)]
        if len(cr) >= 3:
            RES[f"simDer{clave}Fosc"] = 1 / np.mean(np.diff(cr)) / 1e3
        # tiempo de establecimiento al 2 %
        fuera = np.abs(v[w] - hi) > 0.02 * abs(lo - hi)
        RES[f"simDer{clave}Est"] = float(tz[np.where(fuera)[0][-1]] * 1e6) if fuera.any() else 0.0
    guardar("derivador_ac.dat", "f sin rs con", [f] + acs)
    tg = np.arange(-20e-6, 80e-6, 0.1e-6)
    guardar("derivador_tr.dat", "t sin rs con",
            [tg * 1e6] + [np.interp(tg, a, b) for a, b in trs])
    # Teoria: polo de la red de realimentacion y frecuencia natural
    gbw = 3e6
    f1 = 1 / (2 * math.pi * 31.6e3 * 1e-9)
    RES["teoDerFuno"] = f1 / 1e3
    RES["teoDerFcero"] = math.sqrt(gbw * f1) / 1e3
    RES["teoDerFdos"] = 1 / (2 * math.pi * 1e3 * 1e-9) / 1e3
    RES["teoDerFtres"] = 1 / (2 * math.pi * 31.6e3 * 56e-12) / 1e3


def derivador_barrido():
    """Respuesta al vertice de la triangular para varias compensaciones."""
    casos = [("A", "1m", "1f"), ("B", "1k", "1f"), ("C", "1m", "56p"),
             ("D", "1k", "56p"), ("E", "2.7k", "56p"), ("F", "1k", "22p")]
    trabajos = [(f"derb_{k}", DERIV.format(rs=rs, cf=cf),
                 f"tran 5n 700u 400u 20n\nwrdata derb_{k}.txt v(der)")
                for k, rs, cf in casos]
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda tr: correr(*tr), trabajos))
    for k, rs, cf in casos:
        t, (v,) = leer(f"derb_{k}.txt")
        tq = t - 2 * 232.57e-6
        hi = np.median(v[(tq > 80e-6) & (tq < 110e-6)])
        lo = np.median(v[(tq > -60e-6) & (tq < -20e-6)])
        w = (tq > 0) & (tq < 110e-6)
        RES[f"simBarr{k}Sobrepico"] = (hi - v[w].min()) / (lo - hi) * 100
        a = cruce(tq, v, lo - 0.1 * (lo - hi), False, -5e-6)
        b = cruce(tq, v, lo - 0.9 * (lo - hi), False, -5e-6)
        RES[f"simBarr{k}Transicion"] = (b - a) * 1e6
        fuera = np.abs(v[w] - hi) > 0.02 * abs(lo - hi)
        RES[f"simBarr{k}Est"] = float(tq[w][np.where(fuera)[0][-1]] * 1e6) if fuera.any() else 0.0
        # Margen de fase con un modelo de un polo del TL084
        # (A0 = 200 V/mV, B1 = 3 MHz)
        f = np.logspace(2, 7.5, 200000)
        sj = 2j * np.pi * f
        a0 = 2e5
        A = a0 / (1 + sj * a0 / (2 * np.pi * 3e6))
        rsv = float(rs.replace("k", "e3").replace("m", "e-3"))
        cfv = float(cf.replace("p", "e-12").replace("f", "e-15"))
        zi = rsv + 1 / (sj * 1e-9)
        zf = 1 / (1 / 31.6e3 + sj * cfv)
        L = A * zi / (zi + zf)
        i = np.argmin(np.abs(np.abs(L) - 1))
        RES[f"simBarr{k}Fc"] = f[i] / 1e3
        RES[f"simBarr{k}Pm"] = 180 + float(np.angle(L[i], deg=True))


# ---------------------------------------------------------------------------
# E. Generador de impulsos y rectificador: tres diodos distintos
# ---------------------------------------------------------------------------
RECT = """.include ../modelos_tp2.lib
VCCP vcc 0 12
VCCN 0 vee 12
VS3 s3 0 PWL({pwl}) r=0
RS4 s3 c4 4.7k
C4 c4 n6 1n
RF4 n6 vp 4.7k
XU3A 0 n6 vcc vee vp TL084
R12 vp n7 10k
R13 n7 va 10k
D1 o7 n7 {d}
D2 va o7 {d}
XU3B 0 n7 vcc vee o7 TL084
R14 vp n8 20k
R15 va n8 10k
RF8 n8 s4 {rf}
XU3C 0 n8 vcc vee s4 TL084
RL s4 0 {rl}
"""


def rectificador():
    # La senal 3 de la simulacion nominal (un periodo, desde el flanco de
    # subida de la senal 1) se repite con una fuente PWL.
    nd = np.loadtxt(os.path.join(DATOS, "nominal.dat"), skiprows=1)
    per = T0
    ts = np.arange(0, per, 0.1e-6)
    vs = np.interp(ts * 1e6, nd[:, 0], nd[:, 4])
    ts = np.r_[ts, per]
    vs = np.r_[vs, vs[0]]
    pwl = "\n+ ".join(" ".join(f"{a:.4e} {b:.5f}" for a, b in
                                 zip(ts[i:i + 8], vs[i:i + 8]))
                       for i in range(0, len(ts), 8))
    rf = 10e3 + RES["simPtres"] * 1e3
    casos = [("4004", "D1N4004", 1e9), ("4148", "D1N4148", 1e9),
             ("ideal", "DIDEAL", 1e9), ("4004rl", "D1N4004", 1e3),
             ("4148rl", "D1N4148", 1e3)]
    trabajos = []
    for nom, d, rl in casos:
        cuerpo = RECT.format(pwl=pwl, d=d, rf=rf, rl=rl)
        trabajos.append((f"rect_{nom}", cuerpo,
                         "tran 5n 1.2m 0.7m 10n\n"
                         f"wrdata rect_{nom}.txt v(s3) v(vp) v(va) v(s4) v(o7)"))
    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(lambda t: correr(*t), trabajos))
    out = {}
    for nom, d, rl in casos:
        t, v = leer(f"rect_{nom}.txt")
        # ventana: un periodo que empieza 20 us antes del flanco de subida
        # de la senal 1 (la fuente PWL arranca en ese flanco)
        k = math.ceil((0.7e-3 + 20e-6) / per)
        t0 = k * per - 20e-6
        m = (t >= t0) & (t <= t0 + per)
        out[nom] = (t[m] - t0 - 20e-6, [x[m] for x in v])
    tg = np.arange(-20e-6, per - 20e-6, 0.05e-6)
    cols = [tg * 1e6]
    for nom in ("4004", "4148", "ideal"):
        tt, v = out[nom]
        cols += [np.interp(tg, tt, v[3]), np.interp(tg, tt, v[2]),
                 np.interp(tg, tt, v[4])]
    tt, v = out["4004"]
    cols += [np.interp(tg, tt, v[0]), np.interp(tg, tt, v[1])]
    guardar("rectificador.dat",
            "t s4a vaa o7a s4b vab o7b s4c vac o7c s3 vp", cols)
    for nom, clave in (("4004", "A"), ("4148", "B"), ("ideal", "C")):
        tt, v = out[nom]
        s4 = v[3]
        w1 = (tt > -5e-6) & (tt < 0.4 * per)
        w2 = (tt > 0.45 * per) & (tt < 0.9 * per)
        RES[f"simRect{clave}PicoSub"] = float(s4[w1].max())
        RES[f"simRect{clave}PicoBaj"] = float(s4[w2].max())
        RES[f"simRect{clave}Min"] = float(s4.min())
        # area de cada impulso (V*us)
        dt = np.diff(tt).mean()
        RES[f"simRect{clave}AreaSub"] = float(np.sum(np.clip(s4[w1], 0, None)) * dt * 1e6)
        RES[f"simRect{clave}AreaBaj"] = float(np.sum(np.clip(s4[w2], 0, None)) * dt * 1e6)
        # tiempo en que la salida del operacional U3B esta fuera de lazo
        o7 = v[4]
        RES[f"simRect{clave}OsieteMin"] = float(o7.min())
        RES[f"simRect{clave}OsieteMax"] = float(o7.max())
    # Ideal: el area teorica de un impulso es tau * pico (con flanco abrupto)
    # Impedancia de salida por el metodo de la carga (RL = 1 kOhm)
    for nom, clave in (("4004", "A"), ("4148", "B")):
        _, v0 = out[nom]
        _, v1 = out[nom + "rl"]
        p0, p1 = v0[3].max(), v1[3].max()
        RES[f"simZoCarga{clave}"] = 1e3 * (p0 / p1 - 1)


# ---------------------------------------------------------------------------
# F. Impedancias de entrada y de salida (analisis de pequena senal)
# ---------------------------------------------------------------------------
def impedancias():
    base = circuito(RP3=f"{RES['simPtres'] * 1e3:.1f}")
    zin = base.replace("VGEN in 0 PULSE", "VGEN in 0 DC 0 AC 1 PULSE")
    correr("zin", zin, "op\nac dec 50 10 1Meg\n"
           "let z=mag(v(in)/(-i(vgen)))\nwrdata zin.txt z")
    f, (z,) = leer("zin.txt")
    RES["simZin"] = float(np.interp(F0, f, z)) / 1e3
    RES["simZinMeg"] = float(np.interp(1e6, f, z)) / 1e3
    zo = base + "\nIOUT 0 s4 DC 0 AC 1\n"
    correr("zout", zo, "op\nac dec 50 10 10Meg\n"
           "let z=mag(v(s4))\nlet p=180/PI*cph(v(s4))\nwrdata zout.txt z p")
    f, (z, p) = leer("zout.txt")
    guardar("zout.dat", "f z fase", [f, z, p])
    RES["simZoutCien"] = float(np.interp(100, f, z)) * 1e3        # mOhm
    RES["simZoutF"] = float(np.interp(F0, f, z))                    # Ohm
    RES["simZoutDiez"] = float(np.interp(10 * F0, f, z))
    RES["simZoutCienK"] = float(np.interp(100e3, f, z))
    RES["simZoutFaseF"] = float(np.interp(F0, f, p))
    # Estimacion teorica Zo = ro / (1 + A beta) con A = GBW/f
    rf = 10e3 + RES["simPtres"] * 1e3
    rpar = 1 / (1 / 20e3 + 1 / 10e3)
    beta = rpar / (rpar + rf)
    RES["teoBeta"] = beta
    # Por encima del polo dominante: Zo = ro f / (beta GBW) (inductiva).
    # Se obtiene ro de la simulacion en 10 f0 y la inductancia equivalente.
    ro = RES["simZoutDiez"] * beta * 3e6 / (10 * F0)
    RES["teoRo"] = ro
    RES["teoLeq"] = ro / (2 * math.pi * beta * 3e6) * 1e6        # uH


# ---------------------------------------------------------------------------
# G. Referencia: temperatura y tension de alimentacion
# ---------------------------------------------------------------------------
def referencia():
    base = circuito()
    correr("ref_op", base, "op\nprint v(z) v(vref1) v(vref2) i(vccp)\n"
           "wrdata ref_op.txt v(z) v(vref1) v(vref2)")
    _, (z, r1, r2) = leer("ref_op.txt")
    RES["simVz"] = float(z[0])
    RES["simIz"] = (12 - z[0]) / 470 * 1e3 - z[0] / 10e3 * 2 * 1e3
    correr("ref_temp", base, "dc temp 0 60 2\n"
           "wrdata ref_temp.txt v(z) v(vref2)")
    tc, (z, r2) = leer("ref_temp.txt")
    guardar("ref_temp.dat", "T vz vref2", [tc, z, r2])
    p = np.polyfit(tc, r2, 1)
    RES["simRefTc"] = p[0] / np.interp(25, tc, r2) * 1e6       # ppm/C
    RES["simRefDtemp"] = (r2.max() - r2.min()) * 1e3            # mV en 0-60 C
    correr("ref_lin", base, "dc VCCP 10.8 13.2 0.1\n"
           "wrdata ref_lin.txt v(z) v(vref2)")
    vc, (z, r2) = leer("ref_lin.txt")
    RES["simRefLinea"] = (np.interp(13.2, vc, r2) - np.interp(10.8, vc, r2)) * 1e3
    RES["simRefLineaRel"] = RES["simRefLinea"] / 1e3 / 1.25 / (2.4 / 12) * 100
    RES["simZz"] = (np.interp(13.2, vc, z) - np.interp(10.8, vc, z)) / \
        ((2.4 - (np.interp(13.2, vc, z) - np.interp(10.8, vc, z))) / 470)


# ---------------------------------------------------------------------------
# H. Monte Carlo: tolerancias de resistores (1 %) y capacitores (5 %)
# ---------------------------------------------------------------------------
def montecarlo(n=60, semilla=2026):
    rng = np.random.default_rng(semilla)
    base = circuito(RP3=f"{RES['simPtres'] * 1e3:.1f}")
    tol_r = ["R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11",
             "R12", "R13", "R14", "R15", "RF8"]
    trabajos = []
    corridas = []
    for k in range(n):
        txt = base
        u = {}
        for c in ("C1V", "CDV", "C4V"):
            u[c] = rng.uniform(0.95, 1.05)
        for c in ("RIV", "RDV", "RS4V", "RF4V"):
            u[c] = rng.uniform(0.99, 1.01)
        for c, f in u.items():
            txt = re.sub(r"(\b%s=)(\S+)" % c,
                         lambda mm: mm.group(1) + f"{{{mm.group(2)}*{f:.5f}}}",
                         txt)
        for r in tol_r:
            f = rng.uniform(0.99, 1.01)
            txt = re.sub(r"^(%s\s+\S+\s+\S+\s+)(\S+)" % r,
                         lambda mm: mm.group(1) + "{" + mm.group(2) + f"*{f:.5f}" + "}",
                         txt, flags=re.M)
        corridas.append(u)
        trabajos.append((f"mc_{k:03d}", txt,
                         "tran 50n 60m 59m 0.2u uic\n"
                         f"wrdata mc_{k:03d}.txt v(s1) v(s2) v(s3) v(s4)"))
    with ThreadPoolExecutor(max_workers=max(1, os.cpu_count() - 1)) as ex:
        list(ex.map(lambda t: correr(*t), trabajos))
    filas = []
    for k in range(n):
        t, v = leer(f"mc_{k:03d}.txt")
        tt, (s1, s2, s3, s4) = ultimos_periodos(t, v, 2)
        filas.append([k, s2.max() - s2.min(), (s2.max() + s2.min()) / 2,
                      np.percentile(s3, 97), np.percentile(s3, 3), s4.max()])
    filas = np.array(filas)
    guardar("montecarlo.dat", "k vpp centro s3alto s3bajo s4pico", filas.T)
    for i, nom in ((1, "Vpp"), (2, "Centro"), (3, "StresAlto"),
                   (4, "StresBajo"), (5, "Scuatro")):
        x = filas[:, i]
        RES[f"simMc{nom}Media"] = float(x.mean())
        RES[f"simMc{nom}Desv"] = float(x.std(ddof=1))
        RES[f"simMc{nom}Min"] = float(x.min())
        RES[f"simMc{nom}Max"] = float(x.max())
    RES["simMcN"] = n


# ---------------------------------------------------------------------------
# I. Fallas que reproducen los sintomas medidos en la senal 4
# ---------------------------------------------------------------------------
def fallas():
    rp3 = f"{RES['simPtres'] * 1e3:.1f}"
    desb = ("R14  vp n8 20k", "R14  vp n8 10k")
    casos = {
        # a) derivador de la senal 3 poco amortiguado (Rs = 330, sin Cf)
        "amort": circuito(RP3=rp3, RSV="330", CFV="1f"),
        # b) sumador del rectificador con R14 = R15 (relacion 1:1 en vez de 2:1)
        "sumador": circuito(RP3=rp3).replace(*desb),
        # c) ambas
        "ambas": circuito(RP3=rp3, RSV="330", CFV="1f").replace(*desb),
    }
    ctrl = "tran 50n 60m 58.8m 0.1u uic\nwrdata {n}.txt v(s1) v(s3) v(vp) v(s4)"
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(lambda kv: correr("falla_" + kv[0], kv[1],
                                      ctrl.format(n="falla_" + kv[0])),
                    casos.items()))
    cols = []
    for nom in casos:
        t, (s1, s3, vp, s4) = leer(f"falla_{nom}.txt")
        tus = (t - t[0]) * 1e6
        # origen: flanco de subida de la senal 1, como en la captura 6 el
        # primer impulso grande aparece a unos 145 us del borde de pantalla
        cr = tus[1:][(s1[1:] > 0.25) & (s1[:-1] <= 0.25)]
        t0 = cr[0]
        tg = np.arange(0, 1150, 0.2)
        cols += [np.interp(tg + t0 - 100, tus, s4), np.interp(tg + t0 - 100, tus, s3)]
        RES[f"simFalla{nom.capitalize()}Max"] = float(s4.max())
        RES[f"simFalla{nom.capitalize()}Min"] = float(s4.min())
        # pico en cada flanco
        T = T0 * 1e6
        ws = (tus > t0) & (tus < t0 + 0.4 * T)
        wb = (tus > t0 + 0.5 * T) & (tus < t0 + 0.9 * T)
        RES[f"simFalla{nom.capitalize()}PicoSub"] = float(s4[ws].max())
        RES[f"simFalla{nom.capitalize()}PicoBaj"] = float(s4[wb].max())
    guardar("fallas.dat", "t s4amort s3amort s4sumador s3sumador s4ambas s3ambas",
            [tg] + cols)
    # Desfase para superponer el caso "ambas" con la captura 6: se alinea
    # el primer impulso dominante de cada una.
    m6 = np.loadtxt(os.path.join(DATOS, "med6.dat"), skiprows=1)
    w = m6[:, 0] < 233
    t_med = m6[w, 0][np.argmax(m6[w, 1])]
    s4a = cols[4]
    w = tg < 233
    t_sim = tg[w][np.argmax(s4a[w])]
    RES["simFallaDesfase"] = float(t_med - t_sim)


# ---------------------------------------------------------------------------
# Mediciones: digitalizacion de las capturas del osciloscopio
# ---------------------------------------------------------------------------
CAPTURAS = {1: (1.0, 50), 2: (0.5, 50), 3: (2.0, 50),
            4: (5.0, 100), 5: (0.5, 100), 6: (2.0, 100)}


def mediciones():
    """Convierte cada captura (320 x 234 px, 25 px por division) en una
    traza tension-tiempo. La reticula ocupa x = 12..312 y y = 15..215; el
    cero del canal 1 esta en y = 115 en todas las capturas."""
    from PIL import Image
    med = {}
    for i, (vdiv, tdiv) in CAPTURAS.items():
        im = np.array(Image.open(os.path.join(MEDICIONES, f"{i}.bmp"))
                      .convert("RGB")).astype(int)
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        amarillo = (r > 180) & (g > 160) & (b < 120)
        ts, vmed, vmin, vmax = [], [], [], []
        for x in range(13, 312):
            filas = np.where(amarillo[16:200, x])[0] + 16
            if len(filas) == 0:
                continue
            v = (115 - filas) * vdiv / 25
            ts.append((x - 12) * tdiv / 25)
            vmed.append(np.median(v))
            vmin.append(v.min())
            vmax.append(v.max())
        ts, vmed, vmin, vmax = map(np.array, (ts, vmed, vmin, vmax))
        # Las columnas de la reticula punteada tapan la traza en algunos
        # pixeles: filtro de mediana de 3 muestras sobre la traza central
        vpad = np.r_[vmed[0], vmed, vmed[-1]]
        vmed = np.median(np.c_[vpad[:-2], vpad[1:-1], vpad[2:]], axis=1)
        guardar(f"med{i}.dat", "t v vmin vmax", [ts, vmed, vmin, vmax],
                fmt="%.4f")
        med[i] = (ts, vmed, vmin, vmax)
    # Valores caracteristicos
    t, v, vmn, vmx = med[1]
    R = {}
    R["inAlto"] = float(np.percentile(v, 95))
    R["inBajo"] = float(np.percentile(v, 5))
    # Frecuencia: la mide el osciloscopio en la captura 1 (4,292 kHz)
    R["frec"] = 4292.0
    alto = np.mean(v > 1.2)
    R["ciclo"] = alto * 100
    t, v, vmn, vmx = med[2]
    R["s1Alto"] = float(np.percentile(v, 95))
    R["s1Bajo"] = float(np.percentile(v, 5))
    R["s1Max"] = float(vmx.max())
    R["s1Min"] = float(vmn.min())
    t, v, vmn, vmx = med[3]
    R["s2Max"] = float(vmx.max())
    R["s2Min"] = float(vmn.min())
    R["s2MesMax"] = float(np.percentile(v, 97))
    R["s2MesMin"] = float(np.percentile(v, 3))
    # pendientes de la triangular (ajuste lineal en el centro de cada rampa)
    # rampa de subida: entre t = 30 y 110 us; bajada: entre 175 y 230 us
    m = (t > 30) & (t < 110)
    R["s2PendSub"] = float(np.polyfit(t[m], v[m], 1)[0])       # V/us
    m = (t > 175) & (t < 230)
    pb = np.polyfit(t[m], v[m], 1)
    R["s2PendBaj"] = float(pb[0])
    # Vertices de la triangular: interseccion de las rectas ajustadas
    # (descarta los picos que aparecen en los vertices)
    m = (t > 30) & (t < 110)
    ps = np.polyfit(t[m], v[m], 1)
    ts_ = (pb[1] - ps[1]) / (ps[0] - pb[0])
    R["s2VertMax"] = float(np.polyval(ps, ts_))
    T = 1e6 / 4292.0
    ps2 = np.array([ps[0], ps[1] - ps[0] * T])     # rampa del periodo siguiente
    tb_ = (pb[1] - ps2[1]) / (ps2[0] - pb[0])
    R["s2VertMin"] = float(np.polyval(pb, tb_))
    R["s2VertVpp"] = R["s2VertMax"] - R["s2VertMin"]
    R["s2VertCentro"] = (R["s2VertMax"] + R["s2VertMin"]) / 2
    for i in (4, 5, 6):
        t, v, vmn, vmx = med[i]
        R[f"c{i}Max"] = float(vmx.max())
        R[f"c{i}Min"] = float(vmn.min())
    # Captura 5: instantes de los eventos (cruces de +0,4 V hacia arriba en
    # el pico principal)
    t, v, _, _ = med[5]
    picos = t[1:][(v[1:] > 0.5) & (v[:-1] <= 0.5)]
    R["c5Periodo"] = float(np.mean(np.diff(picos)))
    # eventos secundarios: picos > 0,2 V que no son principales
    sec = t[1:][(v[1:] > 0.2) & (v[:-1] <= 0.2)]
    sec = np.array([s for s in sec if np.min(np.abs(picos - s)) > 20])
    dif = []
    for p in picos:
        nxt = sec[(sec > p) & (sec < p + 200)]
        if len(nxt):
            dif.append(nxt[-1] - p)
    R["c5Sep"] = float(np.median(dif)) if dif else float("nan")
    # Capturas 4 y 6: separacion media de los picos secundarios (rafagas)
    for i in (4, 6):
        t, v, _, _ = med[i]
        umbral = 0.35 * v.max()
        pp = []
        for j in range(1, len(v) - 1):
            if v[j] > umbral and v[j] >= v[j - 1] and v[j] > v[j + 1]:
                pp.append(t[j])
        pp = np.array(pp)
        d = np.diff(pp)
        d = d[(d > 8) & (d < 60)]
        R[f"c{i}Rafaga"] = float(np.median(d)) if len(d) else float("nan")
        prin = t[1:][(v[1:] > 0.7 * v.max()) & (v[:-1] <= 0.7 * v.max())]
        R[f"c{i}Periodo"] = float(np.mean(np.diff(prin)))
    for k, val in R.items():
        RES["med" + k[0].upper() + k[1:]] = val
    return R


# ---------------------------------------------------------------------------
def escribir_resultados():
    numeros = "Cero Uno Dos Tres Cuatro Cinco Seis Siete Ocho Nueve".split()

    def nombre_tex(k):
        return "".join(numeros[int(c)] if c.isdigit() else c
                       for c in k.replace("_", ""))
    with open(os.path.join(DATOS, "resultados.tex"), "w") as f:
        f.write("% Generado por simulacion/correr_simulaciones.py\n")
        for k in sorted(RES):
            v = RES[k]
            if isinstance(v, (float, np.floating)) and not math.isfinite(v):
                continue
            f.write(f"\\newcommand{{\\{nombre_tex(k)}}}{{{float(v):.6g}}}\n")
    with open(os.path.join(DATOS, "resultados.json"), "w") as f:
        json.dump({k: float(v) for k, v in RES.items()}, f, indent=1)


def main():
    import sys
    os.makedirs(TRABAJO, exist_ok=True)
    os.makedirs(DATOS, exist_ok=True)
    rapido = "--sin-mc" in sys.argv
    med = mediciones()
    referencia()
    print("referencia ok", flush=True)
    nominal()
    print("nominal ok", flush=True)
    tt, S = medida(med)
    # Figura de comparacion con la medicion: se alinea el flanco de subida
    # de la senal 1 simulada con el de la captura 2, y el minimo de la
    # triangular con el de la captura 3.
    fmed = med["frec"]
    T = 1e6 / fmed
    t2 = np.loadtxt(os.path.join(DATOS, "med2.dat"), skiprows=1)
    tm = t2[:, 0]
    sub_med = tm[1:][(t2[1:, 1] > 0.35) & (t2[:-1, 1] <= 0.35)][0]
    tus = tt * 1e6
    cr = tus[1:][(S["s1"][1:] > 0.35) & (S["s1"][:-1] <= 0.35)]
    sub_sim = cr[cr >= sub_med][0]
    tg = np.arange(0, 600, 0.25)
    s1g = np.interp((tg - sub_med + sub_sim), tus, S["s1"])
    t3 = np.loadtxt(os.path.join(DATOS, "med3.dat"), skiprows=1)
    m3 = t3[:, 0] < T
    tmin_med = t3[:, 0][m3][np.argmin(t3[:, 1][m3])]
    mt = (tus >= tmin_med) & (tus < tmin_med + T)
    tmin_sim = tus[mt][np.argmin(S["s2"][mt])]
    s2g = np.interp((tg - tmin_med + tmin_sim), tus, S["s2"])
    guardar("medida_sim.dat", "t s1 s2", [tg, s1g, s2g])
    print("medida ok", flush=True)
    integrador()
    print("integrador ok", flush=True)
    derivador()
    derivador_barrido()
    print("derivador ok", flush=True)
    rectificador()
    print("rectificador ok", flush=True)
    impedancias()
    print("impedancias ok", flush=True)
    fallas()
    print("fallas ok", flush=True)
    if not rapido:
        montecarlo()
        print("montecarlo ok", flush=True)
    else:
        viejo = os.path.join(DATOS, "resultados.json")
        if os.path.exists(viejo):
            with open(viejo) as f:
                for k, v in json.load(f).items():
                    if k.startswith("simMc"):
                        RES[k] = v
    escribir_resultados()
    for k in sorted(RES):
        print(f"{k:28s} {RES[k]:.6g}")


if __name__ == "__main__":
    main()
