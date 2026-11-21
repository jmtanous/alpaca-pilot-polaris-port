#!/usr/bin/env python3
"""Make a deterministic, symlink-free bundle for the captured Benro FAT SD mount."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

work = Path(__file__).resolve().parent
source = work/'out/runtime-root'
stage = work/'out/runtime-sd-root'
archive = work/'out/benro-alpaca-pilot-2.2-beta8-python313-armel-sd-fat.tar.gz'
epoch = 1792886400
subprocess.run([sys.executable, str(work/'verify-bundle.py'), str(source)], check=True, stdout=sys.stderr)
original = json.loads((source/'BUNDLE-MANIFEST.json').read_text())
names = [p.relative_to(source).as_posix() for p in source.rglob('*')]
assert len({n.casefold() for n in names}) == len(names), 'Case-insensitive filename collision'
for name in names:
    assert name.isascii(), f'Non-ASCII filename requires explicit FAT encoding validation: {name}'
    for part in Path(name).parts:
        assert len(part) <= 255 and not part.endswith((' ', '.')), name
        assert not any(c in part for c in ':*?"<>|\\'), name
if stage.exists():
    shutil.rmtree(stage)  # Dedicated ignored packaging output only.
shutil.copytree(source, stage, symlinks=True)
links = {}
for path in sorted(stage.rglob('*')):
    if path.is_symlink():
        resolved = path.resolve(strict=True)
        assert resolved.is_relative_to(stage) and resolved.is_file(), path
        links[path.relative_to(stage).as_posix()] = path.readlink().as_posix()
        data = resolved.read_bytes()
        path.unlink()
        path.write_bytes(data)
provenance = stage/'opt/benro-python/share/build/sd-layout.json'
provenance.write_text(json.dumps({
    'filesystem': 'FAT with fmask=0022,dmask=0022, executable mount',
    'source_manifest_sha256': hashlib.sha256((source/'BUNDLE-MANIFEST.json').read_bytes()).hexdigest(),
    'replaced_symlinks': links,
    'application_and_runtime_code_modified': False,
}, indent=2, sort_keys=True)+'\n')
manifest = {key: value for key, value in original.items() if key != 'files'}
manifest['storage_profile'] = 'FAT SD: regular files only; modes match captured fmask=0022,dmask=0022'
manifest['files'] = {}
elf_count = 0
for path in sorted(stage.rglob('*')):
    assert not path.is_symlink(), path
    path.chmod(0o755)
    if path.is_file() and path != stage/'BUNDLE-MANIFEST.json':
        data = path.read_bytes()
        elf_count += data.startswith(b'\x7fELF')
        manifest['files'][path.relative_to(stage).as_posix()] = {
            'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data), 'mode': '0o755'}
manifest['stripped_elf_objects'] = elf_count
(stage/'BUNDLE-MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
subprocess.run([sys.executable, str(work/'verify-bundle.py'), str(stage)], check=True, stdout=sys.stderr)
with archive.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=epoch) as compressed:
    with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(stage.rglob('*')):
            info = tar.gettarinfo(str(path), arcname=path.relative_to(stage).as_posix())
            info.uid = info.gid = 0
            info.uname = info.gname = 'root'
            info.mtime = epoch
            info.pax_headers = {}
            assert info.isfile() or info.isdir()
            if info.isfile():
                with path.open('rb') as stream:
                    tar.addfile(info, stream)
            else:
                tar.addfile(info)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_name(archive.name+'.sha256').write_text(digest+'  '+archive.name+'\n')
print(json.dumps({'archive': archive.name, 'sha256': digest,
    'compressed_bytes': archive.stat().st_size,
    'installed_file_bytes': sum(value['size'] for value in manifest['files'].values()),
    'files': len(manifest['files']), 'elf_objects': elf_count,
    'symlinks_replaced': len(links), 'case_insensitive_names_checked': True}, indent=2))
