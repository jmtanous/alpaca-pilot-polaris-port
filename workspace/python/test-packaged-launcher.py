#!/usr/bin/env python3
"""Execute the packaged launcher against a fake upstream app; no network or mount."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

WORK = Path(__file__).resolve().parent


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pilot layout ')
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.prefix = root/'opt/benro-python'
        self.app = root/'opt/alpaca-pilot-2.2'
        (self.prefix/'bin').mkdir(parents=True)
        (self.prefix/'share/pilot').mkdir(parents=True)
        (self.app/'driver').mkdir(parents=True)
        shutil.copy2(WORK/'pilot-launcher.sh', self.prefix/'bin/pilot')
        shutil.copy2(WORK/'pilot_native.py', self.prefix/'share/pilot/pilot_native.py')
        (self.prefix/'bin/python3.13').symlink_to(sys.executable)
        self.config = self.app/'driver/config.py'
        self.config.write_text('''class Config:
    polaris_ip_address = '127.0.0.1'
    polaris_port = 19090
    polaris_auto_retry = False
    restore_tracking_on_restart = False
    @staticmethod
    def load(): pass
    @classmethod
    def apply_changes(cls, values):
        for key, value in values.items(): setattr(cls, key, value)
''')
        (self.app/'driver/app_web.py').write_text('''class AlpacaProxyResource:
    def __init__(self, url): self.url = url
class AlpacaSocketProxyResource(AlpacaProxyResource): pass
''')
        (self.app/'driver/main.py').write_text('''import json, os, sys
from config import Config
import app_web
Config.load()
print(json.dumps({'listen': Config.alpaca_restapi_ip_address,
    'rest': app_web.AlpacaProxyResource('http://localhost:5555').url,
    'socket': app_web.AlpacaSocketProxyResource('ws://localhost:5556').url,
    'argv': sys.argv, 'cwd': os.getcwd(),
    'pythonpath': os.environ.get('PYTHONPATH'),
    'pythonhome': os.environ.get('PYTHONHOME'),
    'usersite': os.environ.get('PYTHONNOUSERSITE')}))
''')

    def run_launcher(self, *args):
        env = dict(os.environ, PYTHONPATH='/invalid/injected', PYTHONHOME='/invalid/injected')
        return subprocess.run(['sh', str(self.prefix/'bin/pilot'), *args], env=env,
                              capture_output=True, text=True, timeout=10)

    def test_relocated_layout_and_default_loopback(self):
        result = self.run_launcher()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['listen'], '127.0.0.1')
        self.assertEqual(data['rest'], 'http://127.0.0.1:5555')
        self.assertEqual(data['socket'], 'ws://127.0.0.1:5556')
        self.assertEqual(data['argv'], [str(self.app/'driver/main.py')])
        self.assertEqual(data['cwd'], str(self.app))
        self.assertIsNone(data['pythonpath'])
        self.assertIsNone(data['pythonhome'])
        self.assertEqual(data['usersite'], '1')

    def test_explicit_network_listen(self):
        result = self.run_launcher('--listen', '0.0.0.0')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['listen'], '0.0.0.0')

    def test_live_saved_config_fails_before_application_runs(self):
        original = self.config.read_text().replace('polaris_port = 19090', 'polaris_port = 9090')
        self.config.write_text(original)
        result = self.run_launcher()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('disconnected target', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(self.config.read_text(), original)

    def test_invalid_listen_rejected(self):
        result = self.run_launcher('--listen', '192.168.0.1')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
