import subprocess
import os
import os.path
import decimal
import math
from tempfile import mkstemp
from shutil import copyfile
import json

from PIL import Image


toggle_adjacent_script = """
<script>
/* Toggle the adjacent pieces next to the one that is clicked. */
fetch("/adjacent.json")
.then(response => response.json())
.then(adjacent => {
    document.addEventListener('click', (event) => {
        for (let target = event.target; target && target != this; target = target.parentNode) {
            if (target.classList && target.classList.contains('p')) {
                const $piece = target;
                const piece_id = $piece.getAttribute("id").replace("p-", "");
                const adjacent_piece_ids = adjacent[piece_id];
                adjacent_piece_ids
                    .map(pc => {return document.getElementById("p-"+pc)})
                    .map(el => el.classList.toggle('is-highlight'))
                break;
            }
        }
    }, false);
});
</script>
"""


def rasterize_svgfile(svgfile, width, height):
    """
    Converts a svg file to png file with same basename.
    """

    output_dir = os.path.dirname(svgfile)
    name = os.path.basename(svgfile)
    (root, ext) = os.path.splitext(name)
    pngfile = os.path.join(output_dir, f"{root}.png")

    # Skip B603; width, height, pngfile, and svgfile are safe inputs.
    subprocess.run(
        [
            "rsvg-convert",
            "--width",
            str(width),
            "--height",
            str(height),
            "--unlimited",
            "--output",
            pngfile,
            "--background-color=white",
            svgfile,
        ]
    )  # nosec B603

    return pngfile


def potrace_to_svg(trimmedbmp, output_dir):
    """
    Convert the mask into a svg file.
    """
    mask_bmp = os.path.basename(trimmedbmp)
    (mask_name, ext) = os.path.splitext(mask_bmp)

    masksvg = os.path.join(output_dir, f"{mask_name}.svg")
    # TODO: suppress speckle size with --turdsize 10
    # Skip B603; trimmedbmp, and masksvg are safe inputs.
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
        "--flat",
        "--svg",
        "--output",
        masksvg,
    ]
    subprocess.run(potrace, check=True)  # nosec B603


def potrace_to_polygon(trimmedbmp, output_dir, min_size=10, target_factor=0.10):
    """
    Convert the mask into a geojson file.
    Set the target_factor to a value of 0.10 to reduce the number of polygon points.
    """
    fd, tmpbmp = mkstemp(suffix=".bmp")
    os.close(fd)

    # Reduce the image to 10% to have less polygons
    factor = target_factor
    if target_factor < 1.0:
        im = Image.open(trimmedbmp)
        (width, height) = im.size
        factor = max(target_factor, min_size / max(width, height))
        reduced_width = max(1, round(width * factor))
        reduced_height = max(1, round(height * factor))
        im = im.resize((reduced_width, reduced_height))
        im.save(tmpbmp)
        im.close()
    else:
        copyfile(trimmedbmp, tmpbmp)

    mask_bmp = os.path.basename(trimmedbmp)
    (mask_name, ext) = os.path.splitext(mask_bmp)

    mask_geojson_file = os.path.join(output_dir, f"{mask_name}.geojson")
    # Skip B603; tmpbmp, and mask_geojson_file are safe inputs.
    potrace = [
        "potrace",
        tmpbmp,
        "--turnpolicy",
        "majority",
        "--alphamax",
        "0",
        "--turdsize",
        "10",
        "--invert",
        "--flat",
        "--backend",
        "geojson",
        "--output",
        mask_geojson_file,
    ]
    subprocess.run(potrace, check=True)  # nosec B603
    os.unlink(tmpbmp)

    with open(mask_geojson_file, mode="rb") as f:
        mask_geojson = json.load(f)

    # Scale the coordinates and bbox from the geojson to match the piece size.
    if target_factor < 1.0:

        def scale_up_coordinates(coordinates):
            for index, item in enumerate(coordinates):
                if isinstance(item, list):
                    scale_up_coordinates(item)
                elif isinstance(item, (int, float)):
                    coordinates[index] = round(item / factor, 2)

        def scale_up_bbox(bbox):
            bbox = [round(x / factor, 2) for x in bbox]

        def scale_up(obj):
            for k, v in obj.items():
                if isinstance(v, list):
                    if k == "coordinates":
                        scale_up_coordinates(v)
                    elif k == "bbox":
                        scale_up_bbox(v)
                    else:
                        for item in v:
                            if isinstance(item, dict):
                                scale_up(item)
                elif isinstance(v, dict):
                    scale_up(v)

        scale_up(mask_geojson)

    with open(mask_geojson_file, mode="w") as f:
        json.dump(mask_geojson, f, separators=(",", ":"))


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
    scale = math.sqrt(float(pixels) / max_pixels)
    height2 = int(float(height) / scale)
    width2 = int(ratio * height / scale)
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
