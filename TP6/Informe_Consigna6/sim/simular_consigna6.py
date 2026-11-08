#!/usr/bin/env python3
"""
Script integral de cálculo analítico y simulación SPICE (ngspice) para Consigna 6 - TP6
Electrónica Aplicada II - UTN FRC
Grupo 6: Ernst Pedro (400624), Rao Valentino (402308)
"""

import os
import subprocess
import json
import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# 1. GENERACIÓN Y EJECUCIÓN DE NETLISTS NGSPICE
# ==============================================================================

spice_netlist = """* Simulacion SPICE Consigna 6 - Fuente con LM7805 y Preregulador Serie
* UTN FRC - Electronica Aplicada II - Grupo 6

* ==============================================================================
* SUBCIRCUITO MACROMODELO LM7805C (Calibrado según hoja de datos TI uA7805C Fig. 6-59)
* - Vo = 5.000 V @ Vi = 10 V, Io = 500 mA, Tj = 25 C
* - Regulación de línea:
*     * Vi = 8 V a 12 V (dVi = 4 V): dVo = 1.0 mV (típico hoja de datos)
*     * Vi = 7 V a 25 V (dVi = 18 V): dVo = 3.2 mV (típico hoja de datos)
* - Dropout: Vdo = 2.0 V @ Io = 1 A (Vi_min = 7.0 V)
* - Regulación de carga: Ro = 0.017 ohm (dVo = 15 mV para dIo = 5 mA a 1.0 A; 5 mV de 250 mA a 750 mA)
* - Corriente de polarización (Bias current): Id = 4.2 mA @ Vi = 10 V (dId = 0.8 mA de 8 V a 25 V)
* - Rechazo de ripple (RR): 78 dB @ 100-120 Hz (atenuación 1/7943 = 1.26e-4 V/V)
* - Limitación de cortocircuito y SOA: Isc = 1.5 A
* ==============================================================================
.SUBCKT LM7805C IN GND OUT
I_BIAS IN GND DC 4.16m
R_BIAS IN GND 22k
* Tensión interna con característica de regulación de línea, transición suave de dropout y clamp en 0 V
B_VO_RAW N_RAW GND V = 0.5 * ( (5.0085 + 0.00025*(V(IN,GND)-10.0) + 0.000010*(V(IN,GND)-10.0)*abs(V(IN,GND)-10.0)) + (V(IN,GND)-1.92) - sqrt(pow((5.0085 + 0.00025*(V(IN,GND)-10.0) + 0.000010*(V(IN,GND)-10.0)*abs(V(IN,GND)-10.0)) - (V(IN,GND)-1.92), 2) + 0.012) )
B_VO INT_REF GND V = V(N_RAW,GND) > 0.0 ? V(N_RAW,GND) : 0.0
R_OUT INT_REF OUT_INT 0.017
B_LIM OUT_INT OUT V = I(B_LIM) > 1.35 ? (I(B_LIM)-1.35)*20.0 : 0.0
B_PASS IN GND I = I(B_LIM) > 0 ? I(B_LIM) : 0
.ENDS LM7805C

* ==============================================================================
* MODELOS DE SEMICONDUCTORES DISCRETOS (Apéndices 1 y 2 de Cátedra)
* ==============================================================================
* Diodo Zener 1N4740A / 1N5240B (Vz = 10.0 V nominal @ Izt = 25 mA, Zzt = 7 ohm)
.MODEL DZ10V D(IS=1.5e-12 RS=4.0 N=1.0 BV=9.92 IBV=25m)
* Diodo Zener 1N4741A / 1N5241B (Vz = 10.8..11.0 V nominal -> Vi_reg = 10.0 V @ Vin=25 V)
.MODEL DZ11V D(IS=1.5e-12 RS=4.0 N=1.0 BV=10.68 IBV=25m)

* Transistor de Paso NPN TIP31C (TO-220, Vceo=100V, Ic=3A, Pc=40W, hFE=85..100)
.MODEL QTIP31C NPN(IS=1.2e-12 BF=90 NF=1.0 VAF=85 IKF=2.5 ISE=5e-12 NE=1.5 BR=4 NR=1.0 RB=0.5 RC=0.05 RE=0.03 CJE=250p CJC=120p TF=25n)

* ==============================================================================
* CIRCUITOS PARA BARRIDO DE LÍNEA Y PUNTO DE OPERACIÓN (RL = 10 ohm -> IL = 500 mA)
* ==============================================================================
V_IN N_IN 0 DC 25.0 AC 1.0 SIN(25.0 1.0 100)

* Circuito A: Con Preregulador Zener 10 V (1N4740A / 1N5240B) y Rz = 180 ohm (Rango extendido 10V-25V)
R_ZA N_IN N_BA 180
D_ZA 0 N_BA DZ10V
Q_1A N_IN N_BA N_IREGA QTIP31C
C_1A N_IREGA 0 330n
X_REG_A N_IREGA 0 N_OUTA LM7805C
C_2A N_OUTA 0 100n
C_3A N_OUTA 0 10u
R_LA N_OUTA 0 10.0

* Circuito B: Con Preregulador Zener 10V (1N5240B) y Rz = 430 ohm (Criterio Secc. 6-9-5h @ Vin=25V)
R_ZB N_IN N_BB 430
D_ZB 0 N_BB DZ10V
Q_1B N_IN N_BB N_IREGB QTIP31C
C_1B N_IREGB 0 330n
X_REG_B N_IREGB 0 N_OUTB LM7805C
C_2B N_OUTB 0 100n
C_3B N_OUTB 0 10u
R_LB N_OUTB 0 10.0

* Circuito C: LM7805C Directo SIN etapa prereguladora (Conexión directa a Vin)
C_1C N_IN 0 330n
X_REG_C N_IN 0 N_OUTC LM7805C
C_2C N_OUTC 0 100n
C_3C N_OUTC 0 10u
R_LC N_OUTC 0 10.0

* Circuito D: Para barrido de Corriente de Carga IL de 0 A a 1.6 A (en Vin = 25 V)
R_ZD N_IN N_BD 180
D_ZD 0 N_BD DZ10V
Q_1D N_IN N_BD N_IREGD QTIP31C
C_1D N_IREGD 0 330n
X_REG_D N_IREGD 0 N_OUTD LM7805C
C_2D N_OUTD 0 100n
V_MEAS_D N_OUTD N_LOAD_D DC 0
I_LOAD N_LOAD_D 0 DC 0.500

.CONTROL
set wr_singlescale
set wr_vecnames

* 1. Barrido DC de Tensión de Entrada Vin de 0 V a 30 V (paso 0.25 V)
dc V_IN 0 30 0.25
wrdata raw_regulacion_linea.txt v(N_BA) v(N_IREGA) v(N_OUTA) v(N_BB) v(N_IREGB) v(N_OUTB) v(N_OUTC)

* 2. Barrido DC de Corriente de Carga I_LOAD de 0.005 A a 1.60 A (paso 0.015 A) con Vin = 25 V
alter V_IN = 25.0
dc I_LOAD 0.005 1.60 0.015
wrdata raw_regulacion_carga.txt v(N_BD) v(N_IREGD) v(N_OUTD)

* 3. Análisis Transitorio con Ripple de Entrada de 2 Vpp (1.0 V pico @ 100 Hz) sobre Vin = 25 V
tran 0.05m 20m 0 0.05m
wrdata raw_ripple_tran.txt v(N_IN) v(N_BA) v(N_IREGA) v(N_OUTA) v(N_OUTC)

quit
.ENDC
.END
"""

cir_path = os.path.join(SIM_DIR, "fuente_7805.cir")
with open(cir_path, "w") as f:
    f.write(spice_netlist)

res = subprocess.run(["ngspice", "-b", "fuente_7805.cir"], cwd=SIM_DIR, capture_output=True, text=True)
if res.returncode != 0:
    print("Error ejecutando ngspice:", res.stderr)
    raise SystemExit(1)

# ==============================================================================
# 2. PROCESAMIENTO Y FORMATEO DE TABLAS PARA PGFPLOTS
# ==============================================================================

# 2.1 Regulación de Línea (raw_regulacion_linea.txt)
# Columnas con wr_singlescale: 0=v-sweep(Vin), 1=v(N_BA), 2=v(N_IREGA), 3=v(N_OUTA), 4=v(N_BB), 5=v(N_IREGB), 6=v(N_OUTB), 7=v(N_OUTC)
data_linea = np.loadtxt(os.path.join(SIM_DIR, "raw_regulacion_linea.txt"), skiprows=1)
vin = data_linea[:, 0]
v_ba = data_linea[:, 1]
v_irega = data_linea[:, 2]
v_outa = data_linea[:, 3]
v_bb = data_linea[:, 4]
v_iregb = data_linea[:, 5]
v_outb = data_linea[:, 6]
v_outc = data_linea[:, 7]

vo_ref_a = np.interp(10.0, vin, v_outa)
vo_ref_c = np.interp(10.0, vin, v_outc)
dvo_a_mv = (v_outa - vo_ref_a) * 1000.0
dvo_c_mv = (v_outc - vo_ref_c) * 1000.0

with open(os.path.join(SIM_DIR, "regulacion_linea.txt"), "w") as f:
    f.write("Vin VzA ViregA VoA VzB ViregB VoB VoDirecto dVoA_mV dVoDirecto_mV\n")
    for i in range(len(vin)):
        f.write(f"{vin[i]:.2f} {v_ba[i]:.4f} {v_irega[i]:.4f} {v_outa[i]:.6f} "
                f"{v_bb[i]:.4f} {v_iregb[i]:.4f} {v_outb[i]:.6f} {v_outc[i]:.6f} "
                f"{dvo_a_mv[i]:.4f} {dvo_c_mv[i]:.4f}\n")

def get_point_linea(v_target):
    idx = np.argmin(np.abs(vin - v_target))
    return {
        "Vin": float(vin[idx]),
        "VzA": float(v_ba[idx]),
        "ViregA": float(v_irega[idx]),
        "VoA": float(v_outa[idx]),
        "VzB": float(v_bb[idx]),
        "ViregB": float(v_iregb[idx]),
        "VoB": float(v_outb[idx]),
        "VoDirecto": float(v_outc[idx]),
    }

pts_linea = {str(v): get_point_linea(v) for v in [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 15.0, 20.0, 22.5, 24.0, 25.0, 27.5, 30.0]}

# 2.2 Regulación de Carga (raw_regulacion_carga.txt)
# Columnas: 0=i-sweep(IL), 1=v(N_BD), 2=v(N_IREGD), 3=v(N_OUTD)
data_carga = np.loadtxt(os.path.join(SIM_DIR, "raw_regulacion_carga.txt"), skiprows=1)
il_vec = data_carga[:, 0]
v_bd = data_carga[:, 1]
v_iregd = data_carga[:, 2]
v_outd = data_carga[:, 3]

with open(os.path.join(SIM_DIR, "regulacion_carga.txt"), "w") as f:
    f.write("IL_A IL_mA Vz Vireg Vo dVo_mV PQ1_W P7805_W PLoad_W Eta_pct\n")
    vo_0 = v_outd[0]
    for i in range(len(il_vec)):
        il = il_vec[i]
        vireg = v_iregd[i]
        vo = v_outd[i]
        dvo_mv = (vo - vo_0) * 1000.0
        ie_q1 = il + 0.0045
        pq1 = (25.0 - vireg) * ie_q1
        p7805 = (vireg - vo) * il + vireg * 0.0045
        pload = vo * il
        pin = 25.0 * (ie_q1 + (25.0 - v_bd[i])/180.0)
        eta = (pload / pin) * 100.0 if pin > 0 else 0.0
        f.write(f"{il:.4f} {il*1000.0:.1f} {v_bd[i]:.4f} {vireg:.4f} {vo:.6f} "
                f"{dvo_mv:.3f} {pq1:.3f} {p7805:.3f} {pload:.3f} {eta:.2f}\n")

# 2.3 Análisis Transitorio de Ripple (raw_ripple_tran.txt)
data_tran = np.loadtxt(os.path.join(SIM_DIR, "raw_ripple_tran.txt"), skiprows=1)
# Submuestreamos para que el archivo tenga ~200 puntos limpios para pgfplots
step = max(1, len(data_tran) // 200)
t_ms = data_tran[::step, 0] * 1000.0
vin_t = data_tran[::step, 1]
vba_t = data_tran[::step, 2]
virega_t = data_tran[::step, 3]
vouta_t = data_tran[::step, 4]
voutc_t = data_tran[::step, 5]

ac_vin_v = vin_t - np.mean(vin_t)
ac_virega_mv = (virega_t - np.mean(virega_t)) * 1000.0
ac_vouta_uv = (vouta_t - np.mean(vouta_t)) * 1e6
ac_voutc_uv = (voutc_t - np.mean(voutc_t)) * 1e6

with open(os.path.join(SIM_DIR, "ripple_tran.txt"), "w") as f:
    f.write("t_ms ac_Vin_V ac_Vireg_mV ac_VoCon_uV ac_VoSin_uV\n")
    for i in range(len(t_ms)):
        f.write(f"{t_ms[i]:.3f} {ac_vin_v[i]:.4f} {ac_virega_mv[i]:.3f} "
                f"{ac_vouta_uv[i]:.3f} {ac_voutc_uv[i]:.3f}\n")

# 2.4 Curvas del Área de Operación Segura (SOA) para TIP31C y BD135-16 (sim/soa_data.txt)
vce_soa = np.logspace(0, 2, 100)  # 1 V a 100 V
ic_tip31_25c = np.minimum(3.0, 40.0 / vce_soa)
ic_tip31_25c = np.where(vce_soa > 40.0, np.minimum(ic_tip31_25c, (40.0/40.0) * (40.0/vce_soa)**1.65), ic_tip31_25c)
ic_tip31_85c = np.minimum(3.0, 20.8 / vce_soa)
ic_tip31_85c = np.where(vce_soa > 40.0, np.minimum(ic_tip31_85c, (20.8/40.0) * (40.0/vce_soa)**1.65), ic_tip31_85c)

ic_bd135_25c = np.minimum(1.5, 12.5 / vce_soa)
ic_bd135_25c = np.where(vce_soa > 25.0, np.minimum(ic_bd135_25c, (12.5/25.0) * (25.0/vce_soa)**1.8), ic_bd135_25c)
ic_bd135_25c = np.where(vce_soa > 45.0, 0.001, ic_bd135_25c)

with open(os.path.join(SIM_DIR, "soa_data.txt"), "w") as f:
    f.write("Vce IC_TIP31C_25C IC_TIP31C_85C IC_BD135_25C\n")
    for i in range(len(vce_soa)):
        f.write(f"{vce_soa[i]:.3f} {ic_tip31_25c[i]:.4f} {ic_tip31_85c[i]:.4f} {ic_bd135_25c[i]:.4f}\n")

# 2.5 Curva de Derating Térmico (sim/termico_data.txt)
tc_vec = np.linspace(0, 150, 76)
pd_tip31 = np.where(tc_vec <= 25.0, 40.0, np.maximum(0.0, 40.0 - (tc_vec - 25.0) / 3.125))
pd_bd135 = np.where(tc_vec <= 25.0, 12.5, np.maximum(0.0, 12.5 - (tc_vec - 25.0) / 10.0))
pd_7805 = np.where(tc_vec <= 25.0, 20.8, np.maximum(0.0, (150.0 - tc_vec) / 6.0))

with open(os.path.join(SIM_DIR, "termico_data.txt"), "w") as f:
    f.write("Tc_C PD_TIP31C_W PD_BD135_W PD_LM7805_W\n")
    for i in range(len(tc_vec)):
        f.write(f"{tc_vec[i]:.1f} {pd_tip31[i]:.3f} {pd_bd135[i]:.3f} {pd_7805[i]:.3f}\n")

summary = {
    "puntos_linea": pts_linea,
    "reg_linea_con_prereg_10_a_25V_CircA": {
        "Vo_10V": pts_linea["10.0"]["VoA"],
        "Vo_25V": pts_linea["25.0"]["VoA"],
        "Vireg_10V": pts_linea["10.0"]["ViregA"],
        "Vireg_25V": pts_linea["25.0"]["ViregA"],
        "dVo_mV": (pts_linea["25.0"]["VoA"] - pts_linea["10.0"]["VoA"]) * 1000.0,
        "Rred_pct": ((pts_linea["25.0"]["VoA"] - pts_linea["10.0"]["VoA"]) / pts_linea["10.0"]["VoA"]) * 100.0
    },
    "reg_linea_con_prereg_12_a_25V_CircB": {
        "Vo_12V": pts_linea["12.0"]["VoB"],
        "Vo_25V": pts_linea["25.0"]["VoB"],
        "Vireg_12V": pts_linea["12.0"]["ViregB"],
        "Vireg_25V": pts_linea["25.0"]["ViregB"],
        "dVo_mV": (pts_linea["25.0"]["VoB"] - pts_linea["12.0"]["VoB"]) * 1000.0,
        "Rred_pct": ((pts_linea["25.0"]["VoB"] - pts_linea["12.0"]["VoB"]) / pts_linea["12.0"]["VoB"]) * 100.0
    },
    "reg_linea_sin_prereg_10_a_25V": {
        "Vo_10V": pts_linea["10.0"]["VoDirecto"],
        "Vo_25V": pts_linea["25.0"]["VoDirecto"],
        "dVo_mV": (pts_linea["25.0"]["VoDirecto"] - pts_linea["10.0"]["VoDirecto"]) * 1000.0,
        "Rred_pct": ((pts_linea["25.0"]["VoDirecto"] - pts_linea["10.0"]["VoDirecto"]) / pts_linea["10.0"]["VoDirecto"]) * 100.0
    },
    "reg_linea_pm10pct_en_25V": {
        "con_prereg_A_dVo_mV": (pts_linea["27.5"]["VoA"] - pts_linea["22.5"]["VoA"]) * 1000.0,
        "con_prereg_B_dVo_mV": (pts_linea["27.5"]["VoB"] - pts_linea["22.5"]["VoB"]) * 1000.0,
        "sin_prereg_C_dVo_mV": (pts_linea["27.5"]["VoDirecto"] - pts_linea["22.5"]["VoDirecto"]) * 1000.0,
    },
    "reg_linea_pm10pct_en_10V": {
        "sin_prereg_C_dVo_mV": (pts_linea["11.0"]["VoDirecto"] - pts_linea["9.0"]["VoDirecto"]) * 1000.0,
    },
    "ripple_2Vpp_100Hz": {
        "Vr_in_pp_V": float(np.max(ac_vin_v) - np.min(ac_vin_v)),
        "Vr_iregA_pp_mV": float(np.max(ac_virega_mv) - np.min(ac_virega_mv)),
        "Vr_outA_pp_uV": float(np.max(ac_vouta_uv) - np.min(ac_vouta_uv)),
        "Vr_outC_pp_uV": float(np.max(ac_voutc_uv) - np.min(ac_voutc_uv)),
    }
}

with open(os.path.join(SIM_DIR, "resumen_resultados.json"), "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
