# Presentación del TP6 · instrucciones de armado

Este documento es el encargo completo para armar la presentación oral del TP6.
Todo lo que hace falta saber está acá o en los archivos que se citan.

## Decisiones que Pedro puede cambiar antes de empezar

Son valores por defecto; si Pedro los editó, vale lo que dice acá.

- **Orden y reparto de expositores**: el mismo de la presentación anterior.
  Bloque 1 Alejo López Demichelis · Bloque 2 Tomás Polizze · Bloque 3 Pedro
  Ernst · Bloque 4 Valentino Rao.
- **Largo**: similar a la anterior (tenía 24 diapositivas, el cierre y 3 de
  respaldo). Apuntar a 22–26 antes del cierre y 3–4 de respaldo. No se conoce
  el tiempo asignado; si hay que recortar, lo primero que pasa a respaldo es el
  detalle de modelos y validación.
- **Guion oral**: sí, un `guion.md` aparte (ver "Entregables").

## Qué hay que hacer y para qué

Somos el Grupo 6 de Electrónica Aplicada II (UTN FRC, curso 4R2, año 2026).
Ya entregamos el informe escrito de la Actividad Evaluativa de la Unidad 6
(fuentes de alimentación), Consigna 6. Ahora tenemos que **exponerlo en clase**
ante los docentes (Carlos Enrique Olmos y Pablo Gabriel Miklosa) y el resto
del curso, hablando los cuatro integrantes.

Hay que armar las diapositivas de esa exposición. El público conoce la teoría
de la unidad pero no leyó nuestro informe: tiene que poder seguir qué se
pidió, qué decidimos, por qué, y qué dio la simulación, mirando la pantalla
desde el fondo del aula mientras alguien habla. Los docentes evalúan y van a
preguntar; por eso los números tienen que ser exactamente los del informe y
las limitaciones del trabajo tienen que estar dichas, no escondidas.

La presentación tiene que quedar **visualmente igual de estilo** que la que
hicimos para el TP anterior, que es la versión ya corregida y la que tomamos
como estándar: `../../presentacion corregida.pdf` (28 páginas, mirarla entera
antes de empezar).

## Con qué se arma

Usar la skill **`presentaciones`** (`~/.claude/skills/presentaciones/`). Trae
la plantilla HTML con ese mismo sistema de diseño, las tipografías, KaTeX, el
estilo de matplotlib, el conversor de circuitikz a SVG y `exportar.py`, que
genera el PDF, las capturas de revisión y un control automático de desbordes.
Seguir su flujo de trabajo y sus criterios de contenido. La plantilla se copia
dentro de esta carpeta (`TP6/presentacion/`), al lado de este archivo.

También están disponibles las skills `electronica` y `ltspice` y el plugin
`frontend-design`, por si sirven.

## De dónde sale el contenido

La fuente de verdad es el informe. Leerlo completo antes de escribir el guion.

| Qué | Dónde |
|---|---|
| Enunciado (somos la **Consigna 6**) | `../Consignas Evaluación.pdf` |
| Informe compilado, 8 páginas | `../EA_TP6.pdf` |
| Informe en LaTeX (texto, tablas, ecuaciones, figuras en TikZ/circuitikz/pgfplots) | `../informe/EA_TP6.tex` y `../informe/capitulos/1…5_*.tex` |
| Todos los números simulados, con nombre | `../informe/datos/resultados.json` (los mismos que `resultados.tex`, sin el prefijo `sim`) |
| Curvas simuladas | `../informe/datos/*.dat` |
| Esquemáticos y script de LTspice | `../simulacion/` |
| Hojas de datos | `../hojas_de_datos/` (µA7805, TIP120/122, TIP31, 1N47xx) |
| Apuntes de la cátedra | `../Contexto Teorico/` |

`../Fuente_Lineal_10A/` es un proyecto de Proteus de 2021 que vino con el
material de la cátedra; no es nuestro y no va en la presentación.
`../Informe_Consigna6/` está vacía.

Columnas y unidades de los `.dat` (son las que usa el informe en sus figuras):

- `linea.dat`: `vp` [V], `vb` (base de Q1), `vireg`, `vo`, `vosin` [V]. Barrido de la primaria de 0 a 30 V con IL = 0,5 A.
- `linea_detalle.dat`: `vp` [V], `dvocon`, `dvosin` [mV] (cambio de VO respecto del valor con VP = 25 V).
- `carga.dat`: `il` [A], `vo`, `vireg` [V], `pq`, `preg` [W].
- `rizado.dat`: `t` [ms]; componente alterna de `vp` [V], `vireg` [mV], `vo` y `vosin` [µV].
- `temperatura.dat`: `t` [°C], `vo`, `vosin`, `vireg` [V].
- `vbe_tip122.dat` (`ic` [A], `vbeorig`, `vbeaj` [V]) y `vbe_hoja.dat` (puntos de la hoja de datos).
- `val_linea.dat`: validación del modelo del LM7805 solo (`vi`, `vo05`, `vo1`).

En todos, el sufijo `sin` es el LM7805 conectado directo a la primaria, sin
la etapa.

**No hace falta volver a simular.** Los datos ya están exportados, y en esta
máquina LTspice no está instalado (el script `correr_simulaciones.py` está
escrito para Windows). Si alguna diapositiva necesita un número que no está en
el informe ni en `resultados.json`, se puede calcular a partir de los `.dat` o
a mano, pero se rotula en la diapositiva como cálculo propio no incluido en el
informe, y va en respaldo.

## El trabajo en pocas líneas

Para ubicarse antes de leer el informe:

- **Se pide** una fuente con LM7805 a partir de una primaria de 25 V de
  continua, con una etapa que lleve la entrada del regulador al rango de 8 a
  12 V para mejorar la regulación de línea; verificar por simulación la
  regulación de línea con Vin = 25 V y Vin = 10 V; elegir transistor, verificar
  SOA, calcular disipador y obtener todos los parámetros de calidad.
- **Se interpretó** que Vin es la entrada del regulador: se compara el LM7805
  directo a 25 V contra el LM7805 detrás de una etapa prereguladora que lo deja
  en unos 10 V. La consigna no fija la carga: se adoptó 0 a 0,5 A.
- **Se diseñó** un prerregulador serie con Darlington TIP122 y Zener 1N4741A
  de 11 V (Fig. 6-71 del apunte), RZ = 680 Ω. El TIP122 se eligió por su
  ganancia mínima garantizada (≥ 1000): con un TIP31C (≥ 25) el Zener tendría
  que conducir más de 200 mA.
- **Se verificó** el transistor en su SOA (peor caso 18,65 V · 0,508 A ·
  9,5 W) y se calcularon los dos disipadores (Aluel ZD-28 de 75 mm para el
  TIP122, 2125D para el regulador).
- **La simulación** (LTspice, con el modelo del LM7805 validado contra su hoja
  de datos y la VBE del TIP122 corregida) da la entrada del regulador en
  9,64 V, y ante ±10 % de la primaria la salida cambia 10,2 µV con la etapa
  contra 742,5 µV sin ella: unas 73 veces menos. El rechazo de rizado pasa de
  76,4 dB a 113,8 dB.
- **Lo que la etapa no hace**: no mejora el rendimiento (18,9 % contra 19,6 %,
  límite ideal 20 %). Lo que cambia es dónde se disipa: el regulador baja de
  10,2 W a 2,4 W y el TIP122 toma 7,8 W.

Ese es el hilo de la exposición: una etapa simple que mejora mucho la
regulación de línea y saca la potencia del regulador, y el costo que tiene.

## Código de color

En todo el mazo:

- **Azul** = la fuente diseñada, con etapa prereguladora.
- **Naranja** = el LM7805 conectado directo a la primaria de 25 V (la referencia contra la que se compara).

Curvas, números grandes, encabezados de tabla y píldoras respetan esa
asignación. Las magnitudes internas (tensión de base, entrada del regulador,
potencias de cada componente) van en marino, gris o verde, no en azul ni
naranja, salvo que representen a una de las dos fuentes. En la comparación
TIP31C / TIP122 no usar el par azul-naranja: resaltar el elegido con una fila
destacada.

## Guion propuesto

Es un punto de partida pensado para que los cuatro bloques queden parejos.
Se puede fusionar, partir o reordenar si mejora la exposición, manteniendo el
orden lógico y el reparto equilibrado. Cada título definitivo tiene que ser la
conclusión de su diapositiva, con el número cuando lo hay.

**Portada.** Título del estilo "Fuente de 5 V con LM7805 y etapa
prereguladora"; bajada "Actividad Evaluativa · Unidad 6 · Consigna 6 ·
Grupo 6". Mismo encabezado institucional y mismos integrantes y legajos que
la referencia (Alejo López Demichelis 401900, Tomás Polizze 400793, Pedro
Ernst 400624, Valentino Rao 402308). El motivo de fondo, con curvas reales del
trabajo: por ejemplo el barrido de línea (`linea.dat`), donde la entrada del
regulador se aplana en ~9,6 V mientras la primaria sigue subiendo.

**Bloque 1 · Consigna y planteo (Alejo)**
1. Recorrido: los cuatro bloques.
2. Qué pide la Consigna 6 y con qué datos se trabajó (las especificaciones adoptadas del informe, Tabla I), dejando claro qué fijó la consigna y qué adoptamos nosotros.
3. Cómo se interpretó "Vin = 25 V y Vin = 10 V".
4. El LM7805 por dentro: diagrama en bloques y sus tres protecciones.
5. Por qué conviene una entrada de 8 a 12 V: regulación de línea de la hoja de datos (3 mV típicos de 7 a 25 V contra 1 mV de 8 a 12 V) y potencia en el regulador (10 W contra ~2,5 W).
6. Las dos topologías del apunte (Zener base-masa, Fig. 6-71, y Zener colector-base, Fig. 6-72) y por qué se eligió la primera.

**Bloque 2 · Diseño de la etapa y verificación del transistor (Tomás)**
7. Separador con la pregunta del bloque.
8. El circuito completo, grande, con la etapa prereguladora señalada.
9. Selección del transistor: TIP31C contra TIP122 por ganancia mínima garantizada.
10. Zener y entrada del regulador: nominal y peor caso (8,85 a 10,35 V, siempre dentro de la ventana).
11. Cálculo de RZ, corrientes y potencias del Zener, y atenuación del rizado en la base.
12. Exigencias sobre el transistor y SOA con los puntos de trabajo nominal, de peor caso y de cortocircuito.
13. Disipadores del TIP122 y del LM7805 con el circuito térmico.
14. Qué pasa con la salida en cortocircuito y quién corta la falla.

**Bloque 3 · Simulación y regulación de línea (Pedro)**
15. Separador con la pregunta del bloque (cuánto mejora la regulación de línea).
16. Con qué modelos se simuló y cómo se validó el del LM7805 contra su hoja de datos, incluida la corrección de la VBE del TIP122. Breve; el detalle va a respaldo.
17. Barrido de la primaria: la entrada del regulador queda en 9,64 V y dentro de la ventana.
18. El resultado central: ΔVO ante ±10 % en los tres casos de la Tabla de regulación de línea (directo a 25 V, directo a 10 V, con etapa) y el factor de mejora.
19. Tolerancia del Zener: la entrada del regulador sigue dentro de la ventana.

**Bloque 4 · Parámetros de calidad y conclusiones (Valentino)**
20. Regulación de carga y resistencia de salida, con la aclaración de que el valor simulado es optimista (~10 mΩ esperables en la práctica).
21. Rizado: de 2 V pico a pico en la primaria a milivolts en la entrada del regulador y microvolts en la salida; rechazo de rizado con y sin etapa.
22. Coeficiente de temperatura: lo fija la referencia del LM7805; la etapa no lo cambia.
23. Rendimiento y reparto de potencia: la etapa no ahorra energía, cambia dónde se disipa.
24. Resumen de parámetros de calidad, con etapa y sin etapa (tabla).
25. Conclusiones (las del capítulo 5 del informe, condensadas).

**Cierre.** "Gracias · ¿Preguntas?", igual que la referencia.

**Respaldo** (después del cierre, para preguntas):
- La otra lectura de la consigna: la primaria misma bajando a 10 V (entrada del regulador en 8,54 V; dentro de la ventana mientras VP ≥ 9,46 V; por debajo de 11 V la etapa deja de regular).
- Tabla completa de validación del modelo del LM7805 contra la hoja de datos.
- Límites de la simulación: regulación de carga unas siete veces mejor que la típica, sin corte térmico en el modelo, y por qué no se usó el análisis `.ac` para el rechazo de rizado.
- VBE del TIP122: hoja de datos, modelo de onsemi y modelo ajustado.

## Figuras

Todas se rehacen con el estilo del mazo; no se pegan recortes del PDF del
informe. Un solo `figuras/generar.py` para los gráficos, leyendo
`../informe/datos/`.

- **Circuito completo, circuito térmico y diagrama en bloques del LM7805**: el
  informe ya los tiene en circuitikz/TikZ (`2_diseno.tex`, `3_transistor_termico.tex`,
  `1_introduccion.tex`). Partir de ese código, recolorearlo con la paleta del
  mazo y compilarlo con `tex2svg.py`. En el diagrama en bloques, reemplazar los
  rellenos pastel del informe por los tintes del mazo.
- **SOA del TIP122**: el informe la dibuja con tramos analíticos (están en
  `3_transistor_termico.tex`); reproducirla en matplotlib con los mismos
  tramos y los tres puntos de trabajo.
- **Gráficos de simulación** (línea, detalle de ΔVO, carga y potencias, rizado
  en cuatro paneles, temperatura, VBE): desde los `.dat`. Cuidar las escalas
  del rizado, que van de volts a microvolts: decirlo en la figura.

Las figuras del informe están pensadas para una columna de papel. Para
proyectar hay que rediseñarlas: menos paneles por diapositiva, trazos más
gruesos, y los valores importantes rotulados sobre la curva.

## Cuidados

- **Números**: los del informe, con su mismo redondeo y unidades. Cuando un
  valor aparece en varias diapositivas tiene que ser idéntico en todas. Antes
  de terminar, contrastar cada número del mazo contra el informe o
  `resultados.json`.
- **Decir lo que el trabajo dice de sí mismo**: la corriente de carga y la
  variación de ±10 % son adopciones nuestras; la regulación de carga simulada
  es optimista; el modelo no tiene corte térmico; la etapa no mejora el
  rendimiento. Son las preguntas más probables de los docentes.
- **Citas a la cátedra**: el informe refiere figuras y ecuaciones del apunte
  (Fig. 6-71, Ec. 6-41…). Mantener esas referencias donde ayuden a que el
  docente reconozca el criterio.
- **No tocar** nada fuera de `TP6/presentacion/`. No hacer commits: eso lo
  decide Pedro.

## Entregables

Todo dentro de `TP6/presentacion/`:

1. `deck.html` con sus `assets/`, `figuras/` (fuentes `.py` y `.tex` más los SVG) y scripts.
2. `EA_TP6_presentacion.pdf`, exportado con `exportar.py`.
3. `guion.md`: por cada diapositiva, quién expone y en tres o cuatro oraciones
   qué dice (lo que la diapositiva no escribe), más una lista final de
   preguntas probables de los docentes con su respuesta y en qué diapositiva
   de respaldo apoyarse.

## Cuándo está terminado

- `exportar.py` termina sin problemas.
- Se miraron las hojas de contacto y las capturas individuales de todas las
  diapositivas con figura o tabla, y no queda texto ilegible, figura apretada,
  hueco grande ni color de serie cruzado.
- Puesta al lado de `presentacion corregida.pdf`, parece del mismo grupo.
- No queda nada del ejemplo de la plantilla.
- Cada número fue contrastado con el informe.

Al terminar, informar a Pedro: cuántas diapositivas quedaron y cómo se
repartieron, qué se cambió respecto del guion propuesto y por qué, cualquier
número o afirmación que no se haya podido respaldar en el informe, y qué
conviene que el grupo revise a mano.
