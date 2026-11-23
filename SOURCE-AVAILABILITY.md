# Dependency source availability

This port's MIT license does not replace dependency licenses. Runtime notices
are under `opt/benro-python/share/licenses`; Python wheel notices are also retained
in their `.dist-info` directories. The bundled `share/build/dependencies.json`
contains exact Python dependency source URLs and SHA-256 hashes, and
`share/build/sources.json` records native source inputs.

The source companion `copyleft-source-companion.tar.gz` contains the pinned,
unchanged certifi (MPL-2.0) and zeroconf 0.150.0 (LGPL-2.1-or-later)
source archives, their hashes and port build recipes. Their respective licenses
remain inside those source archives. Generate it offline with:

```
python3 workspace/python/package-source-companion.py --release beta8 --downloads /path/to/pinned-downloads
python3 workspace/python/package-source-companion.py --release 2.2.0 --downloads /path/to/pinned-downloads
```

Beta 8 pins certifi 2026.7.22; Pilot 2.2.0 pins certifi 2026.10.23. The release
selector uses the matching dependency lock, notices and source hashes. Shared
development recipes are included under recipes/dev-env.

The companion now also includes the exact GCC 12.2.0 source archive and applied
documentation patch for libatomic, libgcc_s, libgfortran and libstdc++. Input hashes
are verified before packaging and recorded in SOURCE-MANIFEST.json. See
[BINARY-DISTRIBUTION.md](BINARY-DISTRIBUTION.md#gcc-source-companion-gap) for the
pinned inputs and outstanding build requirements. Replacement build validation
remains open; including these sources does not establish a validated public SDK.

Distribute the completed companion alongside any future binary release and provide a direct
source download link. It is prepared locally; no public download is promised yet.
These two components have no project-specific source patches. Build recipes and
wheel integrity-record updates are provided separately. The target SDK is not
included; reproducing target binaries still requires the documented SDK inputs.

The installation is an unpacked Python runtime on SD, not an encrypted package.
Modified dependency files will no longer match the original bundle manifest; a
modified distribution needs its own rebuilt manifest and catalog checksums.
Recipients retain the rights granted by each dependency license, including any
applicable modification, replacement and debugging rights.

This companion is not a claim that all binary redistribution work is complete.
Audit transitive native/Rust and bundled web dependencies and confirm the release's
complete notices, sources and replacement instructions before publishing binaries.
