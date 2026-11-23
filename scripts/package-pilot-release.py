#!/usr/bin/env python3
"""Assemble a separate, deterministic v2.2.0 candidate from verified inputs.

Run inside the offline build image. Does not alter the Beta 8 prefix or package.
Unchanged interpreter/libraries are reused explicitly from the pinned rc.2 base.
"""
import argparse,base64,csv,gzip,hashlib,json,os,posixpath,shutil,subprocess,tarfile
from pathlib import Path
from installer import install
from installer.destinations import SchemeDictionaryDestination
from installer.sources import WheelFile

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'workspace/python'
OUT=WORK/'out/releases/2.2.0'
BASE_HASH='30d34031d479505ce3f05a9cdabc6264f231ed7a2aec029edb0fff11c4467f1d'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def package(base):
    if sha(base)!=BASE_HASH: raise ValueError('Base package hash mismatch')
    stage=OUT/'runtime-root'
    if stage.exists(): raise FileExistsError('Candidate staging exists; preserve it and choose a fresh build')
    stage.mkdir(parents=True)
    with tarfile.open(base) as tar: tar.extractall(stage,filter='data')
    old=json.loads((stage/'BUNDLE-MANIFEST.json').read_text())
    for n,v in old['files'].items():
        p=stage/n
        if not p.resolve().is_relative_to(stage.resolve()) or sha(p)!=v['sha256']:raise ValueError('Base file mismatch: '+n)
    prefix=stage/'opt/benro-python'
    site=prefix/'lib/python3.13/site-packages'
    deps=json.loads((ROOT/'dependencies-2.2.0.json').read_text())
    old_versions={p['name']:p['version'] for p in json.loads((ROOT/'dependencies.json').read_text())['packages']}
    wheel_receipt=json.loads((OUT/'build-receipt.json').read_text())['wheels']
    for p in deps['packages']:
        if old_versions.get(p['name'])==p['version']:continue
        name=p['name'].replace('-','_')
        wheel,=(OUT/'wheels').glob(name+'-'+p['version']+'-*.whl')
        if sha(wheel)!=wheel_receipt[wheel.name]:raise ValueError('Wheel changed after build')
        info,=site.glob(name+'-'+old_versions[p['name']]+'.dist-info')
        with (info/'RECORD').open(newline='') as stream:
            for relative,*_ in csv.reader(stream):
                path=(site/relative).resolve()
                if not path.is_relative_to(prefix.resolve()):raise ValueError('Record escaped runtime')
                path.unlink(missing_ok=True)
        shutil.rmtree(info)
        with WheelFile.open(wheel) as source:
            source.validate_record(validate_contents=True)
            schemes={k:'/opt/benro-python/'+v for k,v in {'purelib':'lib/python3.13/site-packages','platlib':'lib/python3.13/site-packages','headers':'include/python3.13','scripts':'bin','data':''}.items()}
            install(source,SchemeDictionaryDestination(scheme_dict=schemes,interpreter='/opt/benro-python/bin/python3.13',script_kind='posix',bytecode_optimization_levels=[],destdir=str(stage),overwrite_existing=False),{'INSTALLER':b'benro-python-lab\n'})
        # Source notices supplement each wheel's own license files.
        source=WORK/'build/packages'/(name+'-'+p['version'])
        dest=prefix/'share/licenses'/p['name']
        if dest.exists():shutil.rmtree(dest)
        dest.mkdir(parents=True)
        for f in source.iterdir():
            if f.is_file() and f.name.upper().startswith(('LICENSE','COPYING','NOTICE','AUTHORS')):shutil.copy2(f,dest/f.name)
    app=stage/'opt/alpaca-pilot-2.2'
    shutil.rmtree(app)
    app.mkdir()
    upstream=ROOT/'workspace/upstream/alpaca-2.2.0'
    for name in ['driver','data','src']:
        shutil.copytree(upstream/name,app/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(upstream/'pilot/dist/spa',app/'pilot/dist/spa')
    shutil.copy2(upstream/'pilot/package.json',app/'pilot/package.json')
    for name in ['LICENSE','README.md','SECURITY.md','pyproject.toml','uv.lock','LAB-SOURCE-RECEIPT.json']:
        shutil.copy2(upstream/name,app/name)
    review=WORK/'out/license-review-2.2.0'
    audit=json.loads((review/'DEPENDENCY-NOTICE-REVIEW.json').read_text())
    if any(p['status']!='notice-found' for p in audit['npm']):raise ValueError('Unresolved web notices')
    if audit['lock_sha256']!=sha(upstream/'pilot/package-lock.json'):raise ValueError('Notice review is for another web lock')
    recovered=prefix/'share/licenses/recovered'
    shutil.rmtree(recovered)
    for name,text in json.loads((review/'RECOVERED-NOTICES.json').read_text()).items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe notice path')
        destination=recovered/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(text)
    for name in ['LICENSE','UPSTREAM-LICENSE.txt','THIRD-PARTY-NOTICES.md','SOURCE-AVAILABILITY.md']:
        shutil.copy2(ROOT/name,prefix/'share/licenses/port'/name)
    repairs=[]
    for f in site.rglob('*.so'):
        original=subprocess.check_output(['patchelf','--print-rpath',str(f)],text=True).strip()
        if not original:continue
        entries=[]
        for entry in original.split(':'):
            if entry==str(WORK/'prefix/opt/benro-python/lib'):
                entry='$ORIGIN/'+os.path.relpath(prefix/'lib',f.parent)
            elif not entry.startswith(('$ORIGIN','${ORIGIN}')):raise ValueError('Unexpected ELF path: '+entry)
            entries.append(entry)
        updated=':'.join(entries)
        if updated!=original:
            subprocess.run(['patchelf','--set-rpath',updated,str(f)],check=True)
            repairs.append({'file':str(f.relative_to(stage)),'before':original,'after':updated})
    for record in site.glob('*.dist-info/RECORD'):
        rows=[]
        with record.open(newline='') as stream:
            for relative,*_ in csv.reader(stream):
                f=(site/relative).resolve()
                if not f.is_relative_to(prefix.resolve()):raise ValueError('Record escaped runtime')
                if not f.is_file():raise ValueError('Missing installed file: '+str(f))
                data=f.read_bytes()
                rows.append([relative,'',''] if f==record.resolve() else [relative,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('='),str(len(data))])
        with record.open('w',newline='') as stream:csv.writer(stream).writerows(rows)
    build=prefix/'share/build'
    shutil.copy2(ROOT/'dependencies-2.2.0.json',build/'dependencies.json')
    receipt={'base_archive_sha256':BASE_HASH,'upstream':json.loads((ROOT/'docs/upstream-v2.2.0.json').read_text()),'changed_wheels':wheel_receipt,'rpath_repairs':repairs,'method':'Incremental source rebuild over verified rc.2 interpreter and unchanged libraries','target_acceptance':'pending'}
    (build/'release-2.2.0.json').write_text(json.dumps(receipt,indent=2)+'\n')
    manifest={**old,'application':'Alpaca/Pilot 2.2.0','port_version':'0.2.0-rc.1','files':{}}
    for f in sorted(stage.rglob('*')):
        if f.is_symlink():raise ValueError('SD package must not contain symlinks')
        if not f.is_file() or f==stage/'BUNDLE-MANIFEST.json':continue
        manifest['files'][f.relative_to(stage).as_posix()]={'sha256':sha(f),'size':f.stat().st_size,'mode':oct(f.stat().st_mode&0o777)}
    (stage/'BUNDLE-MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    archive=OUT/'benro-alpaca-pilot-2.2.0-port.0.2.0-rc.1-sd-fat.tar.gz'
    with archive.open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as tar:
        for f in sorted(stage.rglob('*')):
            if not f.is_file():continue
            info=tar.gettarinfo(str(f),arcname=f.relative_to(stage).as_posix())
            info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
            with f.open('rb') as stream:tar.addfile(info,stream)
    result={'archive':archive.name,'sha256':sha(archive),'archive_bytes':archive.stat().st_size,'manifest_sha256':sha(stage/'BUNDLE-MANIFEST.json'),'files':len(manifest['files']),'validation':'pending'}
    (OUT/'package-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',type=Path,required=True)
    package(parser.parse_args().base)
