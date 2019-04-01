# https://packaging.python.org/en/latest/distributing.html
from setuptools import setup, find_packages
import os

execfile(os.path.join(os.path.dirname(__file__), 'src', 'piecemaker', '__version__.py'))

name = "piecemaker"

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=__version__,
    author='Jake Hickenlooper',
    author_email='jake@weboftomorrow.com',
    description="Create jigsaw puzzle pieces from an image",
    long_description=read('README.rst'),
    url='https://github.com/jkenlooper/piecemaker',
    license='GPL',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Build Tools',
        ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=[
        # glue 0.13 -> Pillow>=2.2.2
        'Pillow',
        'pixsaw >= 0.1.0, < 0.2',
        'beautifulsoup4',
        'lxml',
        'svgwrite',
        'pycairo',
        'cairosvg == 1.0.22',
        # glue 0.13 -> Jinja2>=2.7,<2.10
        'glue == 0.13',
      ],
    entry_points="""
    [console_scripts]
    piecemaker = piecemaker.script:piecemaker
    """,
)
