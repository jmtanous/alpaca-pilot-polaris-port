# Alpaca Pilot Polaris Port

Build recipes and compatibility tools for running Alpaca Benro Polaris / Alpaca
Pilot 2.2 Beta 8 on the Benro Polaris SD card using an ARM EABI soft-float Python
runtime. Independent work, not affiliated with or endorsed by Benro or oGecko.

**Experimental source preview, not a ready-to-install release.** Upstream software,
firmware/sysroot captures, VM images, generated binaries and device configurations
are not included. See [BUILDING.md](BUILDING.md) and [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md).

## Included

- Hash-pinned runtime/dependency source recipes and cross-compilation settings.
- Compatibility patches for the target's older userspace.
- Deterministic runtime/FAT-SD package recipes and integrity verification.
- `workspace/python/pilot_native.py`, the native browser compatibility bootstrap,
  its SD launcher, and isolated proxy and launcher regression tests.

The bootstrap corrects internal Pilot proxy URLs from `localhost` to numeric
loopback for the mount's resolver environment. It preserves upstream proxy behavior
and does not patch firmware or globally replace the resolver. It requires the
staged disconnected configuration and leaves connection to Pilot's normal APIs.

**Local release candidate:** `bin/pilot` now invokes the packaged native bootstrap.
It starts on loopback by default; pass `--listen 0.0.0.0` only when deliberately
exposing the UI/API on a trusted network. It refuses a saved live controller target,
auto retry or tracking restore. The supplied staged configuration is disconnected
at `127.0.0.1:19090`; later connection belongs to the normal Pilot workflow.
MMT uses its separate managed helper. This candidate still needs attended physical
acceptance and binary-distribution review before release.

## Local compatibility tests

```sh
python3 -B workspace/python/test-native-proxy.py
python3 -B workspace/python/test-packaged-launcher.py
```

These tests do not contact or move a mount. Cross-build and physical acceptance
are separate. Do not run vendor startup scripts or install boot hooks. Review
package contents and instructions before any attended hardware use.

## License and upstream

Original port contributions are copyright (c) 2026 Jose Mtanous, under [MIT](LICENSE).
The upstream application remains copyright oGecko Solutions under its unchanged
[license and distribution preamble](UPSTREAM-LICENSE.txt). Dependencies retain
separate terms; see [third-party notices](THIRD-PARTY-NOTICES.md).

Upstream: https://github.com/ogecko/alpaca-benro-polaris
Documentation: https://ogecko.github.io/alpaca-benro-polaris/v2.2/
