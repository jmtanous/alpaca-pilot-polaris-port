#!/bin/bash
set -euo pipefail
root=/project/workspace/python
src="$root/build/Python-3.13.18"
build="$root/build/host-python-build"
prefix="$root/build/host-python"
mkdir -p "$build"
cd "$build"
"$src/configure" --prefix="$prefix" --with-ensurepip=install
make -j12
make install
"$prefix/bin/python3.13" -c 'import sys,ssl,zlib,ctypes,sqlite3,bz2,lzma; print(sys.version, ssl.OPENSSL_VERSION)'
