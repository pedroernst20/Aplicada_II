# Guía de Puesta en Marcha para el Laboratorio (Placa Verificada OK)

Todas las conexiones pasivas, valores de resistencias/capacitores y alimentaciones de la placa fueron verificadas con multímetro y están **100% sanas**.

---

## Orden de Prueba en el Laboratorio (Lunes)

1. **Fuente simétrica (`±12 V`):**
   - Conectar **`GND`** arriba (`G` / `GND`), **`+12 V`** abajo a la izquierda (marca roja) y **`-12 V`** abajo al medio (cable amarillo).

2. **Generador de funciones (¡Clave para no saturar la cascada!):**
   - Poner la salida del canal en **`High-Z` (Alta Impedancia)** *(NO en `50 Ω`, porque en `50 Ω` entrega el doble de tensión sobre tus `15 kΩ` y te da los `4–5 Vpp` que viste antes)*.
   - Configurar onda **cuadrada**, **`f = 4300 Hz`**, nivel bajo **`0 V`** y nivel alto **`+2.5 V`** (`2.5 Vpp` con **Offset DC = `+1.25 V`**), tal como `V1` en [simulacion.asc](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP2/simulacion/simulacion.asc).
   - **Verificar primero con osciloscopio (acoplamiento `DC`)** en el primer pin negro de test (`Adaptacion_Zi`): tiene que verse cuadrada de **`0 V` a `+2.5 V`**.

3. **Chequeo etapa por etapa (siempre osciloscopio en acoplamiento `DC`):**
   - **Pin de test `Offset` (arriba de Pin 1 del 2° [TL082](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP2/pdf/Hoja%20de%20datos%20TL082.pdf)):** Cuadrada de **`-1.54 V` a `+0.96 V`** (`2.5 Vpp`, media `-0.29 V`).
   - **Salida `Pre_int` (Pin 7 del 2° TL082 / pata inferior del capacitor rojo `C1`):** Triangular de **`~1.45 Vpp`** montada sobre **`~+2.9 V` de continua** (va de `~+2.2 V` a `+3.6 V`).
     - *Nota:* Si con `Offset` yendo bien de `-1.54 V` a `+0.96 V`, en **Pin 7** del 2° TL082 seguís teniendo continua pura clavada, entonces **se quemó internamente la mitad derecha del 2° TL082** y hay que reemplazar ese integrado.
   - **Ajuste fino del preset `W503`:** Medir continua en la **pata izquierda de `R25`** (pegada arriba del preset) y retocar el tornillito hasta leer **`+2.06 V` DC** (o mirar directo la salida del OpAmp 3 y girar el preset hasta centrar la triangular).
   - **Pin de test `Señal 2` (arriba del Pin 7 del 3° TL082):** Triangular de **`-1.5 V` a `+4.0 V`** (`5.5 Vpp`).
   - **Salida `Pre_der`:**
     - En **Pin 1 del 3° TL082** (o pata izquierda de la resistencia de `62 kΩ`): cuadrada de **`~±3 V`**.
     - En el conector del **cable marrón** (divisor `200k / 100k` hacia la etapa siguiente): **`1/3` de `Pre_der` (`~±1 V`)**.
