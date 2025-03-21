import os
import json
import shutil
from glob import iglob

from PIL import Image

from piecemaker.tools import scale_down_imgfile, potrace
from piecemaker.cut_proof import generate_cut_proof_html


def reduce_size(scale, minimum_scale, output_dir, scaled_images):
    factor = scale / minimum_scale
    minimum_scaled_dir = os.path.join(output_dir, f"size-{minimum_scale}")
    scaled_dir = os.path.join(output_dir, f"size-{scale}")

    shutil.copytree(minimum_scaled_dir, scaled_dir)

    for filename in [
        "masks.json",
        #"sprite_clip_paths.svg",
        #"sprite_fragments.svg",
        #"sprite_raster.css",
        #"sprite_vector.css",
        #"sprite_raster_proof-0.html",
        #"sprite_vector_proof.html",
        #"sprite_with_padding_layout.json",
        #"sprite_without_padding_layout.json",
    ] + [f"cut_proof-{image_index}.html" for image_index in range(len(scaled_images))]:
        os.unlink(os.path.join(scaled_dir, filename))
    shutil.rmtree(os.path.join(scaled_dir, "vector"))

    for ext in [".jpg", ".png", ".bmp"]:
        for imgfile in iglob(f"{scaled_dir}/**/*{ext}", recursive=True):
            scale_down_imgfile(imgfile, factor)

    with open(os.path.join(scaled_dir, "pieces.json"), "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)
    with open(
        os.path.join(scaled_dir, "piece_id_to_mask.json"), "r"
    ) as piece_id_to_mask_json:
        piece_id_to_mask = json.load(piece_id_to_mask_json)
    for i, bbox in piece_bboxes.items():
        im = Image.open(os.path.join(scaled_dir, "mask", f"{piece_id_to_mask[i]}.bmp"))
        (width, height) = im.size
        im.close()
        bbox[0] = round(bbox[0] * factor)
        bbox[1] = round(bbox[1] * factor)
        bbox[2] = bbox[0] + width
        bbox[3] = bbox[1] + height
    with open(os.path.join(scaled_dir, "pieces.json"), "w") as pieces_json:
        json.dump(piece_bboxes, pieces_json)

    os.mkdir(os.path.join(scaled_dir, "vector"))
    for piece in iglob(os.path.join(scaled_dir, "mask", "*.bmp")):
        potrace(piece, os.path.join(scaled_dir, "vector"))

    # Use the cut proof to check the cut on all images.
    for image_index, image in enumerate(scaled_images):
        generate_cut_proof_html(
            pieces_json_file=os.path.join(scaled_dir, "pieces.json"),
            output_dir=scaled_dir,
            scale=scale,
            image_index=image_index,
        )
