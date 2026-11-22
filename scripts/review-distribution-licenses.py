#!/usr/bin/env python3
"""Audit pinned npm/Rust notices and their presence in a runtime; never execute packages.

A conservative dependency inventory is not proof of exact linked module inclusion.
Output is release-review evidence, not an automatic legal clearance.
"""
import argparse, base64, concurrent.futures, hashlib, io, json, re, tarfile, tomllib
from pathlib import Path
from urllib.request import urlopen


def digest(data): return hashlib.sha256(data).hexdigest()
def notice(name): return bool(re.match(r'^(licen[cs]e|copying|notice|copyright|ofl)(?:[._-]|$)', Path(name).name, re.I))
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--cargo-vendor',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--fetch',action='store_true')
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    cache=a.output/'npm-archives';cache.mkdir(exist_ok=True)
    texts={}; runtime_assets={}; runtime_notices={}
    with tarfile.open(a.runtime) as t:
        for m in t:
            if not m.isfile():continue
            if '/share/licenses/' in m.name or notice(m.name): runtime_notices[m.name]=digest(t.extractfile(m).read())
            if '/pilot/dist/spa/' in m.name:runtime_assets[m.name.split('/pilot/dist/spa/',1)[1]]=digest(t.extractfile(m).read())
    lockfile=a.upstream/'pilot/package-lock.json';lock=json.loads(lockfile.read_text())
    packages=[(k,v) for k,v in lock['packages'].items() if k and not v.get('dev',False)]
    def npm(item):
        path,p=item;row={'path':path,'version':p.get('version'),'license_from_lock':p.get('license'),'resolved':p.get('resolved'),'integrity':p.get('integrity')}
        try:
            url=p['resolved'];sri=p['integrity'];algorithm,expected=sri.split('-',1)
            if not url.startswith('https://registry.npmjs.org/') or algorithm not in ('sha512','sha256'): raise ValueError('Unsupported pinned source')
            archive=cache/(digest(url.encode())+'.tgz')
            if not archive.exists():
                if not a.fetch:raise ValueError('Archive not cached; use --fetch')
                with urlopen(url,timeout=35) as response:data=response.read()
            else:data=archive.read_bytes()
            if base64.b64encode(hashlib.new(algorithm,data).digest()).decode()!=expected:raise ValueError('Integrity mismatch')
            if not archive.exists():archive.write_bytes(data)
            row['archive_sha256']=digest(data);row['integrity_verified']=True
            found={}
            with tarfile.open(fileobj=io.BytesIO(data)) as t:
                manifests=[m for m in t.getmembers() if m.isfile() and m.name.endswith('/package.json') and len(Path(m.name).parts)==2]
                if len(manifests)!=1:raise ValueError('Missing or ambiguous package manifest')
                pkg=json.load(t.extractfile(manifests[0]))
                row.update(name=pkg['name'],license_from_package=pkg.get('license'))
                for m in t:
                    if m.isfile() and notice(m.name):found[m.name]=t.extractfile(m).read().decode('utf-8',errors='replace')
                if not found:
                    for m in t.getmembers():
                        if m.isfile() and Path(m.name).name.lower()=='readme.md':
                            readme=t.extractfile(m).read().decode('utf-8',errors='replace')
                            match=re.search(r'(?mi)^License\s*\n-+\s*\n',readme)
                            if match and 'Permission is hereby granted' in readme[match.end():]:
                                found[m.name+'#License']=readme[match.start():].split('\n[',1)[0].strip()+'\n'
            row['notices']={n:digest(s.encode()) for n,s in found.items()}
            row['status']='notice-found' if found else 'no-notice-file'
            return row, {f'npm/{path}/{n}':s for n,s in found.items()}
        except Exception as e:row['status']='unresolved';row['error']=str(e);return row,{}
    npm_rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for row,found in pool.map(npm,packages):npm_rows.append(row);texts.update(found)
    rust=[]
    for crate in sorted(a.cargo_vendor.iterdir()):
        if not (crate/'Cargo.toml').is_file():continue
        p=tomllib.loads((crate/'Cargo.toml').read_text())['package'];checks=json.loads((crate/'.cargo-checksum.json').read_text())
        changed=[n for n,h in checks['files'].items() if not (crate/n).is_file() or digest((crate/n).read_bytes())!=h]
        found={str(f.relative_to(crate)):f.read_text(errors='replace') for f in crate.rglob('*') if f.is_file() and notice(f.name)}
        texts.update({f'rust/{crate.name}/{n}':s for n,s in found.items()})
        rust.append({'name':p['name'],'version':p['version'],'license':p.get('license'),'package_checksum':checks.get('package'),'verified_files':len(checks['files']),'changed_files':changed,'notices':{n:digest(s.encode()) for n,s in found.items()}})
    upstream_assets={str(p.relative_to(a.upstream/'pilot/dist/spa')):digest(p.read_bytes()) for p in (a.upstream/'pilot/dist/spa').rglob('*') if p.is_file()}
    report={'runtime_sha256':digest(a.runtime.read_bytes()),'lock_sha256':digest(lockfile.read_bytes()),'scope':'All non-dev npm lock entries and all vendored Rust crates, including possible build-only code. Not a linked-module proof.','runtime_notice_files':runtime_notices,'web_asset_count':len(runtime_assets),'web_assets_match_upstream':runtime_assets==upstream_assets,'npm':npm_rows,'rust':rust,'review_cleared':False}
    (a.output/'DEPENDENCY-NOTICE-REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
    (a.output/'RECOVERED-NOTICES.json').write_text(json.dumps(dict(sorted(texts.items())),indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'npm':len(npm_rows),'npm_unresolved':[r['path'] for r in npm_rows if r['status']!='notice-found'],'rust':len(rust),'rust_changed':[r['name'] for r in rust if r['changed_files']],'rust_missing_notices':[r['name'] for r in rust if not r['notices']],'web_assets':len(runtime_assets),'web_assets_match_upstream':runtime_assets==upstream_assets,'recovered_notice_texts':len(texts)},indent=2))
if __name__=='__main__':main()
