# https://packaging.python.org/en/latest/distributing.html
from setuptools import setup, find_packages
import os

name = "piecemaker"

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
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
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Build Tools',
        ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=[
        'Pillow',
        'pixsaw >= 0.1.0, < 0.2',
        'beautifulsoup4',
        'lxml',
        'svgwrite',
        'cairosvg == 1.0.22',
        'glue == 0.9.4',
      ],
    entry_points="""
    [console_scripts]
    piecemaker = piecemaker.script:piecemaker
    """,
)
