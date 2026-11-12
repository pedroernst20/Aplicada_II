"""Activa gotas (teardrops) en todos los pads pasantes y vias de un .kicad_pcb (edita el texto).
Uso: python gotas.py placa.kicad_pcb"""
import re
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
BLOQUE = ("(teardrops (best_length_ratio 0.5) (max_length 1.5) (best_width_ratio 1) (max_width 3) "
          "(curved_edges no) (filter_ratio 0.9) (enabled yes) (allow_two_segments yes) (prefer_zone_connections yes))")
n = 0
salida, i = [], 0
for m in re.finditer(r"\((pad \"[^\"]*\" thru_hole|via)\b", t):
    ini = m.start()
    if ini < i:
        continue
    # fin del bloque por parentesis balanceados
    nivel, k = 0, ini
    while True:
        c = t[k]
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
            if nivel == 0:
                break
        k += 1
    bloque = t[ini:k + 1]
    if "(teardrops" not in bloque and "(uuid" in bloque:
        j = bloque.rfind("(uuid")
        sangria = re.search(r"([\t ]*)\(uuid", bloque).group(1)
        bloque = bloque[:j] + BLOQUE + nl + sangria + bloque[j:]
        n += 1
    salida.append(t[i:ini]); salida.append(bloque)
    i = k + 1
salida.append(t[i:])
open(p, "w", encoding="utf-8", newline="").write("".join(salida))
print("gotas activadas en", n, "pads y vias")
