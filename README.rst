The Jigsaw Piece Maker
======================

A jigsaw puzzle pieces generator that levels the playing field.

Takes some options:
Directory
Target count of pieces

Optional options:

just clips - only create a clips svg file
clips - specify a clips svg file

compute adjacent - adds the adjacent piece id's to each piece in JSON file.

minimum piece size - Will change the count of pieces to meet this requirement
maximum piece size - Will scale down the original image to meet this requirement
scaled sizes - output multiple scaled versions of piece pngs
        
Outputs:
clips svg file
adjacent.json - Lists each piece and their adjacent pieces
pieces/
  full/ - unscaled version
    pieces.json - JSON file with pieces info
    pieces/
      directory with piece png files
  scaled-50/ - scaled 50% version (set by 'scaled sizes' option)
    pieces.json - JSON file with pieces info
    pieces/
      directory with piece png files
