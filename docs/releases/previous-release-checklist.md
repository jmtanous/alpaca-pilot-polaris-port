# Experimental rc.2 release checklist

- [x] MIT original contributions; upstream and dependency terms retained.
- [x] Public snapshot excludes private history, target SDK captures and credentials.
- [x] Pinned npm/Rust input review and 237 recovered notices packaged.
- [x] GCC source, applied patch and Python source companion verified.
- [x] Public Debian SDK and GCC rebuild; ARM replacement-library loading tests.
- [x] Modified certifi and pure-Python zeroconf replacement checks on ARM.
- [x] Runtime and source companion frozen together with hashes.
- [x] MMT-managed existing-SD upgrade, settings retention, startup, webpage, Stop and reconnect.
- [x] Owner authorized experimental prerelease downloads with source companion.
- [ ] Fresh-SD acceptance (not claimed).
- [ ] Standalone-launcher physical acceptance (not claimed).
- [ ] Full clean cross-build and physical acceptance of newly rebuilt dependencies (not claimed).

RELEASE-VALIDATION.json records exact scope. Rebuilt replacement libraries were
validated separately and are not substituted into this released runtime.
