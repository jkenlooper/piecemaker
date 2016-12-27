import os
import json

class Adjacent(object):
    """
    Narrow down potential adjacent pieces by their bounding boxes.
    """
    def num_points(self, x):
        if x < 0: # none
            return -1
        if x > 0: # segment
            return 1
        return 0 # point
    def are_adjacent(self, bbox1, bbox2):
        # expand bbox2 size slightly by one
        expanded_bbox2 = (max(0, bbox2[0]-1), max(0, bbox2[1]-1), bbox2[2]+1, bbox2[3]+1)
        nx = self.num_points(
                min(bbox1[2], expanded_bbox2[2]) -
                max(bbox1[0], expanded_bbox2[0]))
        ny = self.num_points(
                min(bbox1[3], expanded_bbox2[3]) -
                max(bbox1[1], expanded_bbox2[1]))
        if nx == -1 or ny == -1:
            return False
        if nx == 0 or ny == 0:
            return False
        return True


    def __init__(self, directory, clips=None, by_overlap=False):
        # for each piece; list the adjacent pieces
        self.adjacent_pieces = {}

        if clips:
            pass
            # TODO: use scissors on a blank image ( not necessary to have a
            # real image here.
            #pieces_info = 
        else:
            pieces_info = json.load(open(os.path.join(directory,
                'pieces.json')))
        for (piece_id, piece_bbox) in pieces_info.items():
            adjacent = []
            for (other_piece_id, other_piece_bbox) in pieces_info.items():
                if piece_id == other_piece_id:
                    continue
                if (self.are_adjacent(piece_bbox, other_piece_bbox)):
                    adjacent.append(other_piece_id)
            self.adjacent_pieces[piece_id] = adjacent

        if by_overlap:
            pass
            # TODO: further filter out the adjacent pieces by doing the
            # overlapping  mask test.
