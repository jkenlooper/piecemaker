import os

from PIL import Image

from piecemaker.base import JigsawPieceClipsSVG
from piecemaker.tools import gridify, cap_dimensions


def create_lines_svg(
    output_dir,
    minimum_piece_size,
    maximum_piece_size,
    width,
    height,
    number_of_pieces,
    imagefile,
    variant,
):
    # create a grid of puzzle pieces in svg

    _minimum_piece_size = max(
        minimum_piece_size
        + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
        minimum_piece_size
        + (abs((height % minimum_piece_size) / minimum_piece_size - 1)),
    )
    _minimum_piece_size = max(
        _minimum_piece_size
        + (abs((width % _minimum_piece_size) / _minimum_piece_size - 1)),
        _minimum_piece_size
        + (abs((height % _minimum_piece_size) / _minimum_piece_size - 1)),
    )
    _minimum_piece_size = max(
        _minimum_piece_size
        + (abs((width % _minimum_piece_size) / _minimum_piece_size - 1)),
        _minimum_piece_size
        + (abs((height % _minimum_piece_size) / _minimum_piece_size - 1)),
    )
    print(f"minimum_piece_size {_minimum_piece_size}")
    (rows, cols, piece_width, piece_height) = gridify(
        width, height, number_of_pieces, _minimum_piece_size
    )
    _imagefile = imagefile
    if (
        maximum_piece_size != 0
        and maximum_piece_size + _minimum_piece_size < max(piece_width, piece_height)
    ):
        im = Image.open(_imagefile)
        mxpx = (maximum_piece_size * maximum_piece_size) * (rows * cols)
        (width, height) = cap_dimensions(width, height, mxpx)
        im = im.resize((width, height))
        (width, height) = im.size
        _imagefile = os.path.join(output_dir, f"resized-{os.path.basename(_imagefile)}")
        im.save(_imagefile)
        im.close()
    jpc = JigsawPieceClipsSVG(
        width=width,
        height=height,
        pieces=number_of_pieces,
        minimum_piece_size=_minimum_piece_size,
        maximum_piece_size=maximum_piece_size,
        variant=variant,
    )

    svgfile = os.path.join(output_dir, "lines.svg")
    f = open(svgfile, "w")
    f.write(jpc.svg())
    f.close()

    return (_imagefile, jpc)
