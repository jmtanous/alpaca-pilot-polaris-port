# Alpaca Pilot Polaris Port

Build recipes and compatibility tools for running Alpaca Benro Polaris / Alpaca
Pilot on the Benro Polaris SD card with an ARM EABI soft-float Python runtime.
Independent work, not affiliated with or endorsed by Benro or oGecko.

This repository retains immutable Beta 8 and publishes the official Pilot 2.2.0
port as a separate prerelease. MMT downloads application packages from the catalog;
they are no longer embedded in its APK. Beta 8 remains the recommended catalog
version. New applications use the [shared Benro environment](https://github.com/jmtanous/benro-dev-env)
and receive a dedicated integration in an MMT release.

- [Pilot 2.2.0 / port 0.2.0-rc.1](https://github.com/jmtanous/alpaca-pilot-polaris-port/releases/tag/v0.2.0-rc.1)
- [Preserved Beta 8 / port 0.1.0-rc.2](https://github.com/jmtanous/alpaca-pilot-polaris-port/releases/tag/v0.1.0-rc.2)
- [MMT Android app](https://github.com/jmtanous/mount-mischief-toolkit-source)

All new release assets passed full anonymous-download checks. Attended stationary
checks passed for startup, the phone dashboard, Stop, version/settings rollback
and clean Toolkit-directory installation. One recovered connection interruption
did not recur in a 134-second monitored repeat; its cause is unresolved. No
formatted-card, alignment, tracking or observing-accuracy claim is made.
See [publication evidence](docs/PUBLIC-RELEASE.json), [release validation](RELEASE-VALIDATION.json)
and [build instructions](BUILDING.md). The legacy VERSION/default recipes still
select Beta 8; use the release-specific workflow for 2.2.0. Firmware/sysroot
captures, VM images and private configurations are excluded.

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
stationary checks on an existing SD and an empty Toolkit directory. A newly
formatted card and the standalone launcher remain unaccepted on hardware. See RELEASE-VALIDATION.json for exact scope.

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
