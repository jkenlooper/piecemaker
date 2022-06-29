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

WORKDIR /build

COPY MANIFEST.in ./
COPY README.rst ./
COPY setup.py ./
COPY requirements.txt ./

RUN pip3 install --user -r requirements.txt

COPY src/ ./src/

RUN pip3 install --user -e .

ENV PATH=$PATH:/root/.local/bin

CMD ["/root/.local/bin/piecemaker"]
