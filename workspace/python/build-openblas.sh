#!/bin/bash
set -euo pipefail
root=/project/workspace/python
toolchain="$root/build/toolchain/bin"
prefix="$root/prefix/opt/benro-python"
cd "$root/build/OpenBLAS-0.3.34"
# Portable ARMv7 kernels, no NEON dependency. Threading is disabled in BLAS so
# the application controls concurrency on the two-core embedded target.
args=(TARGET=ARMV7 HOSTCC=gcc CC="$toolchain/arm-linux-gnueabi-gcc"
  FC="$toolchain/arm-linux-gnueabi-gfortran" AR=arm-linux-gnueabi-ar
  RANLIB=arm-linux-gnueabi-ranlib BINARY=32 ARM_SOFTFP_ABI=1 CROSS=1
  USE_THREAD=0 USE_OPENMP=0 NO_SHARED=1
  CFLAGS='-O2 -fPIC -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp'
  FFLAGS='-O2 -fPIC -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp')
make -j12 "${args[@]}"
make "${args[@]}" PREFIX="$prefix" install
sed -i "s|$prefix|/opt/benro-python|g" "$prefix/lib/pkgconfig/openblas.pc"
