#!/usr/bin/env python3
"""Prepare exact certifi/zeroconf source archives and build recipes, offline."""
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
parser.add_argument('--downloads', type=Path, default=root/'workspace/python/downloads')
parser.add_argument('--output', type=Path, default=root/'workspace/python/out/copyleft-source-companion.tar.gz')
args = parser.parse_args()
entries = {}
packages = []
for package in json.loads((root/'dependencies.json').read_text())['packages']:
    if package['name'] not in {'certifi', 'zeroconf'}:
        continue
    source = package['sdist']
    name = Path(urlsplit(source['url']).path).name
    data = (args.downloads/name).read_bytes()
    if hashlib.sha256(data).hexdigest() != source['hash'].removeprefix('sha256:'):
        raise SystemExit('Source hash mismatch: '+name)
    entries['sources/'+name] = data
    packages.append(package)
if len(packages) != 2:
    raise SystemExit('Expected certifi and zeroconf source pins')
for name in ['dependencies.json', 'SOURCE-AVAILABILITY.md', 'BUILDING.md']:
    entries['recipes/'+name] = (root/name).read_bytes()
for path in (root/'workspace/python').iterdir():
    if path.is_file() and path.suffix in {'.py', '.sh', '.json', '.lock'}:
        entries['recipes/workspace/python/'+path.name] = path.read_bytes()
for path in (root/'workspace/python/patches').rglob('*'):
    if path.is_file():
        entries['recipes/'+str(path.relative_to(root))] = path.read_bytes()
entries['SOURCE-MANIFEST.json'] = (json.dumps({'packages': packages,
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
