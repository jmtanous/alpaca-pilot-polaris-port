#!/bin/bash
# Run inside the build image after prepare-public-sdk.py --output.
# Compile/link only: no mount connection and no execution of the ARM output.
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
sdk="$root/workspace/python/out/public-sdk-sysroot"
out="$root/workspace/python/out/public-sdk-check"
mkdir -p "$out"
cat > "$out/smoke.c" <<'EOF'
#include <stdio.h>
#include <pthread.h>
static void *worker(void *arg) { return arg; }
int main(void) {
    pthread_t thread;
    if (pthread_create(&thread, 0, worker, 0)) return 1;
    pthread_join(thread, 0);
    puts("public SDK link check");
    return 0;
}
EOF
# Debian's packaged cross compiler otherwise searches its newer cross headers
# even with --sysroot. Explicit paths prevent mixing libc header generations.
arm-linux-gnueabi-gcc --sysroot="$sdk" -B"$sdk/usr/lib/arm-linux-gnueabi/" \
    -nostdinc -isystem "$(arm-linux-gnueabi-gcc -print-file-name=include)" \
    -isystem "$sdk/usr/include/arm-linux-gnueabi" -isystem "$sdk/usr/include" \
    -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp \
    "$out/smoke.c" -pthread -o "$out/smoke"
arm-linux-gnueabi-readelf --version-info "$out/smoke" > "$out/versions.txt"
arm-linux-gnueabi-readelf -A "$out/smoke" > "$out/attributes.txt"
python3 - "$out" <<'PY'
import json, re, sys
from pathlib import Path
out = Path(sys.argv[1])
versions = sorted({tuple(map(int, v.split('.'))) for v in
                   re.findall(r'GLIBC_([0-9.]+)', (out/'versions.txt').read_text())})
attributes = (out/'attributes.txt').read_text()
assert versions and max(versions) <= (2, 24), versions
assert 'Tag_CPU_arch: v7' in attributes and 'VFP registers' not in attributes
report = {'compile_link': 'passed', 'glibc_requirements': versions,
          'armv7_soft_float': True, 'executed': False,
          'full_runtime_replacement_build_validated': False}
(out/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
PY
