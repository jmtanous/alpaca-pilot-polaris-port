#!/usr/bin/env python3
"""Stage the exact local 2.2 release and a disconnected lab configuration."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PIN = '271d56e5031e969bd3f4a9d6405d4a68209947605b4797702008dfec5870dd5a'
DEST = ROOT / 'workspace/upstream/alpaca-2.2-beta8'
SETTINGS = {
    'polaris_ip_address': '127.0.0.1', 'polaris_port': 19090,
    'polaris_auto_retry': False, 'restore_tracking_on_restart': False,
    'enable_remote_shutdown': False, 'enable_synscan': False,
    'enable_discovery': False, 'enable_mdns': False,
    'enable_https': False, 'enable_rest_https': False,
    'alpaca_pilot_http_port': 8081, 'alpaca_restapi_port': 5555,
    'alpaca_socket_port': 5556, 'alpaca_restapi_ip_address': '127.0.0.1',
    'location': 'LAB PLACEHOLDER (0, 0): set actual observing site before use',
    'site_latitude': 0.0, 'site_longitude': 0.0, 'site_elevation': 0.0,
}

def stage(archive):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != PIN:
        raise ValueError('Upstream archive does not match the pinned 2.2 Beta 8 release')
    if DEST.exists():
        raise FileExistsError(f'{DEST} already exists; refusing to replace source or settings')
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DEST.parent) as tmp:
        target = Path(tmp) / 'release'
        target.mkdir()
        with tarfile.open(archive) as tar:
            tar.extractall(target, filter='data')
        project = tomllib.loads((target / 'pyproject.toml').read_text())['project']
        if project['version'] != '2.2.0':
            raise ValueError('Unexpected application version')
        if not (target / 'pilot/dist/spa/index.html').is_file():
            raise ValueError('Matching bundled Pilot UI is absent')
        hashes = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(target.rglob('*')) if p.is_file()}
        config = target / 'driver/config.toml'
        shutil.copy2(config, config.with_suffix('.toml.upstream'))
        text = config.read_text()
        for key, value in SETTINGS.items():
            text, count = re.subn(r'^' + re.escape(key) + r'\s*=.*$',
                                  key + ' = ' + json.dumps(value), text, flags=re.M)
            if count != 1:
                raise ValueError(f'Expected exactly one configuration key: {key}')
        tomllib.loads(text)
        config.write_text(text)
        (target / 'LAB-SOURCE-RECEIPT.json').write_text(json.dumps({
            'archive_sha256': PIN, 'version': '2.2.0 Beta 8',
            'original_files': hashes, 'lab_settings': SETTINGS,
        }, indent=2) + '\n')
        target.rename(DEST)
    print(f'Staged Alpaca/Pilot 2.2.0 Beta 8 at {DEST}')
    print('Disconnected target: 127.0.0.1:19090; no service started')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    stage(parser.parse_args().archive)
