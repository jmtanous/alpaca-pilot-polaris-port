# Port 0.1.0-rc.2 — experimental release candidate

The standalone `bin/pilot` now runs the native browser-proxy bootstrap included in
`share/pilot`. It supports relocated extracted layouts and defaults to loopback.
`--listen 0.0.0.0` deliberately exposes the software services. Startup refuses
live-target, auto-retry or tracking-restore settings; the check still runs under
optimized Python. Saved settings are not rewritten by the guard.

The runtime is repackaged from existing compiled inputs using the pinned offline
build image, with a clean packaging tree. This is not a fresh dependency compiler
rebuild. Normal and FAT layouts have manifest/34-wheel integrity checks. The FAT
layout includes only regular files/directories and is the runtime MMT embeds.

The rc.2 update adds 237 web/font/Rust notices and updates two existing notice
documents; all 4,361 other existing runtime files remain byte-identical. The source
companion contains pinned certifi, zeroconf, supporting ifaddr and GCC sources,
the applied GCC patch, and build/replacement recipes. Public-SDK GCC rebuild and
ARM-QEMU replacement tests pass. See RELEASE-VALIDATION.json and BUILDING.md for
exact hashes, scope and limits. A complete new cross-build of the entire port and
physical acceptance of newly rebuilt dependencies are not claimed.
No firmware, captured SDK, device configuration or physical-session receipts are
included in the public source checkout. No release upload has occurred.

## Final rc.2 managed acceptance

The exact rc.2 FAT runtime passed MMT build 11 installation on existing SD storage,
all 4,600 file checks, preserved observing-site settings, startup/controller
connection, live webpage, Stop and reconnect. Pilot was left stopped. No firmware,
boot, alignment, slew or tracking actions were performed. The source companion is
verified and accompanies the experimental binaries.

Standalone-launcher and fresh-SD hardware acceptance remain open. The full clean
port cross-build and physical testing of rebuilt dependencies are separate; the
replacement libraries are not shipped. Prior preparation text below is historical.
The owner authorized publishing this experimental managed-path candidate.

## Attended handoff

Test the exact candidate on the Pixel/Polaris only when the owner returns. Confirm
Wi-Fi wake and association, SSH identity/pairing, clean install and settings-preserving
reinstall, startup progress (allow up to three minutes), Pilot webpage/API, stop and
reconnect. Exercise standalone and MMT-managed startup as separate installation paths;
do not run both controllers together. Observe startup failures and confirm logs/errors
are actionable. No firmware or boot changes, alignment, slew or tracking tests are
part of this acceptance checklist.

Before binary publication: finish source/notice and chooser-artwork review, supply
and back up the MMT release signer, decide catalog distribution access, coordinate
uploaded archive/catalog hashes, and obtain approval for the exact downloads.

## Attended status after MMT build 3 testing

The exact bundled FAT runtime passed MMT-managed SD reinstall, preserved observing
settings, startup, browser dashboard, reconnect and Stop on Polaris. This supports
the managed MMT path only. The standalone launcher remains separately unaccepted
on physical hardware. The owner is testing fresh-SD setup; no result is claimed yet.
No runtime package bytes, version or catalog hashes changed for the MMT progress
and helper-upgrade fixes. Binary publication blockers in BINARY-DISTRIBUTION.md
remain open.
