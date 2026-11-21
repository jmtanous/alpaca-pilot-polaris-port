openssl-glibc-2.24.patch
----------------------
OpenSSL 3.5.9 normally declares getentropy as a weak ELF symbol. Benro's captured
libc reports 2.24 but exports this backport as GLIBC_2.25, so even the weak
reference introduces a version requirement newer than our declared ceiling.

The opt-in OPENSSL_NO_WEAK_GETENTROPY build flag selects OpenSSL's existing
DSO_global_lookup path instead. It retains runtime getentropy discovery and the
existing Linux getrandom syscall fallback; it does not weaken the entropy source
or disable the OS randomness checks. Only the private target build sets this
flag. The original upstream archive hash remains unchanged. Validate with ELF
version audit and target-runtime OpenSSL RAND_bytes/TLS tests.

openssl-getentropy-enosys.patch
------------------------------
The captured libc's getentropy backport returns ENOSYS even though the kernel's
getrandom syscall works. OpenSSL's DSO lookup branch previously returned that
error immediately. Apply the same ENOSYS fallback handling already present in
its weak-symbol branch. Other errors still fail; no entropy checks are bypassed.
Both patches are required for this captured userspace.

../getrandom-compat.c (link-time compatibility shim)
--------------------------------------------------
Rust 1.100 std also has a weak getrandom reference that binds to GLIBC_2.25 in
the captured libc. The cryptography recipe uses --wrap=getrandom and a private,
hidden C wrapper calling Linux SYS_getrandom. Return values and errno are
preserved, including ENOSYS so Rust can retain its normal fallback handling.
The supported device kernel is 4.9; getrandom exists since Linux 3.17.
This avoids introducing a newer glibc ABI dependency without changing package
versions, weakening entropy, or editing the compiled ELF version metadata.

pandas-target-numpy-headers.patch (test environment only)
--------------------------------------------------------
Pandas 3.0.5 asks the build interpreter for NumPy's include path, which selects
x86-64 headers during cross-compilation. Compilation succeeds but int64_t is
then incorrectly typedef'd to 32-bit long on ARM, causing import failure.
Honor the same numpy-include-dir cross-file property already used by SciPy.
Native builds retain the upstream discovery path. Pandas is a locked analysis
test dependency and is not included in the production runtime bundle.

../pilot_native.py (SD-only process bootstrap)
--------------------------------------------
The physical Benro has no /etc/hosts, /etc/nsswitch.conf or /etc/resolv.conf.
Its captured glibc resolver fails getaddrinfo("localhost", 5555), while numeric
127.0.0.1 succeeds. Original Pilot serves static assets but its same-origin
/proxy REST route returns HTTP 502 because app_web.py constructs its internal
REST and WebSocket destinations with localhost.

The separate bootstrap subclasses only those two proxy resources, converting
localhost URLs to numeric IPv4 loopback before calling their original
constructors. Other hosts and inherited request/proxy behavior are unchanged.
No global socket monkeypatch, host resolver files, firmware edits, or changes
to upstream source/configuration bytes are required. Four focused adapter tests
cover HTTP/HTTPS/WS/WSS, external-host preservation, unexpected credentials,
and delegation to both original constructors.

This is a diagnostic native launcher: it requires the isolated target
127.0.0.1:19090 with auto-retry/tracking restoration disabled on startup. Bind
0.0.0.0 explicitly for external browser tests. A deliberate subsequent target
change/connection uses the normal Pilot APIs. The original runtime archive and
its legacy bin/pilot entrypoint do not automatically include this bootstrap.
Physical acceptance must be repeated for the final standalone release package.
