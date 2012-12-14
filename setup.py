from setuptools import setup, find_packages
import os

name = "piecemaker"
version = "0.0.1"

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    author='Jake Hickenlooper',
    author_email='jake@weboftomorrow.com',
    description="Create jigsaw puzzle pieces from an image",
    long_description=read('README.rst'),
    url='https://github.com/jkenlooper/piecemaker',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Build Tools',
        ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=[
        'setuptools',
        # Like sleeping with scissors under your Pillow.
        'Pillow',
        'scissors'
        'beautifulsoup4',
        'svgwrite',
        #'lxml',
        #'pgmagick', # relies on graphicsmagick

        #'glue',
      ],
    entry_points="""
    [console_scripts]
    piecemaker = piecemaker.script:piecemaker
    """,
)
