#!/bin/bash
set -euo pipefail
root=/project/workspace/python
"$root/build/host-python/bin/python3.13" -m pip install --no-index \
  --find-links "$root/downloads" --require-hashes -r "$root/build-requirements.lock"
"$root/build/host-python/bin/python3.13" -m crossenv \
  "$root/prefix/opt/benro-python/bin/python3.13" "$root/build/crossenv" \
  --clear-both --without-pip --system-site-packages --machine armv7l \
  --cc "$root/build/toolchain/bin/arm-linux-gnueabi-gcc" \
  --cxx "$root/build/toolchain/bin/arm-linux-gnueabi-g++" --ar arm-linux-gnueabi-ar
