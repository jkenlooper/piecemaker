# TODO: create the adjacent info

# narrow down potential adjacent pieces by their bounding boxes and if they
# intersect with the target piece.



class Adjacent(object):
    """

    """

    def __init__(self, directory, clips=None, by_overlap=False):
        if clips:
            # TODO: use scissors on a blank image ( not necessary to have a
            # real image here.
        else:
            # TODO: use existing images in directory instead of creating own
            # with scissors

        # TODO: for each image take it's geometry and find intersecting boxes.


        if by_overlap:
            # TODO: further filter out the adjacent pieces by doing the
            # overlapping  mask test.
