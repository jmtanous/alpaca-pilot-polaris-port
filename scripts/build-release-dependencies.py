#!/usr/bin/env python3
"""Build changed 2.2.0 dependencies without modifying the Beta 8 wheel set.

Fetch on the host; build inside the pinned offline build container. Existing
unchanged portable wheels are selected by exact locked name/version and hashed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'workspace/python'
OUT = WORK / 'out/releases/2.2.0'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def changed():
    old = {p['name']: p['version'] for p in json.loads((ROOT/'dependencies.json').read_text())['packages']}
    return [p for p in json.loads((ROOT/'dependencies-2.2.0.json').read_text())['packages']
            if old.get(p['name']) != p['version']]

def fetch():
    fetcher = module('release_fetch', ROOT/'scripts/fetch-python-sources.py')
    fetcher.OUT.mkdir(exist_ok=True, parents=True)
    for p in changed():
        s = p['sdist']
        print(fetcher.fetch({'url': s['url'], 'sha256': s['hash'].removeprefix('sha256:')}), flush=True)

def build():
    builder = module('release_builder', WORK/'build-wheels.py')
    builder.WHEELS = OUT/'wheels'
    builder.LOGS = ROOT/'state/wheels-2.2.0'
    builder.WHEELS.mkdir(parents=True, exist_ok=True)
    builder.LOGS.mkdir(parents=True, exist_ok=True)
    for p in changed():
        archive = WORK/'downloads'/p['sdist']['url'].rsplit('/', 1)[1]
        if hashlib.sha256(archive.read_bytes()).hexdigest() != p['sdist']['hash'].removeprefix('sha256:'):
            raise ValueError('Source hash mismatch: '+p['name'])
        with tarfile.open(archive) as tar:
            roots = {Path(m.name).parts[0] for m in tar if m.name not in ('.', './')}
            if len(roots) != 1: raise ValueError('Unexpected source archive layout')
            destination = WORK/'build/packages'
            if not (destination/next(iter(roots))).exists():
                tar.extractall(destination, filter='data')
        print('Built: '+builder.build(p), flush=True)
    (OUT/'build-receipt.json').write_text(json.dumps({
        'release': '2.2.0', 'changed': changed(),
        'wheels': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(builder.WHEELS.glob('*.whl'))},
        'target_validation': 'pending',
    }, indent=2)+'\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['fetch', 'build'])
    args = parser.parse_args()
    {'fetch': fetch, 'build': build}[args.action]()
