#!/usr/bin/env python3
"""Replace staging-only ELF search paths with bundle-relative paths.

Keep original wheels; regenerate RECORD in repaired wheels and record hashes.
No symbol, code, ABI version or dependency is removed or renamed.
"""
import hashlib
import json
from pathlib import Path
import posixpath
import shutil
import subprocess
import tempfile
from wheel._commands.pack import pack
from wheel._commands.unpack import unpack

root = Path('/project/workspace/python')
out = root/'out/portable-wheels'
out.mkdir(exist_ok=True)
changes = []
for wheel in sorted((root/'out/wheels').glob('*.whl')):
    modified = []
    with tempfile.TemporaryDirectory(dir=root/'build', prefix='wheel-paths-') as temp:
        unpack(str(wheel), temp)
        directory, = Path(temp).iterdir()
        for path in directory.rglob('*'):
            if not path.is_file():
                continue
            with path.open('rb') as f:
                if f.read(4) != b'\x7fELF':
                    continue
            old = subprocess.check_output(['patchelf', '--print-rpath', str(path)], text=True).strip()
            if not old:
                continue
            relative = path.relative_to(directory).as_posix()
            installed = '/opt/benro-python/lib/python3.13/site-packages/' + relative
            replacement = '$ORIGIN/' + posixpath.relpath('/opt/benro-python/lib', posixpath.dirname(installed))
            entries = []
            for entry in old.split(':'):
                if entry == str(root/'prefix/opt/benro-python/lib'):
                    entry = replacement
                elif not entry.startswith(('$ORIGIN', '${ORIGIN}')):
                    raise ValueError(f'Unexpected search path in {wheel.name}: {entry}')
                if entry not in entries:
                    entries.append(entry)
            new = ':'.join(entries)
            if old != new:
                subprocess.run(['patchelf', '--set-rpath', new, str(path)], check=True)
                modified.append({'file': relative, 'before': old, 'after': new})
        if modified:
            pack(str(directory), str(out), None)
        else:
            shutil.copy2(wheel, out/wheel.name)
    changes.append({'wheel': wheel.name, 'changes': modified,
        'original_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
        'portable_sha256': hashlib.sha256((out/wheel.name).read_bytes()).hexdigest()})
(root/'out/wheel-path-repairs.json').write_text(json.dumps(changes, indent=2)+'\n')
