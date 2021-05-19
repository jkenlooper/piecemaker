The Jigsaw Piece Maker
======================

A jigsaw puzzle pieces generator that levels the playing field.

Currently in use by `Puzzle Massive <http://puzzle.massive.xyz>`_ to create
puzzles with 5000+ pieces.

It creates jigsaw puzzle pieces in multiple formats: svg, jpg, and png.  The
number and size of pieces are set by passing the script different options.  It
takes a while to run if doing a lot of pieces.  Extra JSON files are created
with details on size of pieces and adjacent pieces information which is commonly
used when verifying that two pieces can join together.


Installing
----------

Requires:

Python Packages:

* `Pillow <http://github.com/python-imaging/Pillow>`_
* `pixsaw <http://github.com/jkenlooper/pixsaw>`_
* `beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/bs4/>`_
* `svgwrite <https://pypi.python.org/pypi/svgwrite>`_
* lxml
* `glue <https://github.com/jorgebastida/glue>`_

Other Software needed:

* `potrace <http://potrace.sourceforge.net/>`_
* `svgo <https://github.com/svg/svgo>`_
* `svpng <https://github.com/tylerjpeterson/svpng>`_

If on ubuntu or other debian based distro::

    sudo apt-get --yes install libspatialindex6
    sudo apt-get --yes install optipng
    sudo curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo apt-get --yes install python3-pil
    sudo apt-get --yes install potrace libffi-dev libxml2-dev python3-lxml python3-xcffib
    sudo npm install -g svgo

    # Support for svpng which uses puppeteer
    # https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md
    sudo apt-get --yes install ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils

    # Install a fork of svpng that uses node 14
    npm install jkenlooper/svpng#28554fa32d57df13ec330e3a4df152172b6080bb
    sudo ln -s $PWD/node_modules/svpng/bin/svpng.js /usr/local/bin/svpng


Install with pip in editable mode for developing and use virtualenv to isolate
python dependencies::

    python3 -m venv .
    source ./bin/activate
    pip install -e .


Usage
-----

See the script.py for more.  Not everything has been implemented. Use this
example command to create 100 randomly generated jigsaw puzzle pieces from
test.jpg image. This assumes that the 'test' directory is empty since that is
where it will be placing all the generated files.  The test.jpg is the source
image that will be used when creating the pieces.  It is not modified.::

    piecemaker --dir test  --number-of-pieces 100 test.jpg
