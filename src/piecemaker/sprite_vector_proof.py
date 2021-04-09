import os.path
import json

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
</head>
<body>
<p>
Piece count: {piece_count}
</p>

<!-- Contents of sprite.svg file inlined -->
{sprite_svg}

<!-- All the piece div elements -->
<div class="container">
{pieces}
</div>


</body>
</html>"""

style = """
body {
background: black;
color: white;
}
.container {
position: relative;
}
.pc {
position: absolute;
transition: opacity linear 0.5s;
}
.pc:hover,
.pc:active {
opacity: 0;
}
    """


def generate_sprite_vector_proof_html(pieces_json_file, sprite_svg_file, output_dir, sprite_layout, scale):
    """Create a sprite vector proof showing how the image was cut. Should look like
    original."""

    with open(pieces_json_file, "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)

    with open(sprite_svg_file, "r") as f:
        sprite_svg = f.read().replace(
            """<?xml version="1.0" encoding="utf-8"?>""", ""
        )

    pieces_html = []
    piece_style = []
    hb = HALF_BLEED
    for (i, piece_bbox) in piece_bboxes.items():
        i = int(i)
        x = piece_bbox[0]
        y = piece_bbox[1]
        # TODO: store and retrieve mask-padding dimensions instead of using
        # sprite_layout.
        width = sprite_layout[i][2]
        height = sprite_layout[i][3]

        el = f"""
<div id="pc-{scale}-{i}" class="pc" style="left:{x}px;top:{y}px;">
<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="margin-left:-{hb}px;margin-top:-{hb}px">
<use xlink:href="#piece-fragment-{scale}-{i}"/>
</svg>
</div>"""
        pieces_html.append(el)
        clip_path_style = (
            "{" + f"clip-path: url(#piece-mask-{scale}-{i});" + "}"
        )
        piece_style.append(f"[id=pc-{scale}-{i}] {clip_path_style}")

    pieces = "".join(pieces_html)
    html = template.format(
        **{
            "scale": scale,
            "pieces": pieces,
            "piece_count": len(piece_bboxes.items()),
            "style": style + "".join(piece_style),
            "sprite_svg": sprite_svg,
        }
    )

    f = open(os.path.join(output_dir, "sprite_vector_proof.html"), "w")
    f.write(html)
    f.close()
