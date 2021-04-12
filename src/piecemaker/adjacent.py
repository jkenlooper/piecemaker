from builtins import object
import os
import json


class Adjacent(object):
    """
    Narrow down potential adjacent pieces by their bounding boxes.
    """

    def num_points(self, x):
        if x < 0:  # none
            return -1
        if x > 0:  # segment
            return 1
        return 0  # point

    def are_adjacent(self, bbox1, bbox2):
        # expand bbox2 size slightly by one
        expanded_bbox2 = (
            max(0, bbox2[0] - 1),
            max(0, bbox2[1] - 1),
            bbox2[2] + 1,
            bbox2[3] + 1,
        )
        nx = self.num_points(
            min(bbox1[2], expanded_bbox2[2]) - max(bbox1[0], expanded_bbox2[0])
        )
        ny = self.num_points(
            min(bbox1[3], expanded_bbox2[3]) - max(bbox1[1], expanded_bbox2[1])
        )
        if nx == -1 or ny == -1:
            return False
        if nx == 0 or ny == 0:
            return False
        return True

    def __init__(self, directory, clips=None, by_overlap=False, ignore_corners=True):
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

        # TODO: create index to optimize this.
        for (piece_id, piece_bbox) in self.pieces_info.items():
            adjacent = []
            for (other_piece_id, other_piece_bbox) in self.pieces_info.items():
                if piece_id == other_piece_id:
                    continue
                if self.are_adjacent(piece_bbox, other_piece_bbox):
                    adjacent.append(other_piece_id)
            self.adjacent_pieces[piece_id] = adjacent

        if ignore_corners:
            filtered_adjacent_pieces = {}
            for target_id, target_adjacent_list in self.adjacent_pieces.items():
                filtered_adjacent_pieces[target_id] = self.filter_out_corner_adjacent(target_id, target_adjacent_list)
            self.adjacent_pieces = filtered_adjacent_pieces

        if by_overlap:
            pass
            # TODO: further filter out the adjacent pieces by doing the
            # overlapping  mask test.

    def filter_out_corner_adjacent(self, target_id, target_adjacent_list):
        target_bbox = self.pieces_info[target_id]  # [0, 0, 499, 500]
        target_center_x = target_bbox[0] + int(
            round((target_bbox[2] - target_bbox[0]) * 0.5)
        )
        target_center_y = target_bbox[1] + int(
            round((target_bbox[3] - target_bbox[1]) * 0.5)
        )
        filtered_adjacent_list = []
        for adjacent_id in target_adjacent_list:
            adjacent_bbox = self.pieces_info[adjacent_id]  # [0, 347, 645, 996]
            left = adjacent_bbox[2] < target_center_x #target_bbox[0]
            top = adjacent_bbox[3] < target_center_y #target_bbox[1]
            right = adjacent_bbox[0] > target_center_x #target_bbox[2]
            bottom = adjacent_bbox[1] > target_center_y #target_bbox[3]
            is_top_left = top and left
            is_top_right = top and right
            is_bottom_left = bottom and left
            is_bottom_right = bottom and right
            if not is_top_left and not is_top_right and not is_bottom_left and not is_bottom_right:
                filtered_adjacent_list.append(adjacent_id)

        # TODO: Some corner adjacent pieces are not being filtered out.
        if len(filtered_adjacent_list) > 4:
            print(f"missed corners: {filtered_adjacent_list}")
        if len(filtered_adjacent_list) < 2:
            print(f"suspect: {filtered_adjacent_list}")

        return filtered_adjacent_list
