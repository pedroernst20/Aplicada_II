* Ecualizador de 3 bandas (EA2-TD2) - camino de audio (entrada a EQOUT), para incluir desde cada simulacion
* Los detectores hacia el Blue Pill estan en eq_detectores.inc (solo los incluyen los transitorios).
* Base: ecualizador de Franco Palombo (repo fpp3, tp4/sources/ampli.kicadproj/3band_eq.kicad_sch).
* Cambios: agudos con 10k (3,39 kHz), medios con MFB de ganancia -1 (en vez de SK + inversor x1,2),
* realce/corte por banda con pote lineal, sumador x2,2, detectores de pico al ADC y detector de recorte.
*
* Parametros que define cada simulacion:
*   gb, gm, gt : giro de los potes de graves, medios y agudos (0 = corte maximo, 0,5 = plano, 1 = realce maximo)
*   tolr, tolc : tolerancia de resistencias y capacitores para Monte Carlo (0 en las corridas nominales)
* Entradas: INL, INR (canales del jack). Salida al TP4: EQOUT.
* Las referencias (U1A, RG1...) son provisorias: se igualan a las del esquematico de KiCad en la etapa 2.

.lib tl08x.lib
.lib modelos_eq.lib
.param Rpot=100k

* ---------------- Alimentaciones ----------------
VCC VCC 0 15
VEE VEE 0 -15
V33 V3V3 0 3.3

* ---------------- Entrada: mezcla L+R y buffer (U1A) ----------------
RINL INL MIX {mc(10k,tolr)}
RINR INR MIX {mc(10k,tolr)}
CIN  MIX BUFIN 1u
RBIAS BUFIN 0 {mc(100k,tolr)}
XU1A BUFIN VI VCC VEE VI TL08X_SINGLE

* ---------------- Graves: Sallen-Key pasa-bajos, 282 Hz, Q = 0,5 (U1B) ----------------
RG1 VI G1 {mc(120k,tolr)}
RG2 G1 G2 {mc(120k,tolr)}
CG1 G1 VB {mc(4.7n,tolc)}
CG2 G2 0  {mc(4.7n,tolc)}
XU1B G2 VB VCC VEE VB TL08X_SINGLE

* ---------------- Agudos: Sallen-Key pasa-altos, 3,39 kHz, Q = 0,5 (U1C) ----------------
CA1 VI A1 {mc(4.7n,tolc)}
CA2 A1 A2 {mc(4.7n,tolc)}
RA1 A1 VT {mc(10k,tolr)}
RA2 A2 0  {mc(10k,tolr)}
XU1C A2 VT VCC VEE VT TL08X_SINGLE

* ---------------- Medios: pasa-altos SK 282 Hz (U1D) + pasa-bajos MFB 3,39 kHz, ganancia -1 (U2A) ----------------
CM1 VI M1 {mc(4.7n,tolc)}
CM2 M1 M2 {mc(4.7n,tolc)}
RM1 M1 VMH {mc(120k,tolr)}
RM2 M2 0   {mc(120k,tolr)}
XU1D M2 VMH VCC VEE VMH TL08X_SINGLE
RM3 VMH M3 {mc(10k,tolr)}
RM4 M3  VM {mc(10k,tolr)}
RM5 M3  M4 {mc(12k,tolr)}
CM3 M3  0  {mc(6.8n,tolc)}
CM4 M4  VM {mc(2.7n,tolc)}
XU2A 0 M4 VCC VEE VM TL08X_SINGLE

* ---------------- Realce/corte: inversor con pote lineal de 100k entre dos 22k (U2B, U2C, U2D) ----------------
* Ganancia = -(22k + g*P)/(22k + (1-g)*P): g = 1 -> +15,6 dB, g = 0,5 -> 0 dB, g = 0 -> -15,6 dB
* (en el centro de cada banda queda entre +-11 y +-15 dB porque las bandas vecinas se solapan)
RB1 VB B1 {mc(22k,tolr)}
RVB1 B1 BW {Rpot*max(1-gb,1e-4)}
RVB2 BW B2 {Rpot*max(gb,1e-4)}
RB2 B2 VBO {mc(22k,tolr)}
XU2B 0 BW VCC VEE VBO TL08X_SINGLE

RMM1 VM MM1 {mc(22k,tolr)}
RVM1 MM1 MW {Rpot*max(1-gm,1e-4)}
RVM2 MW MM2 {Rpot*max(gm,1e-4)}
RMM2 MM2 VMO {mc(22k,tolr)}
XU2C 0 MW VCC VEE VMO TL08X_SINGLE

RT1 VT T1 {mc(22k,tolr)}
RVT1 T1 TW {Rpot*max(1-gt,1e-4)}
RVT2 TW T2 {Rpot*max(gt,1e-4)}
RT2 T2 VTO {mc(22k,tolr)}
XU2D 0 TW VCC VEE VTO TL08X_SINGLE

* ---------------- Sumador inversor, ganancia 2,2 (U3A) ----------------
RS1 VBO S {mc(10k,tolr)}
RS2 VMO S {mc(10k,tolr)}
RS3 VTO S {mc(10k,tolr)}
RSF S VEQ {mc(22k,tolr)}
XU3A 0 S VCC VEE VEQ TL08X_SINGLE
ROUT VEQ EQOUT 100
* Carga: entrada del TP4 (C207 470n + R214 100k)
CL EQOUT LIN 470n
RL LIN 0 100k

