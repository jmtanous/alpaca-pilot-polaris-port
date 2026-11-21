#!/bin/bash
set -euo pipefail
root=/project/workspace/python
export PATH="$root/build/crossenv/bin:$root/build/host-python/bin:$PATH"
export PKG_CONFIG_LIBDIR="$root/prefix/opt/benro-python/lib/pkgconfig:$root/prefix/opt/benro-python/lib/python3.13/site-packages/numpy/_core/lib/pkgconfig"
export PKG_CONFIG_SYSROOT_DIR="$root/prefix"
export SOURCE_DATE_EPOCH=1792886400 PIP_NO_INDEX=1
python3.13 "$root/install-wheels.py" "$root"/out/wheels/numpy-*.whl
# Header-only pybind11 must not inject the build machine's Python headers.
# Supply target pkg-config metadata instead of its host config executable.
cp -a "$root/build/host-python/lib/python3.13/site-packages/pybind11/include/pybind11" "$root/prefix/opt/benro-python/include/"
cat > "$root/prefix/opt/benro-python/lib/pkgconfig/pybind11.pc" <<'EOF'
prefix=/opt/benro-python
includedir=${prefix}/include
Name: pybind11
Description: Header-only pybind11 for the captured ARM target
Version: 3.0.4
Cflags: -I${includedir}
EOF
cd "$root/build/packages/scipy-1.18.0"
cross-python -m build --wheel --no-isolation --outdir "$root/out/wheels" \
  -Csetup-args="--cross-file=$root/meson-arm.ini" \
  -Csetup-args=-Dblas=openblas -Csetup-args=-Dlapack=openblas \
  -Ccompile-args=-j12
