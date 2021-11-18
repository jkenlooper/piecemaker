import os
import json
import base64
from glob import iglob

import svgwrite
from bs4 import BeautifulSoup
from PIL import Image
from glue.managers.simple import SimpleManager


def generate_data_uris(raster_dir, output_dir):
    data_uri_dir = os.path.join(output_dir, "data_uri")
    os.mkdir(data_uri_dir)
    for piece in iglob(os.path.join(raster_dir, "*.png")):
        with open(piece, "rb") as img:
            with open(os.path.join(data_uri_dir, os.path.basename(piece) + ".b64"), "wb") as b64:
                b64.write(base64.standard_b64encode(img.read()))


def generate_sprite_without_padding_layout(raster_dir, output_dir):
    " create the sprite using glue "
    sprite_manager = SimpleManager(
        source=raster_dir,
        css_namespace="pc",
        css_pseudo_class_separator="__",
        css_sprite_namespace="",
        css_url="",
        html=False,
        ratios="1",
        follow_links=False,
        quiet=True,
        recursive=False,
        force=True,
        algorithm="square",
        algorithm_ordering="maxside",
        crop=False,
        padding="0",
        margin="0",
        png8=False,
        retina=False,
        output=output_dir,
        img_dir=output_dir,
        css_dir=output_dir,
        html_dir=output_dir,
        css_cachebuster=True,
        css_cachebuster_filename=False,
        css_cachebuster_only_sprites=False,
        css_separator="-",
        enabled_formats=["img"],
    )
    sprite_manager.process()

    sprite = sprite_manager.sprites[0]

    sprite_layout = {}
    for image in sprite.images:
        filename, ext = image.filename.rsplit(".", 1)
        sprite_layout[int(filename)] = (image.x, image.y, image.width, image.height)

    with open(
        os.path.join(output_dir, "sprite_without_padding_layout.json"), "w"
    ) as sprite_layout_json:
        json.dump(sprite_layout, sprite_layout_json)

    raster_png = sprite.sprite_path()
    os.rename(raster_png, os.path.join(output_dir, "sprite_without_padding.png"))

    return sprite_layout


def generate_sprite_with_padding_layout(raster_dir, output_dir):
    " create the sprite using glue "
    sprite_manager = SimpleManager(
        source=raster_dir,
        css_namespace="pc",
        css_pseudo_class_separator="__",
        css_sprite_namespace="",
        css_url="",
        html=False,
        ratios="1",
        follow_links=False,
        quiet=True,
        recursive=False,
        force=True,
        algorithm="square",
        algorithm_ordering="maxside",
        crop=False,
        padding="0",
        margin="0",
        png8=False,
        retina=False,
        output=output_dir,
        img_dir=output_dir,
        css_dir=output_dir,
        html_dir=output_dir,
        css_cachebuster=True,
        css_cachebuster_filename=False,
        css_cachebuster_only_sprites=False,
        css_separator="-",
        enabled_formats=["img"],
    )
    sprite_manager.process()

    sprite = sprite_manager.sprites[0]

    sprite_layout = {}
    for image in sprite.images:
        filename, ext = image.filename.rsplit(".", 1)
        sprite_layout[int(filename)] = (image.x, image.y, image.width, image.height)

    with open(
        os.path.join(output_dir, "sprite_with_padding_layout.json"), "w"
    ) as sprite_layout_json:
        json.dump(sprite_layout, sprite_layout_json)

    raster_png = sprite.sprite_path()

    # No warning about possible DecompressionBombWarning since the png
    # here has been generated on this side.
    Image.MAX_IMAGE_PIXELS = None

    png_sprite = Image.open(raster_png)
    jpg_sprite = png_sprite.convert("RGB")
    png_sprite.close()
    os.unlink(raster_png)
    jpg_sprite_file_name = os.path.join(output_dir, "sprite_with_padding.jpg")
    jpg_sprite.save(jpg_sprite_file_name)
    jpg_sprite.close()

    return sprite_layout


def generate_sprite_svg_clip_paths(
    output_dir,
    scale,
    pieces_json_file,
    vector_dir,
):
    " parse the individual piece svg's and create the svg. "

    with open(
        os.path.join(output_dir, "piece_id_to_mask.json"), "r"
    ) as piece_id_to_mask_json:
        piece_id_to_mask = json.load(piece_id_to_mask_json)

    with open(pieces_json_file, "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)

    dwg = svgwrite.Drawing(
        size=(0, 0),
    )

    for (i, piece_bbox) in piece_bboxes.items():
        clip_path = dwg.defs.add(dwg.clipPath())
        clip_path["id"] = f"piece-mask-{scale}-{i}"
        clip_path["shape-rendering"] = "crispEdges"
    sprite_svg_clip_paths = BeautifulSoup(dwg.tostring(), "xml")

    for (i, piece_bbox) in piece_bboxes.items():
        mask_id = piece_id_to_mask[i]
        piece_svg = os.path.join(vector_dir, f"{mask_id}.svg")
        piece_soup = BeautifulSoup(open(piece_svg), "xml")
        svg = piece_soup.svg
        path = None
        select_first_g = svg.select(':root > g', limit=1)
        if len(select_first_g):
            transform = select_first_g[0].get("transform", None)
            select_path = select_first_g[0].select(':root > g > path', limit=1)
            if len(select_path):
                path = select_path[0]
                if transform:
                    path["transform"] = transform
        else:
            # TODO: This branch hasn't been tested.
            select_path = svg.select(':root > *', limit=1)
            if len(select_path):
                path = select_path[0]

        piece_mask_tag = sprite_svg_clip_paths.defs.find("clipPath", id=f"piece-mask-{scale}-{i}")
        if piece_mask_tag:
            piece_mask_tag.append(path)

    with open(os.path.join(output_dir, "sprite_clip_paths.svg"), "w") as out:
        out.write(sprite_svg_clip_paths.decode(formatter=None))

def generate_sprite_svg_fragments(
    sprite_layout,
    jpg_sprite_file_name,
    scaled_image,
    output_dir,
    scale,
):
    " parse the individual piece svg's and create the svg fragments. "

    dwg = svgwrite.Drawing(
        size=(0, 0),
    )

    common_path = os.path.commonprefix([scaled_image, output_dir])
    relative_scaled_image = jpg_sprite_file_name[len(common_path) + 1 :]
    source_image = dwg.defs.add(
        dwg.image(
            relative_scaled_image,
            id=f"source-image-{scale}",
        )
    )

    for (i, preview_offset) in sprite_layout.items():
        piece_fragment = dwg.defs.add(dwg.svg())
        piece_fragment["id"] = f"piece-fragment-{scale}-{i}"

        piece_fragment.viewbox(
            minx=preview_offset[0],
            miny=preview_offset[1],
            width=preview_offset[2],
            height=preview_offset[3],
        )
        piece_fragment["width"] = preview_offset[2]
        piece_fragment["height"] = preview_offset[3]

        piece_fragment.add(dwg.use(source_image))

    sprite_svg_fragments = BeautifulSoup(dwg.tostring(), "xml")

    with open(os.path.join(output_dir, "sprite_fragments.svg"), "w") as out:
        out.write(sprite_svg_fragments.decode(formatter=None))
