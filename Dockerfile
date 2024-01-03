# Modified from the original in python-worker directory in https://git.sr.ht/~jkenlooper/cookiecutters .

# UPKEEP due: "2024-02-04" label: "Debian base image" interval: "+3 months"
# docker pull debian:bookworm-20231218-slim
# docker image ls --digests debian
FROM debian:bookworm-20231218-slim@sha256:f80c45482c8d147da87613cb6878a7238b8642bcc24fc11bad78c7bec726f340 as build

ARG DEBIAN_FRONTEND=noninteractive

RUN echo "Create dev user"; \
  addgroup --gid 44444 dev && adduser --uid 44444 --gid 44444 --shell /bin/sh --disabled-login --disabled-password --gecos "" dev

WORKDIR /home/dev/app

RUN echo "Install packages for Python"; \
  apt-get --yes update \
  && apt-get --yes install --no-install-suggests --no-install-recommends \
    gcc \
    libffi-dev \
    libpython3-dev \
    python-is-python3 \
    python3-dev \
    python3-venv \
    python3-pip

RUN echo "Setup for Python virtual env"; \
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

# UPKEEP due: "2024-02-04" label: "Debian base image" interval: "+3 months"
# docker pull debian:bookworm-20231218-slim
# docker image ls --digests debian
FROM debian:bookworm-20231218-slim@sha256:f80c45482c8d147da87613cb6878a7238b8642bcc24fc11bad78c7bec726f340 as app

ARG DEBIAN_FRONTEND=noninteractive

RUN echo "Create dev user"; \
  addgroup --gid 44444 dev && adduser --uid 44444 --gid 44444 --shell /bin/sh --disabled-login --disabled-password --gecos "" dev

WORKDIR /home/dev/app

COPY --from=build /home/dev/app /home/dev/app

RUN echo "Install packages for piecemaker"; \
  apt-get --yes update \
  && apt-get --yes install --no-install-suggests --no-install-recommends \
    gcc \
    libffi-dev \
    libpython3-dev \
    librsvg2-bin \
    libspatialindex6 \
    libxml2-dev \
    optipng \
    potrace \
    python-is-python3 \
    python3-dev \
    python3-lxml \
    python3-pil \
    python3-pip \
    python3-venv \
    python3-xcffib

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

RUN echo "Make output directory"; \
  mkdir -p /home/dev/output

ENTRYPOINT ["/home/dev/app/.venv/bin/piecemaker"]
CMD ["--help"]
