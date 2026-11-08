import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_breadboard_base(ax, num_rows=30, title="PROTOBOARD"):
    # Background
    bg = patches.FancyBboxPatch((-0.2, -0.8), 18.4, num_rows + 1.6,
                                boxstyle="round,pad=0.3,rounding_size=0.5",
                                facecolor="#F8F8F5", edgecolor="#B0B0A8", linewidth=2.0)
    ax.add_patch(bg)
    
    # Center trough
    trough = patches.Rectangle((8.6, 0.4), 0.8, num_rows + 0.2, facecolor="#D8D8D0", edgecolor="none")
    ax.add_patch(trough)
    
    # Power Rail Stripes
    # Left +12V (Red)
    ax.plot([0.5, 0.5], [0.8, num_rows + 0.2], color="#E53935", linewidth=3.5, solid_capstyle='round')
    ax.text(0.5, num_rows + 0.65, "+12V", color="#E53935", fontsize=9, fontweight='bold', ha='center')
    # Left GND (Blue)
    ax.plot([2.5, 2.5], [0.8, num_rows + 0.2], color="#1E88E5", linewidth=3.5, solid_capstyle='round')
    ax.text(2.5, num_rows + 0.65, "GND", color="#1E88E5", fontsize=9, fontweight='bold', ha='center')
    
    # Right GND (Blue)
    ax.plot([15.5, 15.5], [0.8, num_rows + 0.2], color="#1E88E5", linewidth=3.5, solid_capstyle='round')
    ax.text(15.5, num_rows + 0.65, "GND", color="#1E88E5", fontsize=9, fontweight='bold', ha='center')
    # Right -12V (Blue)
    ax.plot([17.5, 17.5], [0.8, num_rows + 0.2], color="#3949AB", linewidth=3.5, solid_capstyle='round')
    ax.text(17.5, num_rows + 0.65, "-12V", color="#3949AB", fontsize=9, fontweight='bold', ha='center')

    # Draw Holes
    col_x = {
        'RAIL_+12V': 1.0,
        'RAIL_GND_L': 2.0,
        'A': 4.0, 'B': 5.0, 'C': 6.0, 'D': 7.0, 'E': 8.0,
        'F': 10.0, 'G': 11.0, 'H': 12.0, 'I': 13.0, 'J': 14.0,
        'RAIL_GND_R': 16.0,
        'RAIL_-12V': 17.0
    }
    
    for r in range(1, num_rows + 1):
        y = num_rows - r + 1
        # Left rails
        ax.plot(col_x['RAIL_+12V'], y, 'o', mfc='#2C2C2C', mec='#9E9E9E', ms=3.8)
        ax.plot(col_x['RAIL_GND_L'], y, 'o', mfc='#2C2C2C', mec='#9E9E9E', ms=3.8)
        # Main tie points
        for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            ax.plot(col_x[c], y, 'o', mfc='#333333', mec='#BDBDBD', ms=3.8)
        # Right rails
        ax.plot(col_x['RAIL_GND_R'], y, 'o', mfc='#2C2C2C', mec='#9E9E9E', ms=3.8)
        ax.plot(col_x['RAIL_-12V'], y, 'o', mfc='#2C2C2C', mec='#9E9E9E', ms=3.8)
        
        # Row Numbers
        if r % 5 == 0 or r == 1 or r == num_rows:
            ax.text(3.1, y, str(r), color='#757575', fontsize=8, ha='center', va='center', fontweight='bold')
            ax.text(14.9, y, str(r), color='#757575', fontsize=8, ha='center', va='center', fontweight='bold')

    # Column Letters
    for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        ax.text(col_x[c], num_rows + 0.6, c, color='#616161', fontsize=9, ha='center', fontweight='bold')
        ax.text(col_x[c], 0.25, c, color='#616161', fontsize=9, ha='center', fontweight='bold')

    ax.set_title(title, fontsize=13, fontweight='bold', color='#124182', pad=14)
    ax.set_xlim(-0.8, 18.8)
    ax.set_ylim(-0.4, num_rows + 1.4)
    ax.set_aspect('equal')
    ax.axis('off')
    return col_x

def to_xy(col, row, col_x, num_rows=30):
    return col_x[col], num_rows - row + 1

def draw_dip14(ax, col_x, start_row, num_rows, label="TL084"):
    # DIP-14 occupies 7 rows (start_row to start_row+6)
    y_top = num_rows - start_row + 1
    y_bot = num_rows - (start_row + 6) + 1
    
    # Body
    body = patches.Rectangle((8.3, y_bot - 0.4), 1.4, (y_top - y_bot) + 0.8,
                             facecolor="#212121", edgecolor="#111111", linewidth=1.5,
                             zorder=4)
    ax.add_patch(body)
    
    # Notch
    notch = patches.Arc((9.0, y_top + 0.4), 0.6, 0.4, angle=0, theta1=180, theta2=360,
                        color="#BDBDBD", linewidth=1.8, zorder=5)
    ax.add_patch(notch)
    
    # Text label
    ax.text(9.0, (y_top + y_bot)/2, label, color="white", fontsize=8.5, fontweight='bold',
            rotation=90, ha='center', va='center', zorder=5)
    
    # Pins and pin numbers
    for i in range(7):
        r = start_row + i
        y = num_rows - r + 1
        # Left pin (1 to 7)
        pin_num = i + 1
        ax.plot([8.0, 8.3], [y, y], color="#B0BEC5", linewidth=3.0, zorder=3)
        ax.text(8.5, y, str(pin_num), color="#B0BEC5", fontsize=6.5, ha='center', va='center', zorder=5)
        # Right pin (14 down to 8)
        pin_num_r = 14 - i
        ax.plot([9.7, 10.0], [y, y], color="#B0BEC5", linewidth=3.0, zorder=3)
        ax.text(9.5, y, str(pin_num_r), color="#B0BEC5", fontsize=6.5, ha='center', va='center', zorder=5)

def draw_wire(ax, col_x, c1, r1, c2, r2, num_rows=30, color="#2E7D32", lw=2.2, label=None, arc=0.0):
    x1, y1 = to_xy(c1, r1, col_x, num_rows)
    x2, y2 = to_xy(c2, r2, col_x, num_rows)
    
    # Pins in holes
    ax.plot(x1, y1, 'o', mfc=color, mec='#212121', ms=4.5, zorder=6)
    ax.plot(x2, y2, 'o', mfc=color, mec='#212121', ms=4.5, zorder=6)
    
    if arc == 0.0:
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round', zorder=5)
        xm, ym = (x1 + x2)/2, (y1 + y2)/2
    else:
        # Quadratic bezier curve
        dx, dy = x2 - x1, y2 - y1
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        # Normal vector
        nx, ny = -dy, dx
        norm = np.hypot(nx, ny)
        if norm > 0:
            nx, ny = nx/norm, ny/norm
        cx, cy = mx + arc * nx, my + arc * ny
        t = np.linspace(0, 1, 20)
        bx = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
        by = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
        ax.plot(bx, by, color=color, linewidth=lw, solid_capstyle='round', zorder=5)
        xm, ym = cx, cy

    if label:
        ax.text(xm, ym, label, color=color, fontsize=7, fontweight='bold',
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=0.6, alpha=0.9),
                zorder=7)

def draw_resistor(ax, col_x, c1, r1, c2, r2, num_rows=30, label="", body_color="#E0C39E"):
    x1, y1 = to_xy(c1, r1, col_x, num_rows)
    x2, y2 = to_xy(c2, r2, col_x, num_rows)
    
    # Lead wires
    ax.plot([x1, x2], [y1, y2], color="#8D6E63", linewidth=1.5, zorder=5)
    ax.plot(x1, y1, 'o', mfc="#5D4037", mec="#212121", ms=4.0, zorder=6)
    ax.plot(x2, y2, 'o', mfc="#5D4037", mec="#212121", ms=4.0, zorder=6)
    
    # Center body
    xm, ym = (x1 + x2)/2, (y1 + y2)/2
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    
    # Body patch
    body_len = min(1.2, max(0.8, np.hypot(x2 - x1, y2 - y1) * 0.55))
    body = patches.Rectangle((xm - body_len/2, ym - 0.22), body_len, 0.44,
                             angle=angle, rotation_point=(xm, ym),
                             facecolor=body_color, edgecolor="#5D4037", linewidth=0.8, zorder=7)
    ax.add_patch(body)
    
    # Label
    # Offset text slightly
    dx, dy = x2 - x1, y2 - y1
    norm = np.hypot(dx, dy)
    ox, oy = (-dy/norm)*0.35 if norm > 0 else 0, (dx/norm)*0.35 if norm > 0 else 0.35
    ax.text(xm + ox, ym + oy, label, fontsize=6.8, fontweight='bold', color="#3E2723",
            ha='center', va='center', zorder=8,
            bbox=dict(boxstyle="square,pad=0.1", fc="#FFF9C4", ec="#FBC02D", lw=0.5, alpha=0.95))

def draw_cap_ceramic(ax, col_x, c1, r1, c2, r2, num_rows=30, label=""):
    x1, y1 = to_xy(c1, r1, col_x, num_rows)
    x2, y2 = to_xy(c2, r2, col_x, num_rows)
    
    ax.plot([x1, x2], [y1, y2], color="#F57C00", linewidth=1.4, zorder=5)
    ax.plot(x1, y1, 'o', mfc="#E65100", mec="#212121", ms=4.0, zorder=6)
    ax.plot(x2, y2, 'o', mfc="#E65100", mec="#212121", ms=4.0, zorder=6)
    
    xm, ym = (x1 + x2)/2, (y1 + y2)/2
    disc = patches.Circle((xm, ym), 0.32, facecolor="#FFA726", edgecolor="#E65100", linewidth=0.9, zorder=7)
    ax.add_patch(disc)
    
    ax.text(xm, ym - 0.48, label, fontsize=6.8, fontweight='bold', color="#E65100",
            ha='center', va='center', zorder=8,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="#FFA726", lw=0.5, alpha=0.9))

def draw_diode(ax, col_x, c1, r1, c2, r2, num_rows=30, label="", cathode_is_2=True):
    # c1, r1: Anode (if cathode_is_2=True)
    # c2, r2: Cathode
    x1, y1 = to_xy(c1, r1, col_x, num_rows)
    x2, y2 = to_xy(c2, r2, col_x, num_rows)
    
    ax.plot([x1, x2], [y1, y2], color="#424242", linewidth=1.5, zorder=5)
    ax.plot(x1, y1, 'o', mfc="#212121", mec="#000000", ms=4.0, zorder=6)
    ax.plot(x2, y2, 'o', mfc="#212121", mec="#000000", ms=4.0, zorder=6)
    
    xm, ym = (x1 + x2)/2, (y1 + y2)/2
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    
    # Body
    body = patches.Rectangle((xm - 0.5, ym - 0.22), 1.0, 0.44, angle=angle, rotation_point=(xm, ym),
                             facecolor="#263238", edgecolor="#000000", linewidth=0.8, zorder=7)
    ax.add_patch(body)
    
    # Cathode band (silver stripe near end 2)
    # Cathode position: 0.35 towards end 2
    cx = xm + 0.3 * (x2 - x1) / max(0.001, np.hypot(x2 - x1, y2 - y1))
    cy = ym + 0.3 * (y2 - y1) / max(0.001, np.hypot(x2 - x1, y2 - y1))
    ax.plot(cx, cy, 'o', mfc="#CFD8DC", mec="#ECEFF1", ms=4.0, zorder=8)
    
    ax.text(xm, ym + 0.45, label, fontsize=6.8, fontweight='bold', color="#263238",
            ha='center', va='center', zorder=8,
            bbox=dict(boxstyle="round,pad=0.1", fc="#ECEFF1", ec="#455A64", lw=0.5, alpha=0.9))

def draw_test_point(ax, col_x, col, row, num_rows=30, label="TP", color="#D32F2F", side='left'):
    x, y = to_xy(col, row, col_x, num_rows)
    ax.plot(x, y, 'o', mfc="#FFEB3B", mec=color, ms=6.5, mew=1.5, zorder=9)
    ox = -1.6 if side == 'left' else 1.6
    ax.annotate(label, xy=(x, y), xytext=(x + ox, y),
                fontsize=7.2, fontweight='bold', color='white',
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
                bbox=dict(boxstyle="round,pad=0.2", fc=color, ec="black", lw=0.7),
                ha='center', va='center', zorder=10)

print("Primitives defined.")

def generate_proto_u1():
    fig, ax = plt.subplots(figsize=(10, 16), dpi=200)
    col_x = create_breadboard_base(ax, num_rows=30, title="PROTOBOARD 1: CHIP U1 (TL084)\nEntrada Zi, Offset, Integrador y Señal 2")
    
    # 1. IC U1
    draw_dip14(ax, col_x, start_row=15, num_rows=30, label="TL084 U1")
    
    # 2. Power and Decoupling
    # Rails bridge GND
    draw_wire(ax, col_x, 'RAIL_GND_L', 2, 'RAIL_GND_R', 2, num_rows=30, color="#212121", lw=2.2, label="GND")
    # Bulk Caps row 1
    draw_cap_ceramic(ax, col_x, 'RAIL_+12V', 1, 'RAIL_GND_L', 1, num_rows=30, label="10uF (+)")
    draw_cap_ceramic(ax, col_x, 'RAIL_GND_R', 1, 'RAIL_-12V', 1, num_rows=30, label="10uF (-)")
    
    # Decoupling U1 (Row 18)
    draw_wire(ax, col_x, 'RAIL_+12V', 18, 'D', 18, num_rows=30, color="#E53935", lw=2.5, label="+12V")
    draw_cap_ceramic(ax, col_x, 'C', 18, 'RAIL_GND_L', 18, num_rows=30, label="100nF")
    
    draw_wire(ax, col_x, 'G', 18, 'RAIL_-12V', 18, num_rows=30, color="#3949AB", lw=2.5, label="-12V")
    draw_cap_ceramic(ax, col_x, 'H', 18, 'RAIL_GND_R', 18, num_rows=30, label="100nF")
    
    # 3. Stage 1: Buffer Zi = 15k (U1A)
    # Vin Generator at A17
    draw_test_point(ax, col_x, 'A', 17, num_rows=30, label="ENTRADA Vin\n(Generador)", color="#1976D2", side='left')
    draw_wire(ax, col_x, 'B', 17, 'D', 17, num_rows=30, color="#1976D2", lw=2.0)
    draw_resistor(ax, col_x, 'C', 17, 'RAIL_GND_L', 17, num_rows=30, label="R1: 15k")
    # Buffer feedback pin 1 to 2
    draw_wire(ax, col_x, 'D', 15, 'D', 16, num_rows=30, color="#388E3C", lw=2.2, label="Retorno")
    draw_test_point(ax, col_x, 'A', 15, num_rows=30, label="TEST SEÑAL 1\n(0 a +2.5V)", color="#388E3C", side='left')
    
    # 4. Stage 2: Offset Summer (U1B)
    draw_resistor(ax, col_x, 'C', 15, 'C', 19, num_rows=30, label="R2: 100k")
    draw_resistor(ax, col_x, 'B', 19, 'RAIL_GND_L', 19, num_rows=30, label="R3: 100k")
    # Vref1 Divider (Row 6)
    draw_resistor(ax, col_x, 'RAIL_+12V', 6, 'C', 6, num_rows=30, label="R31: 6.8k")
    draw_resistor(ax, col_x, 'B', 6, 'RAIL_GND_L', 6, num_rows=30, label="R32: 1k")
    draw_wire(ax, col_x, 'D', 6, 'C', 20, num_rows=30, color="#8E24AA", lw=2.0, arc=0.2, label="Vref1 (+1.5V)")
    draw_resistor(ax, col_x, 'D', 20, 'D', 21, num_rows=30, label="R5: 100k")
    draw_test_point(ax, col_x, 'A', 21, num_rows=30, label="TEST Offset\n(Pin 7)", color="#8E24AA", side='left')
    
    # 5. Stage 3: Miller Integrator (U1C)
    draw_wire(ax, col_x, 'G', 19, 'RAIL_GND_R', 19, num_rows=30, color="#212121", lw=2.2, label="GND")
    draw_resistor(ax, col_x, 'C', 21, 'G', 20, num_rows=30, label="R8: 10k")
    draw_cap_ceramic(ax, col_x, 'H', 20, 'H', 21, num_rows=30, label="C1: 10nF")
    draw_resistor(ax, col_x, 'I', 20, 'I', 21, num_rows=30, label="R9: 100k")
    draw_test_point(ax, col_x, 'J', 21, num_rows=30, label="TEST Pre_int\n(Pin 8)", color="#F57C00", side='right')
    
    # 6. Stage 4: Centering S2 (U1D)
    draw_resistor(ax, col_x, 'G', 21, 'G', 17, num_rows=30, label="R6: 100k")
    draw_resistor(ax, col_x, 'H', 17, 'RAIL_GND_R', 17, num_rows=30, label="R7: 390k")
    # Vref2 Divider (Row 10)
    draw_resistor(ax, col_x, 'RAIL_+12V', 10, 'C', 10, num_rows=30, label="R33: 22k")
    draw_resistor(ax, col_x, 'B', 10, 'RAIL_GND_L', 10, num_rows=30, label="R34: 5.6k")
    draw_wire(ax, col_x, 'D', 10, 'J', 10, num_rows=30, color="#00897B", lw=2.0, arc=-0.2, label="Vref2")
    draw_resistor(ax, col_x, 'I', 10, 'G', 16, num_rows=30, label="R25: 100k")
    draw_resistor(ax, col_x, 'H', 16, 'H', 15, num_rows=30, label="R26: 390k")
    # Signal 2 Output
    draw_test_point(ax, col_x, 'J', 15, num_rows=30, label="SALIDA SEÑAL 2\n(-1.5V a +4.0V)\n-> Hacia Proto 2", color="#D32F2F", side='right')
    
    plt.tight_layout()
    fig.savefig("simulacion/proto_chip1.png", dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("proto_chip1.png created successfully.")

generate_proto_u1()

def generate_proto_u2():
    fig, ax = plt.subplots(figsize=(10, 16), dpi=200)
    col_x = create_breadboard_base(ax, num_rows=30, title="PROTOBOARD 2: CHIP U2 (TL084)\nDerivador, Señal 3 y Conformador de Flancos")
    
    # 1. IC U2
    draw_dip14(ax, col_x, start_row=15, num_rows=30, label="TL084 U2")
    
    # 2. Power and Decoupling
    draw_wire(ax, col_x, 'RAIL_GND_L', 2, 'RAIL_GND_R', 2, num_rows=30, color="#212121", lw=2.2, label="GND")
    
    # Decoupling U2 (Row 18)
    draw_wire(ax, col_x, 'RAIL_+12V', 18, 'D', 18, num_rows=30, color="#E53935", lw=2.5, label="+12V")
    draw_cap_ceramic(ax, col_x, 'C', 18, 'RAIL_GND_L', 18, num_rows=30, label="100nF")
    
    draw_wire(ax, col_x, 'G', 18, 'RAIL_-12V', 18, num_rows=30, color="#3949AB", lw=2.5, label="-12V")
    draw_cap_ceramic(ax, col_x, 'H', 18, 'RAIL_GND_R', 18, num_rows=30, label="100nF")
    
    # 3. Stage 5: Miller Differentiator (U2A)
    draw_test_point(ax, col_x, 'A', 11, num_rows=30, label="ENTRADA SEÑAL 2\n(Desde Proto 1)", color="#D32F2F", side='left')
    draw_resistor(ax, col_x, 'B', 11, 'B', 13, num_rows=30, label="R10: 4.7k")
    draw_cap_ceramic(ax, col_x, 'C', 13, 'C', 16, num_rows=30, label="C2: 1nF")
    draw_wire(ax, col_x, 'D', 17, 'RAIL_GND_L', 17, num_rows=30, color="#212121", lw=2.0, label="GND")
    # Feedback R11 // C3
    draw_resistor(ax, col_x, 'B', 15, 'B', 16, num_rows=30, label="R11: 62k")
    draw_cap_ceramic(ax, col_x, 'A', 15, 'A', 16, num_rows=30, label="C3: 56pF")
    draw_test_point(ax, col_x, 'D', 15, num_rows=30, label="TEST Pre_der\n(Pin 1)", color="#7B1FA2", side='left')
    
    # 4. Stage 6: Signal 3 Conditioning (U2B)
    draw_resistor(ax, col_x, 'C', 15, 'C', 19, num_rows=30, label="R27: 200k")
    draw_resistor(ax, col_x, 'B', 19, 'RAIL_GND_L', 19, num_rows=30, label="R28: 100k")
    # Vref3 Divider (-12V) at Row 6
    draw_resistor(ax, col_x, 'RAIL_-12V', 6, 'I', 6, num_rows=30, label="R35: 2.7k")
    draw_resistor(ax, col_x, 'H', 6, 'RAIL_GND_R', 6, num_rows=30, label="R36: 1k")
    draw_wire(ax, col_x, 'G', 6, 'A', 6, num_rows=30, color="#1565C0", lw=2.0, arc=-0.25, label="Vref3 (-3.2V)")
    draw_resistor(ax, col_x, 'B', 6, 'C', 20, num_rows=30, label="R29: 200k")
    draw_resistor(ax, col_x, 'D', 20, 'D', 21, num_rows=30, label="R30: 100k")
    draw_test_point(ax, col_x, 'A', 21, num_rows=30, label="TEST SEÑAL 3\n(0 a +3.0V)", color="#388E3C", side='left')
    
    # 5. Stage 7: Inverter (U2C)
    # Divisor +0.7V at Row 10
    draw_resistor(ax, col_x, 'RAIL_+12V', 10, 'C', 10, num_rows=30, label="R14: 10k")
    draw_resistor(ax, col_x, 'B', 10, 'RAIL_GND_L', 10, num_rows=30, label="R15: 620R")
    draw_wire(ax, col_x, 'D', 10, 'G', 19, num_rows=30, color="#E65100", lw=2.0, arc=-0.2, label="+0.7V")
    draw_resistor(ax, col_x, 'C', 21, 'G', 20, num_rows=30, label="R12: 56k")
    draw_resistor(ax, col_x, 'H', 20, 'H', 21, num_rows=30, label="R13: 43k")
    
    # 6. Passive Derivator C4/R16 and Rectifier Branch A (U2D)
    draw_cap_ceramic(ax, col_x, 'G', 21, 'G', 25, num_rows=30, label="C4: 10nF")
    draw_resistor(ax, col_x, 'H', 25, 'RAIL_GND_R', 25, num_rows=30, label="R16: 470R")
    draw_test_point(ax, col_x, 'J', 25, num_rows=30, label="Nodo seg_derivador\n-> Hacia Proto 3 (D1)", color="#F57C00", side='right')
    # Diode D3: Anode at G25, Cathode at G17 (Pin 12)
    draw_diode(ax, col_x, 'I', 25, 'G', 17, num_rows=30, label="D3: 1N5819 (Rama A)", cathode_is_2=True)
    draw_resistor(ax, col_x, 'H', 17, 'RAIL_GND_R', 17, num_rows=30, label="R17: 100R")
    # Buffer U2D feedback pin 13 to 14
    draw_wire(ax, col_x, 'G', 16, 'G', 15, num_rows=30, color="#2E7D32", lw=2.2, label="Seguidor")
    draw_resistor(ax, col_x, 'H', 15, 'I', 28, num_rows=30, label="R21: 56k")
    draw_test_point(ax, col_x, 'J', 28, num_rows=30, label="Salida Rama A\n-> Hacia Proto 3", color="#00897B", side='right')

    plt.tight_layout()
    fig.savefig("simulacion/proto_chip2.png", dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("proto_chip2.png created successfully.")

def generate_proto_u3():
    fig, ax = plt.subplots(figsize=(10, 16), dpi=200)
    col_x = create_breadboard_base(ax, num_rows=30, title="PROTOBOARD 3: CHIP U3 (TL084)\nRectificador Rama B y Amplificador Señal 4")
    
    # 1. IC U3
    draw_dip14(ax, col_x, start_row=15, num_rows=30, label="TL084 U3")
    
    # 2. Power and Decoupling
    draw_wire(ax, col_x, 'RAIL_GND_L', 2, 'RAIL_GND_R', 2, num_rows=30, color="#212121", lw=2.2, label="GND")
    
    # Decoupling U3 (Row 18)
    draw_wire(ax, col_x, 'RAIL_+12V', 18, 'D', 18, num_rows=30, color="#E53935", lw=2.5, label="+12V")
    draw_cap_ceramic(ax, col_x, 'C', 18, 'RAIL_GND_L', 18, num_rows=30, label="100nF")
    
    draw_wire(ax, col_x, 'G', 18, 'RAIL_-12V', 18, num_rows=30, color="#3949AB", lw=2.5, label="-12V")
    draw_cap_ceramic(ax, col_x, 'H', 18, 'RAIL_GND_R', 18, num_rows=30, label="100nF")
    
    # 3. Stage 8: Rectifier Branch B (U3A)
    draw_test_point(ax, col_x, 'A', 10, num_rows=30, label="ENTRADA seg_derivador\n(Desde Proto 2)", color="#F57C00", side='left')
    # Diode D1: Cathode at B10, Anode at B12
    draw_diode(ax, col_x, 'B', 12, 'B', 10, num_rows=30, label="D1: 1N5819 (Rama B)", cathode_is_2=True)
    draw_resistor(ax, col_x, 'A', 12, 'RAIL_GND_L', 12, num_rows=30, label="R18: 100R")
    draw_resistor(ax, col_x, 'C', 12, 'C', 16, num_rows=30, label="R19: 22k")
    draw_wire(ax, col_x, 'D', 17, 'RAIL_GND_L', 17, num_rows=30, color="#212121", lw=2.0, label="GND")
    # Feedback R20
    draw_resistor(ax, col_x, 'D', 16, 'D', 15, num_rows=30, label="R20: 22k")
    # Output Branch B
    draw_resistor(ax, col_x, 'C', 15, 'C', 19, num_rows=30, label="R22: 56k")
    
    # 4. Stage 9: Output Pulse Amplifier (U3B)
    draw_test_point(ax, col_x, 'A', 19, num_rows=30, label="ENTRADA Rama A\n(Desde R21 de Proto 2)", color="#00897B", side='left')
    draw_wire(ax, col_x, 'B', 19, 'D', 19, num_rows=30, color="#00897B", lw=2.2, label="Suma")
    draw_resistor(ax, col_x, 'B', 20, 'RAIL_GND_L', 20, num_rows=30, label="R23: 1k")
    draw_resistor(ax, col_x, 'D', 20, 'D', 21, num_rows=30, label="R24: 1.2M")
    draw_test_point(ax, col_x, 'A', 21, num_rows=30, label="TEST SEÑAL 4\n(Pulsos 0 a +1.0V)", color="#D32F2F", side='left')
    
    # 5. Protected Unused OpAmps (U3C & U3D)
    # U3C (Pins 8, 9, 10): Pin 10 to GND, Pin 8 to Pin 9
    draw_wire(ax, col_x, 'G', 19, 'RAIL_GND_R', 19, num_rows=30, color="#212121", lw=2.2, label="GND")
    draw_wire(ax, col_x, 'G', 21, 'G', 20, num_rows=30, color="#546E7A", lw=2.2, label="Buffer Protegido")
    # U3D (Pins 12, 13, 14): Pin 12 to GND, Pin 14 to Pin 13
    draw_wire(ax, col_x, 'G', 17, 'RAIL_GND_R', 17, num_rows=30, color="#212121", lw=2.2, label="GND")
    draw_wire(ax, col_x, 'G', 15, 'G', 16, num_rows=30, color="#546E7A", lw=2.2, label="Buffer Protegido")

    plt.tight_layout()
    fig.savefig("simulacion/proto_chip3.png", dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("proto_chip3.png created successfully.")

generate_proto_u2()
generate_proto_u3()

def generate_proto_completo():
    from PIL import Image
    im1 = Image.open("simulacion/proto_chip1.png")
    im2 = Image.open("simulacion/proto_chip2.png")
    im3 = Image.open("simulacion/proto_chip3.png")
    
    # Target height
    h = min(im1.height, im2.height, im3.height)
    w1 = int(im1.width * h / im1.height)
    w2 = int(im2.width * h / im2.height)
    w3 = int(im3.width * h / im3.height)
    
    im1_r = im1.resize((w1, h), Image.Resampling.LANCZOS)
    im2_r = im2.resize((w2, h), Image.Resampling.LANCZOS)
    im3_r = im3.resize((w3, h), Image.Resampling.LANCZOS)
    
    total_w = w1 + w2 + w3 + 80
    comp = Image.new("RGB", (total_w, h + 100), "#FFFFFF")
    
    # Paste images
    comp.paste(im1_r, (20, 80))
    comp.paste(im2_r, (w1 + 40, 80))
    comp.paste(im3_r, (w1 + w2 + 60, 80))
    
    # Draw title
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(comp)
    try:
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((total_w // 2, 35), "VISTA COMPLETA DEL MONTAJE EN 3 PROTOBOARDS (TL084 - TP N.º 2)", fill="#124182", anchor="mm", font=font)
    
    comp.save("simulacion/protoboard_completa.png", quality=95)
    print("protoboard_completa.png created successfully.")

generate_proto_completo()
