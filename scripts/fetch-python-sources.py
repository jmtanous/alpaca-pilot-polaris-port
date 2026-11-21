#!/usr/bin/env python3
"""Fetch hash-pinned Python/runtime source archives; never install or execute them."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'workspace/python/downloads'

def fetch(item):
    url = item['url']
    if urllib.parse.urlparse(url).scheme != 'https':
        raise ValueError('Only HTTPS source URLs are accepted')
    name = Path(urllib.parse.urlparse(url).path).name
    digest = item['sha256']
    path = OUT / name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == digest:
        return f'Cached: {name}'
    tmp = path.with_name(name + '.part')
    try:
        with urllib.request.urlopen(url, timeout=120) as response, tmp.open('wb') as f:
            while chunk := response.read(1024 * 1024):
                f.write(chunk)
        actual = hashlib.sha256(tmp.read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f'Checksum mismatch for {name}: {actual}')
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    return f'Verified: {name}'

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    sources = json.loads((ROOT / 'workspace/python/sources.json').read_text())
    for package in json.loads((ROOT / 'dependencies.json').read_text())['packages']:
        s = package['sdist']
        algorithm, digest = s['hash'].split(':', 1)
        if algorithm != 'sha256':
            raise ValueError('Unsupported lock hash')
        sources.append({'url': s['url'], 'sha256': digest})
    tools = ROOT / 'workspace/python/build-tools.json'
    if tools.exists():
        sources.extend(json.loads(tools.read_text())['packages'])
    tests = ROOT / 'workspace/python/test-dependencies.json'
    if tests.exists():
        sources.extend({'url': p['sdist']['url'], 'sha256': p['sdist']['hash'].removeprefix('sha256:')}
                       for p in json.loads(tests.read_text())['packages'])
        sources.extend({'url': p['wheel']['url'], 'sha256': p['wheel']['hash'].removeprefix('sha256:')}
                       for p in json.loads(tests.read_text())['packages'] if 'wheel' in p)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch, sources):
            print(result, flush=True)
