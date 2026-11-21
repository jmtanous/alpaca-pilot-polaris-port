#!/bin/bash
set -euo pipefail
root=/project/workspace/python
prefix="$root/prefix/opt/benro-python"
export PATH="$root/build/rust-toolchain/bin:$root/build/host-python/bin:$PATH"
export CARGO_HOME="$root/build/cargo-home"
mkdir -p "$CARGO_HOME"
cat > "$CARGO_HOME/config.toml" <<EOF
[source.crates-io]
replace-with = "vendored-sources"
[source.vendored-sources]
directory = "$root/build/cargo-vendor"
EOF
export PYO3_CROSS=1 PYO3_CROSS_PYTHON_VERSION=3.13
export PYO3_CROSS_LIB_DIR="$prefix/lib/python3.13"
export PYO3_PYTHON="$root/build/host-python/bin/python3.13"
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABI_LINKER="$root/build/toolchain/bin/arm-linux-gnueabi-gcc"
export CC_armv7_unknown_linux_gnueabi="$CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABI_LINKER"
export AR_armv7_unknown_linux_gnueabi=arm-linux-gnueabi-ar
export CFLAGS_armv7_unknown_linux_gnueabi='-O2 -fPIC -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp'
export OPENSSL_DIR="$prefix" OPENSSL_STATIC=1
"$CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABI_LINKER" -O2 -fPIC \
  -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp \
  -c "$root/getrandom-compat.c" -o "$root/build/getrandom-compat.o"
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABI_RUSTFLAGS="-C link-arg=-Wl,--wrap=getrandom -C link-arg=$root/build/getrandom-compat.o"
export SOURCE_DATE_EPOCH=1792886400 PIP_NO_INDEX=1 CARGO_NET_OFFLINE=true
cd "$root/build/packages/cryptography-50.0.0"
python3.13 -m maturin build --release --locked --offline --jobs 12 \
  --target armv7-unknown-linux-gnueabi --interpreter python3.13 \
  --compatibility linux --out "$root/out/wheels"
