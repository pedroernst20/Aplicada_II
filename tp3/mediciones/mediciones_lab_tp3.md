# Mediciones de laboratorio — TP3 Amplificador de ECG

**Fecha:** 2026-10-23
**Equipos:** osciloscopio Rigol DS1052E · generador UNI-T UTG1042X (primero se probó un GW Instek GFG-3015) · fuente partida ±15 V
**Alimentación:** ±15 V (no ±12 V como en el diseño)

## Correcciones hechas a la placa
- Pad desoldado en el nodo pin 1 (U1A) – R4 – R7 → la realimentación de U1A estaba abierta (pin 1 saturado de riel a riel, pin 7 en seguidor). Se resoldó.
- R11 era de 47 kΩ en lugar de 4,7 kΩ → la etapa 3 tenía ganancia ≈2. Se cambió por una de 4,7 kΩ.

## 1. Ganancia diferencial (25 Hz)
| Magnitud | Valor |
|---|---|
| Vin medida (CH1, Average) | 11,2 mVpp |
| Pin 1 | 484 mVpp |
| Pin 7 | 492 mVpp |
| Vin calculada = (pin 1 + pin 7) / 100,8 | 9,68 mVpp |
| Vout | 10,8 Vpp |
| A_md (con la Vin calculada) | ≈1116 → 61,0 dB |
| A_md (con la Vin medida, 11,2 mVpp) | ≈964 → 59,7 dB |

Nota: la Vin medida y la calculada difieren un 14 %. Tomar el promedio, A_md ≈ 1040 (≈60,3 dB), o aclararlo en el informe.

## 2. Respuesta en frecuencia
La amplitud del generador quedó fija durante todo el barrido. La Vin leída en CH1 varía por ruido y por el filtro digital del DSO, así que para G se toma **Vin constante = 10,4 mVpp** (la medida a 25 Hz). La columna "dB rel." está normalizada a Vout máx = 11,4 Vpp (1 Hz) y no depende de Vin.

| f (Hz) | Vin leída (mVpp) | Vout (Vpp) | G (V/V) | G (dB) | dB rel. | Teórico rel. | Filtro DSO |
|---|---|---|---|---|---|---|---|
| 1 | 33,4 (ruido) | 11,4 | 1096 | 60,8 | 0,00 | 0,00 | no |
| 5 | 16 | 11,2 | 1077 | 60,6 | −0,15 | −0,01 | sí |
| 10 | 11,2 | 11,1 | 1067 | 60,6 | −0,23 | −0,04 | sí |
| 25 | 10,4 | 10,9 | 1048 | 60,4 | −0,39 | −0,24 | sí |
| 50 | 9,6 | 10,0 | 962 | 59,7 | −1,14 | −0,87 | sí |
| 75 | 10,4 | 9,04 | 869 | 58,8 | −2,01 | −1,76 | sí |
| 98,81 (100) | 15,2 (ruido, CH1 a 20 mV/div) | 8,72 | 838 | 58,5 | −2,33 | −2,70 | no (Average) — captura `capturas/barrido_100hz.png` |
| 125 | – | 7,76 | 746 | 57,5 | −3,34 | −3,78 | no (Average) |
| 150 | – | 7,04 | 677 | 56,6 | −4,19 | −4,77 | no (Average) |
| 200 | – | 5,84 | 562 | 55,0 | −5,81 | −6,58 | no (Average) |
| 300 | – | 4,24 | 408 | 52,2 | −8,59 | −9,55 | no (Average) |
| 500 | – | 2,64 | 254 | 48,1 | −12,7 | −13,7 | no (Average) |
| 1000 | 15,2 (ruido, CH1 a 20 mV/div) | 1,44 | 138 | 42,8 | −18,0 | −19,5 | no — captura `capturas/barrido_1khz.png` |
| 2000 | 10,4 | 0,660 | 63,5 | 36,1 | −24,8 | −25,5 | no |

**Descartados** (medidos con el filtro digital del DSO activado, que atenuaba la señal): 100 Hz 7,76 Vpp · 125 Hz 6,72 · 200 Hz 3,92 · 300 Hz 1,46 · 500 Hz 1,30. Los puntos de 5–75 Hz también se midieron con el filtro, pero a esas frecuencias el efecto parece despreciable.

- Pendiente entre 1 kHz y 2 kHz: −6,8 dB/octava (≈ −20 dB/déc, la de un polo) ✔
- **fH ≈ 116 Hz** (−3 dB respecto del máximo, interpolando en escala log entre 100 y 125 Hz). Diseño: 106 Hz → +9 %, dentro de la tolerancia típica de los capacitores de 15 nF.
- En toda la zona de alta frecuencia la curva medida queda ≈0,5–1 dB por encima de la teórica, coherente con un fH real algo mayor que el de diseño.
- **fL: no se midió.** La respuesta al escalón a 0,02 Hz resultó impracticable con el equipo disponible. Valor por cálculo: fL = 1/(2π·100 kΩ·33 µF) = **0,048 Hz**. Lo único que muestra el barrido es que la curva ya está plana a 1 Hz, o sea fL < ~0,2 Hz con la precisión de la medición (±0,2 dB).

## 3. RRMC
Entradas unidas (jumper 1–2), generador directo. Para calcular se toma A_md ≈ 1040 (60,3 dB), el promedio de la calibración; el rango posible es 964–1116.

| Condición | f (Hz) | Vin_mc (mVpp) | Pin 1 / Pin 7 (mVpp) | Vout_mc (mVpp) | A_mc | RRMC (dB) |
|---|---|---|---|---|---|---|
| Antes de ajustar RV1 | 50,00 | 520 | 512 / 516 | 56,0 | 0,108 | **79,7** (rango 79,0–80,3) |
| Después de ajustar RV1 | 50,00 | 520 | 512 / 516 | 59,2 | 0,114 | **79,2** (rango 78,5–79,8) |

- Ajustar RV1 no mejoró el RRMC: la diferencia entre 56,0 y 59,2 mVpp entra en la incertidumbre de la medición, porque el residuo es ruidoso. Coincide con un residuo dominado por el desbalance reactivo (ver abajo).

### Repetición del RRMC (2026-11-02)
- Piso de ruido (generador conectado con la salida apagada, jumper 1–2), captura `capturas/rrmc_piso_ruido.png`: CH1 = 34,0 mVpp (zumbido de ≈50 Hz captado por la entrada, que queda flotando con la salida del generador apagada). CH2 (`out`, a 50 mV/div, sin Average) = 32,0 mVpp, pero la traza es plana: ese Vpp viene de un pico aislado (glitch). El zumbido real a la salida es de pocos mV (≈34 mV × A_mc ≈ 4 mV). **El residuo de ~56 mVpp de la medición anterior no estaba dominado por el ruido.**

| Condición | f (Hz) | Vin_mc (mVpp) | Vout_mc (mVpp) | A_mc | RRMC (dB) | Captura |
|---|---|---|---|---|---|---|
| b) RV1 como quedó el 23/10, sin retocar hoy; CH2 a 10 mV/div con Average | 50,00 | 520 | 11,6 | 0,0223 | **93,4** (rango 92,7–94,0) | `capturas/rrmc_50hz_b_antes_rv1.png` |
| c) Después de ajustar RV1 al mínimo | 50,00 | 512 | 6,80 | 0,0133 | **97,9** (rango 97,2–98,5) | `capturas/rrmc_50hz_c_despues_rv1.png` |

**RRMC en función de la frecuencia** (RV1 fijo en el mínimo). Para cada frecuencia se usa la A_md del barrido (Vin = 10,4 mVpp):

| f (Hz) | A_md(f) | Vin_mc (mVpp) | Vout_mc (mVpp) | A_mc | RRMC (dB) | Captura |
|---|---|---|---|---|---|---|
| 10,00 | 1067 | 480 | 4,20 | 0,00875 | **≥ 101,7** (limitado por el piso de ruido) | `capturas/rrmc_10hz.png` |
| 46,95 | ≈970 | 512 | 6,40 | 0,0125 | **97,8** | `capturas/rrmc_47hz.png` |
| 50,00 | 962 | 512 | 6,80 | 0,0133 | **97,2** | `capturas/rrmc_50hz_c_despues_rv1.png` |
| 53 | – | – | – | – | (no se guardó) | – |
| 100,0 | 838 | 528 | 11,2 | 0,0212 | **91,9** | `capturas/rrmc_100hz.png` |

- **A 10 Hz** el residuo no es una senoidal de 10 Hz: son picos periódicos de ruido o zumbido. La componente de modo común real está por debajo del piso de ruido, así que el valor es una cota inferior.
- **Entre 47 y 50 Hz** el resultado es prácticamente igual (97,8 contra 97,2 dB): el zumbido de red no contamina la medición a 50 Hz.
- **El RRMC cae con la frecuencia:** ≈−5,3 dB entre 50 y 100 Hz, cerca de los −6 dB/octava. Es lo que se espera de un desbalance **reactivo** (C7 contra C8, 15 nF) que crece con f y que RV1, al ser resistivo, no puede compensar. Confirma la hipótesis.

- Con CH2 a 10 mV/div y Average el residuo da **11,6 mVpp**, unas 5 veces menos que los 56–59 mVpp del 23/10. Aquellas mediciones estaban infladas por la mala resolución (50 y 20 mV/div) y por el ruido sin promediar. El residuo no es una senoidal pura: tiene armónicos.

- La etapa 1 deja pasar el modo común con ganancia ≈1 (512 y 516 mVpp contra 520 mVpp de entrada) ✔
- Resultado: RRMC ≈ 79–80 dB, justo en el límite de la especificación (>80 dB).
- En la captura 3, el residuo de salida está ≈90° desfasado de la entrada. Eso indica que el desbalance que queda es **reactivo**: diferencia entre C7 y C8 (15 nF, tolerancia típica ±10 %). A 50 Hz su reactancia (≈212 kΩ) es comparable a R10/R8+R9+RV1 (≈100 kΩ). RV1 solo compensa la parte resistiva (en fase), por eso el ajuste no baja más el residuo. Mejora posible: aparear C7/C8 o agregar un trimmer capacitivo.

## 4. Simulador de ECG
| QRS (Vpp) | Período (s) | Observaciones |
|---|---|---|
| 1,08 (Vpp de la señal completa) | ≈1,01 s (≈5 div a 200 ms/div) → ≈60 bpm | P-QRS-T limpio, QRS hacia arriba con una onda S chica negativa, P y T bien definidas, sin zumbido de 50 Hz visible. CH2 a 200 mV/div, 200 ms/div, trigger en CH2 a 480 mV. |

- Simulador en QRS Normal, adulto, 60 bpm, 1 mVpp → salida de 1,08 Vpp, o sea una ganancia efectiva ≈1080 (≈60,7 dB), coherente con la calibración (≈1040–1116).
- En el primer intento se veían pulsos rectangulares sueltos y no enganchaba el trigger (CH2 a 2 V/div y el nivel de trigger en 0 V). Después de corregir la configuración y las conexiones apareció el ECG.
- `capturas/ecg2.png`: CH2 a 500 mV/div, 100 ms/div, **Vpp = 2,02 V**. Intervalo R-R ≈3,7 div ≈ 0,37 s → **≈160 bpm**. Morfología P-QRS-T limpia, R hacia arriba y S negativa. Simulador en **2 mVpp** (confirmado) → ganancia ≈ 2,02 V / 2 mV = **1010 (60,1 dB)**, coherente con la calibración. El simulador no estaba en 60 bpm. El ritmo se obtiene de la medición: R-R ≈ 0,37 s → **≈160 bpm**.
- Capturas: `capturas/ecg.png` (bitmap del Rigol, Vpp = 1,07 V, 200 ms/div; tiene algún artefacto de muestreo en los QRS porque a 200 ms/div la frecuencia de muestreo es baja) y `capturas/ecg_foto_pantalla.jpg` (foto con el celular, Vpp = 1,08 V, se ve más limpia).

## 5. Datos generales
- **Fuente:** panel fijo del laboratorio (UTN-FRC, 1995), salidas ±15 V / 1 A, sin indicación de corriente. **Corriente: no medida.**
- **Generador:** UNI-T UTG1042X, conectado **directo, sin divisor resistivo**, con la amplitud fijada en el propio generador (≈10 mVpp en modo diferencial, ≈520 mVpp en modo común). Carga configurada en HighZ. Al principio se probó un GW Instek GFG-3015, que se descartó porque en su escala mínima no es preciso.
- **Continua en reposo: DESCARTADA.** No se sabe con certeza contra qué punto se midió, así que no se incluye en el informe. Si hace falta, se mide otro día.
- **RV1 y RV2: no medidos** (habría que desoldarlos para medirlos fuera del circuito).

## Fotos sacadas
- `capturas/barrido_100hz.png`: f = 98,81 Hz, CH1 (entrada) a 20 mV/div, Vpp(1) = 15,2 mV (mayormente ruido: la señal ocupa ~½ división), CH2 (`out`) a 2 V/div, Vpp(2) = 8,72 V, base de tiempo 2 ms/div.
- `capturas/barrido_1khz.png`: f = 1,000 kHz, CH1 a 20 mV/div, Vpp(1) = 15,2 mV (ruido), CH2 a 1 V/div, Vpp(2) = 1,44 V, base de tiempo 500 µs/div. Confirma el punto de 1 kHz del barrido.
- `capturas/rrmc_50hz_antes_rv1.png`: modo común, ANTES de ajustar RV1, a 50 Hz, Vin = 520 mVpp (CH1 a 200 mV/div), Vout = 56,0 mVpp (CH2 a 50 mV/div), 10 ms/div.
- `capturas/rrmc_50hz_despues_rv1.png`: modo común, DESPUÉS de ajustar RV1, a 50 Hz, Vin = 520 mVpp, Vout = 59,2 mVpp (CH2 a 20 mV/div), 10 ms/div. Residuo ≈90° desfasado.

## Pendiente para el miércoles
- [ ] fL: respuesta al escalón (cuadrada de 0,02 Hz, modo Roll, medir τ ≈ 3,3 s) o puntos a 0,5 / 0,2 / 0,1 Hz
- [ ] RRMC a 10 Hz y a 100 Hz sin tocar RV1 (para confirmar que el límite es C7/C8)
- [ ] Simulador de ECG (QRS normal, adulto, 60 bpm, 1 mVpp) + captura
- [ ] Vin de calibración con la punta de CH1 en ×1 a 2 mV/div (para cerrar la diferencia entre 9,7 y 11,2 mVpp)
- [ ] Corriente de la fuente, continua en reposo (pines 1/7/8/14), valores finales de RV1 y RV2
- [ ] Modelos de la fuente y del tester
