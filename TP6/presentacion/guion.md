# Guion de la exposición · TP6, Consigna 6

Lo que cada uno dice en cada diapositiva, además de lo que está escrito en
pantalla. Los números son los del informe; si alguien los cambia en el mazo,
que los cambie también acá.

Código de color en todo el mazo: **azul = la fuente con la etapa
prereguladora**, **naranja = el LM7805 conectado directo a los 25 V**.
Conviene decirlo una vez, en la diapositiva 4.

---

## Bloque 1 · Alejo López Demichelis (diapositivas 1 a 7)

**1. Portada.** Presentar al grupo y el tema. Las curvas del fondo son reales:
la naranja es la tensión que vería el LM7805 conectado directo, que sube con
la primaria; la azul es la que ve con la etapa, que se aplana en unos 9,6 V
dentro de la ventana de 8 a 12 V (líneas punteadas).

**2. Recorrido.** Anunciar los cuatro bloques y quién expone cada uno.

**3. Datos de partida.** La consigna fija la primaria de 25 V, el LM7805 y la
ventana de 8 a 12 V, y pide verificar la regulación de línea con 25 V y 10 V.
No fija la corriente: adoptamos 0,5 A porque es la corriente con la que la
hoja de datos especifica el regulador. El ±10 % y las temperaturas salen del
apunte; el rizado de 2 Vpp sólo se usa para medir el rechazo.

**4. Interpretación.** $V_{in}$ es la entrada del regulador, porque el rango
de 8 a 12 V es el que la hoja de datos usa para su mejor regulación de línea.
Entonces la comparación es: LM7805 directo a 25 V contra LM7805 detrás de una
etapa que lo deja en unos 10 V. Presentar acá el código de color. Aclarar que
la otra lectura (la primaria misma en 10 V) también está simulada, en el
respaldo.

**5. El LM7805 por dentro.** Recorrer el diagrama: Darlington de paso,
referencia, amplificador de error y muestreo forman el lazo; las tres
protecciones actúan sobre la base del Darlington. La limitación de corriente
y el corte térmico vuelven a aparecer en el cortocircuito (diapositiva 20).

**6. Por qué 8 a 12 V.** Dos razones: la hoja de datos da 1 mV de regulación
de línea en esa zona contra 3 mV entre 7 y 25 V, y la potencia en el
regulador baja de 10 W a unos 2,5 W. El límite inferior sale de 5 V más 3 V
de margen, que deja 1 V sobre el *dropout* de 2 V. Los 2,5 W son una
estimación; la simulación da 2,38 W.

**7. Topología.** El apunte muestra dos circuitos con transistor y Zener. En
el de la Fig. 6-71 el Zener fija la base y el transistor es seguidor de
emisor, así que las variaciones de la primaria llegan atenuadas. En el de la
Fig. 6-72 la tensión de salida es la primaria menos una tensión fija, así que
toda variación pasa. Como el objetivo es mejorar la regulación de línea, se
eligió el primero. Pasar a Tomás.

## Bloque 2 · Tomás Polizze (diapositivas 8 a 14)

**8. Separador.** Plantear las tres preguntas del bloque: qué transistor, qué
Zener y cuánto disipador.

**9. Circuito completo.** Señalar la etapa (recuadro azul), los capacitores
del regulador y el diodo de protección. La tensión de entrada del regulador
es la del Zener menos la $V_{BE}$ del Darlington: 11 − 1,4 = 9,6 V.

**10. Transistor.** El apunte pide que el Zener conduzca diez veces la
corriente de base máxima. El ejemplo del apunte usa la ganancia típica del
TIP31A, pero lo correcto es la mínima garantizada: con el TIP31C ($h_{FE}$ ≥ 25)
el Zener tendría que conducir 203 mA, con $R_Z$ ≈ 52 Ω y varios watts en
juego. El TIP122 garantiza 1000, y con 5,1 mA alcanza. La contrapartida es la
$V_{BE}$ de 1,4 V.

**11. Zener.** Queremos unos 10 V en la entrada: 10 + 1,4 = 11,4 V, y el
comercial más cercano es el 1N4741A de 11 V. Con la tolerancia del Zener y la
dispersión de $V_{BE}$, la entrada queda entre 8,85 y 10,35 V, siempre en la
ventana. El de 10 V la dejaría en 8,6 V, muy cerca del límite.

**12. Cálculo de $R_Z$.** Se fija la corriente del Zener cerca de su $I_{ZT}$,
en unos 20 mA, y da 683 Ω → 680 Ω. Está por debajo del máximo de la Ec. 6-49.
Con los extremos de la primaria y de la carga, el Zener queda entre 16,4 y
24,3 mA y disipa como máximo 0,27 W. La etapa ya atenúa el rizado unos 40 dB
antes del regulador.

**13. SOA.** Peor caso: primaria al máximo y entrada del regulador al mínimo,
18,65 V y 9,5 W. Los tres puntos (nominal, peor caso y cortocircuito) están
dentro de la curva de 25 °C y de la reducida a 80 °C, lejos de la segunda
ruptura.

**14. Disipadores.** Circuito térmico del apunte, con 40 °C de ambiente y
100 °C de juntura de diseño. El TIP122 necesita 3,1 °C/W o menos y se eligió
un ZD-28 de 75 mm (2,9 °C/W); la juntura llega a 98 °C. El LM7805 necesita
17,1 °C/W o menos y alcanza con el 2125D del Ejemplo 9. Sin disipador, el
TIP122 no funciona: llegaría a unos 630 °C. Pasar a Pedro.

## Bloque 3 · Pedro Ernst (diapositivas 15 a 20)

**15. Separador.** La pregunta central del trabajo: cuánto mejora la
regulación de línea.

**16. Modelos.** Antes de confiar en la simulación se validó el modelo del
regulador con los mismos ensayos de su hoja de datos. Sin efecto Early daba
una regulación de línea irreal; con él reproduce línea, rizado, temperatura y
*dropout*. La única diferencia grande es la regulación de carga, unas siete
veces mejor que la real. El TIP122 de onsemi daba una $V_{BE}$ 0,6 V más baja
y se corrigió (detalle en el respaldo).

**17. Barrido de la primaria.** Mientras la primaria supera los 11 V del
Zener, la base queda fija y la entrada del regulador también: 9,64 V con 25 V,
y sólo 58 mV de variación con ±10 %. Por debajo de 11 V el transistor copia
la primaria.

**18. Resultado central.** Ante ±10 % de la primaria, el LM7805 directo a
25 V cambia 742,5 µV. Con 10 V en su entrada cambia 350,9 µV: el mismo
regulador regula mejor en la zona de 8 a 12 V, como dice la hoja de datos.
Con la etapa cambia 10,2 µV, 73 veces menos, porque además de trabajar cerca
de 10 V sólo ve 58 mV de variación en lugar de 5 V.

**19. Tolerancia del Zener.** Con el Zener en −5 %, nominal y +5 %, la
entrada queda en 9,10, 9,64 y 10,18 V, dentro del rango calculado. Con la
primaria en 10 V el Zener no conduce, así que su tolerancia no influye.

**20. Cortocircuito.** El LM7805 limita la corriente a 1,85 A. En ese estado
el TIP122 disipa 29 W y el regulador 17 W. El punto está dentro de la SOA
pero no se sostiene: lo que corta la falla es el corte térmico del
regulador, que deja también al transistor sin corriente. El modelo no tiene
corte térmico, por eso no se simula; en laboratorio, fusible. Pasar a
Valentino.

## Bloque 4 · Valentino Rao (diapositivas 21 a 26)

**21. Regulación de carga.** De vacío a plena carga la salida pasa de 4,9645
a 4,9634 V: 0,021 % y 2,1 mΩ. Son optimistas por lo que vimos en la
validación; con la hoja de datos cabe esperar unos 10 mΩ. La etapa no
influye: el Zener casi no cambia su corriente porque el Darlington pide sólo
0,14 mA de base, y la etapa está fuera del lazo del regulador.

**22. Rizado.** Con 2 Vpp en la primaria, a la entrada del regulador llegan
23,1 mV (el cálculo daba 20,4 mV) y a la salida 4,1 µV, contra 302 µV sin la
etapa. Los rechazos se suman en dB: 38,7 de la etapa más 75,1 del regulador,
113,8 dB contra 76,4 dB. Ojo con las escalas del gráfico.

**23. Temperatura.** El coeficiente es el de la referencia del LM7805, con o
sin etapa: −0,0193 contra −0,0190 %/°C. La entrada del regulador sí se mueve,
13,5 mV/°C, pero el regulador la rechaza como cualquier variación de línea.

**24. Rendimiento.** La etapa no ahorra energía: el rendimiento queda en
18,9 % contra 19,6 % sin ella, y el límite ideal es 20 %. Lo que cambia es el
reparto: el regulador pasa de 10,16 W a 2,38 W y el TIP122 toma 7,76 W, en un
disipador más fácil de dimensionar.

**25. Resumen.** Recorrer la tabla destacando que la etapa mejora la
regulación de red y el rizado, y que carga, temperatura y rendimiento los
fija el regulador.

**26. Conclusiones.** Leer sólo los números clave: 9,64 V en la entrada,
10,2 µV contra 742,5 µV, 113,8 dB contra 76,4 dB, y el regulador de 10,16 W a
2,38 W. Cerrar con las tres recomendaciones para armarla.

**27. Gracias · ¿Preguntas?**

---

## Preguntas probables de los docentes

| Pregunta | Respuesta corta | Apoyo |
|---|---|---|
| ¿Por qué interpretaron $V_{in}$ como la entrada del regulador y no la primaria? | El rango de 8 a 12 V es el de la hoja de datos para la entrada del regulador. Igual simulamos la otra lectura: con la primaria en 10 V la entrada queda en 8,54 V, dentro de la ventana mientras $V_P$ ≥ 9,46 V. | Diap. 4 y respaldo 28 |
| ¿Por qué 0,5 A si la consigna no lo dice? | Es la corriente con la que la hoja de datos especifica las características eléctricas del LM7805. | Diap. 3 |
| ¿Por qué no un TIP31 como en el apunte? | El apunte usa la ganancia típica. Con la mínima garantizada (25) el Zener debería conducir 203 mA. | Diap. 10 |
| ¿Qué pasa si la primaria baja de 11 V? | El Zener deja de conducir, el transistor copia la primaria y la etapa no regula. Con 10 V a 25 V, la salida cambia 194 µV con etapa y 2472,80 µV sin ella. | Respaldo 28 |
| ¿Cómo saben que el modelo del LM7805 es confiable? | Se lo validó con los ensayos de la hoja de datos; reproduce línea, rizado, temperatura y *dropout*. | Diap. 16 y respaldo 29 |
| La resistencia de salida de 2,1 mΩ parece muy baja. | Lo es: el modelo da una regulación de carga unas siete veces mejor que la típica. En la práctica, unos 10 mΩ. | Diap. 21 y respaldo 31 |
| ¿Por qué no usaron el análisis `.ac` para el rechazo de rizado? | Con este modelo da unos 38 dB, que no coincide con la regulación en continua ni con el transitorio. Se midió en transitorio con la definición del Coughlin. | Respaldo 31 |
| ¿Por qué corrigieron el modelo del TIP122? | El de onsemi daba 0,77 V de $V_{BE}$ a 0,5 A contra 1,35 V de la hoja de datos. Con el ajuste la entrada simulada (9,64 V) coincide con la calculada. | Respaldo 30 |
| ¿Qué pasa en cortocircuito sostenido? | Limita el LM7805 a 1,85 A; el TIP122 disipa 29 W y el regulador 17 W. Corta el corte térmico del regulador. No se simula porque el modelo no lo tiene. | Diap. 20 |
| ¿La etapa mejora el rendimiento? | No: 18,9 % contra 19,6 %. Saca potencia del regulador y la pone en el transistor. | Diap. 24 |
| ¿Por qué mica entre el TIP122 y el disipador? | Porque la aleta del TO-220 está unida al colector. Se tomó 1,3 °C/W para mica más grasa. | Diap. 14 y 26 |
