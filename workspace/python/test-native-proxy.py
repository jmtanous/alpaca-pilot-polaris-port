#!/usr/bin/env python3
"""Verify the compatibility adapter only rewrites actual loopback hostnames."""
import types
import unittest
from pilot_native import install_proxy_compat, numeric_loopback


class ProxyTests(unittest.TestCase):
    def test_internal_urls(self):
        for scheme in ('http', 'https', 'ws', 'wss'):
            self.assertEqual(numeric_loopback(f'{scheme}://localhost:5555/ws?q=1'),
                             f'{scheme}://127.0.0.1:5555/ws?q=1')

    def test_external_urls_unchanged(self):
        for url in ('http://192.168.0.1:5555', 'ws://127.0.0.1:5556',
                    'http://localhost.example/path/localhost', 'file://localhost/path'):
            self.assertEqual(numeric_loopback(url), url)

    def test_unexpected_credentials_rejected(self):
        with self.assertRaises(ValueError):
            numeric_loopback('http://user:password@localhost:5555')

    def test_both_proxy_resources_keep_upstream_behavior(self):
        class Resource:
            def __init__(self, url):
                self.url = url
            def behavior(self):
                return 'original'
        module = types.SimpleNamespace(AlpacaProxyResource=Resource, AlpacaSocketProxyResource=Resource)
        install_proxy_compat(module)
        for name, url in (('AlpacaProxyResource', 'http://localhost:5555'),
                          ('AlpacaSocketProxyResource', 'ws://localhost:5556')):
            proxy = getattr(module, name)(url)
            self.assertEqual(proxy.url, url.replace('localhost', '127.0.0.1'))
            self.assertEqual(proxy.behavior(), 'original')


if __name__ == '__main__':
    unittest.main()
