#!/bin/bash
set -euo pipefail
source /project/workspace/python/cross-env.sh
cd "$python_root/build/bzip2-1.0.8"
make -j12 libbz2.a CC="$CC" AR="$AR" RANLIB="$RANLIB" CFLAGS="$CFLAGS"
install -m644 bzlib.h "$python_prefix/include/"
install -m644 libbz2.a "$python_prefix/lib/"
