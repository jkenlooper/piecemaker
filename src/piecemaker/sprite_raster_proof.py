import os.path
import json
import time

from PIL import Image

from piecemaker.tools import toggle_adjacent_script as script

template = """
<!doctype html>
<html>
<head>
<title>Sprite Raster Proof - {scale}</title>
<link rel="stylesheet" media="all" href="sprite_p.css">
<link rel="stylesheet" media="all" href="sprite_raster.css">
<style>
{style}
</style>
</head>
<body>
<p>
Piece count: {piece_count}<br>
<button>
<label for="assembled">Toggle Assembled State</label>
</button>
</p>

<!-- All the piece div elements -->
<input type="checkbox" checked id="assembled" name="assembled">
<div class="container">
{pieces}
</div>
{script}
</body>
</html>"""

style = """
body {
background: black;
color: white;
}
.container {
position: relative;
display: flex;
flex-wrap: wrap;
}
.p {
transition: opacity linear 0.5s;
}
input[name=assembled]:checked + .container .p {
position: absolute;
}
.p.is-highlight,
.p:hover,
.p:active {
opacity: 0;
}
"""


def generate_sprite_raster_proof_html(pieces_json_file, output_dir, sprite_layout, scale):
    """Create a sprite proof showing how the image was cut. Should look like
    original."""

    with open(pieces_json_file, "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)

    im = Image.open(os.path.join(output_dir, "sprite_without_padding.png"))
    (bg_image_width, bg_image_height) = im.size
    im.close()

    pieces_style = []

    for (i, v) in sprite_layout.items():
        x = v[0]
        y = v[1]
        width = v[2]
        height = v[3]
        pieces_style.append(
            f".pc-{i}"
            + "{"
            + f"background-position:{x * -1}px {y * -1}px;"
            + f"width:{width}px;height:{height}px;"
            + "}"
        )

    cachebust = str(int(time.time()))
    with open(os.path.join(output_dir, "sprite_p.css"), "a") as css:
        css.write(
            ".p{"
            + f"background-image:url('sprite_without_padding.png?{cachebust}');"
            + f"background-size:{bg_image_width}px {bg_image_height}px;"
            + "}"
        )

    with open(os.path.join(output_dir, "sprite_raster.css"), "w") as css:
        css.write("".join(pieces_style))

    pieces_html = []
    for (i, v) in piece_bboxes.items():
        i = int(i)
        x = v[0]
        y = v[1]
        width = v[2] - v[0]
        height = v[3] - v[1]
        el = f"""
<div id='p-{i}' class='p pc-{i}' style='left:{x}px;top:{y}px;'></div>"""
        pieces_html.append(el)

    pieces = "".join(pieces_html)
    html = template.format(
        **{
            "scale": scale,
            "pieces": pieces,
            "piece_count": len(piece_bboxes.items()),
            "style": style,
            "script": script,
        }
    )

    f = open(os.path.join(output_dir, "sprite_raster_proof.html"), "w")
    f.write(html)
    f.close()
