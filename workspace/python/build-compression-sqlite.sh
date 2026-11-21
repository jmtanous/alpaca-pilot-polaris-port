#!/bin/bash
set -euo pipefail
source /project/workspace/python/cross-env.sh
mkdir -p "$python_root/build/xz-build"
cd "$python_root/build/xz-build"
../xz-5.8.4/configure --host=arm-linux-gnueabi --build=x86_64-linux-gnu \
  --prefix=/opt/benro-python --disable-shared --enable-static --with-pic \
  --disable-nls --disable-xz --disable-xzdec --disable-lzmadec --disable-lzmainfo \
  --disable-scripts --disable-doc
make -j12
make DESTDIR="$python_stage" install

mkdir -p "$python_root/build/sqlite-build"
cd "$python_root/build/sqlite-build"
../sqlite-autoconf-3540100/configure --host=arm-linux-gnueabi --build=x86_64-linux-gnu \
  --prefix=/opt/benro-python --disable-shared --enable-static --disable-readline
make -j12 libsqlite3.a
make DESTDIR="$python_stage" install
patchelf --set-rpath '$ORIGIN/../lib' "$python_prefix/bin/sqlite3"
