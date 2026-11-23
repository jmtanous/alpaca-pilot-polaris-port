# Source validation — Pilot 2.2.0 candidate

Pinned official v2.2.0 source and matching UI are staged separately from Beta 8.
The five changed locked dependencies were rebuilt in the pinned offline ARM
build image. The package has 4,605 verified files and 34 verified wheel records.
The captured-userspace ABI/application tests, public SDK library/source replacement
checks and MMT full-archive version switching passed. Final packaging changed
only notices relative to the application-tested archive. Source companion entries
and release-specific notices match their recorded hashes. No physical acceptance
or complete clean port rebuild is claimed. See RELEASE-VALIDATION.json.
