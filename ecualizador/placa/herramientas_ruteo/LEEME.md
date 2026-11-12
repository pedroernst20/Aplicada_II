# Herramientas de ruteo de la placa doble faz

Placa de 178 × 105 mm, doble faz sin agujeros metalizados: el CNC solo perfora, así que cada vía es un alambre soldado de los dos lados. Ruteada con Freerouting 1.9.0 (`C:\Users\valen\Documents\KiCad\freerouting\`) y retocada a mano.

Los scripts de KiCad se corren con `C:\Users\valen\AppData\Local\Programs\KiCad\10.0\bin\python.exe`. Ninguno pisa el `.kicad_pro`.

| Script | Qué hace |
|---|---|
| `freeroute_df.py carpeta [pasadas]` | Exporta el DSN, marca las huellas que no se sueldan arriba (pad solo en B.Cu y obstáculo en F.Cu), le da más costo a la cara de arriba, corre Freerouting e importa el resultado. Con `FIJAR=1` lo ya ruteado queda fijo. |
| `ses_parcial.py placa.kicad_pcb ruteo.ses red1,red2` | Agrega a la placa solo las redes indicadas de un `.ses`. Sirve para rerutear unas pocas redes sin perder el resto. |
| `partir.py placa.kicad_pcb` | Parte una pista donde le llega otra por el medio (unión en T), para que `chaflan.py` la vea. |
| `unir.py placa.kicad_pcb` | Une tramos colineales y corre los codos a 90° que tienen una pata muy corta. |
| `chaflan.py entrada salida [tope_mm]` | Pasa a 45° los codos y las uniones en T a 90°. |
| `gotas.py placa.kicad_pcb` | Activa las gotas en pads y vías; el DRC con `--refill-zones` las genera. |
| `cuenta_df.py placa.kicad_pcb` | Cuenta vías y pads que llevan soldadura arriba. |
| `mapa_soldadura.py` | Rehace `imagenes/doble_faz_como_se_suelda.png` y `doble_faz_montaje.md` (dos pasos, ver el encabezado). |

Regla de la doble faz sin metalizar: las pistas de arriba solo llegan a pads que se pueden soldar de ese lado (resistencias, diodos, cerámicos de disco, TO-92, puntos de prueba). Zócalos, tiras de pines, potes, jack, pulsador, LED, electrolíticos, capacitores de caja y pads de cocodrilo van solo abajo. El plano de masa va solo abajo.
