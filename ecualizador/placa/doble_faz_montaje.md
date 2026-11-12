# Placa doble faz: montaje

Agujeros sin metalizar: cada via y cada pad con pista de arriba se suelda tambien del lado de los componentes.
Mapa: `imagenes/doble_faz_como_se_suelda.png` (lo generan `herramientas_ruteo/mapa_soldadura.py`).

## Vias (13): alambre pasante soldado de los dos lados

| Via | x (mm) | y (mm) | red |
|---|---|---|---|
| V1 | 23.86 | 100.03 | /Audio/BUFIN |
| V2 | 40.48 | 71.66 | GND |
| V3 | 56.68 | 52.66 | /Audio/VI |
| V4 | 57.22 | 79.23 | Net-(C10-Pad1) |
| V5 | 61.02 | 90.69 | Net-(R14-Pad1) |
| V6 | 70.72 | 67.93 | GND |
| V7 | 86.08 | 33.23 | Net-(J4-Pin_2) |
| V8 | 96.97 | 78.35 | Net-(R16-Pad1) |
| V9 | 106.77 | 52.34 | GND |
| V10 | 114.94 | 37.90 | Net-(C6-Pad2) |
| V11 | 115.87 | 15.22 | +3.3VA |
| V12 | 131.94 | 55.99 | Net-(C6-Pad2) |
| V13 | 132.56 | 88.71 | Net-(R18-Pad1) |

## Pads que llevan soldadura arriba (65)

Soldar estas piezas un poco levantadas (1 o 2 mm) para llegar con el soldador al pad de arriba.

- **C12**: pata 2
- **C13**: pata 1
- **C14**: pata 2
- **C15**: pata 1
- **C16**: pata 2
- **C17**: pata 1
- **C25**: pata 2
- **C26**: pata 1
- **D1**: pata 2
- **D2**: pata 1
- **D4**: pata 1
- **D6**: pata 1, 2
- **D7**: pata 1
- **D9**: pata 1
- **R1**: pata 2
- **R2**: pata 2
- **R3**: pata 1, 2
- **R4**: pata 1, 2
- **R5**: pata 1
- **R6**: pata 1, 2
- **R8**: pata 1
- **R10**: pata 1
- **R11**: pata 2
- **R13**: pata 1
- **R14**: pata 1
- **R16**: pata 1
- **R18**: pata 1, 2
- **R21**: pata 1
- **R22**: pata 2
- **R23**: pata 1, 2
- **R24**: pata 1, 2
- **R25**: pata 1, 2
- **R26**: pata 1
- **R27**: pata 2
- **R28**: pata 2
- **R29**: pata 1, 2
- **R30**: pata 2
- **R33**: pata 1
- **R35**: pata 1
- **R41**: pata 1
- **TP3**: pata 1, 1
- **TP4**: pata 1
- **TP5**: pata 1, 1
- **TP6**: pata 1, 1
- **TP7**: pata 1, 1
- **TP8**: pata 1, 1
- **TP10**: pata 1
- **TP11**: pata 1, 1
- **TP15**: pata 1
- **TP20**: pata 1

Orden: primero las vias, despues las piezas bajas con soldadura arriba y al final las que van solo abajo.
Solo abajo: zocalos, tiras de pines, potes, jack, pulsador, LED, electroliticos, capacitores de caja y pads de
cocodrilo (el ruteo nunca les lleva pistas por arriba).
