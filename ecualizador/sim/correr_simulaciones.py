"""Corre las simulaciones LTspice del ecualizador y resume los resultados.

Uso (desde esta carpeta, en Windows):  python correr_simulaciones.py

Copia los netlists a _corridas/ (no se versiona), los simula en modo batch,
lee los .raw binarios y escribe:
  - resultados.json con los numeros que cita resultados_simulacion.md
  - figuras/*.png
"""
import json
import os
import re
import shutil
import subprocess
import time

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
TRABAJO = os.path.join(AQUI, "_corridas")
FIGURAS = os.path.join(AQUI, "figuras")
LTSPICE = r"C:\Program Files\ADI\LTspice\LTspice.exe"
GANANCIA_TP4 = 4.97      # 1 + 27k/6k8 (TP4)
RL = 8.0                 # parlante


# ---------------------------------------------------------------- LTspice

def decodificar(ruta):
    with open(ruta, "rb") as f:
        crudo = f.read()
    txt = crudo.decode("utf-16-le") if b"\x00" in crudo[:40] else crudo.decode("latin-1")
    return txt.replace("\r\n", "\n")


def correr(cir):
    os.makedirs(TRABAJO, exist_ok=True)
    for f in os.listdir(AQUI):
        if f.endswith((".cir", ".inc", ".lib")):
            shutil.copy(os.path.join(AQUI, f), TRABAJO)
    t0 = time.time()
    subprocess.run([LTSPICE, "-b", cir], cwd=TRABAJO, check=True)
    base = os.path.splitext(cir)[0]
    log = decodificar(os.path.join(TRABAJO, base + ".log"))
    for mala in ("singular matrix", "time step too small", "error", "undefined"):
        if mala in log.lower():
            raise SystemExit(f"{cir}: {mala}\n{log}")
    print(f"  {cir}: {time.time() - t0:.0f} s")
    return leer_raw(os.path.join(TRABAJO, base + ".raw")), log


def leer_raw(ruta):
    """Lee un .raw binario de LTspice. Devuelve una lista de corridas (una por .step)."""
    with open(ruta, "rb") as f:
        crudo = f.read()
    marca = "Binary:\n".encode("utf-16-le")
    i = crudo.index(marca)
    cab = crudo[:i].decode("utf-16-le").replace("\r\n", "\n")
    datos = crudo[i + len(marca):]
    nv = int(re.search(r"No\. Variables:\s*(\d+)", cab).group(1))
    npts = int(re.search(r"No\. Points:\s*(\d+)", cab).group(1))
    flags = re.search(r"Flags:(.*)", cab).group(1)
    nombres = re.findall(r"^\t\d+\t(\S+)\t", cab.split("Variables:")[-1], re.M)
    if "complex" in flags:
        m = np.frombuffer(datos, dtype=np.complex128, count=npts * nv).reshape(npts, nv)
        escala = m[:, 0].real
    elif len(datos) == npts * 8 * nv:
        m = np.frombuffer(datos, dtype=np.float64, count=npts * nv).reshape(npts, nv)
        escala = np.abs(m[:, 0])
    else:  # tiempo en doble precision, el resto en simple
        dt = np.dtype([("t", "<f8"), ("v", "<f4", (nv - 1,))])
        r = np.frombuffer(datos, dtype=dt, count=npts)
        escala = np.abs(r["t"])
        m = np.column_stack([escala, r["v"].astype(np.float64)])
    cortes = [0] + [k for k in range(1, npts) if escala[k] < escala[k - 1]] + [npts]
    corridas = []
    for a, b in zip(cortes[:-1], cortes[1:]):
        d = {n.upper(): m[a:b, k] for k, n in enumerate(nombres)}
        d["X"] = escala[a:b]
        corridas.append(d)
    return corridas


def db(x):
    return 20 * np.log10(np.abs(x))


def en(f, y, f0):
    """Valor de y en la frecuencia f0 (interpolado en escala log)."""
    return float(np.interp(np.log10(f0), np.log10(f), y))


def cruce(t, y, nivel, desde=0.0, subida=True):
    """Primer instante despues de 'desde' en que y cruza 'nivel'."""
    k0 = np.searchsorted(t, desde)
    for k in range(max(k0, 1), len(t)):
        a, b = y[k - 1], y[k]
        if (subida and a < nivel <= b) or (not subida and a > nivel >= b):
            return float(t[k - 1] + (t[k] - t[k - 1]) * (nivel - a) / (b - a))
    return None


def media(t, y, t1, t2):
    sel = (t >= t1) & (t <= t2)
    return float(np.mean(y[sel]))


# ---------------------------------------------------------------- analisis

R = {}


def ac_eq():
    corr, _ = correr("eq_ac.cir")
    nombres = ["plano", "graves_max", "graves_min", "medios_max", "medios_min", "agudos_max", "agudos_min"]
    curvas = {}
    for n, c in zip(nombres, corr):
        curvas[n] = (c["X"], db(c["V(EQOUT)"]))
    f, plano = curvas["plano"]
    sel = (f >= 20) & (f <= 20e3)
    R["plano"] = {
        "ganancia_1k_dB": round(en(f, plano, 1e3), 2),
        "max_dB": round(float(plano[sel].max()), 2),
        "min_dB": round(float(plano[sel].min()), 2),
        "ondulacion_dB": round(float(plano[sel].max() - plano[sel].min()), 2),
    }
    rango = {}
    for banda, frecs in (("graves", (50, 100)), ("medios", (1000,)), ("agudos", (10000, 5000))):
        for f0 in frecs:
            ref = en(f, plano, f0)
            rango[f"{banda}_{f0}Hz"] = {
                "realce_dB": round(en(*curvas[banda + "_max"], f0) - ref, 1),
                "corte_dB": round(en(*curvas[banda + "_min"], f0) - ref, 1),
            }
    R["rango"] = rango
    # cruces entre bandas: donde el realce de graves y el de medios valen lo mismo, etc.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    estilos = {"plano": ("k", "-"), "graves": ("tab:red", None), "medios": ("tab:green", None), "agudos": ("tab:blue", None)}
    ax.semilogx(f, plano, "k", lw=2, label="potes al medio")
    for banda in ("graves", "medios", "agudos"):
        col = estilos[banda][0]
        ax.semilogx(*curvas[banda + "_max"], color=col, lw=1.2, label=f"{banda} al máximo / mínimo")
        ax.semilogx(*curvas[banda + "_min"], color=col, lw=1.2, ls="--")
    ax.set_xlim(10, 100e3)
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Ganancia EQOUT / entrada [dB]")
    ax.set_title("Ecualizador: respuesta con cada pote en sus extremos")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="lower center", ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, "eq_bode.png"), dpi=150)
    plt.close(fig)
    return curvas


def ac_franco(curvas_eq):
    corr, _ = correr("franco_eq_ac.cir")
    nombres = ["plano", "graves_max", "graves_min"]
    cf = {n: (c["X"], db(c["V(VO)"])) for n, c in zip(nombres, corr)}
    f, plano = cf["plano"]
    sel = (f >= 20) & (f <= 20e3)
    R["franco"] = {
        "plano_ondulacion_dB": round(float(plano[sel].max() - plano[sel].min()), 2),
        "graves_realce_50Hz_dB": round(en(*cf["graves_max"], 50) - en(f, plano, 50), 1),
        "graves_corte_50Hz_dB": round(en(*cf["graves_min"], 50) - en(f, plano, 50), 1),
        "medios_con_graves_al_max_1k_dB": round(en(*cf["graves_max"], 1e3) - en(f, plano, 1e3), 1),
        "agudos_con_graves_al_max_10k_dB": round(en(*cf["graves_max"], 1e4) - en(f, plano, 1e4), 1),
    }
    fig, ax = plt.subplots(figsize=(8, 4.2))
    fe, pe = curvas_eq["plano"]
    for (x, y), col, lab in (((fe, pe - en(fe, pe, 1e3)), "k", "nuevo, potes al medio"),
                             ((curvas_eq["graves_max"][0], curvas_eq["graves_max"][1] - en(fe, pe, 1e3)), "tab:red", "nuevo, graves al máximo"),
                             ((curvas_eq["graves_min"][0], curvas_eq["graves_min"][1] - en(fe, pe, 1e3)), "tab:red", "nuevo, graves al mínimo")):
        ax.semilogx(x, y, color=col, lw=1.6, ls="-" if "mín" not in lab else "--", label=lab)
    for n, col, ls, lab in (("plano", "tab:gray", "-", "Franco, potes al medio"),
                            ("graves_max", "tab:orange", "-", "Franco, graves al máximo"),
                            ("graves_min", "tab:orange", "--", "Franco, graves al mínimo")):
        x, y = cf[n]
        ax.semilogx(x, y - en(f, plano, 1e3), color=col, lw=1.2, ls=ls, label=lab)
    ax.set_xlim(10, 100e3)
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Ganancia relativa a 1 kHz plano [dB]")
    ax.set_title("Sumador de Franco contra el nuevo (pote de graves)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, ncol=2, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, "franco_vs_nuevo.png"), dpi=150)
    plt.close(fig)


def monte_carlo():
    corr, _ = correr("eq_mc.cir")
    assert len(corr) == 200, len(corr)
    ond, g1k, corte = [], [], []
    nominal_1k = R["plano"]["ganancia_1k_dB"]
    for k, c in enumerate(corr):
        f, g = c["X"], db(c["V(EQOUT)"])
        if k < 100:
            ond.append(float(g.max() - g.min()))
            g1k.append(en(f, g, 1e3))
        else:
            corte.append(en(f, g, 1e3) - nominal_1k)
    R["monte_carlo"] = {
        "corridas": 100,
        "ondulacion_plano_dB": {"media": round(float(np.mean(ond)), 2), "peor": round(float(np.max(ond)), 2)},
        "ganancia_1k_dB": {"min": round(float(np.min(g1k)), 2), "max": round(float(np.max(g1k)), 2)},
        "corte_medios_1k_dB": {"media": round(float(np.mean(corte)), 1), "peor": round(float(np.max(corte)), 1)},
    }


def tran_bandas():
    corr, _ = correr("eq_tran_bandas.cir")
    tramos = {"100 Hz": (0.225, 0.25), "1 kHz": (0.475, 0.5), "8 kHz": (0.725, 0.75)}
    res = {}
    for nombre, c in zip(("centro", "graves_max_medios_min", "sobrecarga_1V5_graves_max"), corr):
        t = c["X"]
        d = {}
        for tono, (a, b) in tramos.items():
            d[tono] = {s: round(media(t, c[f"V(ADC_{s[0].upper()})"], a, b), 2) for s in ("b", "m", "t")}
        d["adc_max_V"] = round(float(max(c["V(ADC_B)"].max(), c["V(ADC_M)"].max(), c["V(ADC_T)"].max())), 2)
        # corriente por cada Schottky = la que llega por los 10k menos la que carga los 10 nF
        d["corriente_schottky_max_mA"] = round(1e3 * float(max(np.abs(c[f"I(RAD{s})"] - c[f"I(CAD{s})"]).max() for s in "BMT")), 2)
        d["veq_max_V"] = round(float(np.abs(c["V(VEQ)"]).max()), 2)
        d["banda_max_V"] = round(float(max(np.abs(c["V(VBO)"]).max(), np.abs(c["V(VMO)"]).max(), np.abs(c["V(VTO)"]).max())), 2)
        # descarga del agudo despues de cortar el tono (0,75 s): tiempo hasta 37 %
        v0 = media(t, c["V(ADC_T)"], 0.745, 0.75)
        t37 = cruce(t, c["V(ADC_T)"], 0.368 * v0, desde=0.75, subida=False)
        d["descarga_tau_ms"] = round(1e3 * (t37 - 0.75), 1) if t37 else None
        res[nombre] = d
        if nombre != "sobrecarga_1V5_graves_max":
            fig, ax = plt.subplots(figsize=(8, 3.6))
            for s, col, lab in (("B", "tab:red", "ADC graves (PA1)"), ("M", "tab:green", "ADC medios (PA2)"), ("T", "tab:blue", "ADC agudos (PA0)")):
                ax.plot(t, c[f"V(ADC_{s})"], color=col, lw=1.3, label=lab)
            for x in (0.25, 0.5, 0.75):
                ax.axvline(x, color="gray", lw=0.6, ls=":")
            for x, txt in ((0.125, "100 Hz"), (0.375, "1 kHz"), (0.625, "8 kHz"), (0.875, "silencio")):
                ax.text(x, 3.15, txt, ha="center", fontsize=8)
            ax.set_ylim(-0.1, 3.4)
            ax.set_xlim(0, 1)
            ax.set_xlabel("Tiempo [s]")
            ax.set_ylabel("Tensión al ADC [V]")
            tit = "potes al medio" if nombre == "centro" else "graves al máximo, medios al mínimo"
            ax.set_title(f"Detectores de banda con 0,5 V pico de entrada, {tit}")
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8, loc="center right")
            fig.tight_layout()
            fig.savefig(os.path.join(FIGURAS, f"bandas_{nombre}.png"), dpi=150)
            plt.close(fig)
    R["bandas"] = res


def tran_recorte():
    corr, _ = correr("eq_tran_recorte.cir")
    c = corr[0]
    t = c["X"]
    veq, ref, exti = c["V(VEQ)"], c["V(REF)"], c["V(EXTI)"]
    vth = media(t, ref, 0.15, 0.2)
    t_cruce = cruce(t, veq, vth, desde=0.2)
    t_exti = cruce(t, exti, 1.65, desde=0.2)
    t_suelta = cruce(t, exti, 1.65, desde=0.3, subida=False)
    t_rafaga_on = cruce(t, exti, 1.65, desde=0.6)
    t_rafaga_off = cruce(t, exti, 1.65, desde=0.605, subida=False)
    R["recorte"] = {
        "ref_sin_recorte_V": round(vth, 3),
        "ref_con_recorte_V": round(media(t, ref, 0.25, 0.3), 3),
        "retardo_exti_us": round(1e6 * (t_exti - t_cruce), 1),
        "exti_bajo_V": round(media(t, exti, 0.1, 0.2), 3),
        "exti_alto_V": round(media(t, exti, 0.25, 0.3), 3),
        "led_mA": round(1e3 * media(t, np.abs(c["I(DLED)"]), 0.25, 0.3), 1),
        "sostiene_despues_del_recorte_ms": round(1e3 * (t_suelta - 0.3), 1),
        "rafaga_5ms_dura_ms": round(1e3 * (t_rafaga_off - t_rafaga_on), 1),
    }
    fig, axs = plt.subplots(3, 1, figsize=(8, 6.5), sharex=True)
    axs[0].plot(t, veq, color="tab:gray", lw=0.5, label="VEQ")
    axs[0].plot(t, c["V(CC)"], color="k", lw=1.3, label="pico retenido (CC)")
    axs[0].plot(t, ref, color="tab:red", lw=1.3, label="umbral (REF)")
    axs[0].set_ylim(-1.5, 1.5)
    axs[0].set_ylabel("[V]")
    axs[0].legend(fontsize=8, loc="lower right", ncol=3)
    axs[1].plot(t, exti, color="tab:blue", lw=1.3)
    axs[1].set_ylabel("EXTI (PB0) [V]")
    axs[2].plot(t, 1e3 * np.abs(c["I(DLED)"]), color="tab:red", lw=1.3)
    axs[2].set_ylabel("LED [mA]")
    axs[2].set_xlabel("Tiempo [s]")
    for a in axs:
        a.grid(True, alpha=0.3)
    axs[0].set_title("Detector de recorte: 1 kHz, recorte de 0,2 a 0,3 s y ráfaga de 5 ms en 0,6 s")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, "recorte.png"), dpi=150)
    plt.close(fig)


def tran_histeresis():
    corr, _ = correr("eq_tran_histeresis.cir")
    c = corr[0]
    t, cc, exti = c["X"], c["V(CC)"], c["V(EXTI)"]
    t_on = cruce(t, exti, 1.65)
    t_off = cruce(t, exti, 1.65, desde=t_on + 1e-3, subida=False)
    v_on = float(np.interp(t_on, t, cc))
    v_off = float(np.interp(t_off, t, cc))
    R["histeresis"] = {
        "dispara_VEQ_pico_V": round(v_on, 3),
        "suelta_VEQ_pico_V": round(v_off, 3),
        "dispara_parlante_V": round(v_on * GANANCIA_TP4, 2),
        "dispara_potencia_W": round((v_on * GANANCIA_TP4) ** 2 / (2 * RL), 2),
        "suelta_potencia_W": round((v_off * GANANCIA_TP4) ** 2 / (2 * RL), 2),
    }


def main():
    os.makedirs(FIGURAS, exist_ok=True)
    print("Simulando...")
    curvas = ac_eq()
    ac_franco(curvas)
    monte_carlo()
    tran_bandas()
    tran_recorte()
    tran_histeresis()
    with open(os.path.join(AQUI, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, ensure_ascii=False)
    print(json.dumps(R, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
