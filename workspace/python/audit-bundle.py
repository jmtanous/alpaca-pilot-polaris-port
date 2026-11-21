#!/usr/bin/env python3
"""Audit every ELF object in a Python bundle against captured target libraries.

Run with guest Python outside the chroot. Never execute the audited objects.
Extension symbols may resolve against the Python executable and its dependency
closure. Other dependencies must resolve within the bundle/captured userspace.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

spec = importlib.util.spec_from_file_location('target_audit', Path(__file__).with_name('audit.py'))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

def elf(path):
    with path.open('rb') as f:
        return f.read(4) == b'\x7fELF'

def inspect(root, path, prefix):
    header = helper.readelf(path, '-h')
    for value in ['ELF32', 'little endian', 'ARM', 'Version5 EABI']:
        if value not in header:
            raise ValueError(f'{path}: wrong architecture/ABI ({value})')
    relocatable = bool(re.search(r'Type:\s+REL\b', header))
    # Relocatable CPython development objects do not carry the linker's float
    # ABI flag. ARM ELF attributes use the base AAPCS when VFP_args is absent.
    if relocatable:
        attributes = helper.readelf(path, '-A')
        if 'Tag_ABI_VFP_args: VFP registers' in attributes or 'hard-float ABI' in header:
            raise ValueError(f'{path}: hard-float relocatable object')
    elif 'soft-float ABI' not in header:
        raise ValueError(f'{path}: missing soft-float ABI flag')
    program = helper.readelf(path, '-l')
    interpreter = re.findall(r'\[Requesting program interpreter: (.*?)\]', program)
    if interpreter and interpreter != ['/lib/ld-linux.so.3']:
        raise ValueError(f'{path}: incorrect interpreter {interpreter}')
    versions = helper.readelf(path, '--version-info').partition('Version needs section')[2]
    for version in re.findall(r'GLIBC_([0-9.]+)', versions):
        if tuple(map(int, version.split('.'))) > (2, 24):
            raise ValueError(f'{path}: requires GLIBC_{version}')
    dynamic = helper.readelf(path, '-d')
    search = []
    for value in re.findall(r'\((?:RPATH|RUNPATH)\).*?\[(.*?)\]', dynamic):
        for entry in value.split(':'):
            if not entry.startswith(('$ORIGIN', '${ORIGIN}')):
                raise ValueError(f'{path}: unapproved library search path {entry}')
            origin = '/' + str(path.parent.relative_to(root))
            expanded = os.path.normpath(entry.replace('${ORIGIN}', origin).replace('$ORIGIN', origin))
            if not (expanded == prefix or expanded.startswith(prefix + '/')):
                raise ValueError(f'{path}: library search path escapes bundle')
            search.append(expanded)
    search.extend([prefix + '/lib', '/lib', '/usr/lib', '/app/lib'])
    needed = []
    for name in re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic):
        if '/' in name:
            raise ValueError(f'{path}: non-SONAME dependency {name}')
        found = None
        for directory in search:
            try:
                found = helper.resolve(root, directory + '/' + name)
                break
            except ValueError:
                pass
        if found is None:
            raise ValueError(f'{path}: missing dependency {name}')
        needed.append(found)
    if interpreter:
        needed.append(helper.resolve(root, interpreter[0]))
    exports, undefined = set(), set()
    for line in helper.readelf(path, '--dyn-syms', '--wide').splitlines():
        cols = line.split()
        if len(cols) < 8 or not cols[0].endswith(':') or cols[4] not in ('GLOBAL', 'WEAK'):
            continue
        name = cols[7].replace('@@', '@')
        if cols[6] == 'UND':
            if cols[4] == 'GLOBAL':
                undefined.add(name)
        else:
            exports.update([name, name.split('@')[0]])
    return {'needed': needed, 'exports': exports, 'undefined': undefined,
            'sha256': helper.digest(path)}

def audit(root, prefix, extra_trees=()):
    bundle = root / prefix.lstrip('/')
    binary = helper.resolve(root, prefix + '/bin/python3.13')
    objects = sorted({p.resolve() for p in bundle.rglob('*') if p.is_file() and elf(p)})
    bundle_count = len(objects)
    for tree in extra_trees:
        directory = root / tree.lstrip('/')
        if not directory.resolve().is_relative_to(root):
            raise ValueError('Extra audit tree escapes runtime root')
        objects.extend(p.resolve() for p in directory.rglob('*') if p.is_file() and elf(p))
    objects = sorted(set(objects))
    if not objects:
        raise ValueError('No ELF objects found')
    info = {}
    def closure(start):
        todo = list(start)
        seen = set()
        while todo:
            path = todo.pop()
            if path in seen:
                continue
            seen.add(path)
            if path not in info:
                info[path] = inspect(root, path, prefix)
            todo.extend(info[path]['needed'])
        return seen
    base = closure([binary])
    for path in objects:
        current = closure([path]) | base
        exports = set().union(*(info[p]['exports'] for p in current))
        missing = {str(p.relative_to(root)): sorted(info[p]['undefined'] - exports)
                   for p in current if info[p]['undefined'] - exports}
        if missing:
            raise ValueError('Unresolved strong symbols: ' + json.dumps(missing))
    return {'result': 'passed', 'bundle': prefix, 'glibc_ceiling': '2.24',
            'elf_objects_in_bundle': bundle_count,
            'extra_trees': list(extra_trees), 'extra_elf_objects': len(objects)-bundle_count,
            'objects': {str(p.relative_to(root)): {'sha256': d['sha256'],
                'needed': [str(n.relative_to(root)) for n in d['needed']]}
                for p, d in sorted(info.items())}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('/opt/benro-target'))
    parser.add_argument('--prefix', default='/opt/benro-python')
    parser.add_argument('--extra-tree', action='append', default=[])
    args = parser.parse_args()
    print(json.dumps(audit(args.root.resolve(), args.prefix, args.extra_tree), indent=2))
