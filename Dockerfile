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

VOLUME /build/src/piecemaker
VOLUME /out

COPY MANIFEST.in ./
COPY README.rst ./
COPY setup.py ./
COPY requirements.txt ./

RUN mkdir -p /out && chown -R piecemaker:piecemaker /out

RUN pip3 install --user -r requirements.txt

COPY src/ ./src/
RUN chown -R piecemaker:piecemaker /build

RUN pip3 install --user -e .
RUN chown -R piecemaker:piecemaker /build

ENV PATH=$PATH:/home/piecemaker/.local/bin

USER piecemaker

CMD ["piecemaker"]
