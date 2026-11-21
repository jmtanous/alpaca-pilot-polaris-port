#!/bin/bash
# Public-source fetch is separate; compilation runs in an offline container.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p state
python scripts/fetch-python-sources.py > state/source-fetch.log
python workspace/python/prepare-sources.py > state/source-extraction.log
step() {
  name=$1
  printf 'Running %s (log: state/%s.log)\n' "$name" "$name"
  scripts/python-build-container bash "/project/workspace/python/$name.sh" > "state/$name.log" 2>&1
}
step build-host-python
step build-toolchain
step stage-toolchain-libs
step build-native-libs
step build-compression-sqlite
step build-bzip2
step build-target-python
step create-crossenv
step build-openblas
step install-rust-tools
BENRO_BUILD_NETWORK=bridge step vendor-rust
scripts/python-build-container /project/workspace/python/build/host-python/bin/python3.13 \
  /project/workspace/python/build-wheels.py > state/build-wheels.log 2>&1
step build-numpy
step build-scipy
step build-cryptography
scripts/python-build-container bash -c 'export SOURCE_DATE_EPOCH=1792886400; /project/workspace/python/build/host-python/bin/python3.13 /project/workspace/python/repair-wheel-paths.py; /project/workspace/python/build/host-python/bin/python3.13 /project/workspace/python/install-wheels.py /project/workspace/python/out/portable-wheels/*.whl' > state/install-portable-wheels.log 2>&1
scripts/python-build-container /project/workspace/python/build/host-python/bin/python3.13 \
  /project/workspace/python/package-runtime.py > state/runtime-package.json
python workspace/python/verify-bundle.py workspace/python/out/runtime-root
scripts/python-build-container /project/workspace/python/build/host-python/bin/python3.13 \
  /project/workspace/python/make-sd-bundle.py > state/sd-runtime-package.json
printf '%s\n' 'Linux and FAT SD bundles built. Run ABI and fresh captured-runtime acceptance before physical use.'
