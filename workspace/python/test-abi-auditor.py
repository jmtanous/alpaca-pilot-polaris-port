#!/usr/bin/env python3
"""Compile deliberately invalid ELF fixtures and verify the auditor rejects them."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

work = Path('/project/workspace/python')
spec = importlib.util.spec_from_file_location('bundle_audit', work/'audit-bundle.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
cc = work/'build/toolchain/bin/arm-linux-gnueabi-gcc'
rejected = []
with tempfile.TemporaryDirectory(prefix='abi-negative-', dir=work/'build') as temp:
    root = Path(temp)
    prefix = root/'opt/benro-python'
    (prefix/'bin').mkdir(parents=True)
    (prefix/'lib').mkdir()
    shutil.copy2(work/'prefix/opt/benro-python/bin/python3.13', prefix/'bin/python3.13')
    shutil.copytree(work/'build/audit-root/lib', root/'lib', symlinks=True)
    def compile_fixture(name, source, extra=()):
        c = root/(name+'.c')
        so = root/(name+'.so')
        c.write_text(source)
        subprocess.run([str(cc), '-shared', '-fPIC', '-march=armv7-a',
            '-mfpu=vfpv3-d16', '-mfloat-abi=softfp', str(c), '-o', str(so), *extra], check=True)
        return so
    fixtures = [
        ('wrong_architecture', Path('/usr/bin/python3'), 'wrong architecture'),
        ('hard_float', compile_fixture('hard', 'void test(void) {}', ['-nostdlib', '-mfloat-abi=hard']), 'soft-float'),
        ('newer_glibc', compile_fixture('newer', 'extern int getentropy(void *, unsigned); int test(void) { char c; return getentropy(&c,1); }'), 'GLIBC_2.25'),
        ('build_rpath', compile_fixture('rpath', 'void test(void) {}', ['-nostdlib', '-Wl,-rpath,/project/forbidden']), 'library search path'),
    ]
    for name, path, message in fixtures:
        try:
            audit.inspect(root, path, '/opt/benro-python')
        except ValueError as error:
            assert message in str(error), (name, error)
            rejected.append(name)
        else:
            raise AssertionError('Auditor accepted '+name)
    valid = compile_fixture('valid', 'void test(void) {}', ['-nostdlib'])
    shutil.copy2(valid, prefix/'lib/fixture.so')
    assert audit.audit(root, '/opt/benro-python')['result'] == 'passed'
    missing = compile_fixture('missing', 'extern int benro_nonexistent_symbol(void); int test(void) { return benro_nonexistent_symbol(); }', ['-nostdlib'])
    shutil.copy2(missing, prefix/'lib/fixture.so')
    try:
        audit.audit(root, '/opt/benro-python')
    except ValueError as error:
        assert 'Unresolved strong symbols' in str(error), error
        rejected.append('unresolved_symbol')
    else:
        raise AssertionError('Auditor accepted an unresolved strong symbol')
print(json.dumps({'result': 'passed', 'valid_fixture': 'accepted', 'invalid_fixtures_rejected': rejected}, indent=2))
