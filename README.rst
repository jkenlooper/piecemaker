The Jigsaw Piece Maker
======================

A jigsaw puzzle pieces generator that levels the playing field.

This script may change a lot as I have yet to really use it for any active
projects.

It basically creates jigsaw puzzle pieces in two formats: svg, and png.  The
number and size of pieces are set by passing the script different options.  It
takes a while to run if doing a lot of pieces. It currently uses potrace, and
imagemagick convert subprocesses.


Installing
----------

Requires:

Python Packages:

* `Pillow <http://github.com/python-imaging/Pillow>`_
* `pixsaw <http://github.com/jkenlooper/pixsaw>`_
* `beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/bs4/>`_
* `svgwrite <https://pypi.python.org/pypi/svgwrite>`_
* `html <https://pypi.python.org/pypi/html>`_
* lxml
* cairosvg
* `glue <https://github.com/jorgebastida/glue>`_

Other Software needed:

* `potrace <http://potrace.sourceforge.net/>`_
* `imagemagick <http://www.imagemagick.org/script/index.php>`_
* `svgo <https://github.com/svg/svgo>`_

If on ubuntu or other debian based distro::

    $ apt-get install imagemagick potrace libffi-dev python-libxml2 libxml2-dev python-lxml


Install with pip in editable mode for developing and such::

    $ pip install -e .


Usage
-----

See the script.py for more.  Not everything has been implemented, but to create
100 randomly generated jigsaw puzzle pieces::

    ./bin/piecemaker --dir test  --number-of-pieces 100 test.jpg


Some in progress notes and such
*******************************

``These notes and such are probably outdated...``

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


