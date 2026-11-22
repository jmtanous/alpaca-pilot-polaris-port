# Binary distribution review — experimental rc.2

The runtime has 34 Python distributions. Each has retained license/notice files;
exact versions, source URLs/hashes and notice paths are in
[DEPENDENCY-INVENTORY.json](DEPENDENCY-INVENTORY.json).

The native package retains CPython, OpenSSL, zlib, libffi, XZ/liblzma, bzip2,
SQLite, OpenBLAS, GCC-runtime and Rust-runtime notices. The XZ source's COPYING
identifies liblzma as 0BSD; the presence of an LGPL notice for other XZ components
does not by itself make liblzma LGPL. GCC runtime exception text is retained with
the copied toolchain libraries; transitive linking coverage still needs review.

Two previously identified source-delivery components are certifi (MPL-2.0) and zeroconf
(LGPL-2.1-or-later). Their pinned source archives and build recipes are prepared
as an offline companion. A byte comparison found all 6 matching installed certifi
source/data files and 51 matching zeroconf Python/interface files unchanged.
Generated zeroconf extension objects are additionally covered by bundle integrity
and target ABI checks. No claim of bit-identical recompilation is made.

Mozilla describes source-location notification for compiled MPL components in
[its distribution FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/), question 8.
The exact LGPL text is retained in zeroconf's `.dist-info/licenses/COPYING` and its
source archive; [the published license](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)
provides the complete terms. The source companion does not relicense either library.

The upstream web lock has 585 dependency records; 171 omit a license field.
Three of nine direct production dependencies lack that field (Quasar, Quasar
extras and Vue Router). [WEB-DEPENDENCY-INVENTORY.json](WEB-DEPENDENCY-INVENTORY.json)
records exact versions/integrities and these gaps. Missing lock metadata does not
mean a dependency is unlicensed; it means the lock alone cannot establish notices.

## Pinned-input review (build 9 runtime)

[DEPENDENCY-NOTICE-REVIEW.json](DEPENDENCY-NOTICE-REVIEW.json) records the
runtime hash, all 156 non-development npm lock entries and 32 vendored Rust crates.
All npm archives passed their lockfile integrity checks; every vendored crate file
passed its recorded checksum. All entries yielded license notices: 237 texts are
preserved in [RECOVERED-NOTICES.json](RECOVERED-NOTICES.json). All 129 packaged web
assets match the pinned upstream bundle. This is a conservative input inventory,
including possible build-only code, not proof of which modules were linked.

The missing lockfile license fields above are now supplemented by archive notices.
Recovered texts include font notices from Quasar extras, the Unicode notice from
unicode-ident, and the available Apache-2.0 branch for self_cell. These recovered
notices are now included in the rc.2 runtime and build 10 APK. The baseline
audit JSON remains bound to the original rc.1 archive.

Reproduce the review with `scripts/review-distribution-licenses.py --help`.
Use `--fetch` once to retrieve integrity-pinned npm archives, then rerun offline
against the same cache, upstream bundle, runtime archive and Cargo vendor tree.
The tool does not execute package code or extract archives onto the filesystem.

### GCC source companion gap

The runtime ships libatomic, libgcc_s, libgfortran and libstdc++ shared libraries.
The GCC runtime exception does not waive source delivery for the library binaries
themselves; see the [GNU exception FAQ](https://www.gnu.org/licenses/gcc-exception-3.1-faq.html).
The expanded companion now includes the pinned GCC source archive and applied
patch, alongside certifi and zeroconf. The public-SDK GCC rebuild and ARM runtime replacement checks now pass; physical
acceptance and a complete cross-build of all other components remain separate.

The build recipe identifies Debian gcc-12-source 12.2.0-14+deb12u1,
`gcc-12.2.0-dfsg.tar.xz` SHA-256
`50c63ff82919323c25fbbb4a9eae259edc974118a0fb30c905190cb782ec11c2`,
and `gcc-gfdl-build.diff` SHA-256
`29b36f739f29959b580364a7aff45a0f291a6bd7c803af6794b737130acfb751`.
Provide the corresponding source, applied patches and build instructions for the
actual distributed libraries, then validate that companion. The public replacement SDK and checked replacement recipes are documented in BUILDING.md.

## Still required before binary publication

- Complete physical acceptance and review the exact release/source artifacts.
- Make the source companion publicly downloadable alongside authorized binaries,
  with tested replacement/rebuild instructions and the required notices.
- Keep captured target SDK inputs private. The pinned public replacement SDK
  passes GCC/Python component checks; a clean rebuild of the whole port is not claimed.
- Repeat final signed-APK notice verification; build 10 debug packaging is verified.
  MMT records the corrected Stitch chooser image hash and its live-design receipt.

Local packaging and tests do not clear these publication items. No binary upload
or release publication is part of this unattended preparation.

## Final rc.2 distribution status

Signed build 11 notice/asset coverage, artwork provenance and the matching source
companion have been verified. The exact runtime passed existing-SD MMT-managed
upgrade, startup, webpage, Stop and reconnect. The owner authorized publishing
this experimental candidate with its source companion and checksum manifest.
Fresh-SD, standalone physical acceptance and a full clean port cross-build remain
separate limits, not claims of this release. Earlier preparation requirements
above are retained as review history.
