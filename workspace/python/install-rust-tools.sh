#!/bin/bash
set -euo pipefail
root=/project/workspace/python
prefix="$root/build/rust-toolchain"
for component in rustc-1.100.0-x86_64-unknown-linux-gnu \
  cargo-1.100.0-x86_64-unknown-linux-gnu \
  rust-std-1.100.0-x86_64-unknown-linux-gnu \
  rust-std-1.100.0-armv7-unknown-linux-gnueabi; do
  bash "$root/build/$component/install.sh" --prefix="$prefix" --disable-ldconfig
done
"$prefix/bin/rustc" -vV
"$prefix/bin/cargo" --version
