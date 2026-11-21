#!/bin/bash
# Only this source-preparation step needs networking on a fresh build.
set -euo pipefail
root=/project/workspace/python
export PATH="$root/build/rust-toolchain/bin:$PATH"
export CARGO_HOME="$root/build/cargo-fetch-home"
cd "$root/build/packages/cryptography-50.0.0"
cargo vendor --locked --versioned-dirs "$root/build/cargo-vendor"
