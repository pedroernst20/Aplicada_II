# Ecualizador de 3 bandas: cálculo y simulación (etapa 1)

**Base:** el ecualizador de Franco Palombo (repo `fpp3/ElectronicaAplicada2`, `tp4/sources/ampli.kicadproj/3band_eq.kicad_sch` y `sim/eq.asc`). Se mantienen sus filtros de graves y de la banda media; cambian el sumador, el agudo y la ganancia de la banda media, y se agregan los detectores para el Blue Pill.

**Archivos:** el circuito está en `eq_audio.inc` (de la entrada a `EQOUT`) y `eq_detectores.inc` (hacia el Blue Pill); cada `.cir` es una simulación. `python correr_simulaciones.py` corre todo en LTspice 24 (unos 7 min), escribe `resultados.json` y las figuras de `figuras/`.

**Modelos:** TL084/TL082 de TI (`tl08x.lib`, el mismo del TP4). Contra la hoja de datos: GBW = 282,8 µS / (2π · 15 pF) = 3,0 MHz y SR = 195 µA / 15 pF = 13 V/µs, iguales a los típicos (3 MHz y 13 V/µs). 1N4148, BC547B y el LED rojo QTLP690C salen de las bibliotecas estándar de LTspice; el 1N5711 es el modelo de Diodes Inc para el 1N5711WS (mismo chip); contra la hoja de datos del 1N5711 da 0,43 V a 1 mA (máximo 0,41 V) y 0,61 V a 15 mA (máximo 1 V), o sea que cae un poco más que el diodo real y el resultado del ADC queda del lado seguro. Todos están en `modelos_eq.lib`.

**Condiciones:** ±15 V; entrada de 0,5 V pico en L y R (el nivel del anteproyecto); carga = entrada del TP4 (C207 470 nF + R214 100 kΩ).

## Qué cambia respecto del ecualizador de Franco

| Parte | Franco | Nuevo | Motivo |
|---|---|---|---|
| Agudos | SK 8k2 / 4n7: 4,13 kHz | SK 10k / 4n7: **3,39 kHz** | El anteproyecto pide 3,4 kHz |
| Medios | SK pasa-bajos + SK pasa-altos + inversor ×1,2 (3 operacionales) | SK pasa-altos + **MFB pasa-bajos de ganancia −1** (2 operacionales) | Con ×1,2 la suma con los potes al medio tiene un pico de +1,2 dB; con ×1 queda plana dentro de 0,16 dB. El MFB invierte solo, así que ahorra el inversor |
| Ajuste por banda | Pote de 500k como resistencia en serie hacia un sumador pasivo, ×4,92 | **Etapa de realce/corte por banda**: pote lineal de 100k entre dos 22k, cursor a la entrada inversora | El de Franco corta solo −4,8 dB, y al realzar los graves baja los medios 6,7 dB y los agudos 14,9 dB (figura 2) |
| Sumador | No inversor ×4,92 | Inversor ×2,2 (10k / 22k) | Con 0,5 V pico de entrada la potencia queda cerca de 2 W con los potes al medio |
| Entrada | Directo al buffer | L y R por 10k, 1 µF y 100k a masa | Mezcla a mono y saca la continua del generador o del celular |
| Agregados | — | 3 detectores de pico al ADC, detector de recorte con LED y EXTI, 100 Ω en serie a la salida | Parte de TD2 del anteproyecto |

## Diseño por bloques

| Bloque | Circuito | Valores | Resultado |
|---|---|---|---|
| Entrada | L y R por 10k a un nodo, 1 µF + 100k, seguidor | — | Corte de 1,6 Hz; pierde 0,4 dB (100k contra 5k) |
| Graves | Sallen-Key pasa-bajos de componentes iguales | 120k, 120k, 4n7, 4n7 | f = 1/(2π · 120k · 4n7) = **282 Hz**, Q = 0,5 |
| Agudos | Sallen-Key pasa-altos de componentes iguales | 4n7, 4n7, 10k, 10k | f = 1/(2π · 10k · 4n7) = **3,39 kHz**, Q = 0,5 |
| Medios (1) | Sallen-Key pasa-altos | 4n7, 4n7, 120k, 120k | 282 Hz, Q = 0,5 |
| Medios (2) | MFB pasa-bajos | R1 = R2 = 10k, R3 = 12k, C1 = 6n8 (a masa), C2 = 2n7 (realimentación) | H0 = −R2/R1 = −1; f = 1/(2π√(R2·R3·C1·C2)) = **3,39 kHz**; Q = √(R2·R3·C1·C2) / (C2·(R2 + R3 + R2·R3/R1)) = 0,51. Centro de la banda: √(282 · 3390) = **978 Hz** |
| Realce/corte | Inversor; pote B100K entre dos 22k, cursor a la entrada − | 22k, 100k, 22k | G = −(22k + g·100k)/(22k + (1−g)·100k): de −15,6 dB a +15,6 dB, 0 dB con el pote al medio |
| Sumador | Inversor | 3 × 10k, Rf = 22k | ×2,2. Los medios llegan invertidos dos veces (MFB y realce/corte) y los graves y agudos una: queda la polaridad relativa que hace plana la suma |
| Salida al TP4 | 100 Ω en serie | — | Aísla el operacional de la capacidad del cable |
| Detector de banda (×3) | Detector de pico de precisión con ganancia | 1N4148, 470 nF, 33k + 68k | Ganancia 1 + 33k/68k = 1,49; descarga 101k · 470 nF = 47 ms |
| Protección del ADC (×3) | 10k en serie, Schottky a 3,3 V, 10 nF a masa | 1N5711 (el BAT46 y el BAT41 no se consiguieron) | El detector nunca da tensión negativa, así que alcanza un solo diodo |
| Detector de recorte | Detector de pico de VEQ + comparador con histéresis | 1N4148, 220 nF // 1M; umbral 82k / 6k2 desde +15 V, 1M de realimentación | Umbral: 5,66 V pico en el parlante (2 W en 8 Ω) / 4,97 (ganancia del TP4) = 1,14 V pico |
| Salida del recorte | Comparador → 1N4148 → 22k → BC547B (47k base-emisor), 10k a 3,3 V; LED rojo con 1k5 y 1N4148 hacia la salida del comparador | — | Sin recorte el BC547 conduce y EXTI queda en 0 V. Con recorte la salida del comparador baja a −13 V: EXTI sube a 3,3 V y el LED prende |

### Reparto de operacionales (provisorio)

| Integrado | A | B | C | D |
|---|---|---|---|---|
| U1 TL084 | Buffer de entrada | Graves | Agudos | Medios, pasa-altos |
| U2 TL084 | Medios, MFB | Realce/corte graves | Realce/corte medios | Realce/corte agudos |
| U3 TL084 | Sumador | Detector graves | Detector medios | Detector agudos |
| U4 TL082 | Pico de VEQ | Comparador de recorte | — | — |

Las unidades de cada integrado son iguales: el reparto final se decide al ubicar las piezas (etapa 3).

## Resultados

### Respuesta en frecuencia (`eq_ac.cir`)

![Respuesta con cada pote en sus extremos](figuras/eq_bode.png)

| Ensayo | Resultado |
|---|---|
| Potes al medio, 20 Hz a 20 kHz | **6,29 a 6,45 dB (ondulación 0,16 dB)**; 6,31 dB a 1 kHz (×2,07) |
| Graves, 50 Hz | **+14,7 / −13,8 dB** |
| Graves, 100 Hz | +14,0 / −11,3 dB |
| Medios, 1 kHz | **+13,9 / −10,8 dB** |
| Agudos, 10 kHz | **+14,1 / −11,5 dB** |
| Agudos, 5 kHz | +12,3 / −7,1 dB |

El anteproyecto pide al menos ±10 dB por banda: se cumple en el centro de cada banda (50 Hz, 1 kHz y 10 kHz). El corte llega a menos que el realce porque, con filtros de Q = 0,5, las bandas vecinas siguen aportando: a 1 kHz los graves y los agudos pasan un 8 % cada uno. Con 33k en vez de 22k la etapa daría ±12 dB justos, pero el corte de medios quedaba en −9,2 dB.

### Comparación con el sumador de Franco (`franco_eq_ac.cir`)

![Sumador de Franco contra el nuevo](figuras/franco_vs_nuevo.png)

| Ensayo | Franco | Nuevo |
|---|---|---|
| Ondulación con los potes al medio | 1,3 dB | 0,16 dB |
| Graves al máximo, a 50 Hz | +13,2 dB | +14,7 dB |
| Graves al mínimo, a 50 Hz | **−4,8 dB** | −13,8 dB |
| Graves al máximo: efecto sobre los medios (1 kHz) | **−6,7 dB** | +2,3 dB (la cola del pasa-bajos de graves) |
| Graves al máximo: efecto sobre los agudos (10 kHz) | **−14,9 dB** | 0,0 dB |

### Tolerancias (`eq_mc.cir`, 100 corridas, resistencias 1 % y capacitores 5 %)

| Ensayo | Resultado |
|---|---|
| Ondulación con los potes al medio | media 0,29 dB, peor 0,53 dB |
| Ganancia a 1 kHz | 6,03 a 6,51 dB |
| Corte de medios a 1 kHz | media −10,8 dB, **peor −10,4 dB** (sigue cumpliendo los −10 dB) |

### Detectores de banda (`eq_tran_bandas.cir`)

Tono de 100 Hz, 1 kHz y 8 kHz (250 ms cada uno) y silencio. Tensión media al ADC en los últimos 25 ms de cada tono:

| Caso | Tono | Graves (PA0) | Medios (PA1) | Agudos (PA2) |
|---|---|---|---|---|
| 0,5 V pico, potes al medio | 100 Hz | **0,58 V** | 0,08 V | 0,02 V |
| | 1 kHz | 0,05 V | **0,60 V** | 0,05 V |
| | 8 kHz | 0,02 V | 0,07 V | **0,53 V** |
| 0,5 V pico, graves al máximo y medios al mínimo | 100 Hz | **3,17 V** | 0,02 V | 0,02 V |
| | 1 kHz | 0,28 V | **0,11 V** | 0,05 V |
| | 8 kHz | 0,02 V | 0,02 V | 0,53 V |

![Detectores con los potes al medio](figuras/bandas_centro.png)

![Detectores con graves al máximo y medios al mínimo](figuras/bandas_graves_max_medios_min.png)

- Las barras siguen a los potes: con los graves al máximo, la barra de graves sube de 0,58 V a 3,17 V.
- Descarga: la tensión cae al 37 % en 49 ms (diseño: 47 ms; se suman los 10k y los 10 nF del ADC).
- Con 0,5 V pico y los potes al medio la barra queda en unos 0,6 V: el fondo de escala se usa recién con realce. Con 12 bits son unas 740 cuentas, resolución de sobra para barras en dB.
- **Sobrecarga** (1,5 V pico con graves al máximo): el detector querría unos 11 V, pero el pin no pasa de **3,71 V** y por el Schottky circulan **0,69 mA**. El 1N5711 cae más que el BAT46 (3,53 V) y que el BAT41 (3,65 V), así que el pin pasa unos 0,1 V los 3,6 V (3,3 + 0,3 V); la hoja del STM32 lo admite mientras la corriente inyectada quede limitada, y los 10k la dejan en 0,69 mA contra 5 mA permitidos por pin. El modelo es pesimista: con la caída máxima de la hoja (0,41 V a 1 mA) el pin quedaría en unos 3,68 V.
- En el peor caso de uso normal (0,5 V pico, graves al máximo) las salidas de banda llegan a 2,4 V pico y VEQ a 5,3 V pico: ningún operacional satura.

### Detector de recorte (`eq_tran_recorte.cir`, `eq_tran_histeresis.cir`)

![Detector de recorte](figuras/recorte.png)

| Ensayo | Resultado |
|---|---|
| Dispara con VEQ de | **1,14 V pico** → 5,67 V en el parlante = **2,01 W** |
| Suelta con VEQ de | 0,97 V pico (1,46 W) |
| Umbral sin recorte / con recorte | 1,126 V / 0,971 V |
| Retardo desde que VEQ pasa el umbral hasta que EXTI sube | **4,7 µs** (el anteproyecto pide menos de 20 µs) |
| EXTI sin recorte / con recorte | 0,009 V / 3,30 V |
| Corriente del LED | 7,3 mA |
| Después de 100 ms de recorte, el LED sigue prendido | 51 ms |
| Ráfaga de 5 ms: el LED queda prendido | **66 ms** (se ve) |

## Niveles de la cadena completa

- Con 0,5 V pico de entrada y los potes al medio: VEQ = 1,03 V pico → TP4 ×4,97 = 5,1 V pico → **1,65 W** en 8 Ω.
- Con 0,55 V pico la salida llega a 2 W y el LED de recorte empieza a prender. Con cualquier realce de +12 dB el TP4 recorta (pasa de ±10,9 V), y para eso está el LED.

## Limitaciones

- El detector de recorte mira VEQ, no la salida real del TP4: avisa cuando la salida pasa de 2 W, no cuando el amplificador recorta de verdad (≈ 6,8 W). Así no hace falta traer la salida del TP4 con otro cable (decisión del 2026-11-08).
- Solo detecta los picos positivos. Para audio alcanza, porque la señal es simétrica.
- El umbral depende de los +15 V (divisor 82k / 6k2): un 1 % de error en la fuente corre el umbral un 1 %.

## Paridad con el esquemático de KiCad

`python paridad_kicad_ltspice.py` exporta el netlist de `../placa/ecualizador.kicad_sch` y lo compara con `eq_audio.inc` y `eq_detectores.inc`: **87 elementos y 57 nodos, cada nodo de LTspice es una sola red de KiCad y viceversa** (2026-11-10). Hay que volver a correrlo después de cualquier cambio en el esquemático o en la simulación.

Correspondencia de referencias (LTspice → KiCad): RINL/RINR → R1/R2, CIN → C3, RBIAS → R3, RG1/RG2/CG1/CG2 → R4/R5/C4/C5, CA1/CA2/RA1/RA2 → C6/C7/R6/R7, CM1/CM2/RM1/RM2 → C8/C9/R8/R9, RM3/RM4/RM5/CM3/CM4 → R10/R11/R12/C10/C11, realce/corte → R13–R18 y RV1–RV3, sumador → R19–R22, ROUT → R23, detectores de banda → D3–D8, C18–C23, R24–R32, recorte → D9–D12, C24, R33–R40, Q1. El mapa completo está en el script.

## Conexiones definidas en el esquemático

- **Alimentación:** ±15 V de fuente de laboratorio por J1 (1 masa, 2 +15 V) y J2 (1 masa, 2 −15 V), igual que P_POW y N_POW del TP4, o por los pads para cocodrilo TP12–TP14. 1N4007 en paralelo y 47 µF por riel.
- **Al TP4:** J4, KF2510 de 3 pines con el mismo orden que J108 (1 masa, 2 señal, 3 masa).
- **Entrada:** jack de 3,5 mm (J3) y pads para cocodrilo del generador (TP1 señal, TP2 masa).
- **Blue Pill:** alimentado por su USB. ADC en PA0 (graves), PA1 (medios) y PA2 (agudos). Recorte en PB12 (EXTI12, flanco ascendente) y pulsador de modo en PB5 (EXTI5): los dos salen por la fila de J5 para que en la placa no se crucen con el ADC. OLED por I2C1 (PB6 SCL, PB7 SDA) en J7, alimentado desde J5.1 (+3.3VA, el mismo 3,3 V que J6.18). UART1 (PA9 TX, PA10 RX) en J8 para un adaptador USB-TTL. Avisarle a TD2 de estos pines.
