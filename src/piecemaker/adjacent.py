import os
import json

from PIL import Image
from rtree import index


class Adjacent():
    """
    Narrow down potential adjacent pieces by their bounding boxes.
    """

    def __init__(self, directory, clips=None, by_overlap=True, overlap_threshold=20):
        # for each piece; list the adjacent pieces
        self.adjacent_pieces = {}

        self.pieces_info = {}
        if clips:
            pass
            # TODO: use scissors on a blank image ( not necessary to have a
            # real image here.
            # self.pieces_info =
        else:
            with open(os.path.join(directory, "pieces.json"), "r") as f:
                self.pieces_info = json.load(f)

        rtree_idx = index.Index(interleaved=True)

        for (piece_id, piece_bbox) in self.pieces_info.items():
            rtree_idx.insert(int(piece_id), piece_bbox)

        for (piece_id, piece_bbox) in self.pieces_info.items():
            expanded_piece_bbox = (
                piece_bbox[0] - 1,
                piece_bbox[1] - 1,
                piece_bbox[2] + 1,
                piece_bbox[3] + 1,
            )
            adjacent = list(map(str, rtree_idx.intersection(expanded_piece_bbox)))
            adjacent.remove(piece_id)
            if len(adjacent) == 0:
                adjacent = list(map(str, rtree_idx.nearest(piece_bbox, num_results=2)))
                adjacent.remove(piece_id)
            self.adjacent_pieces[piece_id] = adjacent

        if not by_overlap:
            return

        with open(
            os.path.join(directory, "piece_id_to_mask.json"), "r"
        ) as piece_id_to_mask_json:
            piece_id_to_mask = json.load(piece_id_to_mask_json)

        for (piece_id, adjacent_pieces) in self.adjacent_pieces.items():
            if len(adjacent_pieces) < 2:
                # pass any that may have been added by the nearest only
                continue
            mask_id = piece_id_to_mask[piece_id]
            target_piece_mask_im = Image.open(os.path.join(directory, "mask", f"{mask_id}.bmp"))
            target_piece_bbox = self.pieces_info[piece_id]
            no_overlap = []
            for adjacent_piece_id in adjacent_pieces:
                adjacent_piece_bbox = self.pieces_info[adjacent_piece_id]
                adjacent_mask_id = piece_id_to_mask[adjacent_piece_id]
                adjacent_piece_mask_im = Image.open(os.path.join(directory, "mask", f"{adjacent_mask_id}-padding.bmp"))
                width = max(target_piece_bbox[2], adjacent_piece_bbox[2]) - min(target_piece_bbox[0], adjacent_piece_bbox[0])
                height = max(target_piece_bbox[3], adjacent_piece_bbox[3]) - min(target_piece_bbox[1], adjacent_piece_bbox[1])
                target_piece_bbox_in_canvas = (
                    max(0, target_piece_bbox[0] - adjacent_piece_bbox[0]),
                    max(0, target_piece_bbox[1] - adjacent_piece_bbox[1]),
                    max(0, target_piece_bbox[0] - adjacent_piece_bbox[0]) + (target_piece_bbox[2] - target_piece_bbox[0]),
                    max(0, target_piece_bbox[1] - adjacent_piece_bbox[1]) + (target_piece_bbox[3] - target_piece_bbox[1]),
                )
                adjacent_piece_bbox_in_canvas = (
                    max(0, adjacent_piece_bbox[0] - target_piece_bbox[0]),
                    max(0, adjacent_piece_bbox[1] - target_piece_bbox[1]),
                    max(0, adjacent_piece_bbox[0] - target_piece_bbox[0]) + (adjacent_piece_bbox[2] - adjacent_piece_bbox[0]),
                    max(0, adjacent_piece_bbox[1] - target_piece_bbox[1]) + (adjacent_piece_bbox[3] - adjacent_piece_bbox[1]),
                )
                canvas = Image.new("1", (width, height), color=0)
                adjacent_mask_for_canvas = canvas.copy()
                adjacent_mask_for_canvas.paste(adjacent_piece_mask_im, box=(adjacent_piece_bbox_in_canvas[0] - 1, adjacent_piece_bbox_in_canvas[1] - 1))
                adjacent_piece_mask_im.close()
                target_mask_for_canvas = canvas.copy()
                canvas.close()
                target_mask_for_canvas.paste(target_piece_mask_im, box=(target_piece_bbox_in_canvas[0], target_piece_bbox_in_canvas[1]))

                # Get the count of overlapping pixels (last value in the
                # histogram) with the target piece and adjacent piece.
                overlap = target_mask_for_canvas.histogram(mask=adjacent_mask_for_canvas)[-1]
                adjacent_mask_for_canvas.close()
                target_mask_for_canvas.close()
                if overlap <= overlap_threshold:
                    no_overlap.append(adjacent_piece_id)

            target_piece_mask_im.close()

            for n in no_overlap:
                adjacent_pieces.remove(n)

            # Make sure that there is still at least one adjacent piece in case
            # all the adjacent pieces had too small of overlapping pieces.
            if len(adjacent_pieces) == 0:
                adjacent = list(map(str, rtree_idx.nearest(target_piece_bbox, num_results=2)))
                adjacent.remove(piece_id)
                adjacent_pieces.extend(adjacent)
