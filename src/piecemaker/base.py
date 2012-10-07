import os
from tempfile import SpooledTemporaryFile

import svgwrite
#from scissors.base import Clips, Scissors



class JigsawPieceClips(object):
    """
    Renders a svg file of jigsaw puzzle piece paths.
    """
    title = "Jigsaw puzzle piece clips"

    def __init__(self, size, pieces):
        #TODO: minimum piece size
        #TODO: maximum piece size

        #TODO: rows and columns count
        self._rows = 10
        self._cols = 10

        #TODO: pieces
        self._pieces = self._rows * self._cols

        description = "Created with the piecemaker. Piece count: %i" % pieces
        # create a drawing
        self._dwg = svgwrite.Drawing(size=(1280,960), profile='full')
        self._dwg.viewbox(width=1280, height=960)
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
        for range(0, self.cols): #TODO: except last one
            g = layer.add(self._dwg.g())
            path = g.add(
                    self._dwg.path('M 0 0 L 250 0 L 200 300 L 250 960 L 0 960')
                    )
        #TODO: last one is full size rect

    def _horizontal_layer(self):
        layer = self._dwg.add(self._dwg.g())
        for range(0, self.rows): #TODO: except last one
            g = layer.add(self._dwg.g())
            path = g.add(
                    self._dwg.path('M 0 0 L 250 0 L 200 300 L 250 960 L 0 960')
                    )
        #TODO: last one is full size rect



