#!/bin/sh
# Explicit foreground launcher; does not install services or change boot behavior.
set -eu
prefix=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
app="$prefix/../alpaca-pilot-2.2"
unset PYTHONHOME PYTHONPATH
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="$prefix/lib:/lib:/usr/lib:/app/lib"
export SSL_CERT_FILE="$prefix/lib/python3.13/site-packages/certifi/cacert.pem"
export PATH="$prefix/bin:/bin:/usr/bin:/sbin:/usr/sbin"
cd "$app"
exec "$prefix/bin/python3.13" -B "$app/driver/main.py" "$@"
