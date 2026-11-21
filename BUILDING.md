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

The native bootstrap and tests are included, but the legacy packaged launcher has
not yet been replaced. No new standalone hardware acceptance is claimed. Static ELF audit tools (`audit-bundle.py` and `audit.py`) are included; their
ABI fixture test requires a separately provisioned target root and toolchain. Private
lab VM tools, session orchestration, firmware captures and physical receipts were
intentionally excluded from this source snapshot.
