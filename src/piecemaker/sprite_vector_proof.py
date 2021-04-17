import os.path
import json

from piecemaker.tools import toggle_adjacent_script as script

BLEED = 2
HALF_BLEED = BLEED * 0.5

template = """
<!doctype html>
<html>
<head>
<title>Sprite Vector Proof - {scale}</title>
<style>
{style}
</style>
<link rel="stylesheet" media="all" href="sprite_p.css">
<link rel="stylesheet" media="all" href="sprite_vector.css">
</head>
<body>
<p>
Piece count: {piece_count}<br>
<button>
<label for="assembled">Toggle Assembled State</label>
</button>
</p>

<!-- Contents of sprite_fragments.svg file inlined -->
{sprite_fragments_svg}

<!-- Contents of sprite_clip_paths.svg file inlined -->
{sprite_clip_paths_svg}

<!-- All the piece div elements -->
<input type="checkbox" checked id="assembled" name="assembled">
<div class="container">
{pieces}
</div>

{script}
</body>
</html>"""


style = (
    """
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
    + ".p-f {"
    + f"margin-left:-{HALF_BLEED}px;margin-top:-{HALF_BLEED}px;"
    + "display: block;}"
)


def generate_sprite_vector_proof_html(
    mydir, output_dir, sprite_layout, scale
):
    """Create a sprite vector proof showing how the image was cut. Should look like
    original."""
    pieces_json_file = os.path.join(mydir, "pieces.json")
    sprite_fragments_svg_file = os.path.join(mydir, "sprite_fragments.svg")
    sprite_clip_paths_svg_file = os.path.join(mydir, "sprite_clip_paths.svg")

    with open(pieces_json_file, "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)

    with open(sprite_fragments_svg_file, "r") as f:
        sprite_fragments_svg = f.read().replace("""<?xml version="1.0" encoding="utf-8"?>""", "")
    with open(sprite_clip_paths_svg_file, "r") as f:
        sprite_clip_paths_svg = f.read().replace("""<?xml version="1.0" encoding="utf-8"?>""", "")

    pieces_html = []
    pieces_style = []
    for (i, piece_bbox) in piece_bboxes.items():
        i = int(i)
        x = piece_bbox[0]
        y = piece_bbox[1]
        # TODO: store and retrieve mask-padding dimensions instead of using
        # sprite_layout?
        width = sprite_layout[i][2]
        height = sprite_layout[i][3]

        el = f"""
<div id="p-{i}" class="p pc-{i}" style="left:{x}px;top:{y}px;">
<svg class="p-f" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<use xlink:href="#piece-fragment-{scale}-{i}"/>
</svg>
</div>"""
        pieces_html.append(el)
        pieces_style.append(
            f".pc-{i}"
            + "{"
            + f"clip-path:url(#piece-mask-{scale}-{i});"
            + "}"
        )

    with open(os.path.join(output_dir, "sprite_p.css"), "a") as css:
        css.write(
            ".p-f {"
            + f"margin-left:-{HALF_BLEED}px;margin-top:-{HALF_BLEED}px;"
            + "display: block;}"
        )

    with open(os.path.join(output_dir, "sprite_vector.css"), "w") as css:
        css.write("".join(pieces_style))

    pieces = "".join(pieces_html)
    html = template.format(
        **{
            "scale": scale,
            "pieces": pieces,
            "piece_count": len(piece_bboxes.items()),
            "style": style,
            "sprite_clip_paths_svg": sprite_clip_paths_svg,
            "sprite_fragments_svg": sprite_fragments_svg,
            "script": script,
        }
    )

    f = open(os.path.join(output_dir, "sprite_vector_proof.html"), "w")
    f.write(html)
    f.close()
