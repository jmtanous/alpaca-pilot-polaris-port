This repository retains the published Beta 8 port and adds a separate Pilot 2.2.0
candidate. The legacy VERSION and default build recipes still select Beta 8.
Use the release-specific workflow in BUILDING.md for 2.2.0. Packages are downloaded
through the MMT catalog; they are no longer embedded in the MMT APK. The new
candidate is local and has not completed physical acceptance or publication.

# Alpaca Pilot Polaris Port

Build recipes and compatibility tools for running Alpaca Benro Polaris / Alpaca
Pilot 2.2 Beta 8 on the Benro Polaris SD card using an ARM EABI soft-float Python
runtime. Independent work, not affiliated with or endorsed by Benro or oGecko.

**Experimental release candidate.** Download the MMT-compatible runtime and matching
source companion from [GitHub Releases](https://github.com/jmtanous/alpaca-pilot-polaris-port/releases/tag/v0.1.0-rc.2).
Firmware/sysroot captures, VM images and private device configurations are not included. See [BUILDING.md](BUILDING.md) and [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md).

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

**Standalone launcher:** `bin/pilot` now invokes the packaged native bootstrap.
It starts on loopback by default; pass `--listen 0.0.0.0` only when deliberately
exposing the UI/API on a trusted network. It refuses a saved live controller target,
auto retry or tracking restore. The supplied staged configuration is disconnected
at `127.0.0.1:19090`; later connection belongs to the normal Pilot workflow.
MMT uses its separate managed helper. The existing-SD MMT-managed workflow passed
physical acceptance; the standalone launcher and fresh-SD installation remain
unaccepted on hardware. See RELEASE-VALIDATION.json for exact scope.

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
