#!/bin/bash
set -euo pipefail
root=/project/workspace/python
export PATH="$root/build/crossenv/bin:$root/build/host-python/bin:$PATH"
export PKG_CONFIG_LIBDIR="$root/prefix/opt/benro-python/lib/pkgconfig:$root/prefix/opt/benro-python/lib/python3.13/site-packages/numpy/_core/lib/pkgconfig"
export PKG_CONFIG_SYSROOT_DIR="$root/prefix"
export SOURCE_DATE_EPOCH=1792886400 PIP_NO_INDEX=1
mkdir -p "$root/out/test-wheels"
python3.13 -m pip install --no-index --find-links "$root/downloads" \
  --require-hashes -r "$root/build-requirements.lock"
python3.13 - <<'PY'
import hashlib, json, pathlib, shutil
root = pathlib.Path('/project/workspace/python')
for p in json.loads((root/'test-dependencies.json').read_text())['packages']:
    if 'wheel' not in p: continue
    w = p['wheel']
    source = root/'downloads'/w['url'].rsplit('/', 1)[1]
    assert source.name.endswith('none-any.whl')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == w['hash'].split(':')[1]
    shutil.copy2(source, root/'out/test-wheels'/source.name)
PY
cd "$root/build/packages/pandas-3.0.5"
if ! grep -q 'numpy-include-dir' pandas/meson.build; then
  patch -p1 < "$root/patches/pandas-target-numpy-headers.patch"
fi
cross-python -m build --wheel --no-isolation --outdir "$root/out/test-wheels" \
  -Csetup-args="--cross-file=$root/meson-arm.ini" -Ccompile-args=-j12
