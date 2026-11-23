#!/usr/bin/env python3
"""Resolve the pinned runtime dependency graph for CPython 3.13/Linux ARM.

Requires host packaging. This inventories sources; it does not install packages.
Build-system dependencies (PEP 517), BLAS/Fortran/OpenSSL and the interpreter
need their own build manifests before a complete offline build is possible.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tomllib
from packaging.markers import Marker

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'workspace/upstream/alpaca-2.2-beta8'
ENV = {
    'implementation_name': 'cpython', 'implementation_version': '3.13.18',
    'os_name': 'posix', 'platform_machine': 'armv7l',
    'platform_python_implementation': 'CPython', 'platform_release': '4.9.37',
    'platform_system': 'Linux', 'platform_version': '',
    'python_full_version': '3.13.18', 'python_version': '3.13',
    'sys_platform': 'linux', 'extra': '',
}

def applies(marker):
    return not marker or Marker(marker).evaluate(ENV)

def inventory(app_directory=APP, label="2.2.0 Beta 8"):
    lock_file = app_directory / 'uv.lock'
    lock = tomllib.loads(lock_file.read_text())
    packages = lock['package']
    app = next(p for p in packages if p['name'] == 'alpaca-benro-polaris')
    queue = list(app['dependencies'])
    selected = {}
    while queue:
        dep = queue.pop()
        if not applies(dep.get('marker')):
            continue
        candidates = [p for p in packages if p['name'] == dep['name']
                      and ('version' not in dep or p['version'] == dep['version'])
                      and (not p.get('resolution-markers') or
                           any(applies(m) for m in p['resolution-markers']))]
        if len(candidates) != 1:
            raise ValueError(f'Ambiguous/missing locked package: {dep}')
        p = candidates[0]
        if p['name'] in selected:
            if selected[p['name']]['version'] != p['version']:
                raise ValueError('Conflicting dependency versions')
            continue
        selected[p['name']] = p
        queue.extend(p.get('dependencies', []))
    rows = []
    for name, p in sorted(selected.items()):
        source = p.get('sdist')
        if not source:
            raise ValueError('Source distribution missing: ' + name)
        pure = any(w['url'].endswith('-none-any.whl') for w in p.get('wheels', []))
        rows.append({'name': name, 'version': p['version'], 'sdist': source,
                     'build_class': 'universal-wheel-available' if pure else 'native-build-required',
                     'dependencies': [d['name'] for d in p.get('dependencies', [])
                                      if applies(d.get('marker'))]})
    return {'application': 'Alpaca Benro Polaris / Pilot ' + label,
            'lock_sha256': hashlib.sha256(lock_file.read_bytes()).hexdigest(),
            'target_environment': ENV, 'packages': rows,
            'limitations': ['Runtime dependency closure only; build dependencies not yet locked.',
                            'Wheel classification is based on the pinned lock; target builds remain untested.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', choices=['beta8', '2.2.0'], default='beta8')
    args = parser.parse_args()
    modern = args.release == '2.2.0'
    output = ROOT / ('dependencies-2.2.0.json' if modern else 'dependencies.json')
    result = inventory(ROOT / 'workspace/upstream/alpaca-2.2.0' if modern else APP, '2.2.0' if modern else '2.2.0 Beta 8')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(f"Inventoried {len(result['packages'])} pinned runtime packages: {output}")
