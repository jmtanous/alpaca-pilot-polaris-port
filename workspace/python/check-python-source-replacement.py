#!/usr/bin/env python3
"""Verify pure-Python source replacement offline without opening network sockets.

Runs a host import/DNS serialization check, not ARM or hardware acceptance.
Python 3.12+ is needed for tarfile's data extraction filter.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--arm-runtime-prefix', type=Path,
                    help='Run with this ARM Python prefix under qemu-arm-static')
args = parser.parse_args()
packages = json.loads((root/'dependencies.json').read_text())['packages']
with tempfile.TemporaryDirectory(prefix='mmt-source-check-') as tmp:
    stage = Path(tmp)
    paths = []
    for package in packages:
        if package['name'] not in {'certifi', 'zeroconf', 'ifaddr'}:
            continue
        source = package['sdist']
        archive = root/'workspace/python/downloads'/Path(urlsplit(source['url']).path).name
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == source['hash'].removeprefix('sha256:')
        with tarfile.open(archive) as bundle:
            bundle.extractall(stage, filter='data')
        folder = stage/(package['name']+'-'+package['version'])
        paths.append(str(folder/'src' if (folder/'src').is_dir() else folder))
    assert len(paths) == 3
    # Demonstrate that a source modification is loaded, without compiled .so files.
    certifi = next(stage.glob('certifi-*/certifi/__init__.py'))
    with certifi.open('a') as stream:
        stream.write('\nMMT_REPLACEMENT_CHECK = True\n')
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join(paths)
    code = '''
import certifi, zeroconf
from zeroconf import DNSQuestion, DNSOutgoing
assert certifi.MMT_REPLACEMENT_CHECK
assert b'BEGIN CERTIFICATE' in open(certifi.where(), 'rb').read()
message = DNSOutgoing(0)
message.add_question(DNSQuestion('mmt.local.', 1, 1))
assert message.packets() and all(isinstance(p, bytes) for p in message.packets())
assert zeroconf.__version__ == '0.150.0'
print('Modified certifi source loaded; pure-Python zeroconf DNS serialization passed')
'''
    command = [sys.executable, '-S', '-c', code]
    if args.arm_runtime_prefix:
        prefix = args.arm_runtime_prefix.resolve()
        sdk = root/'workspace/python/out/public-sdk-sysroot'
        command = ['qemu-arm-static', '-L', str(sdk),
                   '-E', 'PYTHONHOME='+str(prefix),
                   '-E', 'LD_LIBRARY_PATH='+str(prefix/'lib'),
                   str(prefix/'bin/python3.13'), '-S', '-c', code]
    subprocess.run(command, cwd=stage, env=env, check=True)
