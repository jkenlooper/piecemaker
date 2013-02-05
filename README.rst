The Jigsaw Piece Maker
======================

A jigsaw puzzle pieces generator that levels the playing field.

Depends on scissors to do a lot of the work.  This script may change a lot as I
have yet to really use it for any active projects.


Installing
----------

See the scissors package for now for help on installing.


Usage
-----

See the script.py for more.  Not everything has been implemented, but to create
100 randomly generated jigsaw puzzle pieces::

    ./bin/piecemaker --dir test  --number-of-pieces 100 test.jpg



Some in progress notes and such
*******************************

just clips - only create a clips svg file

clips - specify a clips svg file

compute adjacent - adds the adjacent piece id's to each piece in JSON file.

minimum piece size - Will change the count of pieces to meet this requirement

max pixels - Will scale down the original image to meet this requirement

scaled sizes - output multiple scaled versions of piece pngs

Outputs:

clips svg file

adjacent.json - Lists each piece and their adjacent pieces

Directory::

    pieces/
      full/ - unscaled version
        pieces.json - JSON file with pieces info
        pieces/
          directory with piece png files
      scaled-50/ - scaled 50% version (set by 'scaled sizes' option)
        pieces.json - JSON file with pieces info
        pieces/
          directory with piece png files
