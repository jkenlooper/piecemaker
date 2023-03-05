# syntax=docker/dockerfile:1.4.3

# Modified from the original in python-worker directory in https://github.com/jkenlooper/cookiecutters .

# UPKEEP due: "2023-04-21" label: "Alpine Linux base image" interval: "+3 months"
# docker pull alpine:3.17.1
# docker image ls --digests alpine
FROM alpine:3.17.1@sha256:f271e74b17ced29b915d351685fd4644785c6d1559dd1f2d4189a5e851ef753a

RUN <<DEV_USER
addgroup -g 44444 dev
adduser -u 44444 -G dev -s /bin/sh -D dev
DEV_USER

WORKDIR /home/dev/app

RUN <<PACKAGE_DEPENDENCIES
# apk add package dependencies
set -o errexit
apk update
apk add --no-cache \
  -q --no-progress \
  build-base \
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
  py3-yaml
PACKAGE_DEPENDENCIES

RUN  <<PYTHON_VIRTUALENV
# Setup for python virtual env
set -o errexit
mkdir -p /home/dev/app
chown -R dev:dev /home/dev/app
su dev -c '/usr/bin/python3 -m venv /home/dev/app/.venv'
PYTHON_VIRTUALENV
# Activate python virtual env by updating the PATH
ENV VIRTUAL_ENV=/home/dev/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --chown=dev:dev pip-requirements.txt /home/dev/app/pip-requirements.txt
COPY --chown=dev:dev pyproject.toml /home/dev/app/pyproject.toml
COPY --chown=dev:dev dep /home/dev/app/dep
COPY --chown=dev:dev README.md /home/dev/app/README.md
RUN <<PIP_DOWNLOAD
# Download python packages listed in pyproject.toml
set -o errexit
# Install these first so packages like PyYAML don't have errors with 'bdist_wheel'
python -m pip install wheel
python -m pip install pip
python -m pip install hatchling
python -m pip download --disable-pip-version-check \
    --exists-action i \
    --no-build-isolation \
    --find-links /home/dev/app/dep/ \
    --destination-directory /home/dev/app/dep \
    -r /home/dev/app/pip-requirements.txt
python -m pip download --disable-pip-version-check \
    --exists-action i \
    --no-build-isolation \
    --find-links /home/dev/app/dep/ \
    --destination-directory /home/dev/app/dep \
    .[dev,test]
PIP_DOWNLOAD

USER dev

RUN <<PIP_INSTALL
# Install pip-requirements.txt
set -o errexit
python -m pip install \
  --no-index \
  --no-build-isolation \
  --find-links /home/dev/app/dep/ \
  -r /home/dev/app/pip-requirements.txt
PIP_INSTALL

RUN <<SETUP
set -o errexit
cat <<'HERE' > /home/dev/sleep.sh
#!/usr/bin/env sh
while true; do
  printf 'z'
  sleep 60
done
HERE
chmod +x /home/dev/sleep.sh
SETUP

COPY --chown=dev:dev README.md /home/dev/app/README.md

RUN <<PIP_DOWNLOAD_APP_DEPENDENCIES
# Download python packages described in pyproject.toml
set -o errexit
python -m pip download --disable-pip-version-check \
    --exists-action i \
    --destination-directory /home/dev/app/dep \
    .[dev,test]
PIP_DOWNLOAD_APP_DEPENDENCIES

RUN <<UPDATE_REQUIREMENTS
# Generate the hashed requirements*.txt files that the main container will use.
set -o errexit
# Change to the app directory so the find-links can be relative.
cd /home/dev/app
pip-compile --generate-hashes \
    --resolver=backtracking \
    --allow-unsafe \
    --no-index --find-links="./dep" \
    --output-file ./requirements.txt \
    pyproject.toml
pip-compile --generate-hashes \
    --resolver=backtracking \
    --allow-unsafe \
    --no-index --find-links="./dep" \
    --extra dev \
    --output-file ./requirements-dev.txt \
    pyproject.toml
pip-compile --generate-hashes \
    --resolver=backtracking \
    --allow-unsafe \
    --no-index --find-links="./dep" \
    --extra test \
    --output-file ./requirements-test.txt \
    pyproject.toml
UPDATE_REQUIREMENTS

COPY --chown=dev:dev update-dep-run-audit.sh /home/dev/app/
RUN <<AUDIT
# Audit packages for known vulnerabilities
set -o errexit
./update-dep-run-audit.sh > /home/dev/vulnerabilities-pip-audit.txt || echo "WARNING: Vulnerabilities found."
AUDIT

COPY --chown=dev:dev src/piecemaker/ /home/dev/app/src/piecemaker/
RUN <<BANDIT
# Use bandit to find common security issues
set -o errexit
bandit \
    --recursive \
    /home/dev/app/src/ > /home/dev/security-issues-from-bandit.txt || echo "WARNING: Issues found."
BANDIT

CMD ["/home/dev/sleep.sh"]
