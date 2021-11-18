# https://packaging.python.org/en/latest/distributing.html
from setuptools import setup, find_packages
import os

__version__ = "0.4.3"  # Also set in src/piecemaker/_version.py

name = "piecemaker"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=__version__,
    author="Jake Hickenlooper",
    author_email="jake@weboftomorrow.com",
    description="Create jigsaw puzzle pieces from an image",
    long_description=read("README.rst"),
    url="https://github.com/jkenlooper/piecemaker",
    license="GPL",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Build Tools",
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # glue 0.13 -> Pillow>=2.2.2
        "Pillow >= 8.1.1, < 9",
        "pixsaw >= 0.3, <0.4",
        "beautifulsoup4",
        "future",
        "lxml",  # wanted by beautifulsoup4
        "svgwrite >= 1.4.1",
        # glue 0.13 -> Jinja2>=2.7,<2.10
        "glue >= 0.13, <1.0",
        "Rtree"
    ],
    entry_points="""
    [console_scripts]
    piecemaker = piecemaker.script:piecemaker
    """,
)
