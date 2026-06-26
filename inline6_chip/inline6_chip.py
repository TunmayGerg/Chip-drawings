import gdstk as gd
import numpy as np

def linc_ear(triangle_a, triangle_b, pad_radius, pad_center_to_triangle, angle, layer, tol):
    # triangle connecting to pad
    triangle_points = [0 + 0j, triangle_a + triangle_b*1j, -triangle_a + triangle_b*1j] 
    triangle = gd.Polygon(triangle_points)

    # rectangle connecting triangle to pad
    rectangle_connect = gd.rectangle(-triangle_a + triangle_b*1j, triangle_a + (triangle_b + pad_center_to_triangle)*1j) 

    # circle pad
    circle = gd.ellipse((triangle_b + pad_center_to_triangle)*1j, pad_radius, tolerance=tol)

    # union circle and rectangle and triangle to make ear. Result after boolean is list of polygons
    rectangle_pad = gd.boolean(circle, rectangle_connect, "or", precision=tol)
    ear = gd.boolean(rectangle_pad, triangle, "or", precision=tol, layer=layer)

    # rotate elements
    angle_rad = np.radians(angle) # transform angle to radians
    ear[0].rotate(angle_rad, center=0 + 0j)

    return ear[0]

def main():

    tolerance = 0.01
    # linc dimensions
    triangle_a = 75
    triangle_b = 500
    pad_radius = 700
    pad_center_to_triangle = 800
    angle = 62 # in degrees

    # The GDSII file is called a library, which contains multiple cells.
    lib = gd.Library()

    # Geometry must be placed in cells.
    coupler_chip = lib.new_cell("Coupler")

    linc_ear1 = linc_ear(triangle_a, triangle_b, pad_radius, pad_center_to_triangle, angle, layer = 0, tol=tolerance)

    coupler_chip.add(linc_ear1)

    # Save the library in a GDSII or OASIS file.
    lib.write_gds("chip.gds")
    lib.write_oas("chip.oas")

    # Optionally, save an image of the cell as SVG.
    coupler_chip.write_svg("chip.svg")

if __name__ == "__main__":
    main()