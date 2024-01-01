#!/usr/bin/env sh
set -o errexit

set -- ""


#---
# Replace example of using a vulnerability exception

# exampleUPKEEP due: "2023-04-21" label: "Vuln exception GHSA-r9hx-vwmv-q579" interval: "+3 months"
# n/a
# https://osv.dev/vulnerability/GHSA-r9hx-vwmv-q579
#set -- "$@" --ignore-vuln "GHSA-r9hx-vwmv-q579"

#---

pip-audit \
    --progress-spinner off \
    --local \
    --strict \
    --vulnerability-service osv \
    $@ \
    -r ./requirements.txt > vulnerabilities-pip-audit.txt

