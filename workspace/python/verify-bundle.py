#!/usr/bin/env python3
"""Verify an extracted bundle's complete manifest and wheel RECORD contents."""
import base64
import csv
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
manifest = json.loads((root/'BUNDLE-MANIFEST.json').read_text())
for name, expected in manifest['files'].items():
    path = root/name
    assert path.resolve().is_relative_to(root), name
    if 'symlink' in expected:
        assert path.is_symlink() and str(path.readlink()) == expected['symlink'], name
    else:
        assert path.is_file() and not path.is_symlink(), name
        assert path.stat().st_size == expected['size'], name
        assert oct(path.stat().st_mode & 0o777) == expected['mode'], name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'], name
actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
expected_names = set(manifest['files']) | {'BUNDLE-MANIFEST.json'}
assert expected_names <= actual, expected_names-actual
extras = actual-expected_names
if '--captured-root' in sys.argv[2:]:
    assert not any(name.startswith('opt/') for name in extras), extras
else:
    assert not extras, extras
site = root/'opt/benro-python/lib/python3.13/site-packages'
records = list(site.glob('*.dist-info/RECORD'))
assert len(records) == 34, len(records)
for record in records:
    with record.open(newline='') as f:
        for name, digest, size in csv.reader(f):
            path = (site/name).resolve()
            assert path.is_relative_to(root) and path.is_file(), name
            if path == record:
                assert not digest and not size
            else:
                data = path.read_bytes()
                value = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')
                assert digest == 'sha256='+value and size == str(len(data)), name
print(json.dumps({'result': 'passed', 'manifest_files': len(manifest['files']),
                  'wheel_records': len(records)}, indent=2))
