import subprocess
import os
import os.path

def rasterize_svgfile(svgfile):
    """
    Converts a svg file to png file with same basename.
    """

    output_dir = os.path.dirname(svgfile)
    name = os.path.basename(svgfile)
    (root, ext) = os.path.splitext(name)
    pngfile = os.path.join(output_dir, f"{root}.png")
    # Use svgo to optimize the svg and move vector-effect to an attribute.
    subprocess.call(["svgo", "-i", svgfile, "-o", svgfile], shell=False)
    pngfile = os.path.join(output_dir, f"{root}.png")
    subprocess.call(["svpng", svgfile, pngfile], shell=False)

    return pngfile


def potrace(trimmedbmp, output_dir):
    """
    Convert the mask into a svg file.
    """
    mask_bmp = os.path.basename(trimmedbmp)
    (mask_name, ext) = os.path.splitext(mask_bmp)

    masksvg = os.path.join(output_dir, f"{mask_name}.svg")
    # TODO: add --flat to set the whole image as single path
    # TODO: suppress speckle size with --turdsize 10
    potrace = [
        "potrace",
        trimmedbmp,
        "--turnpolicy",
        "majority",
        "--opttolerance",
        "0",
        "--alphamax",
        "0",
        "--invert",
        "--svg",
        "--output",
        masksvg,
    ]
    subprocess.call(potrace, shell=False)
