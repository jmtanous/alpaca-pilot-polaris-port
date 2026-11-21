#!/bin/bash
# Source inside benro-python-build; all outputs belong to this project.
python_root=/project/workspace/python
python_sdk="$python_root/build/benro-sdk"
python_stage="$python_root/prefix"
python_prefix="$python_stage/opt/benro-python"
export CC="$python_sdk/cc"
export AR=arm-linux-gnueabi-ar
export RANLIB=arm-linux-gnueabi-ranlib
export STRIP=arm-linux-gnueabi-strip
export CFLAGS='-O2 -fPIC -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp'
export CPPFLAGS="-I$python_prefix/include"
export LDFLAGS="-L$python_prefix/lib -Wl,-rpath-link,$python_prefix/lib"
export PKG_CONFIG_LIBDIR="$python_prefix/lib/pkgconfig"
export PKG_CONFIG_SYSROOT_DIR="$python_stage"
mkdir -p "$python_prefix"
