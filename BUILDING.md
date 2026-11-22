# Building the port

Target: ARMv7 EABI soft-float, glibc no newer than 2.24, stock Linux 4.9 userspace.
The checked-in files are recipes and source, not a complete redistributable SDK.
A full clean cross-build has not been repeated from this public snapshot.

## Inputs you must supply

- Python 3.11+ for host tools; Linux Docker for the cross-build environment.
- The exact upstream 2.2 Beta 8 source archive, obtained under its license.
  SHA-256: `271d56e5031e969bd3f4a9d6405d4a68209947605b4797702008dfec5870dd5a`.
- A lawfully obtained target SDK archive matching the recipe's expected layout
  and hash. `workspace/python/downloads/captured-sdk.tar.gz` is **not distributed**.
  Expected SHA-256: `2c34f504c2dca33882b99f53102402b8779f1152f3b69c8ec2bcd1a52583fc29`.
  Do not substitute an arbitrary sysroot: that requires a deliberate recipe change
  and renewed ABI validation. Providing a publicly reproducible SDK is release work.

Stage upstream into a fresh tree; the script refuses to overwrite it:

```sh
python3 scripts/stage-upstream.py /path/to/alpaca-2.2-beta8.tar.gz
```

This creates a disconnected placeholder site and target. Review real site settings
before later use; no controller connection is performed by staging.

## Build environment

```sh
docker build -t benro-dev-tools:bookworm .
docker build -t benro-python-build:bookworm -f config/python-build.Dockerfile .
export BENRO_BUILD_IMAGE="$(docker image inspect --format '{{.Id}}' benro-python-build:bookworm)"
bash scripts/build-python-runtime.sh
```

The explicit image override uses the image you built; without it, the wrapper
expects the recorded immutable reference image. Existing package inventories and
source pins document the original build but do not guarantee bit-identical apt
repositories today. Source acquisition uses the network; compilation normally
runs offline, with the existing Rust-vendoring step explicitly enabling networking.

Generated archives and manifests go under `workspace/python/out/` and stay ignored.
The packaging verifier checks manifests and wheel RECORD files. Port/upstream
licenses and dependency notices are copied into the archives. Inspect the final
package and complete binary-distribution license/source obligations before release.

The packaged entrypoint now invokes `share/pilot/pilot_native.py`. From the
extracted layout, run `opt/benro-python/bin/pilot` for loopback-only services or
append `--listen 0.0.0.0` for deliberate network exposure. Its disconnected guard
checks saved configuration before application startup and does not rewrite it.
No new standalone hardware acceptance is claimed. Static ELF audit tools (`audit-bundle.py` and `audit.py`) are included; their
ABI fixture test requires a separately provisioned target root and toolchain. Private
lab VM tools, session orchestration, firmware captures and physical receipts were
intentionally excluded from this source snapshot.

## Source companion

Prepare the pinned certifi/zeroconf/GCC sources and applied GCC patch with
`python3 workspace/python/package-source-companion.py --downloads /path/to/downloads`.
See [source availability](SOURCE-AVAILABILITY.md). The candidate is repackaged from
existing compiled inputs in the pinned offline build image; this is not a fresh
compiler/dependency rebuild. Captured-userspace tests do not certify physical
hardware timing or the vendor kernel.

## Public replacement-SDK candidate

The frozen runtime was built using the captured SDK above. A separate candidate
uses only public Debian archive inputs pinned in `workspace/python/public-sdk.json`.
It is a host build sysroot, not a firmware or libc update for the mount. Do not copy
its libraries onto the SD runtime or mount operating system.

Fetch with `python3 workspace/python/prepare-public-sdk.py --fetch`. Inside the
existing build container with this checkout mounted at `/project`, extract with:

```sh
python3 /project/workspace/python/prepare-public-sdk.py --output /project/workspace/python/out/public-sdk-sysroot
bash /project/workspace/python/check-public-sdk.sh
```

Extraction requires a fresh output directory and runs no package maintainer scripts.
The compile/link smoke test passes for ARMv7 soft-float, with GLIBC_2.4 symbol
requirements, and the executable runs under qemu-arm-static. It explicitly isolates
old libc headers from the container's newer cross headers. The extraction recipe
rewrites absolute development-library symlinks to relative links within the sysroot;
without this, the linker can select static libm and introduce private loader symbols.

The GCC toolchain and four distributed GCC libraries were rebuilt from the pinned
source against this SDK. Inside the offline build container, use a separate output:

```sh
MMT_TOOLCHAIN_WORK_ROOT=/project/workspace/python/out/public-toolchain MMT_TOOLCHAIN_SYSROOT=/project/workspace/python/out/public-sdk-sysroot bash /project/workspace/python/build-toolchain.sh
```

On the host with readelf and qemu-arm-static, run:

```sh
python3 workspace/python/check-gcc-replacement.py --runtime-prefix /path/to/extracted/opt/benro-python
python3 workspace/python/check-python-source-replacement.py --arm-runtime-prefix /path/to/extracted/opt/benro-python
```

These checks pass: all four rebuilt GCC libraries actually load into the frozen
ARM Python runtime; NumPy/SciPy calculations and cryptography operations succeed.
Their highest GLIBC requirement is 2.18, within the 2.24 ceiling. Modified certifi
source loads and uncompiled zeroconf serializes DNS packets under the ARM interpreter.
The source companion includes ifaddr to support the offline zeroconf check.
OpenSSL reports its legacy provider unavailable in this QEMU setup; tested modern
cryptography operations pass. No mount execution or legacy-algorithm claim is made.

For a modified zeroconf, its source build supports `SKIP_CYTHON=1` to omit optional
extensions. Work in a copy of the extracted runtime, replace the zeroconf package
with the source `src/zeroconf` tree (remove that package's old extension modules),
and retain its COPYING and metadata. Certifi likewise permits replacement of its
source/data files. Rebuild wheel RECORD entries and bundle/catalog hashes using
the supplied packaging recipes before distributing a modified package; the frozen
manifest must not be reused. The check scripts use temporary copies and never
modify the frozen runtime.

The main full-runtime pipeline still defaults to its original SDK. A complete clean
cross-build of every port dependency against the public SDK and physical acceptance
of those newly built binaries remain separate work. The rc.2 candidate retains the
already tested executable payload; the replacement libraries are validation outputs
only and are not shipped in it.
