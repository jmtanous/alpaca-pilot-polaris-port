#!/bin/bash
set -euo pipefail
source /project/workspace/python/cross-env.sh
cd "$python_root/build/zlib-1.4"
CHOST=arm-linux-gnueabi ./configure --static --prefix=/opt/benro-python
make -j12
make DESTDIR="$python_stage" install

mkdir -p "$python_root/build/libffi-build"
cd "$python_root/build/libffi-build"
../libffi-3.8.1/configure --host=arm-linux-gnueabi --build=x86_64-linux-gnu \
  --prefix=/opt/benro-python --libdir=/opt/benro-python/lib \
  --disable-shared --enable-static --with-pic --disable-docs
make -j12
make DESTDIR="$python_stage" install

cd "$python_root/build/openssl-3.5.9"
if ! grep -q OPENSSL_NO_WEAK_GETENTROPY providers/implementations/rands/seeding/rand_unix.c; then
  patch -p1 < "$python_root/patches/openssl-glibc-2.24.patch"
fi
if ! grep -A5 'if (p_getentropy.p != NULL)' providers/implementations/rands/seeding/rand_unix.c | grep -q ENOSYS; then
  patch -p1 < "$python_root/patches/openssl-getentropy-enosys.patch"
fi
./Configure linux-armv4 no-shared no-tests \
  --prefix=/opt/benro-python --libdir=lib -DOPENSSL_NO_WEAK_GETENTROPY
make -j12 build_libs
make DESTDIR="$python_stage" install_dev
