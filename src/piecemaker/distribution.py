from random import randint, choices

from rtree import index


def bbox_area(bbox):
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return w * h


def random_pos_outside_of_outline(table_bbox, outline_bbox, bbox, regions=("left_side", "top_middle", "bottom_middle", "right_side")):
    piece_width = (bbox[2] - bbox[0])
    piece_height = (bbox[3] - bbox[1])
    left_side_bbox = [
        table_bbox[0],
        table_bbox[1],
        max(outline_bbox[0] - piece_width, table_bbox[0]),
        max(table_bbox[3] - piece_height, table_bbox[1])
    ]
    left_side_area = bbox_area(left_side_bbox) if "left_side" in regions else 0
    top_middle_bbox = [
        outline_bbox[0] - piece_width,
        table_bbox[1],
        max(outline_bbox[2], outline_bbox[0] - piece_width),
        max(outline_bbox[1] - piece_height, table_bbox[1])
    ]
    top_middle_area = bbox_area(top_middle_bbox) if "top_middle" in regions else 0
    bottom_middle_bbox = [
        outline_bbox[0] - piece_width,
        outline_bbox[3],
        max(outline_bbox[2] - piece_width, outline_bbox[0] - piece_width),
        max(table_bbox[3] - piece_height, outline_bbox[3])
    ]
    bottom_middle_area = bbox_area(bottom_middle_bbox) if "bottom_middle" in regions else 0
    right_side_bbox = [
        outline_bbox[2],
        table_bbox[1],
        max(table_bbox[2] - piece_width, outline_bbox[2] - piece_width),
        max(table_bbox[3] - piece_height, table_bbox[1])
    ]
    right_side_area = bbox_area(right_side_bbox) if "right_side" in regions else 0
    box = choices(
        [left_side_bbox,
         top_middle_bbox,
         bottom_middle_bbox,
         right_side_bbox],
        weights=[left_side_area, top_middle_area, bottom_middle_area, right_side_area])[0]
    x = randint(box[0], box[2])
    y = randint(box[1], box[3])
    return [x, y]


def random_outside(table_bbox, outline_bbox, piece_bboxes, regions=("left_side", "top_middle", "bottom_middle", "right_side")):
    rtree_idx = index.Index(interleaved=True)
    outline_id = len(piece_bboxes) + 1
    rtree_idx.insert(outline_id, outline_bbox)
    positions = {}

    def nonoverlapping(bbox, attempt=15, regions=regions):
        (x, y) = random_pos_outside_of_outline(table_bbox, outline_bbox, bbox, regions=regions)
        if attempt > 0:
            count = rtree_idx.count([x, y, x + (bbox[2] - bbox[0]), y + (bbox[3] - bbox[1])])
            if count > 0:
                return nonoverlapping(bbox, attempt=attempt - 1, regions=regions)
            else:
                return [x, y]
        else:
            return [x, y]

    for (i, bbox) in piece_bboxes.items():
        (x, y) = nonoverlapping(bbox, regions=regions)
        rtree_idx.insert(int(i), [x, y, x + bbox[2] - bbox[0], y + bbox[3] - bbox[1]])
        positions[i] = [x, y]
    return positions


def grid(table_bbox, outline_bbox, piece_bboxes):
    pass
    # TODO: insert a column of pieces by checking the nearest from bottom right
    # corner of table.  With each column; shift over when adding next column.
    # Readjust the placed piece in the column to the nearest of the previous
    # column piece.

    #rtree_idx = index.Index(interleaved=True)
    #outline_id = len(piece_bboxes) + 1
    #rtree_idx.insert(outline_id, outline_bbox)


    ##    x = randint(0, table_width - (bbox[2] - bbox[0]))
    ##    y = randint(0, table_height - (bbox[3] - bbox[1]))
    ##    next_nearest = rtree_idx.nearest([table_width, table_height, table_width, table_height], num_results=2)
    ##    next_nearest.remove(outline_id)

    ##    rtree_idx.insert(int(i), piece_bbox)

    #return {
    #    "1": [0, 0]
    #}
