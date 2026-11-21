#!/usr/bin/env python3
"""Install verified wheels into the target staging tree, never the host Python."""
from pathlib import Path
import sys
from installer import install
from installer.destinations import SchemeDictionaryDestination
from installer.sources import WheelFile

ROOT = Path('/project/workspace/python')
PREFIX = '/opt/benro-python'
scheme = {
    'purelib': PREFIX + '/lib/python3.13/site-packages',
    'platlib': PREFIX + '/lib/python3.13/site-packages',
    'headers': PREFIX + '/include/python3.13',
    'scripts': PREFIX + '/bin',
    'data': PREFIX,
}
for path in map(Path, sys.argv[1:]):
    with WheelFile.open(path) as wheel:
        wheel.validate_record(validate_contents=True)
        destination = SchemeDictionaryDestination(
            scheme_dict=scheme, interpreter=PREFIX+'/bin/python3.13',
            script_kind='posix', bytecode_optimization_levels=[],
            destdir=str(ROOT/'prefix'), overwrite_existing=True,
        )
        install(wheel, destination, {'INSTALLER': b'benro-python-lab\n'})
    print('Installed', path.name, flush=True)
