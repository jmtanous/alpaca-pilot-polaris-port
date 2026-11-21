#!/bin/bash
set -euo pipefail
root=/project/workspace/python
# Keep the same conservative ABI ceiling as CPython despite vendor backports.
export ac_cv_func_getentropy=no ac_cv_func_getrandom=no ac_cv_func_explicit_bzero=no
mkdir -p "$root/build/gcc-source" "$root/build/gcc-build" "$root/build/toolchain"
source_archive=$(find /usr/src/gcc-12 -maxdepth 1 -name 'gcc-12*.tar.*' -print -quit)
test -n "$source_archive"
test "$(sha256sum "$source_archive" | cut -d' ' -f1)" = 50c63ff82919323c25fbbb4a9eae259edc974118a0fb30c905190cb782ec11c2
sha256sum "$source_archive" > "$root/build/gcc-source.sha256"
dpkg-query -W gcc-12-source > "$root/build/gcc-source-package.txt"
if [ ! -d "$root/build/gcc-source/gcc-12.2.0" ]; then
  tar -xf "$source_archive" -C "$root/build/gcc-source"
fi
src="$root/build/gcc-source/gcc-12.2.0"
test -x "$src/configure"
doc_patch=/usr/src/gcc-12/debian/patches/gcc-gfdl-build.diff
sha256sum "$doc_patch" > "$root/build/gcc-documentation-patch.sha256"
if [ ! -f "$src/.benro-documentation-patch" ]; then
  patch -d "$src" -p2 < "$doc_patch"
  touch "$src/.benro-documentation-patch"
fi
cd "$root/build/gcc-build"
"$src/configure" --prefix="$root/build/toolchain" --target=arm-linux-gnueabi \
  --with-sysroot="$root/build/benro-sdk/sysroot" \
  --with-native-system-header-dir=/usr/include --enable-multiarch \
  --with-arch=armv7-a --with-fpu=vfpv3-d16 --with-float=softfp \
  --enable-languages=c,c++,fortran --enable-threads=posix \
  --disable-bootstrap --disable-multilib --disable-nls --disable-libsanitizer \
  --disable-libssp --disable-libquadmath --disable-libstdcxx-pch
if [ -f arm-linux-gnueabi/libgfortran/config.h ] && \
   grep -q '^#define HAVE_GETENTROPY 1' arm-linux-gnueabi/libgfortran/config.h; then
  (cd arm-linux-gnueabi/libgfortran; rm -f config.cache; ./config.status --recheck; ./config.status)
fi
make -j12 MAKEINFO=true
make MAKEINFO=true install
# GCC's source tarball does not include binutils. Supply the pinned container's
# matching cross tools at the installed compiler's standard lookup location.
mkdir -p "$root/build/toolchain/arm-linux-gnueabi/bin"
for tool in as ld ar nm ranlib strip objcopy objdump readelf; do
  ln -sf "/usr/bin/arm-linux-gnueabi-$tool" "$root/build/toolchain/arm-linux-gnueabi/bin/$tool"
done
"$root/build/toolchain/bin/arm-linux-gnueabi-gcc" -v
