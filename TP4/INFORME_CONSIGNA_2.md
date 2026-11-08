# Electrónica Aplicada II – UTN F.R.C.
## Trabajo Práctico N° 4: Respuesta en Frecuencia con Realimentación
### Resolución Completa y Fundamentada de la **Consigna 2**

---

**Curso:** 4R2  
**Grupo Asignado:** Grupo 6  
**Marco Teórico y Bibliográfico:** *Respuesta en frecuencia de amplificadores realimentados*, Cátedra de Electrónica Aplicada II, Prof. Titular Ing. Eduardo A. González (UTN F.R.C.).

---

## 1. Parámetros Asignados (Tabla 1 - Grupo 6)

A partir de la Tabla 1 de la consigna oficial, para el **Grupo 6** se definen los siguientes valores de partida:

| Parámetro | Símbolo | Valor | Valor Angular $\omega = 2\pi f$ |
| :--- | :---: | :---: | :---: |
| **Ganancia en Continua** | $K$ | $1100$ ($60.83\text{ dB}$) | - |
| **Primer Polo de la Planta** | $f_1$ | $18\text{ kHz}$ | $\omega_1 \approx 113.10\times 10^3\text{ rad/s}$ |
| **Segundo Polo de la Planta** | $f_2$ | $90\text{ kHz}$ | $\omega_2 \approx 565.49\times 10^3\text{ rad/s}$ |
| **Tercer Polo de la Planta** | $f_3$ | $180\text{ kHz}$ | $\omega_3 \approx 1.13\times 10^6\text{ rad/s}$ |
| **Frecuencia Compensador Retardo** | $f_d$ | $1.8\text{ kHz}$ | $\omega_d \approx 11.31\times 10^3\text{ rad/s}$ |
| **Polo Compensador Atraso-Adelanto** | $f_p$ | $350\text{ kHz}$ | $\omega_p \approx 2.20\times 10^6\text{ rad/s}$ |
| **Cero Compensador Atraso-Adelanto** | $f_z$ | $1.8\text{ MHz}$ | $\omega_z \approx 11.31\times 10^6\text{ rad/s}$ |

---

## 2. Desarrollo Punto por Punto

---

### Subpunto 2.1: Función de Transferencia de la Planta y Diagrama de Bode

La función de transferencia en el dominio de Laplace de la planta sin compensar es:

$$G(s) = \frac{K}{\left(1 + \frac{s}{2\pi f_1}\right)\left(1 + \frac{s}{2\pi f_2}\right)\left(1 + \frac{s}{2\pi f_3}\right)} = \frac{1100}{\left(1 + \frac{s}{2\pi \cdot 18\times 10^3}\right)\left(1 + \frac{s}{2\pi \cdot 90\times 10^3}\right)\left(1 + \frac{s}{2\pi \cdot 180\times 10^3}\right)}$$

Evaluando en régimen permanente sinusoidal ($s = j\omega = j2\pi f$):

- **Magnitud en escala logarítmica (dB):**
  $$|G(j2\pi f)|_{\text{dB}} = 20\log_{10}(1100) - 10\log_{10}\left(1 + \left(\frac{f}{18\text{k}}\right)^2\right) - 10\log_{10}\left(1 + \left(\frac{f}{90\text{k}}\right)^2\right) - 10\log_{10}\left(1 + \left(\frac{f}{180\text{k}}\right)^2\right)$$
  - Ganancia en continua ($f \to 0$): $|G(0)|_{\text{dB}} = 20\log_{10}(1100) \approx \mathbf{60.83\text{ dB}}$.
  - Pendientes asintóticas del trazado de Bode:
    - $f < 18\text{ kHz}$: pendiente de $0\text{ dB/década}$.
    - $18\text{ kHz} < f < 90\text{ kHz}$: pendiente de $-20\text{ dB/década}$.
    - $90\text{ kHz} < f < 180\text{ kHz}$: pendiente de $-40\text{ dB/década}$.
    - $f > 180\text{ kHz}$: pendiente de $-60\text{ dB/década}$.

- **Fase (grados sexagesimales):**
  $$\phi(f) = \angle G(j2\pi f) = -\arctan\left(\frac{f}{18\text{ kHz}}\right) - \arctan\left(\frac{f}{90\text{ kHz}}\right) - \arctan\left(\frac{f}{180\text{ kHz}}\right)$$
  - Para $f \to 0$: $\phi \to 0^\circ$.
  - Para $f \to \infty$: $\phi \to -270^\circ$.

> **Gráfico generado:** [bode_planta_original.png](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP4/graficos/bode_planta_original.png)

---

### Subpunto 2.2: Frecuencia de Corte Superior y Margen de Ganancia para $MF = 45^\circ$

El **Margen de Fase ($MF$)** en un amplificador con realimentación negativa y ganancia de lazo $T(s) = \beta G(s)$ se evalúa en la frecuencia de cruce de ganancia de lazo ($f_c$, donde $|T(j2\pi f_c)| = 1 = 0\text{ dB}$):
$$MF = 180^\circ + \phi(f_c)$$

Para cumplir la especificación requerida de **$MF = 45^\circ$**:
$$45^\circ = 180^\circ + \phi(f_c) \implies \phi(f_c) = -135^\circ$$

#### 1. Frecuencia de cruce de ganancia de lazo ($f_c$):
Resolviendo numéricamente la ecuación de fase:
$$-\arctan\left(\frac{f_c}{18\text{k}}\right) - \arctan\left(\frac{f_c}{90\text{k}}\right) - \arctan\left(\frac{f_c}{180\text{k}}\right) = -135^\circ \implies \mathbf{f_c = 70.34\text{ kHz}}$$

#### 2. Ganancia de lazo, Factor de Realimentación $\beta$ y Ganancia a Lazo Cerrado:
Evaluando la magnitud de la planta en $f_c = 70.34\text{ kHz}$:
$$|G(j2\pi f_c)|_{\text{dB}} = \mathbf{46.03\text{ dB}} \quad (|G(j2\pi f_c)| \approx 200.13)$$

Para que el cruce de ganancia de lazo ($|T| = 1$) ocurra exactamente en $f_c$, la red de realimentación $\beta$ debe cumplir:
$$|T(j2\pi f_c)| = \beta |G(j2\pi f_c)| = 1 \implies \beta = \frac{1}{|G(j2\pi f_c)|} = \frac{1}{200.13} \approx 0.004997 \quad (-46.03\text{ dB})$$

El producto de lazo en continua resulta $T_0 = \beta K = 0.004997 \cdot 1100 \approx 5.50$.  
Aplicando la relación exacta de Black para la ganancia a lazo cerrado en continua:
$$A_{f0} = \frac{K}{1 + \beta K} = \frac{1100}{1 + 5.50} \approx \mathbf{169.32} \quad (\mathbf{44.57\text{ dB}})$$

> [!NOTE] **Aclaración sobre la aproximación ideal $A_{f0} \approx 1/\beta$:**  
> En la literatura simplificada suele asumirse $A_{f0} \approx 1/\beta = 200.13$ ($46.03\text{ dB}$). Sin embargo, con un producto de lazo moderado como $\beta K = 5.50$, la condición de fuerte realimentación ($\beta K \gg 1$) no se cumple con holgura. Esto genera un error relativo del **$18.2\%$** ($1.46\text{ dB}$) respecto del valor real. Por rigor analítico, en este trabajo se utiliza el valor exacto de lazo cerrado.

#### 3. Distinción Rigurosa: Frecuencia de Cruce de Lazo ($f_c$) vs. Ancho de Banda Real a Lazo Cerrado ($BW_{\text{real}}$):
La consigna solicita la *"frecuencia de corte superior"*. En el marco teórico de la cátedra de Electrónica Aplicada II es fundamental no confundir la frecuencia de cruce de ganancia de lazo ($f_c$) con el ancho de banda a $-3\text{ dB}$ del amplificador realimentado ($BW_{\text{real}}$):

1. **Frecuencia de cruce de lazo ($f_c = 70.34\text{ kHz}$):** Es el cruce por $0\text{ dB}$ de la ganancia de lazo $T(j\omega)$, donde la fase de la planta vale $-135^\circ$.
2. **Ancho de banda real a lazo cerrado ($BW_{\text{real}} = 124.8\text{ kHz}$):**  
   Según el material de cátedra (*Respuesta en frecuencia de amplificadores realimentados*, diapositiva 4, Ing. Eduardo A. González), la función de transferencia a lazo cerrado normalizada responde a:
   $$\frac{|A_f|}{|A_{f0}|} = \frac{1}{\sqrt{\left[1 - \left(\frac{\omega}{\omega_0}\right)^2\right]^2 + 4K^2 \left(\frac{\omega}{\omega_0}\right)^2}}$$
   donde la cátedra utiliza el símbolo $K$ para designar al factor de amortiguamiento ($\zeta$). El apunte destaca textualmente:
   > *"Para K = 0,707 se da un cambio en la forma de la curva; para K < 0,707 hay sobre pico"*,  
   > con un valor máximo en $\omega_m = \omega_0 \sqrt{1 - 2K^2}$ y magnitud $\frac{|A_f|_{\text{máx}}}{A_{f0}} = \frac{1}{2K\sqrt{1 - K^2}}$.

   Para un margen de fase de $MF = 45^\circ$, el factor de amortiguamiento equivalente es $K \approx \zeta \approx 0.42 < 0.707$. Esto provoca un **sobrepico resonante (peaking)** pronunciado:
   $$M_p = \max_f \left(20\log_{10}\left|\frac{A_f(f)}{A_{f0}}\right|\right) = \mathbf{4.16\text{ dB}} \approx \mathbf{4.2\text{ dB}}$$
   Debido a este sobrepico, la curva de ganancia se eleva antes de caer, y el punto donde cruza la cota de $-3\text{ dB}$ (relativa a $A_{f0}$) se traslada significativamente hacia la derecha de $f_c$:
   $$\mathbf{BW_{\text{real,-3dB}} = 124.8\text{ kHz}} \quad (\approx 77\% \text{ superior a } f_c)$$

#### 4. Frecuencia de Cruce de Fase ($f_{180}$), Margen de Ganancia ($MG$) y Límite de Estabilidad:
La frecuencia donde la fase de la planta alcanza los $-180^\circ$ es:
$$\phi(f_{180}) = -\arctan\left(\frac{f_{180}}{18\text{k}}\right) - \arctan\left(\frac{f_{180}}{90\text{k}}\right) - \arctan\left(\frac{f_{180}}{180\text{k}}\right) = -180^\circ \implies \mathbf{f_{180} = 145.12\text{ kHz}}$$

Evaluando la magnitud en $f_{180}$:
$$|G(j2\pi f_{180})|_{\text{dB}} = \mathbf{34.89\text{ dB}}$$

El **Margen de Ganancia ($MG$)** para $MF = 45^\circ$ resulta:
$$MG = -|T(j2\pi f_{180})|_{\text{dB}} = |G(j2\pi f_c)|_{\text{dB}} - |G(j2\pi f_{180})|_{\text{dB}} = 46.03\text{ dB} - 34.89\text{ dB} = \mathbf{11.13\text{ dB}}$$

> **Criterio de estabilidad de la cátedra (diapositivas 8 y 9):**  
> Para que el sistema no oscile, la ganancia de lazo en la frecuencia de $-180^\circ$ debe ser estrictamente menor que 1:
> $$|\beta G(f_{180})| < 1 \implies \beta < \beta_{\text{máx}} = \frac{1}{|G(f_{180})|}$$
> Por lo tanto, la **ganancia mínima a lazo cerrado estable** que tolera esta planta sin volverse inestable es:
> $$A_{f,\text{mín}} \approx |G(j2\pi f_{180})|_{\text{dB}} = \mathbf{34.89\text{ dB}}$$

---

### Subpunto 2.3: Compensador de Retardo (Polo Dominante)

#### 1. Función de Transferencia del Compensador
Conforme al apunte de cátedra (diapositiva 12, *"1- Polo dominante o retardo"*), se agrega a la función de lazo abierto un polo dominante a una frecuencia $f_d \ll f_1$. Con $f_d = 1.8\text{ kHz}$:
$$G_{c,\text{ret}}(s) = \frac{1}{1 + \frac{s}{2\pi f_d}} = \frac{1}{1 + \frac{s}{2\pi \cdot 1800}}$$
En continua ($s = 0$), $G_{c,\text{ret}}(0) = 1 = 0\text{ dB}$, por lo que la ganancia de continua permanece en $|G_{\text{comp1}}(0)|_{\text{dB}} = 20\log_{10}(1100) = \mathbf{60.83\text{ dB}}$.

#### 2. Circuito Eléctrico, Efecto de Carga y Selección de Componentes
Tal como se describe en la diapositiva 12 del material de cátedra, este polo se implementa mediante una red RC pasiva pasa-bajos conectada a masa:

```
        R_d
Vi o---\/\/\/\----+----> Vo
                  |
                 --- C_d
                 ---
                  |
                 GND
```

La función de transferencia en vacío es:
$$\left.\frac{V_o(s)}{V_i(s)}\right|_{\text{vacío}} = \frac{1}{1 + s R_d C_d} \implies 2\pi f_d = \frac{1}{R_d C_d}$$

> [!WARNING] **Efecto de Carga e Intercalación de Buffers:**  
> En una aplicación práctica entre etapas amplificadoras, es imprescindible intercalar buffers seguidores de tensión (alta impedancia de entrada y baja impedancia de salida) para que las impedancias de los bloques anterior y posterior no alteren la frecuencia de corte $f_d = 1/(2\pi R_d C_d)$.

Adoptando un capacitor estándar comercial:
$$C_d = 10\text{ nF} = 10 \times 10^{-9}\text{ F}$$
Despejamos el valor teórico de la resistencia:
$$R_d = \frac{1}{2\pi f_d C_d} = \frac{1}{2\pi \cdot 1800\text{ Hz} \cdot 10\times 10^{-9}\text{ F}} \approx \mathbf{8841.94\,\Omega} \approx 8.84\text{ k}\Omega$$

**Selección de componentes comerciales normalizados:**
- **Opción recomendada E96 (Tolerancia 1%):** Valor estándar **$R_d = 8.87\text{ k}\Omega$**.  
  Brinda una frecuencia real de:
  $$f_{d,\text{real}} = \frac{1}{2\pi \cdot 8870\,\Omega \cdot 10\text{ nF}} = \mathbf{1.794\text{ kHz}} \quad (\text{error insignificante del } 0.32\%)$$
- **Opción E24 (Tolerancia 5%):** Valor estándar $R_d = 9.1\text{ k}\Omega$, que arroja $f_{d,\text{real}} = 1.749\text{ kHz}$ (error del $2.84\%$).

#### 3. Función de Transferencia Global Compensada
$$G_{\text{comp1}}(s) = G(s) \cdot G_{c,\text{ret}}(s) = \frac{1100}{\left(1 + \frac{s}{2\pi \cdot 1.8\text{k}}\right)\left(1 + \frac{s}{2\pi \cdot 18\text{k}}\right)\left(1 + \frac{s}{2\pi \cdot 90\text{k}}\right)\left(1 + \frac{s}{2\pi \cdot 180\text{k}}\right)}$$

#### 4. Obtención de Parámetros para $MF = 45^\circ$
Ecuación de fase total:
$$\phi_{\text{ret}}(f) = -\arctan\left(\frac{f}{1.8\text{k}}\right) -\arctan\left(\frac{f}{18\text{k}}\right) - \arctan\left(\frac{f}{90\text{k}}\right) - \arctan\left(\frac{f}{180\text{k}}\right)$$

- **Frecuencia de cruce de lazo ($MF = 45^\circ \implies \phi = -135^\circ$):**
  $$\mathbf{f_{c,\text{ret}} = 14.34\text{ kHz}}$$
- **Ganancia en $f_{c,\text{ret}}$ y factor de realimentación:**
  $$|G_{\text{comp1}}(j2\pi f_{c,\text{ret}})|_{\text{dB}} = \mathbf{40.46\text{ dB}} \implies \beta_{\text{ret}} = \frac{1}{105.47} \approx 0.009481 \quad (-40.46\text{ dB})$$
  $$T_0 = \beta K = 10.43 \implies A_{f0,\text{ret}} = \frac{1100}{1 + 10.43} \approx \mathbf{96.25} \quad (\mathbf{39.67\text{ dB}})$$
- **Respuesta a lazo cerrado:**
  - Sobrepico resonante: $M_{p,\text{ret}} = \mathbf{3.27\text{ dB}} \approx \mathbf{3.3\text{ dB}}$.
  - **Ancho de banda real a lazo cerrado ($-3\text{ dB}$):** $\mathbf{BW_{\text{real,ret}} = 25.57\text{ kHz}} \approx \mathbf{25.6\text{ kHz}}$.
- **Frecuencia de cruce de fase ($f_{180,\text{ret}}$), Margen de Ganancia y Límite de Estabilidad:**
  $$\phi_{\text{ret}}(f_{180,\text{ret}}) = -180^\circ \implies \mathbf{f_{180,\text{ret}} = 33.72\text{ kHz}}$$
  $$|G_{\text{comp1}}(j2\pi f_{180,\text{ret}})|_{\text{dB}} = \mathbf{28.10\text{ dB}}$$
  $$MG_{\text{ret}} = 40.46\text{ dB} - 28.10\text{ dB} = \mathbf{12.36\text{ dB}}$$
  - **Ganancia mínima a lazo cerrado estable:** $A_{f,\text{mín}} \approx \mathbf{28.10\text{ dB}}$.  
    Al reducirse $|G(f_{180})|$ de $34.89\text{ dB}$ a $28.10\text{ dB}$, el sistema tolera **$6.79\text{ dB} \approx 7\text{ dB}$ MÁS de realimentación** que la planta sin compensar.

> **Gráfico generado:** [bode_compensador_retardo.png](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP4/graficos/bode_compensador_retardo.png)

---

### Subpunto 2.4: Red Atraso-Adelanto (Lead-Lag)

#### 1. Función de Transferencia de la Red
Según el apunte de cátedra (diapositiva 17, *"2- Polo – cero o retardo avance"*), la red introduce un polo y un cero. Con los parámetros asignados $f_p = 350\text{ kHz}$ y $f_z = 1.8\text{ MHz}$ ($f_p < f_z$):
$$G_{c,aa}(s) = \frac{1 + \frac{s}{2\pi f_z}}{1 + \frac{s}{2\pi f_p}} = \frac{1 + \frac{s}{2\pi \cdot 1.8\times 10^6}}{1 + \frac{s}{2\pi \cdot 350\times 10^3}}$$
En continua ($s = 0$), $G_{c,aa}(0) = 1 = 0\text{ dB}$, manteniendo la ganancia estática $|G_{\text{comp2}}(0)|_{\text{dB}} = \mathbf{60.83\text{ dB}}$.

#### 2. Topología Circuital y Consideraciones de Impedancia
Se implementa mediante la red pasiva RC serie-shunt presentada en la diapositiva 17 de la cátedra:

```
        R_1
Vi o---\/\/\/\----+----> Vo
                  |
                 [R_2]
                  |
                 --- C
                 ---
                  |
                 GND
```

La función de transferencia en vacío es:
$$\left.\frac{V_o(s)}{V_i(s)}\right|_{\text{vacío}} = \frac{1 + s R_2 C}{1 + s (R_1 + R_2) C}$$

Comparando con la forma normalizada:
$$f_z = \frac{1}{2\pi R_2 C}, \qquad f_p = \frac{1}{2\pi (R_1 + R_2) C}$$
Como $f_p < f_z$, se cumple $R_1 + R_2 > R_2 \implies R_1 > 0$, demostrando la realizabilidad pasiva.

**Cálculo de componentes:**
Adoptando un capacitor cerámico de alta frecuencia $C = 1.0\text{ nF} = 10^{-9}\text{ F}$:
$$R_2 = \frac{1}{2\pi f_z C} = \frac{1}{2\pi \cdot 1.8\times 10^6 \cdot 10^{-9}} \approx \mathbf{88.42\,\Omega}$$
$$R_1 + R_2 = \frac{1}{2\pi f_p C} = \frac{1}{2\pi \cdot 350\times 10^3 \cdot 10^{-9}} \approx 454.73\,\Omega \implies R_1 = 454.73\,\Omega - 88.42\,\Omega \approx \mathbf{366.31\,\Omega}$$

**Valores comerciales E24:**
- $R_2 = \mathbf{91\,\Omega}$
- $R_1 = \mathbf{360\,\Omega}$
- Con estos componentes: $f_{z,\text{real}} = 1.749\text{ MHz}$ y $f_{p,\text{real}} = 352.89\text{ kHz}$ (error $< 1\%$).

> [!CAUTION] **Fuerte efecto de carga en la etapa previa:**  
> La impedancia de entrada de esta red es extremadamente baja:
> $$Z_{\text{in}}(0) = R_1 + R_2 \approx 451\,\Omega, \qquad Z_{\text{in}}(\infty) = R_1 = 360\,\Omega$$
> Una impedancia de entrada de apenas $360\text{ a }451\,\Omega$ sobrecarga severamente a cualquier etapa amplificadora de tensión previa. Por lo tanto, en un montaje práctico es **estrictamente imprescindible añadir un buffer seguidor de tensión** para excitar la red.

#### 3. Análisis Físico y Confrontación con el Apunte de Cátedra
> [!IMPORTANT] **Análisis Crítico según la Teoría de la Cátedra:**  
> - **Regla de diseño áureo de la cátedra (Diapositiva 17):** El apunte de cátedra establece textualmente:  
>   > *"La frecuencia del cero se elige de modo que anule el polo de baja frecuencia de la función sin compensar o sea que $f_z = f_1$"*.  
>   En el desarrollo teórico ideal, el cero $f_z$ cancela algebraicamente el primer polo de la planta ($18\text{ kHz}$), permitiendo que el polo del compensador controle la pendiente mientras se retrasa el aporte de fase negativa.  
> - **Inaplicabilidad en el Grupo 6:** Con los valores asignados en la Tabla 1 del TP ($f_p = 350\text{ kHz}$ y $f_z = 1.8\text{ MHz}$), el cero está en $1.8\text{ MHz}$, mientras que los polos de la planta están en $18\text{ kHz}, 90\text{ kHz}$ y $180\text{ kHz}$. El cero se encuentra un orden de magnitud por encima de todos los polos de la planta: **no cancela absolutamente ningún polo**.  
> - **Aporte de fase real en $f_c = 61.59\text{ kHz}$:**  
>   $$\phi_z(f_c) = +\arctan\left(\frac{61.59\text{ kHz}}{1.8\text{ MHz}}\right) = \mathbf{+1.96^\circ} \approx \mathbf{+2^\circ}$$  
>   $$\phi_p(f_c) = -\arctan\left(\frac{61.59\text{ kHz}}{350\text{ kHz}}\right) = \mathbf{-9.98^\circ} \approx \mathbf{-10^\circ}$$  
>   $$\phi_{\text{neto}}(f_c) = +1.96^\circ - 9.98^\circ = \mathbf{-8.02^\circ} \approx \mathbf{-8^\circ}$$  
>   **Conclusión:** En la frecuencia de cruce, la red **atrasa la fase en $8^\circ$**. No existe ninguna recuperación virtuosa de fase por parte del cero.  
> - **¿Por qué conserva el $87.6\%$ del ancho de banda aparente ($61.59\text{ kHz}$ vs $70.34\text{ kHz}$)?**  
>   No lo hace por una acción compensatoria virtuosa, sino porque ambas singularidades ($350\text{ kHz}$ y $1.8\text{ MHz}$) se encuentran a frecuencias tan elevadas respecto de $f_c \approx 60-70\text{ kHz}$ que la red tiene un efecto casi inapreciable en la zona de cruce: apenas atenúa $1.48\text{ dB}$ y atrasa $8^\circ$. Lejos de optimizar la respuesta, ese atraso de $-8^\circ$ fuerza a cruzar antes y degrada el margen de ganancia.

#### 4. Obtención de Parámetros para $MF = 45^\circ$
Ecuación de fase total:
$$\phi_{aa}(f) = \arctan\left(\frac{f}{1.8\text{M}}\right) - \arctan\left(\frac{f}{18\text{k}}\right) - \arctan\left(\frac{f}{90\text{k}}\right) - \arctan\left(\frac{f}{180\text{k}}\right) - \arctan\left(\frac{f}{350\text{k}}\right)$$

- **Frecuencia de cruce de lazo ($MF = 45^\circ \implies \phi = -135^\circ$):**
  $$\mathbf{f_{c,aa} = 61.59\text{ kHz}}$$
- **Ganancia en $f_{c,aa}$ y factor de realimentación:**
  $$|G_{\text{comp2}}(j2\pi f_{c,aa})|_{\text{dB}} = \mathbf{47.51\text{ dB}} \implies \beta_{aa} \approx 0.004211 \quad (-47.51\text{ dB})$$
  $$T_0 = \beta K = 4.63 \implies A_{f0,aa} = \frac{1100}{1 + 4.63} \approx \mathbf{195.29} \quad (\mathbf{45.81\text{ dB}})$$
- **Respuesta a lazo cerrado:**
  - Sobrepico resonante: $M_{p,aa} = \mathbf{4.73\text{ dB}} \approx \mathbf{4.7\text{ dB}}$.
  - **Ancho de banda real a lazo cerrado ($-3\text{ dB}$):** $\mathbf{BW_{\text{real,aa}} = 112.78\text{ kHz}} \approx \mathbf{112.8\text{ kHz}}$.
- **Frecuencia $f_{180,aa}$, Margen de Ganancia y Estabilidad:**
  $$\phi_{aa}(f_{180,aa}) = -180^\circ \implies \mathbf{f_{180,aa} = 114.75\text{ kHz}}$$
  $$|G_{\text{comp2}}(j2\pi f_{180,aa})|_{\text{dB}} = \mathbf{38.53\text{ dB}}$$
  $$MG_{aa} = 47.51\text{ dB} - 38.53\text{ dB} = \mathbf{8.98\text{ dB}}$$
  - **Ganancia mínima a lazo cerrado estable:** $A_{f,\text{mín}} \approx \mathbf{38.53\text{ dB}}$.  
    Este compensador **admite $3.64\text{ dB}$ MENOS de realimentación** que la planta sin compensar antes de entrar en oscilación.

> **Gráfico generado:** [bode_compensador_atraso_adelanto.png](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP4/graficos/bode_compensador_atraso_adelanto.png)

---

### Subpunto 2.5: Cuadro Comparativo y Explicación Fundamentada de las Diferencias

A continuación se resume de forma exhaustiva la respuesta en frecuencia y estabilidad de los tres sistemas analizados:

| Parámetro | Planta Original $G(s)$ | Compensador de Retardo | Red Atraso-Adelanto |
| :--- | :---: | :---: | :---: |
| **Ganancia en Continua $G(0)$** | $60.83\text{ dB}$ | $60.83\text{ dB}$ | $60.83\text{ dB}$ |
| **Frecuencia de Cruce de Lazo ($f_c$ para $MF = 45^\circ$)** | **$70.34\text{ kHz}$** | **$14.34\text{ kHz}$** | **$61.59\text{ kHz}$** |
| **Relación de $f_c$ respecto a la Planta Original** | $100\%$ | **$20.4\%$** | **$87.6\%$** |
| **Sobrepico Resonante a Lazo Cerrado ($M_p$)** | $4.16\text{ dB}$ ($4.2\text{ dB}$) | $3.27\text{ dB}$ ($3.3\text{ dB}$) | $4.73\text{ dB}$ ($4.7\text{ dB}$) |
| **Ancho de Banda Real Lazo Cerrado ($-3\text{ dB}$)** | **$124.73\text{ kHz}$ ($124.8\text{k}$)** | **$25.57\text{ kHz}$ ($25.6\text{k}$)** | **$112.78\text{ kHz}$ ($112.8\text{k}$)** |
| **Ganancia de Lazo en Cruce $|G(f_c)|$** | $46.03\text{ dB}$ | $40.46\text{ dB}$ | $47.51\text{ dB}$ |
| **Factor de Realimentación $\beta$** | $0.00500$ ($-46.03\text{ dB}$) | $0.00948$ ($-40.46\text{ dB}$) | $0.00421$ ($-47.51\text{ dB}$) |
| **Ganancia DC a Lazo Cerrado Exacta ($A_{f0}$)** | $169.32$ ($44.57\text{ dB}$) | $96.25$ ($39.67\text{ dB}$) | $195.29$ ($45.81\text{ dB}$) |
| **Frecuencia de Fase $-180^\circ$ ($f_{-180}$)** | $145.12\text{ kHz}$ | $33.72\text{ kHz}$ | $114.75\text{ kHz}$ |
| **Ganancia $|G(f_{-180})|$** | $34.89\text{ dB}$ | $28.10\text{ dB}$ | $38.53\text{ dB}$ |
| **Margen de Ganancia ($MG$)** | **$11.13\text{ dB}$** | **$12.36\text{ dB}$** | **$8.98\text{ dB}$** |
| **Ganancia Mínima Estable a Lazo Cerrado ($A_{f,\text{mín}}$)** | **$34.89\text{ dB}$** (ref) | **$28.10\text{ dB}$** | **$38.53\text{ dB}$** |
| **Capacidad de Realimentación Admisible ($\Delta\beta_{\text{máx}}$)** | $0\text{ dB}$ (base) | **$+6.79\text{ dB}$ (admite $\approx 7\text{ dB}$ más)** | **$-3.64\text{ dB}$ (admite menos)** |
| **Impedancia de entrada de la red pasiva** | - | Media ($8.87\text{ k}\Omega$) | Muy baja ($360\text{ a }451\,\Omega$) |

> **Gráficos comparativos generados:**  
> - Comparativa de Bodes de lazo abierto: [bode_comparativa_compensadores.png](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP4/graficos/bode_comparativa_compensadores.png)  
> - Comparativa de respuesta a lazo cerrado y anchos de banda reales: [respuesta_lazo_cerrado_comparativa.png](file:///home/pedro/Facultad/Cuarto/Aplicada/TP's/TP4/graficos/respuesta_lazo_cerrado_comparativa.png)

---

### Análisis Teórico y Discusión Crítica de los Resultados

#### 1. ¿Por qué "BW = fc" es conceptualmente erróneo en sistemas con $MF = 45^\circ$?
Igualar el ancho de banda a lazo cerrado con la frecuencia de cruce de lazo ($f_c$) solo es válido en aproximaciones unipolares o sistemas fuertemente amortiguados ($\zeta \ge 0.707$, equivalente a $MF \ge 65^\circ$).  
Al exigir la consigna $MF = 45^\circ$, el lazo cerrado presenta amortiguamiento reducido ($K \approx 0.42$), lo cual produce resonancia:
- Sobrepicos de entre $3.3\text{ dB}$ y $4.7\text{ dB}$.
- La frecuencia donde la ganancia cae $-3\text{ dB}$ respecto a continua ($A_{f0}$) se extiende aproximadamente un **$77\%$ a $83\%$ más arriba que $f_c$** ($124.8\text{ kHz}$ vs $70.3\text{ kHz}$ en la planta original).

#### 2. Crítica al Desempeño de la Red Atraso-Adelanto:
- **Margen de Ganancia:** El valor obtenido ($MG = 8.98\text{ dB}$) **no es óptimo**: empeoró respecto de la planta original ($11.13\text{ dB}$) y queda por debajo de la regla empírica clásica de diseño analógico ($MG \ge 10\text{ dB}$ a $12\text{ dB}$).
- **Ancho de banda:** Con la condición obligatoria de fijar $MF = 45^\circ$, la red atraso-adelanto **no supera en ancho de banda a la planta original** ($61.59\text{ kHz}$ vs $70.34\text{ kHz}$).
- **Motivo físico real:** La red conserva el $87.6\%$ del ancho de banda simplemente porque sus polos y ceros están colocados demasiado altos ($350\text{ kHz}$ y $1.8\text{ MHz}$) en relación a los polos de la planta ($18\text{k}, 90\text{k}, 180\text{ kHz}$), actuando como un elemento casi transparente que apenas modifica la respuesta en la zona de cruce e introduce un atraso parásito de $-8^\circ$.

#### 3. El Verdadero Propósito del Compensador de Retardo (Polo Dominante):
El compensador por polo dominante reduce drásticamente el ancho de banda ($f_c$ cae a $14.34\text{ kHz}$), pero cumple el propósito esencial de la compensación por retardo según la teoría de la cátedra:
- Al atenuar fuertemente a altas frecuencias, la ganancia en la frecuencia de $-180^\circ$ se reduce de $34.89\text{ dB}$ a $28.10\text{ dB}$.
- Esto permite al diseñador **aumentar el factor de realimentación $\beta$ en casi $7\text{ dB}$** (pudiendo fijar ganancias a lazo cerrado tan bajas como $28.1\text{ dB}$) sin peligro de oscilación.
- Mayor realimentación se traduce en mayor linealidad, menor distorsión y mayor desensibilización paramétrica. El sacrificio de ancho de banda es el costo directo a pagar por dicha estabilidad.

#### 4. Punto Clave para Coloquio y Defensa Oral: ¿Alcanza alguno de estos compensadores para un Seguidor de Tensión ($\beta = 1$)?
Una pregunta clásica de examen es si este amplificador podría configurarse como un seguidor de ganancia unitaria (buffer con $\beta = 1 = 0\text{ dB}$).
- **Respuesta:** **Ninguno de los dos compensadores lo permite**.
- **Fundamentación:** Para que el lazo sea estable con $\beta = 1$, la ganancia de la planta debe caer por debajo de $0\text{ dB}$ antes de que la fase cruce los $-180^\circ$ (es decir, $|G(f_{-180})| < 0\text{ dB}$).
- Con el compensador de retardo asignado, la ganancia en $-180^\circ$ sigue siendo muy alta: $|G_{\text{comp1}}(f_{180})| = \mathbf{+28.10\text{ dB}}$. Si se conectara con $\beta = 1$, la ganancia de lazo sería $+28.1\text{ dB} \gg 0\text{ dB}$ con una fase de $-180^\circ$, provocando una oscilación violenta.
- **Conclusión:** Con $f_d = 1.8\text{ kHz}$, el polo asignado **no es lo suficientemente dominante**. Para compensar el amplificador hasta ganancia unitaria ($\beta = 1$) manteniendo $MF \ge 45^\circ$, se requeriría situar el polo dominante a una frecuencia mucho más baja, del orden de **$30\text{ a }50\text{ Hz}$** (típico de compensaciones internas tipo Miller en amplificadores operacionales comerciales).

---
