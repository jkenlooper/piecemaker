import os
import json
import shutil
from glob import iglob

from PIL import Image

from piecemaker.tools import scale_down_imgfile, potrace_to_svg
from piecemaker.cut_proof import generate_cut_proof_html


def reduce_size(scale, minimum_scale, output_dir, scaled_images):
    factor = scale / minimum_scale
    minimum_scaled_dir = os.path.join(output_dir, f"size-{minimum_scale}")
    scaled_dir = os.path.join(output_dir, f"size-{scale}")

    shutil.copytree(minimum_scaled_dir, scaled_dir)

    for filename in [
        f"cut_proof-{image_index}.html" for image_index in range(len(scaled_images))
    ]:
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
        bbox[0] = round(bbox[0] * factor, 5)
        bbox[1] = round(bbox[1] * factor, 5)
        bbox[2] = bbox[0] + width
        bbox[3] = bbox[1] + height

        bbox[7] = bbox[7] * factor
        bbox[8] = bbox[8] * factor

        bbox[9] = round(bbox[9] * factor, 5)
        bbox[10] = round(bbox[10] * factor, 5)
        bbox[11] = round(bbox[11] * factor, 5)
        bbox[12] = round(bbox[12] * factor, 5)
    with open(os.path.join(scaled_dir, "pieces.json"), "w") as pieces_json:
        json.dump(piece_bboxes, pieces_json)

    os.mkdir(os.path.join(scaled_dir, "vector"))
    for piece in iglob(os.path.join(scaled_dir, "mask", "*.bmp")):
        potrace_to_svg(piece, os.path.join(scaled_dir, "vector"))

    # Use the cut proof to check the cut on all images.
    for image_index, image in enumerate(scaled_images):
        generate_cut_proof_html(
            pieces_json_file=os.path.join(scaled_dir, "pieces.json"),
            output_dir=scaled_dir,
            scale=factor,
            image_index=image_index,
        )
