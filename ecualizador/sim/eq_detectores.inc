* Ecualizador de 3 bandas (EA2-TD2) - detectores hacia el Blue Pill. Se incluye despues de eq_audio.inc.
* Salidas: ADC_B, ADC_M, ADC_T (PA0..PA2) y EXTI (PB0). Usa los nodos VBO, VMO, VTO, VEQ, VCC, VEE y V3V3.

* ---------------- Detectores de pico por banda -> ADC (U3B, U3C, U3D) ----------------
* Detector de pico de precision con ganancia 1 + 33k/68k = 1,49; descarga por el divisor (101k * 470n = 47 ms)
* Al ADC: 10k en serie, Schottky BAT41 a 3,3 V y 10 nF
XU3B VBO FBB VCC VEE OB TL08X_SINGLE
DPB OB CB 1N4148
CPB CB 0 470n
RPB1 CB FBB 33k
RPB2 FBB 0 68k
RADB CB ADC_B 10k
XDCB ADC_B V3V3 BAT41
CADB ADC_B 0 10n

XU3C VMO FBM VCC VEE OM TL08X_SINGLE
DPM OM CM 1N4148
CPM CM 0 470n
RPM1 CM FBM 33k
RPM2 FBM 0 68k
RADM CM ADC_M 10k
XDCM ADC_M V3V3 BAT41
CADM ADC_M 0 10n

XU3D VTO FBT VCC VEE OT TL08X_SINGLE
DPT OT CT 1N4148
CPT CT 0 470n
RPT1 CT FBT 33k
RPT2 FBT 0 68k
RADT CT ADC_T 10k
XDCT ADC_T V3V3 BAT41
CADT ADC_T 0 10n

* ---------------- Detector de recorte (U4 = TL082) ----------------
* U4A: detector de pico de VEQ (220n // 1M = 220 ms: el LED queda prendido unas decenas de ms). U4B: comparador con histeresis.
* Umbral: 5,66 V pico en el parlante (2 W en 8 ohm) / 4,97 (ganancia del TP4) = 1,14 V pico en VEQ.
XU4A VEQ CC VCC VEE OC TL08X_SINGLE
DPC OC CC 1N4148
CPC CC 0 220n
RPC CC 0 1Meg
XU4B REF CC VCC VEE OK TL08X_SINGLE
RR1 VCC REF 82k
RR2 REF 0 6.2k
RRH OK REF 1Meg
* Sin recorte OK esta alto: Q1 conduce y EXTI queda en 0. Con recorte OK baja: EXTI sube a 3,3 V y se prende el LED.
DQ OK NQ 1N4148
RQB NQ QB 22k
RQBE QB 0 47k
Q1 EXTI QB 0 BC547B
RPU V3V3 EXTI 10k
DLED 0 NL QTLP690C
RLED NL NL2 1.5k
DL2 NL2 OK 1N4148
