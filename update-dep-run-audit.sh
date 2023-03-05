#!/usr/bin/env sh
set -o errexit

set -- ""

# exampleUPKEEP due: "2023-04-21" label: "Vuln exception GHSA-r9hx-vwmv-q579" interval: "+3 months"
# n/a
# https://osv.dev/vulnerability/GHSA-r9hx-vwmv-q579
#set -- "$@" --ignore-vuln "GHSA-r9hx-vwmv-q579"

# Change to the app directory so the find-links can be relative.
cd /home/dev/app
pip-audit \
    --require-hashes \
    --progress-spinner off \
    --local \
    --strict \
    --vulnerability-service pypi \
    $@ \
    -r ./requirements.txt
pip-audit \
    --progress-spinner off \
    --local \
    --strict \
    --vulnerability-service osv \
    $@ \
    -r ./requirements.txt
