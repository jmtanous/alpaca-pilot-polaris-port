#!/bin/sh
# SD-only foreground launcher; does not connect the mount or install a service.
set -eu
awk '$2 == "/app/sd" && $3 == "vfat" {found=1} END {exit !found}' /proc/mounts || {
    echo 'The Benro SD card is not mounted at /app/sd.' >&2
    exit 1
}
native_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
prefix=/app/sd/opt/benro-python
unset PYTHONHOME PYTHONPATH
export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="$prefix/lib:/lib:/usr/lib:/app/lib"
export SSL_CERT_FILE="$prefix/lib/python3.13/site-packages/certifi/cacert.pem"
export PATH="$prefix/bin:/bin:/usr/bin:/sbin:/usr/sbin"
cd /app/sd/opt/alpaca-pilot-2.2
exec "$prefix/bin/python3.13" -B "$native_dir/pilot_native.py" --listen 0.0.0.0 "$@"
