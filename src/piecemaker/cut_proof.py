import os.path
import json
import time

from piecemaker.tools import toggle_adjacent_script as script

template = """
<!doctype html>
<html>
<head>
<title>Cut Proof - {scale}</title>
<link rel="stylesheet" media="all" href="sprite_p.css">
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
background-image: none;
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


def generate_cut_proof_html(pieces_json_file, output_dir, scale):
    """Create a cut proof showing how the image was cut. Should look like
    original."""

    with open(pieces_json_file, "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)

    cachebust = str(int(time.time()))
    pieces_html = []
    for (i, v) in piece_bboxes.items():
        i = int(i)
        x = v[0]
        y = v[1]
        width = v[2] - v[0]
        height = v[3] - v[1]
        el = "".join([
            f"<div id='p-{i}' class='p pc-{i}' style='left:{x}px;top:{y}px;'>",
            f"<img class='p-img' src='raster/{i}.png?{cachebust}' width='{width}' height='{height}'>",
            "</div>"
        ])
        pieces_html.append(el)

    with open(os.path.join(output_dir, "sprite_p.css"), "a") as css:
        css.write(".p-img{display:block;}")

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

    f = open(os.path.join(output_dir, "cut_proof.html"), "w")
    f.write(html)
    f.close()
