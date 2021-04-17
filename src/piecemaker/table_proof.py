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
Piece count: {piece_count}
</p>

<div class="container">
    <canvas id="piecemaker-table" width="{table_width}" height="{table_height}">
        <img id="piecemaker-sprite_with_padding" width="{sprite_with_padding_width}" height="{sprite_with_padding_height}" src="size-{scale}/sprite_with_padding.jpg">

        {sprite_clip_paths_svg}

        {pieces}
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
position: absolute;
z-index: 10;
background-color: rgba(0,0,0,0.9);
}
.container {
/* fails on larger puzzles
width: 100vw;
height: 100vh;
overflow: hidden;
*/
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

    sprite_clip_paths_svg = "<!-- TODO: Use sprite_with_padding.jpg and clip paths instead of the above inlined images. -->"
    #sprite_clip_paths_svg_file = os.path.join(full_size_dir, "sprite_clip_paths.svg")
    #with open(sprite_clip_paths_svg_file, "r") as f:
    #    sprite_clip_paths_svg = f.read().replace("""<?xml version="1.0" encoding="utf-8"?>""", "")

    with open(
        os.path.join(full_size_dir, "sprite_with_padding_layout.json"), "r"
    ) as sprite_layout_json:
        sprite_layout = json.load(sprite_layout_json)

    pieces_html = []
    for (i, piece_bbox) in piece_bboxes.items():
        #x = piece_bbox[0]
        #y = piece_bbox[1]
        width = piece_bbox[2] - piece_bbox[0]
        height = piece_bbox[3] - piece_bbox[1]
        with open(os.path.join(full_size_dir, "data_uri", f"{i}.png.b64"), "r") as f:
            b64 = f.read()

        el = f"""
<img id="p-img-{i}" width="{width}" height="{height}" src="data:image/png;base64,{b64}">"""
        pieces_html.append(el)

    im = Image.open(os.path.join(full_size_dir, "sprite_with_padding.jpg"))
    (sprite_with_padding_width, sprite_with_padding_height) = im.size
    im.close()

    pieces = "".join(pieces_html)
    html = template.format(
        **{
            "scale": scale,
            "pieces": pieces,
            "piece_count": len(piece_bboxes.items()),
            "style": style,
            "sprite_clip_paths_svg": sprite_clip_paths_svg,
            "sprite_with_padding_width": sprite_with_padding_width,
            "sprite_with_padding_height": sprite_with_padding_height,
            "table_width": piecemaker_index["table_width"],
            "table_height": piecemaker_index["table_height"],
        }
    )

    f = open(os.path.join(mydir, "table_proof.html"), "w")
    f.write(html)
    f.close()
