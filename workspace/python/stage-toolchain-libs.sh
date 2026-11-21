#!/bin/bash
set -euo pipefail
root=/project/workspace/python
src="$root/build/toolchain/arm-linux-gnueabi/lib"
dest="$root/prefix/opt/benro-python/lib"
mkdir -p "$dest"
for name in libgcc_s.so.1 libatomic.so libatomic.so.1 libatomic.so.1.2.0 \
  libstdc++.so libstdc++.so.6 libstdc++.so.6.0.30 \
  libgfortran.so libgfortran.so.5 libgfortran.so.5.0.0; do
  cp -a "$src/$name" "$dest/"
done
