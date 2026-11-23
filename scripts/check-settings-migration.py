#!/usr/bin/env python3
"""Exercise actual upstream configuration loading across Beta 8 and 2.2.0.

No application startup, sockets, mount access or saved user files are involved.
"""
import importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(release):
    path=ROOT/'workspace/upstream'/release/'driver/config.py'
    spec=importlib.util.spec_from_file_location('config_'+release.replace('-','_').replace('.','_'),path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

with tempfile.TemporaryDirectory(prefix='pilot-config-migration-') as tmp:
    saved=Path(tmp)/'config.pilot.json'
    settings={'location':'Migration fixture','site_latitude':19.25,'site_longitude':-99.15,
              'site_elevation':2250.0,'polaris_ip_address':'127.0.0.1','polaris_port':19090,
              'polaris_auto_retry':False,'restore_tracking_on_restart':False}
    saved.write_text(json.dumps(settings))
    for release in ['alpaca-2.2-beta8','alpaca-2.2.0']:
        module=load(release)
        module.Config.load(module.CONFIG_TOML_PATH,saved)
        for key,value in settings.items():assert getattr(module.Config,key)==value,(release,key)
        assert saved.read_text()==json.dumps(settings), 'Config.load unexpectedly rewrote settings'
        assert isinstance(module.Config._base,dict) and module.Config._base
    # The loaders are byte-identical. Forward migration is the existing defaults
    # merge; downgrade uses MMT's saved snapshot rather than reverse migration.
    paths=[ROOT/'workspace/upstream'/r/'driver/config.py' for r in ['alpaca-2.2-beta8','alpaca-2.2.0']]
    assert paths[0].read_bytes()==paths[1].read_bytes()
    print(json.dumps({'result':'passed','forward_migration':'unchanged upstream defaults/override merge',
        'fields_preserved':list(settings),'source_files_modified':False,'physical_device_contacted':False}))
