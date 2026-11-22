# Public release checklist

This repository is an experimental source preview with fresh history.
Installable releases are still being prepared; no signed download is available.

- [x] MIT for original contributions; upstream notices retained unchanged.
- [x] Exclude private lab history, physical-session evidence and personal device/network identifiers.
- [x] Exclude firmware/sysroot captures, VM images, credentials and generated binaries.
- [x] Record pinned npm/Rust notice review and exact runtime web-asset comparison.
- [x] Integrate recovered notices and include pinned GCC source and patch.
- [x] Prepare public Debian SDK inputs and pass ARM compile/link smoke test.
- [x] Rebuild GCC with public SDK and validate actual replacement-library loading under ARM QEMU.
- [x] Validate modified certifi and pure-Python zeroconf under the ARM interpreter.
- [ ] Complete full-port clean cross-build and physical acceptance separately.
- [ ] Complete the component-level binary license/source compliance review.
- [ ] Freeze versioned release packages and their hashes together.
- [ ] Complete attended Pixel/Polaris acceptance of those exact packages.
- [x] Review the source snapshot and authorize public source-preview publication.
- [ ] Review and authorize the final installable downloads before release.

Default device addresses, disconnected loopback targets and fictional test
coordinates are intentional. They are not private network configuration.

## Port remaining work

- [x] Integrate the native browser bootstrap as the standalone packaged entrypoint.
- Provide or document a reproducible, redistributable SDK/build environment.
- Repeat a clean cross-build and ABI/runtime acceptance; this snapshot includes source recipes, not a newly qualified runtime.
- Complete browser/API validation of the exact standalone package on hardware.
