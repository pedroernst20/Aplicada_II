# TP4 – Simulación del amplificador clase AB Darlington (rev 2.4)

**Archivo:** `ampli.asc` (LTspice 24). Es el `ampli.asc` de Franco Palombo (repo fpp3, `tp4/sources/sim`) adaptado a nuestro circuito: mismo dibujo, con las referencias del esquemático de KiCad.

**Modelos:** `TIP122.LIB`, `TIP127.LIB`, `bjt.lib` (BC337/BC327) y `tl08x.lib` (TL082, para el simulador de KiCad).

**Condiciones:** ±15 V, R_L = 8 Ω, R209 = R210 = 0,47 Ω, Av = 1 + 27k/6k8 = 4,97.

**Verificación:** el netlist de LTspice coincide pin por pin con el de KiCad en los 36 componentes que tienen ambos. El netlist que exporta KiCad, corrido en el ngspice de KiCad 10, da Iq = 24,1 mA y V_o = ±5,66 V.

## Qué cambia respecto del circuito de Franco

| Parte | Franco (`ampli.asc`) | Nuestro | Motivo |
|---|---|---|---|
| Carga | 4 Ω | 8 Ω | Consigna |
| Ganancia | 1 + 33k/3k9 = 9,46 | 1 + 27k/6k8 = 4,97 | Como quedó en el esquemático |
| R de emisor | 0,1 Ω | 0,47 Ω | Iq medible y limitador sin resistencias raras |
| R208 | 3k3 fija | 3k + trimpot 1k | Iq ajustable |
| R203, R202 | 1k | 2k2 | Como quedó en el esquemático |
| Transistores chicos | BC547C/BC557C | BC337/BC327 | Los de la placa |
| Agregados | — | C207 (470 nF) + R214, Zobel, limitador, desacople, diodos de polaridad | Placa autónoma |

Referencia: el circuito original de Franco da Iq = 73 mA y 11,2 W sobre 4 Ω con 1 V pico de entrada.

## Resultados

| Ensayo | Resultado |
|---|---|
| Iq vs RV201 (1 Ω → 1 kΩ) | 92 → 70 → 52 → 36 → **24 (400 Ω)** → 15 → 9 → 3,4 → 1,4 mA |
| 2 W en 8 Ω (1,14 V pico de entrada) | P_L = 2,006 W, ±5,66 V, distorsión armónica 0,04 % |
| Disipación por transistor a 2 W | 2,34 W: **lleva disipador** |
| Máximo sin distorsión | 6,8 W (10,4 V pico, 0,01 %) |
| Límite | ≈ ±10,9 V, 1,36 A pico |
| Corto a la salida (0,1 Ω) | 1,47 A pico, 10,3 W por transistor |
| Cruce por cero, 0,3 V pico, 1 kHz | Iq 24 mA: 0,0017 % · Iq 1,4 mA: 0,017 % |
| Cruce por cero, 0,3 V pico, 20 kHz | Iq 24 mA: 0,016 % · Iq 1,4 mA: 0,17 % |
| Bode | 13,9 dB; −3 dB en 3,4 Hz y 59 kHz; −0,12 dB a 20 Hz |
| Escalón con 8 Ω + 0,5 mH | Sin sobrepico, con y sin Zobel |

### Temperatura (Iq en reposo, fuentes de corriente a 27 °C)

| Darlington a | Q205 sin acople térmico | Q205 a la misma temperatura |
|---|---|---|
| 27 °C | 24 mA | 24 mA |
| 50 °C | 70 mA | 20 mA |
| 75 °C | 136 mA | 17 mA |
| 100 °C | 211 mA | 14 mA |

### Fallas de alimentación (sin señal)

| Falla | Resultado |
|---|---|
| Se suelta −15 V | Salida en +2,3 V; D202 limita el riel a +0,65 V |
| Se suelta +15 V | Salida en −2,3 V; D201 limita el riel a −0,65 V |
| Ambas polaridades invertidas (fuente limitada) | Rieles en ±0,78 V; no llega tensión inversa a los componentes |

Sin los diodos, perder un riel deja ±10,6 V de continua sobre la carga.

## Procedimiento en banco

1. RV201 en 1 kΩ: es la posición de Iq mínima. Medirlo con el tester antes de alimentar.
2. Fuente de ±15 V con límite de corriente en unos 200 mA, sin carga y con la entrada a masa.
3. Sin jumper en JP202 (sin carga), bajar RV201 hasta leer **11,3 mV entre TP208 y TP210** (Iq ≈ 24 mA): es una medición indirecta, la tensión sobre R209.
4. Carga de 8 Ω / 10 W en TP204/TP205, JP202 en 2-3 y JP201 en 2-3, con el generador en TP206/TP207: 1 kHz, 1,14 V pico → 5,66 V pico a la salida (2 W).
5. Dejar calentar unos minutos, sacar la señal y volver a medir entre TP208 y TP210.
6. Recién después, parlante en J110 con JP202 en 1-2.
