# Port 0.1.0-rc.1 — local candidate

The standalone `bin/pilot` now runs the native browser-proxy bootstrap included in
`share/pilot`. It supports relocated extracted layouts and defaults to loopback.
`--listen 0.0.0.0` deliberately exposes the software services. Startup refuses
live-target, auto-retry or tracking-restore settings; the check still runs under
optimized Python. Saved settings are not rewritten by the guard.

The runtime is repackaged from existing compiled inputs using the pinned offline
build image, with a clean packaging tree. This is not a fresh dependency compiler
rebuild. Normal and FAT layouts have manifest/34-wheel integrity checks. The FAT
layout includes only regular files/directories and is the runtime MMT embeds.

The source companion contains pinned certifi and zeroconf source archives plus
build recipes. See BINARY-DISTRIBUTION.md for remaining component/provenance work.
No firmware, captured SDK, device configuration or physical-session receipts are
included in the public source checkout. No release upload has occurred.

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
