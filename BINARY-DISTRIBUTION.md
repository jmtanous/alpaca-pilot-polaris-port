# Binary distribution review — local candidate

The runtime has 34 Python distributions. Each has retained license/notice files;
exact versions, source URLs/hashes and notice paths are in
[DEPENDENCY-INVENTORY.json](DEPENDENCY-INVENTORY.json).

The native package retains CPython, OpenSSL, zlib, libffi, XZ/liblzma, bzip2,
SQLite, OpenBLAS, GCC-runtime and Rust-runtime notices. The XZ source's COPYING
identifies liblzma as 0BSD; the presence of an LGPL notice for other XZ components
does not by itself make liblzma LGPL. GCC runtime exception text is retained with
the copied toolchain libraries; transitive linking coverage still needs review.

Two identified source-delivery components are certifi (MPL-2.0) and zeroconf
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

## Still required before binary publication

- Resolve notices/source coverage for the exact bundled Pilot web assets and
  transitive Rust/native components, not only top-level package labels.
- Make the source companion publicly downloadable alongside authorized binaries,
  with tested replacement/rebuild instructions and the required notices.
- Establish a redistributable/reproducible SDK path; captured target SDK inputs
  remain private and are not included in these artifacts.
- In MMT, verify provenance of the remaining Stitch-derived Polaris chooser image.
  The old Stitch emblem has been replaced with recorded generated clay artwork.

Local packaging and tests do not clear these publication items. No binary upload
or release publication is part of this unattended preparation.
