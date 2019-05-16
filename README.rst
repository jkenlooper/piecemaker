The Jigsaw Piece Maker
======================

A jigsaw puzzle pieces generator that levels the playing field.

Currently in use by `Puzzle Massive <http://puzzle.massive.xyz>`_ to create
puzzles with 5000+ pieces.

It creates jigsaw puzzle pieces in multiple formats: svg, jpg, and png.  The
number and size of pieces are set by passing the script different options.  It
takes a while to run if doing a lot of pieces. It currently uses potrace, and
imagemagick convert subprocesses.  Extra JSON files are created with details on
size of pieces and adjacent pieces information which is commonly used when
verifying that two pieces can join together.


Installing
----------

Requires:

Python Packages:

* `Pillow <http://github.com/python-imaging/Pillow>`_
* `pixsaw <http://github.com/jkenlooper/pixsaw>`_
* `beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/bs4/>`_
* `svgwrite <https://pypi.python.org/pypi/svgwrite>`_
* lxml
* `cairosvg <https://cairosvg.org>`_
* `glue <https://github.com/jorgebastida/glue>`_

Other Software needed:

* `potrace <http://potrace.sourceforge.net/>`_
* `imagemagick <http://www.imagemagick.org/script/index.php>`_
* `svgo <https://github.com/svg/svgo>`_

If on ubuntu or other debian based distro::

    $ apt-get install imagemagick potrace libffi-dev python-libxml2 libxml2-dev python-lxml


Install with pip in editable mode for developing and use virtualenv to isolate
python dependencies::

    $ virtualenv . -p python3
    $ source ./bin/activate
    $ pip install -e .


Usage
-----

See the script.py for more.  Not everything has been implemented, but to create
100 randomly generated jigsaw puzzle pieces::

    piecemaker --dir test  --number-of-pieces 100 test.jpg
