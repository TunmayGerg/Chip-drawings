import os  # used to build output paths relative to this script's folder
import gdstk as gd  # gdstk is the CAD library we use to generate GDSII layout files
import numpy as np  # kept for style parity with inline6_chip (handy for tolerances/math)

# Folder where this script lives -> we save all outputs into Ebeam_training,
# no matter which directory the script is run from.
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------- #
# Layer map (per the LayoutEditor tutorial assignment).
# In e-beam CAD, a LAYER represents one processing step / one mask plate.
#   LAYER 0 -> alignment marks
#   LAYER 1 -> silicon isolation mesa (the active island)
#   LAYER 2 -> implant dopants (source & drain doped regions)
#   LAYER 3 -> metal (source, drain, and gate contacts)
# ----------------------------------------------------------------------------- #
LAYER_ALIGN  = 0  # alignment marks live here
LAYER_MESA   = 1  # silicon isolation mesa
LAYER_DOPANT = 2  # implant dopants
LAYER_METAL  = 3  # source/drain/gate metal


def main():
    # The GDSII file is called a library, which contains the cell(s) of our design.
    lib = gd.Library()

    # Everything for this device lives in ONE cell. The top-level cell should
    # look just like the final device, so the alignment marks (LAYER 0) and the
    # transistor (LAYERS 1-3) all go into this single cell on their own layers.
    chip = lib.new_cell("TRANSISTOR")

    # ===================================================================== #
    # LAYER 0: alignment marks
    # Requirement (3): 20 um squares, in the corners.
    # Requirement (4): each mark's center must be a multiple of 10 um.
    # We center each 20 um square on a corner coordinate that is a multiple
    # of 10, so the square spans center +/- 10 um.
    # ===================================================================== #
    half = 20 / 2.0  # half the 20 um side -> the square reaches +/-10 um from its center
    mark_centers = [(-120, -70), (-120, 70), (120, -70), (120, 70)]  # all multiples of 10
    for cx, cy in mark_centers:
        # Build each square from its two opposite corners, centered on (cx, cy).
        mark = gd.rectangle((cx - half) + (cy - half) * 1j,
                            (cx + half) + (cy + half) * 1j,
                            layer=LAYER_ALIGN)
        chip.add(mark)

    # ===================================================================== #
    # LAYER 1: silicon isolation mesa
    # The mesa is the active silicon island (the vertical bar in the figure).
    # Source above, drain below, channel in the middle -- all sit on this mesa.
    # ===================================================================== #
    mesa = gd.rectangle(-8 - 30j, 8 + 30j, layer=LAYER_MESA)  # vertical bar, x:-8..8, y:-30..30
    chip.add(mesa)

    # ===================================================================== #
    # LAYER 2: implant dopants (two stacked squares, like the figure)
    # Requirement (1): dopants go UP TO the gate but NOT under it.
    # Requirement (2): dopants go UNDER the source and drain contacts.
    # The gate will cross the channel band y = -4..+4, so we keep the dopants
    # out of that band (leaving an intrinsic channel under the gate).
    # ===================================================================== #
    # Source dopant region (top of the mesa): from above the gate band up to the
    # mesa top, so the source contact finger lands on doped silicon.
    source_dopant = gd.rectangle(-8 + 6j, 8 + 28j, layer=LAYER_DOPANT)
    chip.add(source_dopant)

    # Drain dopant region (bottom of the mesa): mirror image below the gate band.
    drain_dopant = gd.rectangle(-8 - 28j, 8 - 6j, layer=LAYER_DOPANT)
    chip.add(drain_dopant)

    # ===================================================================== #
    # LAYER 3: metal (source, drain, gate)
    # Two big pads on the LEFT (source on top, drain on bottom), each with a
    # finger reaching in to contact its dopant square. The gate is a stripe
    # crossing the channel, wired out to its own pad on the RIGHT.
    # ===================================================================== #
    # Each metal piece is drawn as a SINGLE polygon (pad + finger/wire in one
    # closed outline) rather than as overlapping rectangles. Vertices are listed
    # as (x, y) pairs that trace the outline of the shape.

    # --- Source: L-shaped polygon = big bond pad (top-left) + finger to top dopant ---
    source_metal = gd.Polygon(
        [
            (-70, 15),  # bottom-left corner of the pad
            (8, 15),    # follow the bottom edge right, out to the finger tip
            (8, 25),    # up the right edge of the finger
            (-25, 25),  # back left to where the finger meets the pad
            (-25, 45),  # up the right edge of the pad
            (-70, 45),  # across the top of the pad
        ],
        layer=LAYER_METAL,
    )
    chip.add(source_metal)

    # --- Drain: L-shaped polygon (mirror of source) = pad (bottom-left) + finger ---
    drain_metal = gd.Polygon(
        [
            (-70, -15),  # top-left corner of the pad
            (8, -15),    # along the top edge right, out to the finger tip
            (8, -25),    # down the right edge of the finger
            (-25, -25),  # back left to where the finger meets the pad
            (-25, -45),  # down the right edge of the pad
            (-70, -45),  # across the bottom of the pad
        ],
        layer=LAYER_METAL,
    )
    chip.add(drain_metal)

    # --- Gate: single polygon = stripe across channel + wire + bond pad (right) ---
    gate_metal = gd.Polygon(
        [
            (-8, -4),   # bottom-left of the stripe (over the channel)
            (50, -4),   # bottom edge of stripe+wire running right to the pad
            (50, -20),  # down the left edge of the gate pad
            (90, -20),  # across the bottom of the gate pad
            (90, 20),   # up the right edge of the gate pad
            (50, 20),   # across the top of the gate pad, back to the wire
            (50, 4),    # down to the top edge of the wire
            (-8, 4),    # top edge of stripe+wire running back left
        ],
        layer=LAYER_METAL,
    )
    chip.add(gate_metal)

    # --- Write outputs into the Ebeam_training folder (same formats as inline6_chip) --- #
    lib.write_gds(os.path.join(OUT_DIR, "transistor.gds"))  # GDSII, preferred format for e-beam
    lib.write_oas(os.path.join(OUT_DIR, "transistor.oas"))  # OASIS, an alternative binary format

    # Optionally, save an image of the cell as SVG for a quick visual check.
    chip.write_svg(os.path.join(OUT_DIR, "transistor.svg"))


if __name__ == "__main__":
    main()
