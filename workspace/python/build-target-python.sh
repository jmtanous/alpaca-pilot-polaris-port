#!/bin/bash
set -euo pipefail
source /project/workspace/python/cross-env.sh
mkdir -p "$python_root/build/target-python-build"
cd "$python_root/build/target-python-build"
export ac_cv_file__dev_ptmx=yes ac_cv_file__dev_ptc=no ac_cv_buggy_getaddrinfo=no
# Captured libc reports 2.24 but backports symbols under GLIBC_2.25. The SDK
# headers intentionally stay at 2.24; use CPython's portable fallbacks instead.
export ac_cv_func_explicit_bzero=no ac_cv_func_getentropy=no ac_cv_func_getrandom=no
# Our prerequisite libraries are PIC static archives. Keep their transitive
# link flags (pthread/dl/math/zlib) when configure checks and links modules.
export PKG_CONFIG='pkg-config --static'
export CFLAGS="$CFLAGS -pthread"
"$python_root/build/Python-3.13.18/configure" \
  --host=arm-linux-gnueabi --build=x86_64-linux-gnu \
  --with-build-python="$python_root/build/host-python/bin/python3.13" \
  --prefix=/opt/benro-python --with-ensurepip=no \
  --with-openssl-rpath=no \
  --disable-test-modules
# CPython's make dependencies do not track our external static archives.
# Force extension relinking whenever this recipe is invoked.
find Modules -maxdepth 1 -name '*.so' -delete
make -j12
make DESTDIR="$python_stage" install
arm-linux-gnueabi-readelf -h "$python_prefix/bin/python3.13"
