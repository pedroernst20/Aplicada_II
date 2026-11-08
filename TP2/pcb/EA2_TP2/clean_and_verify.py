import sys, re, uuid, os
import pcbnew

def main():
    bak_path = 'pcb/EA2_TP2/EA2_TP2.kicad_pcb.bak'
    out_path = 'pcb/EA2_TP2/EA2_TP2.kicad_pcb'

    with open(bak_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.splitlines(keepends=True)
    header = []
    top_items = []
    current_item = []
    depth = 0

    for line in lines:
        if depth == 0:
            if line.startswith('\t('):
                delta = line.count('(') - line.count(')')
                if delta == 0:
                    top_items.append(line)
                else:
                    current_item = [line]
                    depth = delta
            else:
                header.append(line)
        else:
            current_item.append(line)
            depth += line.count('(') - line.count(')')
            if depth == 0:
                top_items.append(''.join(current_item))
                current_item = []

    print(f'Parsed {len(top_items)} top-level items.')

    bite_positions = {
        '-12': (120.0, 36.0),
        'J1': (120.0, 58.75),
        'GND': (120.0, 72.0),
    }

    new_items = []
    for item in top_items:
        first_token = item.split()[0].lstrip('(').rstrip(')')

        if first_token == 'footprint':
            if 'MountingHole' in item:
                continue

            for u in ['U1', 'U2', 'U3', 'U4', 'U5']:
                if f'(property "Reference" "{u}"' in item:
                    item = item.replace('Package_DIP:DIP-8_W7.62mm', 'Package_DIP:DIP-8_W7.62mm_Socket')
                    break

            # Drop original Vi pin header (it is replaced by JP_Vi pad 2 landing pad and Vi_IN bite pad)
            if '(property "Reference" "Vi"' in item:
                continue

            for ref, (bx, by) in bite_positions.items():
                if f'(property "Reference" "{ref}"' in item:
                    item = re.sub(r'\(at\s+[\d\.\-]+\s+[\d\.\-]+(?:\s+[\d\.\-]+)?\)', f'(at {bx} {by})', item, count=1)
                    item = re.sub(r'\(footprint\s+\"[^\"]+\"', '(footprint "TestPoint:TestPoint_THTPad_D4.0mm_Drill2.0mm"', item, count=1)
                    item = re.sub(r'\(pad\s+\"1\"\s+thru_hole\s+\w+\s+\(at\s+0\s+0\)\s+\(size\s+[\d\.\-]+\s+[\d\.\-]+\)\s+\(drill\s+[\d\.\-]+\)',
                                  '(pad "1" thru_hole circle (at 0 0) (size 4 4) (drill 2)', item)
                    break

            for tp_ref in ['Offset', 'Integrador', 'Derivador', 'Seg_der', 'Rect', 'Rect_amp']:
                if f'(property "Reference" "{tp_ref}"' in item:
                    item = re.sub(r'\(footprint\s+\"[^\"]+\"', '(footprint "TestPoint:TestPoint_THTPad_D3.0mm_Drill1.5mm"', item, count=1)
                    item = re.sub(r'\(pad\s+\"1\"\s+thru_hole\s+\w+\s+\(at\s+0\s+0\)\s+\(size\s+[\d\.\-]+\s+[\d\.\-]+\)\s+\(drill\s+[\d\.\-]+\)',
                                  '(pad "1" thru_hole circle (at 0 0) (size 3 3) (drill 1.5)', item)
                    break

            new_items.append(item)

        elif first_token == 'zone':
            continue

        elif first_token == 'segment':
            # Remove crossing GND segment at (204.75, 42.0) -> (209.50, 42.0)
            if '(net "GND")' in item and '204.75' in item and '42' in item and '209.5' in item:
                print('Removing crossing GND segment at Y=42.0')
                continue
            # All remaining tracks moved to B.Cu
            item = item.replace('(layer "F.Cu")', '(layer "B.Cu")')
            new_items.append(item)

        elif first_token == 'gr_rect':
            continue
        elif first_token == 'dimension':
            continue
        else:
            new_items.append(item)

    # Edge.Cuts rectangle: exactly 200mm x 100mm: (110 32) to (310 132)
    edge_cuts_rect = f'''\t(gr_rect
\t\t(start 110 32)
\t\t(end 310 132)
\t\t(stroke (width 0.1) (type default))
\t\t(fill none)
\t\t(layer "Edge.Cuts")
\t\t(uuid "{uuid.uuid4()}")
\t)
'''
    new_items.append(edge_cuts_rect)

    # 1. Vi bite pad at (120, 54.5)
    vi_bite_str = f'''\t(footprint "TestPoint:TestPoint_THTPad_D4.0mm_Drill2.0mm"
\t\t(layer "F.Cu")
\t\t(uuid "{uuid.uuid4()}")
\t\t(at 120 54.5)
\t\t(property "Reference" "Vi_IN"
\t\t\t(at 0 -3.0 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "Vi"
\t\t\t(at 0 3.0 0)
\t\t\t(layer "F.Fab")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(pad "1" thru_hole circle (at 0 0) (size 4 4) (drill 2)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(net "/Vi")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t)
\t)
'''
    new_items.append(vi_bite_str)

    # 2. GND_SCOPE bite pad at (120, 84)
    gnd_scope_str = f'''\t(footprint "TestPoint:TestPoint_THTPad_D4.0mm_Drill2.0mm"
\t\t(layer "F.Cu")
\t\t(uuid "{uuid.uuid4()}")
\t\t(at 120 84)
\t\t(property "Reference" "GND_SCOPE"
\t\t\t(at 0 -3.0 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "GND"
\t\t\t(at 0 3.0 0)
\t\t\t(layer "F.Fab")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(pad "1" thru_hole circle (at 0 0) (size 4 4) (drill 2)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(net "GND")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t)
\t)
'''
    new_items.append(gnd_scope_str)

    # Function to create clean wire jumper with duplicate pad numbers for 0 DRC unconnected
    def make_jumper(ref, val, x1, y1, x2, y2, net):
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        dx1, dy1 = x1 - cx, y1 - cy
        dx2, dy2 = x2 - cx, y2 - cy
        return f'''\t(footprint "Jumper:Jumper_Horizontal_RM10.16mm"
\t\t(layer "F.Cu")
\t\t(uuid "{uuid.uuid4()}")
\t\t(at {cx:.4f} {cy:.4f})
\t\t(duplicate_pad_numbers_are_jumpers yes)
\t\t(property "Reference" "{ref}"
\t\t\t(at 0 -2.0 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "{val}"
\t\t\t(at 0 2.0 0)
\t\t\t(layer "F.Fab")
\t\t\t(uuid "{uuid.uuid4()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(fp_line (start {dx1:.4f} {dy1:.4f}) (end {dx2:.4f} {dy2:.4f})
\t\t\t(stroke (width 0.2) (type solid)) (layer "F.SilkS") (uuid "{uuid.uuid4()}"))
\t\t(pad "1" thru_hole circle (at {dx1:.4f} {dy1:.4f}) (size 1.8 1.8) (drill 0.9)
\t\t\t(layers "*.Cu" "*.Mask") (net "{net}") (uuid "{uuid.uuid4()}"))
\t\t(pad "1" thru_hole circle (at {dx2:.4f} {dy2:.4f}) (size 1.8 1.8) (drill 0.9)
\t\t\t(layers "*.Cu" "*.Mask") (net "{net}") (uuid "{uuid.uuid4()}"))
\t)
'''

    # JP_Vi: jumps over +12 from (146.0, 54.5) to (151.25, 54.5)
    new_items.append(make_jumper('JP_Vi', 'Jumper', 146.0, 54.5, 151.25, 54.5, '/Vi'))

    # JP1: at X=174.0, from Y=66.5 to Y=92.37 (jumps over R11, R24, R12)
    new_items.append(make_jumper('JP1', 'Jumper', 174.0, 66.5, 174.0, 92.37, '/-12'))

    # JP2: at Y=117.0, from X=144.0 to X=152.5 (jumps over /Rect and +12, outside U5 courtyard)
    new_items.append(make_jumper('JP2', 'Jumper', 144.0, 114.75, 153.5, 114.75, '/-12'))

    # JP3: from (221.12, 73.0) to (227.12, 93.5) (jumps over Pre_der / U3 signals)
    new_items.append(make_jumper('JP3', 'Jumper', 221.12, 73.0, 227.12, 93.5, '/-12'))

    def make_seg(net, x1, y1, x2, y2, width=0.8):
        return f'''\t(segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {width}) (layer "B.Cu") (net "{net}") (uuid "{uuid.uuid4()}"))\n'''

    # Vi track from bite pad (120, 54.5) to JP_Vi pad 1 (146.0, 54.5)
    new_items.append(make_seg('/Vi', 120.0, 54.5, 146.0, 54.5, 0.8))

    # +12 track from bite pad (120, 58.75) to (151.25, 58.75)
    new_items.append(make_seg('/+12', 120.0, 58.75, 151.25, 58.75, 0.8))

    # -12 top highway from bite pad (120, 36.0) to (208.13, 36.0) -> (208.13, 52.75) [U2.4]
    new_items.append(make_seg('/-12', 120.0, 36.0, 208.13, 36.0, 0.8))
    new_items.append(make_seg('/-12', 208.13, 36.0, 208.13, 52.75, 0.8))

    # -12 highway continuation: (208.13, 36.0) -> (255.0, 36.0) -> (255.0, 127.0) -> (144.0, 127.0)
    new_items.append(make_seg('/-12', 208.13, 36.0, 255.0, 36.0, 0.8))
    new_items.append(make_seg('/-12', 255.0, 36.0, 255.0, 127.0, 0.8))
    new_items.append(make_seg('/-12', 255.0, 127.0, 144.0, 127.0, 0.8))

    # -12 R37.1 to bottom highway: (227.12, 90.75) -> (227.12, 127.0)
    new_items.append(make_seg('/-12', 227.12, 90.75, 227.12, 127.0, 0.8))

    # JP1 connections:
    # Pad 1 at (174.0, 66.5) -> U1.4 at (174.04, 64.12)
    new_items.append(make_seg('/-12', 174.0, 66.5, 174.04, 64.12, 0.8))
    # Pad 2 at (174.0, 92.37) -> U4.4 at (170.00, 92.37)
    new_items.append(make_seg('/-12', 174.0, 92.37, 170.00, 92.37, 0.8))

    # JP2 connections:
    # Pad 1 at (144.0, 117.0) -> bottom highway at (144.0, 127.0)
    new_items.append(make_seg('/-12', 144.0, 114.75, 144.0, 127.0, 0.8))
    # Pad 2 at (152.5, 117.0) -> U5.4 at (154.17, 114.75)
    new_items.append(make_seg('/-12', 153.5, 114.75, 154.17, 114.75, 0.8))

    # JP3 connections:
    # Pad 1 at (221.12, 73.0) -> U3.4 at (221.12, 75.75)
    new_items.append(make_seg('/-12', 221.12, 73.0, 221.12, 75.75, 0.8))
    # Pad 2 at (227.12, 93.5) -> R37.1 at (227.12, 90.75)
    new_items.append(make_seg('/-12', 227.12, 93.5, 227.12, 90.75, 0.8))

    # Ground Plane Zone on B.Cu
    gnd_zone_str = f'''\t(zone
\t\t(net "GND")
\t\t(layer "B.Cu")
\t\t(uuid "{uuid.uuid4()}")
\t\t(hatch edge 0.5)
\t\t(connect_pads (clearance 0.4))
\t\t(min_thickness 0.25)
\t\t(fill yes
\t\t\t(thermal_gap 0.4)
\t\t\t(thermal_bridge_width 0.4)
\t\t\t(island_removal_mode 0)
\t\t)
\t\t(polygon
\t\t\t(pts (xy 109 31) (xy 311 31) (xy 311 133) (xy 109 133))
\t\t)
\t)
'''
    new_items.append(gnd_zone_str)

    final_output = header[0] + ''.join(new_items) + header[1]
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f'Successfully wrote updated PCB to {out_path}')

if __name__ == '__main__':
    main()
