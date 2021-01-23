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

    $ sudo apt-get --yes install optipng
    $ sudo curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    $ sudo apt-get install -y nodejs
    $ sudo apt-get --yes install python3-pil
    $ sudo apt-get --yes install imagemagick potrace libffi-dev libxml2-dev python3-lxml python3-xcffib
    $ sudo apt-get --yes install libcairo2-dev
    $ sudo apt-get --yes install python3-cairo
    $ sudo npm install -g svgo


Install with pip in editable mode for developing and use virtualenv to isolate
python dependencies::

    $ python3 -m venv .
    $ source ./bin/activate
    $ pip install -e .


Usage
-----

See the script.py for more.  Not everything has been implemented. Use this
example command to create 100 randomly generated jigsaw puzzle pieces from
test.jpg image. This assumes that the 'test' directory (`mkdir test`) and
test.jpg exist::

    piecemaker --dir test  --number-of-pieces 100 test.jpg
