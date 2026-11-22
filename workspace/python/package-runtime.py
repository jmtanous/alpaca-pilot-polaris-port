#!/usr/bin/env python3
"""Create a deterministic runtime candidate archive from validated build outputs.

No install, service, network, firmware or hardware operation is performed.
"""
import gzip
import base64
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path('/project')
WORK = ROOT/'workspace/python'
OUT = WORK/'out'
STAGE = OUT/'runtime-root'
PREFIX = STAGE/'opt/benro-python'
APP = STAGE/'opt/alpaca-pilot-2.2'
EPOCH = 1792886400

if STAGE.exists():
    shutil.rmtree(STAGE)  # Dedicated generated packaging tree only.
PREFIX.mkdir(parents=True)
(PREFIX/'bin').mkdir()
shutil.copy2(WORK/'prefix/opt/benro-python/bin/python3.13', PREFIX/'bin/python3.13')
(PREFIX/'bin/python3').symlink_to('python3.13')
shutil.copy2(WORK/'pilot-launcher.sh', PREFIX/'bin/pilot')
(PREFIX/'bin/pilot').chmod(0o755)
(PREFIX/'share/pilot').mkdir(parents=True)
shutil.copy2(WORK/'pilot_native.py', PREFIX/'share/pilot/pilot_native.py')
(PREFIX/'lib').mkdir()
for path in (WORK/'prefix/opt/benro-python/lib').glob('*.so*'):
    if path.is_symlink():
        (PREFIX/'lib'/path.name).symlink_to(os.readlink(path))
    else:
        shutil.copy2(path, PREFIX/'lib'/path.name)

def ignore(directory, names):
    ignored = {n for n in names if n == '__pycache__' or n.endswith(('.pyc', '.a'))}
    # Remove interpreter development config; preserve all runtime package files.
    if directory.endswith('/lib/python3.13'):
        ignored.update(n for n in names if n in {'test', 'idlelib', 'tkinter', 'turtledemo', 'ensurepip'} or n.startswith('config-'))
    return ignored

shutil.copytree(WORK/'prefix/opt/benro-python/lib/python3.13', PREFIX/'lib/python3.13', ignore=ignore)
source = ROOT/'workspace/upstream/alpaca-2.2-beta8'
APP.mkdir()
for name in ['driver', 'data', 'src']:
    shutil.copytree(source/name, APP/name, ignore=ignore)
shutil.copytree(source/'pilot/dist/spa', APP/'pilot/dist/spa')
for name in ['LICENSE', 'README.md', 'SECURITY.md', 'pyproject.toml', 'uv.lock', 'LAB-SOURCE-RECEIPT.json']:
    shutil.copy2(source/name, APP/name)
shutil.copy2(source/'pilot/package.json', APP/'pilot/package.json')
assert not (APP/'data/config.pilot.json').exists()

licenses = PREFIX/'share/licenses'
licenses.mkdir(parents=True, exist_ok=True)
port_licenses = licenses/'port'
port_licenses.mkdir()
for name in ['LICENSE', 'UPSTREAM-LICENSE.txt', 'THIRD-PARTY-NOTICES.md', 'SOURCE-AVAILABILITY.md']:
    shutil.copy2(ROOT/name, port_licenses/name)
recovered = json.loads((ROOT/'RECOVERED-NOTICES.json').read_text())
for name, text in recovered.items():
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe recovered notice path: '+name)
    destination = licenses/'recovered'/relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text)
license_files = {
    'cpython': ['Python-3.13.18/LICENSE'],
    'openssl': ['openssl-3.5.9/LICENSE.txt'],
    'zlib': ['zlib-1.4/LICENSE'],
    'libffi': ['libffi-3.8.1/LICENSE'],
    'xz': ['xz-5.8.4/COPYING', 'xz-5.8.4/COPYING.0BSD', 'xz-5.8.4/COPYING.LGPLv2.1'],
    'bzip2': ['bzip2-1.0.8/LICENSE'],
    'openblas': ['OpenBLAS-0.3.34/LICENSE'],
    'gcc-runtime': ['gcc-source/gcc-12.2.0/COPYING3', 'gcc-source/gcc-12.2.0/COPYING.RUNTIME'],
    'rust-runtime': ['rustc-1.100.0-x86_64-unknown-linux-gnu/LICENSE-MIT',
        'rustc-1.100.0-x86_64-unknown-linux-gnu/LICENSE-APACHE',
        'rustc-1.100.0-x86_64-unknown-linux-gnu/rustc/share/doc/rust/COPYRIGHT-library.html'],
}
for component, files in license_files.items():
    destination = licenses/component
    destination.mkdir()
    for filename in files:
        path = WORK/'build'/filename
        shutil.copy2(path, destination/path.name)
(licenses/'sqlite-public-domain.txt').write_text(
    (WORK/'build/sqlite-autoconf-3540100/sqlite3.h').read_text().split('*/', 1)[0]+'*/\n')
for package in json.loads((ROOT/'dependencies.json').read_text())['packages']:
    # Supplement wheel notices with original source license files.
    sources = list((WORK/'build/packages').glob(package['name'].replace('-', '_')+'-'+package['version']))
    sources += list((WORK/'build/packages').glob(package['name']+'-'+package['version']))
    for package_source in set(sources):
        for path in package_source.iterdir():
            if path.is_file() and path.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE', 'AUTHORS')):
                destination = licenses/package['name']
                destination.mkdir(exist_ok=True)
                shutil.copy2(path, destination/path.name)

provenance = PREFIX/'share/build'
provenance.mkdir(parents=True)
for path in [ROOT/'dependencies.json', ROOT/'lab-provenance.json', WORK/'sources.json',
    WORK/'build-tools.json', WORK/'build-environment.json', WORK/'build-container-packages.lock',
    OUT/'wheel-path-repairs.json']:
    shutil.copy2(path, provenance/path.name)
shutil.copytree(WORK/'patches', provenance/'patches')
shutil.copy2(WORK/'getrandom-compat.c', provenance/'getrandom-compat.c')

elf_count = 0
for path in PREFIX.rglob('*'):
    if path.is_file() and not path.is_symlink():
        with path.open('rb') as f:
            is_elf = f.read(4) == b'\x7fELF'
        if is_elf:
            subprocess.run(['arm-linux-gnueabi-strip', '--strip-unneeded', str(path)], check=True)
            elf_count += 1

# Stripping changes ELF bytes; keep distribution integrity records accurate.
site = PREFIX/'lib/python3.13/site-packages'
for record in site.glob('*.dist-info/RECORD'):
    rows = []
    with record.open(newline='') as f:
        for name, _, _ in csv.reader(f):
            path = (site/name).resolve()
            assert path.is_relative_to(PREFIX.resolve()), name
            if not path.is_file():
                continue  # Development archives/CLI scripts omitted from this bundle.
            if path == record.resolve():
                rows.append([name, '', ''])
            else:
                data = path.read_bytes()
                digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')
                rows.append([name, 'sha256='+digest, str(len(data))])
    with record.open('w', newline='') as f:
        csv.writer(f).writerows(rows)

manifest = {'format': 1, 'application': 'Alpaca/Pilot 2.2.0 Beta 8',
    'port_version': (ROOT/'VERSION').read_text().strip(),
    'entrypoint': 'opt/benro-python/bin/pilot',
    'bootstrap': 'opt/benro-python/share/pilot/pilot_native.py',
    'python': '3.13.18', 'target': 'ARMv7 EABI soft-float; glibc <=2.24',
    'configuration': 'Disconnected lab target 127.0.0.1:19090; no automatic connection',
    'stripped_elf_objects': elf_count, 'files': {}}
for path in sorted(STAGE.rglob('*')):
    name = path.relative_to(STAGE).as_posix()
    if path.is_symlink():
        manifest['files'][name] = {'symlink': os.readlink(path)}
    elif path.is_file():
        manifest['files'][name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                  'size': path.stat().st_size, 'mode': oct(path.stat().st_mode & 0o777)}
(STAGE/'BUNDLE-MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
archive = OUT/'benro-alpaca-pilot-2.2-beta8-python313-armel.tar.gz'
with archive.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=EPOCH) as compressed:
    with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(STAGE.rglob('*')):
            info = tar.gettarinfo(str(path), arcname=path.relative_to(STAGE).as_posix())
            info.uid = info.gid = 0
            info.uname = info.gname = 'root'
            info.mtime = EPOCH
            info.pax_headers = {}
            if info.isfile():
                with path.open('rb') as f:
                    tar.addfile(info, f)
            else:
                tar.addfile(info)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(archive.with_name(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n')
print(json.dumps({'archive': archive.name, 'sha256': digest, 'compressed_bytes': archive.stat().st_size,
    'installed_file_bytes': sum(x.get('size', 0) for x in manifest['files'].values()),
    'elf_objects': elf_count, 'files': len(manifest['files'])}, indent=2))
