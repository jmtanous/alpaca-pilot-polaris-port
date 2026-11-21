#!/usr/bin/env python3
"""Build the non-numerical, non-Rust locked packages in an offline crossenv."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path('/project')
WORK = ROOT / 'workspace/python'
PREFIX = WORK / 'prefix/opt/benro-python'
CROSS = WORK / 'build/crossenv/bin/cross-python'
TOOLCHAIN = WORK / 'build/toolchain/bin'
WHEELS = WORK / 'out/wheels'
LOGS = ROOT / 'state/wheels'

def build(package):
    name = package['name']
    archive = WORK / 'downloads' / Path(package['sdist']['url']).name
    if hashlib.sha256(archive.read_bytes()).hexdigest() != package['sdist']['hash'].split(':')[1]:
        raise ValueError('Source hash mismatch: ' + name)
    with tarfile.open(archive) as tar:
        directory = tar.getnames()[0].split('/')[0]
    src = WORK / 'build/packages' / directory
    env = dict(os.environ)
    env.update({
        'CC': str(TOOLCHAIN/'arm-linux-gnueabi-gcc'),
        'CXX': str(TOOLCHAIN/'arm-linux-gnueabi-g++'),
        'AR': 'arm-linux-gnueabi-ar',
        'CFLAGS': '-O2 -fPIC -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -pthread',
        'CPPFLAGS': f'-I{PREFIX}/include',
        'LDFLAGS': f'-L{PREFIX}/lib -Wl,-rpath-link,{PREFIX}/lib',
        'PKG_CONFIG_LIBDIR': str(PREFIX/'lib/pkgconfig'),
        'PKG_CONFIG_SYSROOT_DIR': str(WORK/'prefix'),
        'PIP_NO_INDEX': '1', 'SOURCE_DATE_EPOCH': '1792886400',
        'PATH': str(WORK/'build/crossenv/bin') + ':' + str(WORK/'build/host-python/bin') + ':' + env['PATH'],
    })
    with (LOGS/(name+'.log')).open('w') as log:
        result = subprocess.run([str(CROSS), '-m', 'build', '--wheel', '--no-isolation',
                                 '--outdir', str(WHEELS)], cwd=src, env=env,
                                stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'{name}: build failed; see state/wheels/{name}.log')
    return name

if __name__ == '__main__':
    WHEELS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    packages = [p for p in json.loads((ROOT/'dependencies.json').read_text())['packages']
                if p['name'] not in {'numpy', 'scipy', 'cryptography'}]
    errors = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(build, p) for p in packages]
        for future in as_completed(futures):
            try:
                print('Built:', future.result(), flush=True)
            except Exception as error:
                errors.append(str(error))
                print(error, flush=True)
    if errors:
        raise SystemExit('\n'.join(errors))
