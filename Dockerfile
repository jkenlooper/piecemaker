# Modified from the original in python-worker directory in https://git.sr.ht/~jkenlooper/cookiecutters .

# UPKEEP due: "2024-03-14" label: "Alpine Linux base image" interval: "+3 months"
# docker pull alpine:3.19.0
# docker image ls --digests alpine
FROM alpine:3.19.0@sha256:51b67269f354137895d43f3b3d810bfacd3945438e94dc5ac55fdac340352f48 as build

RUN echo "Create dev user"; \
  addgroup -g 44444 dev && adduser -u 44444 -G dev -s /bin/sh -D dev

WORKDIR /home/dev/app

RUN echo "apk add package dependencies"; \
  apk update \
  && apk add --no-cache \
    -q --no-progress \
    build-base \
    gcc \
    musl-dev \
    py3-pip \
    python3 \
    python3-dev

RUN echo "Setup for python virtual env"; \
  mkdir -p /home/dev/app \
  && chown -R dev:dev /home/dev/app \
  && su dev -c 'python -m venv /home/dev/app/.venv'

# Activate python virtual env by updating the PATH
ENV VIRTUAL_ENV=/home/dev/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --chown=dev:dev pip-requirements.txt /home/dev/app/pip-requirements.txt

USER dev

RUN echo "Install pip-requirements.txt"; \
  python -m pip install \
    --disable-pip-version-check \
    --no-build-isolation \
    -r /home/dev/app/pip-requirements.txt

COPY --chown=dev:dev pyproject.toml /home/dev/app/pyproject.toml
COPY --chown=dev:dev src/piecemaker/_version.py /home/dev/app/src/piecemaker/_version.py
COPY --chown=dev:dev README.md /home/dev/app/README.md
COPY --chown=dev:dev COPYING /home/dev/app/
COPY --chown=dev:dev COPYING.LESSER /home/dev/app/

RUN echo "Download python packages listed in pyproject.toml"; \
  mkdir -p /home/dev/app/dep \
  && python -m pip download --disable-pip-version-check \
    --exists-action i \
    --no-build-isolation \
    --destination-directory /home/dev/app/dep \
    .[dev,test]

RUN echo "Generate the requirements.txt file"; \
  pip-compile \
    --resolver=backtracking \
    --allow-unsafe \
    --find-links="./dep" \
    --extra dev \
    --extra test \
    --output-file ./requirements.txt \
    pyproject.toml

COPY pip-audit.sh /home/dev/app/pip-audit.sh
RUN echo "Audit packages for known vulnerabilities"; \
  /home/dev/app/pip-audit.sh

CMD ["sh", "-c", "while true; do printf 'z'; sleep 60; done"]

# UPKEEP due: "2024-03-14" label: "Alpine Linux base image" interval: "+3 months"
# docker pull alpine:3.19.0
# docker image ls --digests alpine
FROM alpine:3.19.0@sha256:51b67269f354137895d43f3b3d810bfacd3945438e94dc5ac55fdac340352f48 as app

RUN echo "Create dev user"; \
  addgroup -g 44444 dev && adduser -u 44444 -G dev -s /bin/sh -D dev

WORKDIR /home/dev/app

COPY --from=build /home/dev/app /home/dev/app

RUN echo "apk add package dependencies"; \
  apk update \
  && apk add --no-cache \
    -q --no-progress \
    build-base \
    cmake \
    freetype \
    freetype-dev \
    fribidi \
    fribidi-dev \
    gcc \
    harfbuzz \
    harfbuzz-dev \
    jpeg \
    jpeg-dev \
    lcms2 \
    lcms2-dev \
    libffi-dev \
    libjpeg \
    libstdc++ \
    libstdc++-dev \
    gcompat \
    musl-dev \
    openjpeg \
    openjpeg-dev \
    py3-pip \
    python3 \
    python3-dev \
    tcl \
    tcl-dev \
    tiff \
    tiff-dev \
    tk \
    tk-dev \
    zlib \
    zlib-dev \
  && apk add --no-cache \
    -q --no-progress \
    optipng \
    potrace \
    rsvg-convert

COPY install-libspatialindex.sh /home/dev/install-libspatialindex.sh
RUN echo "Install libspatialindex for Python Rtree"; \
  /home/dev/install-libspatialindex.sh
ENV SPATIALINDEX_C_LIBRARY=/usr/lib/libspatialindex

# Activate python virtual env by updating the PATH
ENV VIRTUAL_ENV=/home/dev/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER dev

RUN echo "Install dependencies"; \
  python -m pip install \
    --disable-pip-version-check \
    --compile \
    --no-build-isolation \
    --no-index \
    -r /home/dev/app/requirements.txt

COPY --chown=dev:dev src /home/dev/app/src
RUN echo "Use bandit to find common security issues"; \
  bandit \
    --recursive \
    -c pyproject.toml \
    /home/dev/app/src/ > /home/dev/security-issues-from-bandit.txt || echo "WARNING: Issues found."

RUN echo "Install in editable mode for local development"; \
  python -m pip install --disable-pip-version-check --compile \
    --no-build-isolation \
    -e '/home/dev/app[dev,test]'

ENTRYPOINT ["/home/dev/app/.venv/bin/piecemaker"]
CMD ["--help"]
