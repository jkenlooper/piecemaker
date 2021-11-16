FROM ubuntu:20.04

RUN apt-get --yes update
RUN apt-get --yes install \
    libffi-dev \
    librsvg2-bin \
    libspatialindex6 \
    libxml2-dev \
    optipng \
    potrace \
    python3-lxml \
    python3-pil \
    python3-xcffib

RUN apt-get --yes install \
    python3-pip

# Create an unprivileged user that will only have access to /build directory.
RUN adduser --disabled-login --disabled-password --gecos "" piecemaker


WORKDIR /build

COPY MANIFEST.in ./
COPY README.rst ./
COPY setup.py ./
VOLUME /build/src/piecemaker
COPY src/ ./src/

RUN chown -R piecemaker:piecemaker /build

USER piecemaker

RUN pip3 install -e .

ENV PATH=$PATH:/home/piecemaker/.local/bin

CMD ["piecemaker"]
