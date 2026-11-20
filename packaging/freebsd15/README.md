# FreeBSD 15.1 Poudriere / OPNsense 26.7 package validation

Status: **tested locally, pending source-port import and release hardening**. This is an unofficial community build, not a Microsoft or OPNsense distribution.

## Validated environments (November 2026)

- Poudriere: FreeBSD 15.1-RELEASE-p6, `151amd64` jail, `default` ports tree, `opnsense_custom` overlay, `opnsense_dotnet` set (`DEFAULT_VERSIONS+= ssl=openssl`).
- FreeBSD packages: `dotnet-runtime10-10.0.15`, `aspnetcore-runtime10-10.0.15`, `dotnet-sdk10-10.0.115`, `technitium-dns-15.6.2_2`.
- Clean FreeBSD 15.1 jail: `pkg` installation, .NET runtime, Technitium `rc.d` start/stop/start, and web UI confirmed. A previous isolated instance answered DNS requests on UDP/TCP `127.0.0.1:8053` with `REFUSED` as expected under `DNS_SERVER_RECURSION=Deny`.
- Separate `opnsense-pkg-test` VNET jail (FreeBSD 15.1 userland, **not** a full OPNsense installation): official OPNsense `pkg-2.8.4_1,1` plus eight official dependencies and three custom packages. Solver dry-run selected 11 new packages; no upgrades, downgrades, conflicts, or FreeBSD `openssl` package. Actual installation succeeded.
- In that jail, `dotnet --list-runtimes` reported both runtimes at 10.0.15. Technitium 15.6.2 started via `rc.d` as UID/GID 1001, served HTTP at `127.0.0.1:5380`, and its new configuration files had mode 0600. `pkg check -s -n dotnet-runtime10 aspnetcore-runtime10 technitium-dns` passed.
- This does **not** establish full OPNsense VM integration, DNS backend operation on this last jail, reboot integration, or production migration readiness.

## Package source locations on the builder

The tested **uncommitted** local overlay is:
```text
/usr/local/poudriere/ports/opnsense-custom/
  lang/dotnet-runtime10/
  www/aspnetcore-runtime10/
  devel/dotnet-sdk10/
  dns/technitium-dns/
```

The Technitium port uses `USE_RC_SUBR=technitium`, `SUB_FILES=technitium-run`, a dedicated service user, and `/var/db/technitium` for persistent state. The launcher applies `umask 077` and initializes the web listener to loopback when no persisted setting exists. Existing persisted web settings are **not** overridden by the environment value. The application still defaults to privileged DNS port 53, which a non-root service user cannot bind; use an administrator-selected backend port or other explicitly designed privilege architecture.

**Source-port import is not complete in this PR until the literal, reviewed `Makefile`, `distinfo`, `pkg-descr`, `pkg-plist`, `files/*.in`, and package installation scripts are copied from the builder.** Do not reconstruct `pkg-plist` from memory; do not add a claimed reproducible port unless hashes, payload lists, and templates match the tested source.

Exclude from Git: `work/`, `*.pkg`, distfiles, generated manifests, `/var/db/technitium`, `auth.config`, tokens, local credentials, network-specific settings, test-jail copies, backup files (`*.pre-*`).

## FreeBSD versus OPNsense OpenSSL

FreeBSD Poudriere built `dotnet-runtime10` with `USES=ssl:run` and the runtime package declared `openssl-3.5.9,1` from `security/openssl`. OPNsense 26.7.9_3 provides `openssl35-3.5.9` from `security/openssl35` with the required `libssl.so.17` and `libcrypto.so.17`.

The tested OPNsense derivative package changed **only** the runtime's explicit dependency record:
```diff
- openssl: { origin: "security/openssl", version: "3.5.9,1" }
+ openssl35: { origin: "security/openssl35", version: "3.5.9" }
```

Use [`repack_runtime_opnsense.py`](repack_runtime_opnsense.py) to reproduce that change on a staging root **containing the original installed runtime**. It deliberately does not rebuild .NET, modify OpenSSL libraries, or touch OPNsense. Compare manifest and payload after repacking. Example (run on `dotnet-build`, not OPNsense):

```sh
python3 packaging/freebsd15/repack_runtime_opnsense.py \\
  /usr/local/poudriere/data/packages/151amd64-default-opnsense_dotnet/All/dotnet-runtime10-10.0.15.pkg \\
  /usr/local/poudriere/test-jails/technitium-pkg-final \\
  /root/dotnet10-opnsense-package/output-new
```

The script is committed for review; re-run it against the validated staging root and compare the result with the recorded manifest and package hash before using its output. It refuses to overwrite a non-empty output directory. The result is a derived package and needs a separate repository catalog.

Recorded test derivative SHA256 (local build, not a published release):
```
faf0d36791e86ee0a55c22bcf8c16df9a772fe2f8387f9243988df72efbd060c
```
Recorded Technitium 15.6.2_2 SHA256:
```
a62e7465fdf3ccfa8f880f014658576c2cc468943dd75cd7fa7cd602be41fe1e
```
These checksums are for the **recorded local artifacts**, not general reproducibility guarantees.

## Before any OPNsense production migration

1. Import and review literal source port definitions from the build host, including owner/maintainer identity and package lifecycle behavior.
2. Validate OPNsense-compatible repository creation/verification with isolated package-manager testing. Use a signed, controlled repository for any production deployment; the unsigned `file://` test repository was isolated.
3. Test on a full OPNsense VM with a representative package set. The jail test is not equivalent to a full firewall.
4. Verify web access restrictions, service account, privileged DNS listener strategy, dnsdist forwarding/backend ports, API credentials, config integrity, and service restart/reboot.
5. Back up persistent Technitium data, retain the existing `/opt/dotnet-10.0.15` and `/opt/technitium/dns` deployment, and verify rollback *before* any production switch.
6. Avoid simultaneous use of the old and new service instances and avoid overwriting existing `/usr/local/etc/rc.d/technitium` without a planned cutover.

Tracking: [issue #1](https://github.com/setsor/dotnet/issues/1).
