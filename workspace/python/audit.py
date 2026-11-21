#!/usr/bin/env python3
"""Inherited ELF executable auditor for the captured glibc 2.24 userspace.
Extension-module and packaged-library auditing remains a Python build milestone.
"""
import hashlib,json,os,pathlib,subprocess,sys

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def readelf(p,*args): return subprocess.check_output(['readelf',*args,str(p)],text=True)

def resolve(root,path):
 path=pathlib.PurePosixPath(path)
 parts=list(path.parts[1:] if path.is_absolute() else path.parts); done=[]; links=0
 while parts:
  part=parts.pop(0)
  if part in ('','.'): continue
  if part=='..':
   if not done: raise ValueError('Runtime path escape')
   done.pop();continue
  candidate=root.joinpath(*done,part)
  if candidate.is_symlink():
   links+=1
   if links>40: raise ValueError('Symlink loop')
   target=pathlib.PurePosixPath(os.readlink(candidate))
   if target.is_absolute(): done=[]; parts=list(target.parts[1:])+parts
   else: parts=list(target.parts)+parts
  else: done.append(part)
 result=root.joinpath(*done)
 if not result.is_file(): raise ValueError('Missing runtime file: '+str(path))
 return result

def audit(binary,root=pathlib.Path('/opt/benro-target')):
 import re
 h=readelf(binary,'-h')
 for required in ['ELF32','little endian','ARM','Version5 EABI','soft-float ABI']:
  if required not in h: raise ValueError('Invalid target ELF: '+required)
 program=readelf(binary,'-l')
 if '[Requesting program interpreter: /lib/ld-linux.so.3]' not in program: raise ValueError('Wrong target interpreter')
 queue=[binary,resolve(root,'/lib/ld-linux.so.3')];seen={};exports=set();undefined=[]
 while queue:
  p=queue.pop()
  if str(p) in seen: continue
  seen[str(p)]=digest(p)
  dynamic=readelf(p,'-d')
  if '(RPATH)' in dynamic or '(RUNPATH)' in dynamic: raise ValueError('Unapproved library search path: '+str(p))
  versions=readelf(p,'--version-info')
  for version in re.findall(r'GLIBC_([0-9.]+)',versions.partition('Version needs section')[2]):
   if tuple(map(int,version.split('.')))>(2,24): raise ValueError('Newer glibc required: '+version+' in '+str(p))
  for name in re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic):
   if '/' in name: raise ValueError('Non-SONAME dependency')
   found=None
   for directory in ['/lib/','/usr/lib/','/app/lib/']:
    try: found=resolve(root,directory+name);break
    except ValueError: pass
   if found is None: raise ValueError('Unavailable library: '+name)
   queue.append(found)
  for line in readelf(p,'--dyn-syms','--wide').splitlines():
   cols=line.split()
   if len(cols)<8 or not cols[0].endswith(':') or cols[4] not in ('GLOBAL','WEAK'): continue
   name=cols[7].replace('@@','@')
   if cols[6]=='UND':
    if cols[4]=='GLOBAL': undefined.append((str(p),name))
   else: exports.update([name,name.split('@')[0]])
 missing=[(p,n) for p,n in undefined if n not in exports]
 if missing: raise ValueError('Unresolved strong symbols: '+repr(missing))
 return {'objects':seen,'interpreter':'/lib/ld-linux.so.3','glibc_ceiling':'2.24'}
if __name__ == '__main__':
    print(json.dumps(audit(pathlib.Path(sys.argv[1])),indent=2))
