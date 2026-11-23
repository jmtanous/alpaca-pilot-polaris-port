# Local candidate validation

2026-11-21, port 0.1.0-rc.1:

- Six proxy/disconnected-config tests passed, also under optimized Python.
- Four packaged-launcher tests passed: relocated layout with spaces, explicit
  network listen, rejected live saved target and rejected invalid listen address.
- Python and shell syntax, local Markdown links and private-marker checks passed.
- Normal/FAT packaging repeated with identical hashes. Both manifests and all
  34 wheel RECORD files verify; FAT archive is regular-files/directories only.
- Captured-userspace ABI audit passed: 236 bundled ELF objects, glibc <=2.24.
- Captured-userspace Python/dependency/numerical/crypto tests passed for the final
  archive. Final application acceptance passed with exit 0: disconnected startup,
  all 129 UI assets, WebSocket status, stationary simulator telemetry and disconnect.
- Pinned source companion hashes verify; matching installed certifi/zeroconf
  source files compare unchanged to their pinned archives.
- Upstream license preserved byte-for-byte. Dependency and artifact scans found
  no confirmed secrets; a parser's private-key delimiter is a known false positive.

These are offline repackaging and software tests using existing compiled inputs,
not a fresh dependency/compiler rebuild or physical vendor-kernel acceptance.
See BINARY-DISTRIBUTION.md and RELEASE-CANDIDATE.md for remaining release work.
