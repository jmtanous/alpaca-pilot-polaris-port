#!/usr/bin/env python3
"""Create a notice-only successor to the audited runtime without executing it."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Input and output must differ')
    report = json.loads((root/'DEPENDENCY-NOTICE-REVIEW.json').read_text())
    if sha(args.input.read_bytes()) != report['runtime_sha256']:
        raise SystemExit('Input differs from audited runtime')
    entries = {}
    with tarfile.open(args.input) as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir()):
                raise SystemExit('Unsafe archive entry: '+member.name)
            if member.name in entries:
                raise SystemExit('Duplicate archive entry: '+member.name)
            entries[member.name] = (member, archive.extractfile(member).read() if member.isfile() else b'')
    manifest = json.loads(entries.pop('BUNDLE-MANIFEST.json')[1])
    original = {name: sha(data) for name, (info, data) in entries.items() if info.isfile()}
    if set(original) != set(manifest['files']):
        raise SystemExit('Input manifest file set mismatch')
    for name, digest in original.items():
        if digest != manifest['files'][name]['sha256']:
            raise SystemExit('Input manifest hash mismatch: '+name)

    def add(name, data):
        info = tarfile.TarInfo(name)
        info.size = len(data)
        info.mode = 0o644
        entries[name] = (info, data)

    prefix = 'opt/benro-python/share/licenses/'
    for name, text in json.loads((root/'RECOVERED-NOTICES.json').read_text()).items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts:
            raise SystemExit('Unsafe notice path: '+name)
        add(prefix+'recovered/'+name, text.encode())
    for name in ['SOURCE-AVAILABILITY.md', 'THIRD-PARTY-NOTICES.md']:
        add(prefix+'port/'+name, (root/name).read_bytes())
    manifest['port_version'] = (root/'VERSION').read_text().strip()
    manifest['files'] = {
        name: {'sha256': sha(data), 'size': len(data), 'mode': oct(info.mode)}
        for name, (info, data) in sorted(entries.items()) if info.isfile()
    }
    changed = [name for name, digest in original.items()
               if sha(entries[name][1]) != digest]
    if any(not name.startswith(prefix) for name in changed):
        raise SystemExit('Unexpected non-notice change')
    add('BUNDLE-MANIFEST.json', (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=1792886400) as gz:
        with tarfile.open(fileobj=gz, mode='w|', format=tarfile.PAX_FORMAT) as archive:
            for name, (info, data) in sorted(entries.items()):
                info.uid = info.gid = 0
                info.uname = info.gname = 'root'
                info.mtime = 1792886400
                info.pax_headers = {}
                archive.addfile(info, io.BytesIO(data) if info.isfile() else None)
    print(json.dumps({'sha256': sha(args.output.read_bytes()), 'port_version': manifest['port_version'],
                      'changed_existing_files': changed, 'unchanged_existing_files': len(original)-len(changed),
                      'added_files': len(manifest['files'])-len(original)}, indent=2))


if __name__ == '__main__':
    main()
