# Public release checklist

This repository is an experimental source preview with fresh history.
Installable releases are still being prepared; no signed download is available.

- [x] MIT for original contributions; upstream notices retained unchanged.
- [x] Exclude private lab history, physical-session evidence and personal device/network identifiers.
- [x] Exclude firmware/sysroot captures, VM images, credentials and generated binaries.
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
