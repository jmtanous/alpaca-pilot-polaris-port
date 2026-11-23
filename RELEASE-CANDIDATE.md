# Pilot 2.2.0 / port 0.2.0-rc.1 candidate

This candidate uses the official v2.2.0 tag pinned to commit
5e92a54e54fa17643a7908d0de82d2544269a6cd and its matching web UI. Five changed
locked dependencies were rebuilt for ARM: aiohttp, certifi, multidict, urllib3
and yarl. The interpreter and unchanged libraries are reused from the verified
Beta 8 rc.2 package; a clean rebuild of the whole port is not claimed.

The 4,605-file package and all 34 wheel records verify. All 238 ELF objects passed
the captured-userspace ABI audit. ARM runtime and application checks passed,
including 129 matching UI assets, REST/WebSocket, stationary fixture initialization,
telemetry and disconnect. Final notice-only updates preserve all tested executable
and application bytes. Public SDK GCC-library and certifi/zeroconf replacement
checks also pass. These automated results are separate from the attended check below.

The release-specific source companion contains the correct certifi version,
zeroconf/ifaddr and GCC sources, patches and shared build recipes. All 156 web
package archives and 32 Rust crate inventories verify, with 237 retained notices.
The new package is staged as a nonrecommended catalog version alongside unchanged
recommended Beta 8. Public assets and source companions are uploaded and verified anonymously. Existing-SD startup, phone dashboard, Stop and
settings rollback passed after connection recovery; clean-directory installation and a 134-second monitored post-stop repeat passed
as well. The earlier recovered drop remains unexplained. No formatted-card or
observing-accuracy claim is made. See docs/validation/pilot-2.2.0-clean-install.json.
Publication evidence is recorded in docs/PUBLIC-RELEASE.json. See docs/validation/pilot-2.2.0-build.json.

The default legacy VERSION/build pipeline continues to describe Beta 8. Use the
release-specific scripts for 2.2.0; versions share this repository. Prior rc.2
evidence is retained under docs/releases/pilot-beta8-rc2.
