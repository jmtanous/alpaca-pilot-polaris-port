#!/usr/bin/env python3
"""Prepare pinned Python/GCC sources, applied patch and build recipes offline."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', choices=['beta8', '2.2.0'], default='beta8')
parser.add_argument('--dev-env', type=Path, default=root.parent.parent/'dev-env',
                    help='Shared development recipe checkout')
parser.add_argument('--downloads', type=Path, default=root/'workspace/python/downloads')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output is None:
    suffix = '' if args.release == 'beta8' else '-2.2.0'
    args.output = root/('workspace/python/out/copyleft-source-companion'+suffix+'.tar.gz')
dependencies = 'dependencies.json' if args.release == 'beta8' else 'dependencies-2.2.0.json'
entries = {}
packages = []
for package in json.loads((root/dependencies).read_text())['packages']:
    if package['name'] not in {'certifi', 'zeroconf', 'ifaddr'}:
        continue
    source = package['sdist']
    name = Path(urlsplit(source['url']).path).name
    data = (args.downloads/name).read_bytes()
    if hashlib.sha256(data).hexdigest() != source['hash'].removeprefix('sha256:'):
        raise SystemExit('Source hash mismatch: '+name)
    entries['sources/'+name] = data
    packages.append(package)
if len(packages) != 3:
    raise SystemExit('Expected certifi, zeroconf and supporting ifaddr source pins')
gcc = {
    'gcc-12.2.0-dfsg.tar.xz': '50c63ff82919323c25fbbb4a9eae259edc974118a0fb30c905190cb782ec11c2',
    'gcc-gfdl-build.diff': '29b36f739f29959b580364a7aff45a0f291a6bd7c803af6794b737130acfb751',
}
for name, expected in gcc.items():
    data = (args.downloads/name).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit('GCC source/patch hash mismatch: '+name)
    entries['sources/'+name] = data
for name in ['dependencies.json', 'SOURCE-AVAILABILITY.md', 'BUILDING.md',
             'LICENSE', 'UPSTREAM-LICENSE.txt', 'THIRD-PARTY-NOTICES.md',
             'VERSION', 'Dockerfile', 'lab-provenance.json',
             'RECOVERED-NOTICES.json', 'DEPENDENCY-NOTICE-REVIEW.json']:
    entries['recipes/'+name] = (root/name).read_bytes()
provenance = json.loads(entries['recipes/lab-provenance.json'])
upstream = provenance['upstream']
entries['recipes/lab-provenance.json'] = (json.dumps({
    'project': 'Alpaca Pilot Polaris Port',
    'base_upstream': {key: upstream[key] for key in ('release', 'repository', 'license')},
    'base_upstream_archive_sha256': upstream.get('sha256', upstream.get('source_archive_sha256')),
    'scope': 'Public build recipes; private VM snapshots, device configuration and session scripts excluded.',
}, indent=2)+'\n').encode()
recipe_files = json.loads((root/'SOURCE-RECIPE-FILES.json').read_text())
for name in recipe_files:
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Invalid source recipe path')
    entries['recipes/'+name] = (root/path).read_bytes()
entries['recipes/SOURCE-RECIPE-FILES.json'] = (root/'SOURCE-RECIPE-FILES.json').read_bytes()
entries['recipes/'+dependencies] = (root/dependencies).read_bytes()
if args.release == '2.2.0':
    upstream = json.loads((root/'docs/upstream-v2.2.0.json').read_text())
    upstream.pop('source_directory', None)
    entries['recipes/docs/upstream-v2.2.0.json'] = (json.dumps(upstream,indent=2)+'\n').encode()
    for name in ['RECOVERED-NOTICES.json', 'DEPENDENCY-NOTICE-REVIEW.json']:
        entries['recipes/'+name] = (root/'workspace/python/out/license-review-2.2.0'/name).read_bytes()
# Project VM wrappers refer to shared tooling; include those exact recipes so
# the companion remains useful independently of the workspace layout.
shared = args.dev_env
for name in ['Dockerfile', 'public-sdk.json', 'LICENSE', 'SOURCE-PROVENANCE.json',
             'benro-dev', 'README.md', 'VERSION', '.dockerignore']:
    entries['recipes/dev-env/'+name] = (shared/name).read_bytes()
for path in (shared/'scripts').glob('*'):
    if path.is_file(): entries['recipes/dev-env/scripts/'+path.name] = path.read_bytes()
for path in (shared/'templates').rglob('*'):
    if path.is_file(): entries['recipes/dev-env/'+str(path.relative_to(shared))] = path.read_bytes()
entries['SOURCE-MANIFEST.json'] = (json.dumps({'release': args.release, 'packages': packages,
    'gcc': {'debian_source_package': 'gcc-12-source 12.2.0-14+deb12u1',
            'inputs': gcc, 'libraries': ['libatomic', 'libgcc_s', 'libgfortran', 'libstdc++']},
    'validation_scope': 'Source/hash packaging; release acceptance receipts record runtime replacement tests separately.',
    'sha256': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(entries.items())}},
    indent=2, sort_keys=True)+'\n').encode()
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=1792886400) as gz:
    with tarfile.open(fileobj=gz, mode='w|') as tar:
        for name, data in sorted(entries.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 1792886400
            tar.addfile(info, io.BytesIO(data))
print(json.dumps({'archive': args.output.name,
    'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
    'packages': [p['name'] for p in packages], 'files': len(entries)}, indent=2))
