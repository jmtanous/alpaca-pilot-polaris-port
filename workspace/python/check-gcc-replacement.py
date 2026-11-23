#!/usr/bin/env python3
"""Exercise rebuilt GCC libraries with the frozen ARM Python runtime under QEMU.

No mount or network operations; the runtime files are never changed.
Requires readelf and qemu-arm-static on the host.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sdk', type=Path, default=root/'workspace/python/out/public-sdk-sysroot')
parser.add_argument('--libraries', type=Path, default=root/'workspace/python/out/public-toolchain/build/toolchain/arm-linux-gnueabi/lib')
parser.add_argument('--output', type=Path, default=root/'workspace/python/out/public-sdk-check/gcc-replacement-validation.json')
parser.add_argument('--runtime-prefix', type=Path,
                    default=root/'workspace/python/out/runtime-sd-root/opt/benro-python')
args = parser.parse_args()
prefix = args.runtime_prefix.resolve()
sdk = args.sdk.resolve()
libraries = args.libraries.resolve()
names = ['libatomic.so.1', 'libgcc_s.so.1', 'libgfortran.so.5', 'libstdc++.so.6']
rows = []
for name in names:
    path = libraries/name
    symbols = subprocess.check_output(['readelf', '--version-info', str(path)], text=True)
    needs = symbols.split('Version needs section', 1)[1]
    versions = sorted({tuple(map(int, v.split('.'))) for v in re.findall(r'GLIBC_([0-9.]+)', needs)})
    assert versions and max(versions) <= (2, 24), (name, versions)
    rows.append({'library': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'max_glibc': versions[-1]})
code = '''
import ctypes, os, sys
directory = sys.argv[1]
names = ['libatomic.so.1', 'libgcc_s.so.1', 'libgfortran.so.5', 'libstdc++.so.6']
handles = [ctypes.CDLL(os.path.join(directory, name), mode=ctypes.RTLD_GLOBAL) for name in names]
import numpy as np, scipy.linalg, zeroconf, certifi
from cryptography.hazmat.primitives import hashes
assert np.allclose(scipy.linalg.solve(np.array([[2., 0.], [0., 4.]]), np.array([4., 8.])), [2., 2.])
h = hashes.Hash(hashes.SHA256())
h.update(b'mmt')
assert len(h.finalize()) == 32
maps = open('/proc/self/maps').read()
for name in names:
    assert os.path.realpath(os.path.join(directory, name)) in maps, name
print('ARM runtime loaded rebuilt GCC libraries; numeric and cryptography checks passed')
'''
subprocess.run(['qemu-arm-static', '-L', str(sdk),
                '-E', 'PYTHONHOME='+str(prefix),
                '-E', 'LD_LIBRARY_PATH='+str(libraries)+':'+str(prefix/'lib'),
                str(prefix/'bin/python3.13'), '-B', '-c', code, str(libraries)], check=True)
report = {'gcc_build': 'passed', 'libraries': rows,
          'arm_runtime_imports_and_numeric_crypto_operations': 'passed',
          'rebuilt_library_mappings_verified': True,
          'physical_mount_tested': False, 'original_runtime_modified': False}
output = args.output
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
