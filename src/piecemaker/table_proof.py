import os.path
import json
import shutil

from PIL import Image

#from piecemaker.tools import toggle_adjacent_script as script

BLEED = 2
HALF_BLEED = BLEED * 0.5

template = """
<!doctype html>
<html>
<head>
<title>Table Proof - {scale}</title>
<style>
{style}
</style>
</head>
<body>
<p class="piece-count">
Piece count: {piece_count}<br>
</p>
<div class="controls">
<button>
<label for="assembled">Toggle Assembled State</label>
</button>
<input type="checkbox" id="assembled" name="assembled">
<button id="zoom-in">+</button>
<button id="zoom-out">-</button>
</div>

<div class="container">
    <canvas class="piecemaker-table" id="piecemaker-table" data-size="{scale}">
        <img id="piecemaker-sprite_without_padding" style="image-rendering:crisp-edges;" width="{sprite_without_padding_width}" height="{sprite_without_padding_height}" src="size-{scale}/sprite_without_padding.png">

        <!-- TODO: Option to switch to clip paths
        <img id="piecemaker-sprite_with_padding" style="image-rendering:crisp-edges;" width="{sprite_with_padding_width}" height="{sprite_with_padding_height}" src="size-{scale}/sprite_with_padding.jpg">
        {sprite_clip_paths_svg}
        -->
    </canvas>
</div>

    <script src="table_proof_canvas.js"></script>
</body>
</html>"""


style = (
    """
body {
background: rgb(20,20,20);
color: white;
margin: 0;
padding: 0;
}
.piece-count {
}
.container {
width: 100vw;
height: 100vh;
overflow: hidden;
}
.controls {
display: flex;
}
.piecemaker-table {
image-rendering: -moz-crisp-edges;
image-rendering: -webkit-crisp-edges;
image-rendering: pixelated;
image-rendering: crisp-edges;
}
"""
)


def generate_table_proof_html(mydir):
    """Table proof"""
    index_json_file = os.path.join(mydir, "index.json")

    shutil.copy(os.path.join(os.path.dirname(__file__), "table_proof_canvas.js"), os.path.join(mydir, "table_proof_canvas.js"))

    with open(index_json_file, "r") as index_json:
        piecemaker_index = json.load(index_json)

    scale = piecemaker_index['full_size']
    full_size_dir = os.path.join(mydir, f"size-{scale}")

    pieces_json_file = os.path.join(full_size_dir, "pieces.json")
    with open(pieces_json_file, "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)

    sprite_clip_paths_svg = ""
    #sprite_clip_paths_svg_file = os.path.join(full_size_dir, "sprite_clip_paths.svg")
    #with open(sprite_clip_paths_svg_file, "r") as f:
    #    sprite_clip_paths_svg = f.read().replace("""<?xml version="1.0" encoding="utf-8"?>""", "")

    im = Image.open(os.path.join(full_size_dir, "sprite_with_padding.jpg"))
    (sprite_with_padding_width, sprite_with_padding_height) = im.size
    im.close()
    im = Image.open(os.path.join(full_size_dir, "sprite_without_padding.png"))
    (sprite_without_padding_width, sprite_without_padding_height) = im.size
    im.close()

    html = template.format(
        **{
            "scale": scale,
            "piece_count": len(piece_bboxes.items()),
            "style": style,
            "sprite_clip_paths_svg": sprite_clip_paths_svg,
            "sprite_with_padding_width": sprite_with_padding_width,
            "sprite_with_padding_height": sprite_with_padding_height,
            "sprite_without_padding_width": sprite_without_padding_width,
            "sprite_without_padding_height": sprite_without_padding_height,
            "table_width": piecemaker_index["table_width"],
            "table_height": piecemaker_index["table_height"],
        }
    )

    f = open(os.path.join(mydir, "table_proof.html"), "w")
    f.write(html)
    f.close()
