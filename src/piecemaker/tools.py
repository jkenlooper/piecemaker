import subprocess
import os
import os.path
import decimal
import math

from PIL import Image


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


def scale_down_imgfile(imgfile, factor):
    im = Image.open(imgfile)
    (width, height) = im.size
    width = max(1, round(width * factor))
    height = max(1, round(height * factor))
    im = im.resize((width, height))
    im.save(imgfile)
    im.close()


def cap_dimensions(width, height, max_pixels):
    "https://stackoverflow.com/questions/10106792/resize-image-by-pixel-amount"
    pixels = width * height
    if pixels <= max_pixels:
        return (width, height)
    ratio = float(width) / height
    scale = (float(pixels) / max_pixels) ** (width / (height * 2))
    height2 = round(float(height) / scale)
    width2 = round(ratio * height2)
    return (width2, height2)


def gridify(width, height, pieces, minimum_piece_size, add_more_pieces=True):
    """
    Based on area of the box, determine the count of rows and cols that
    will meet the number of pieces.
    """
    area = decimal.Decimal(width * height)
    s = area.sqrt()
    n = decimal.Decimal(pieces).sqrt()
    piece_size = max(float(s / n), minimum_piece_size)
    # print(f"gridify {piece_size}")
    # use math.ceil to at least have the target count of pieces
    rounder = math.ceil
    if not add_more_pieces:
        rounder = math.floor
    rows = int(rounder(height / piece_size))
    cols = int(rounder(width / piece_size))
    piece_width = float(width) / float(cols)
    piece_height = float(height) / float(rows)
    return (rows, cols, piece_width, piece_height)
