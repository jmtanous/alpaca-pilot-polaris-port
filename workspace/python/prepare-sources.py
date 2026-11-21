#!/usr/bin/env python3
"""Verify and extract pinned archives; preserve existing build caches."""
import hashlib
import json
from pathlib import Path
import tarfile

root = Path(__file__).resolve().parent
project = root.parents[1]
build = root/'build'
build.mkdir(exist_ok=True)

def extract(filename, digest, destination):
    archive = root/'downloads'/filename
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest, filename
    with tarfile.open(archive) as tar:
        names = {Path(m.name).parts[0] for m in tar.getmembers() if m.name not in ('.', './')}
        assert len(names) == 1, (filename, names)
        directory = destination/next(iter(names))
        if directory.exists():
            print('Using source cache:', directory.name)
        else:
            destination.mkdir(parents=True, exist_ok=True)
            tar.extractall(destination, filter='data')
            print('Extracted verified source:', directory.name)

extract('captured-sdk.tar.gz', '2c34f504c2dca33882b99f53102402b8779f1152f3b69c8ec2bcd1a52583fc29', build)
for package in json.loads((root/'sources.json').read_text()):
    extract(package['url'].rsplit('/', 1)[1], package['sha256'], build)
for lock in [project/'dependencies.json', root/'test-dependencies.json']:
    for package in json.loads(lock.read_text())['packages']:
        source = package['sdist']
        extract(source['url'].rsplit('/', 1)[1], source['hash'].removeprefix('sha256:'), build/'packages')
