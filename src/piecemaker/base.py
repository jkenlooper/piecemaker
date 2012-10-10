import os
import decimal
import math
from tempfile import SpooledTemporaryFile

import svgwrite
#from scissors.base import Clips, Scissors

from paths.interlockingnubs import HorizontalPath, VerticalPath

class Pieces(object):
    """
    Creates the piece pngs and pieces info
    """
    def __init__(self, clips, image, directory,
            scale=100, max_pixels=10000000
            ):
        if scale != 100:
            # TODO: scale the image

        # TODO; get the width and height from the image
        if max_pixels > 0 and (width*height) > max_pixels:
            # resize the image using image magick @
            # '%i@' % max_pixels
            # TODO: get new width and height

        # TODO: use scissors to create all the pieces
        # TODO: get info for each piece and add it to the pieces info

# see adjacent.py

class JigsawPieceClips(object):
    """
    Renders a svg file of jigsaw puzzle piece paths.
    """
    title = "Jigsaw puzzle piece clips"
    MINIMUM_COUNT_OF_PIECES = 9
    MAXIMUM_COUNT_OF_PIECES = 50000 #how many is too many?

    def __init__(self, width, height, pieces=0, minimum_piece_size=42,
            ):

        if minimum_piece_size > 0:
            # Get the maximum number of pieces that can fit within the
            # dimensions depending on the minimum piece size.
            max_pieces_that_will_fit = int((width/minimum_piece_size)*(height/minimum_piece_size))
            if pieces > 0:
                # Only use the piece count that is smaller to avoid getting too
                # small of pieces.
                pieces = min(max_pieces_that_will_fit, pieces)
            else:
                pieces = max_pieces_that_will_fit

        pieces = max(pieces, MINIMUM_COUNT_OF_PIECES)
        pieces = min(pieces, MAXIMUM_COUNT_OF_PIECES)

        area = decimal.Decimal(width * height)
        s = area.sqrt()
        n = decimal.Decimal(pieces).sqrt()
        piece_size = float(s/n)
        # use math.ceil to at least have the target count of pieces
        self._rows = int(math.ceil(height/piece_size))
        self._cols = int(math.ceil(width/piece_size))

        #adjust piece count
        pieces = self._pieces = self._rows*self._cols
        self._piece_width = float(width)/float(self._cols)
        self._piece_height = float(height)/float(self._rows)

        self._width = width
        self._height = height

        description = "Created with the piecemaker. Piece count: %i" % pieces
        # create a drawing
        self._dwg = svgwrite.Drawing(size=(self._width,self._height), profile='full')
        self._dwg.viewbox(width=self._width, height=self._height)
        self._dwg.stretch()
        self._dwg.set_desc(title=self.title, desc=description)

        self._create_layers()

    def svg(self, filename=None):
        if not filename:
            return self._dwg.tostring()
        else:
            #TODO: write svg to filename
            pass

    def _create_layers(self):
        # create 2 layers
        self._vertical_layer()
        self._horizontal_layer()

    def _vertical_layer(self):
        layer = self._dwg.add(self._dwg.g())
        for i in range(0, self.cols-1): #except last one
            g = layer.add(self._dwg.g())
            start = (i+1)*self._col_spacing
            curvelines = [
                    'M 0 0 ', # origin
                    'L %f 0 ' % start,
                    ]
            for j in range(0, self._rows):
                interlockingnub_path = VerticalPath(width=self._piece_height)
                curvelines.append(interlockingnub_path.render())

            curvelines.append('L 0 %i ' % self._height) # end
            curveline = ' '.join(curvelines)
            path = g.add(self._dwg.path(curveline))
        fullsize_rect = g.add(self._dwg.rect(insert=(0,0), size=(self._width, self._height)))

    def _horizontal_layer(self):
        layer = self._dwg.add(self._dwg.g())
        for i in range(0, self._rows-1): #except last one
            g = layer.add(self._dwg.g())
            start = (i+1)*self._row_spacing
            curvelines = [
                    'M 0 0 ',
                    'L 0 %f ' % start,
                    ]
            for j in range(0, self._rows):
                interlockingnub_path = HorizontalPath(width=self._piece_width)
                curveline.append(interlockingnub_path.render())

            curvelines.append('L %i 0 ' % self._width) # end
            curveline = ' '.join(curvelines)
            path = g.add(self._dwg.path(curveline))
        fullsize_rect = g.add(self._dwg.rect(insert=(0,0), size=(self._width, self._height)))



