#!/bin/bash
set -euo pipefail
root=/project/workspace/python
export PATH="$root/build/crossenv/bin:$root/build/host-python/bin:$PATH"
export PKG_CONFIG_LIBDIR="$root/prefix/opt/benro-python/lib/pkgconfig"
export PKG_CONFIG_SYSROOT_DIR="$root/prefix"
export SOURCE_DATE_EPOCH=1792886400 PIP_NO_INDEX=1
cd "$root/build/packages/numpy-2.3.5"
cross-python -m build --wheel --no-isolation --outdir "$root/out/wheels" \
  -Csetup-args="--cross-file=$root/meson-arm.ini" \
  -Csetup-args=-Dblas=openblas -Csetup-args=-Dlapack=openblas \
  -Csetup-args=-Dcpu-baseline=none -Csetup-args=-Dcpu-dispatch=none \
  -Ccompile-args=-j12
