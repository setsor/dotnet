# Native .NET 10 source build — FreeBSD 15.1 x64 (November 2026)

> Unofficial community build and local deployment record. This is **not** an official Microsoft distribution and **not** a newly published GitHub release. This note supplements the historical 10.0.112 cross-build documented in [FREEBSD.md](FREEBSD.md).

## Build result

| Item | Recorded result |
| --- | --- |
| .NET SDK | 10.0.115 |
| Microsoft.NETCore.App | 10.0.15 |
| Microsoft.AspNetCore.App | 10.0.15 |
| Target | FreeBSD 15.1 amd64, RID `freebsd-x64` |
| Build | Native FreeBSD source-build, successful |
| Build summary | 0 warnings, 0 errors |
| Successful build elapsed time | Approximately 3h18m |
| SDK artifact size | Approximately 641 MB |
| Target deployment | OPNsense 26.7 / FreeBSD 15.1 amd64 |

This is a record of the verified local outcome, not a claim of byte-for-byte reproducibility.

## Native build environment and fixes

- FreeBSD 15.1 virtual machine using 4 vCPU, 8 GB RAM and 8 GB swap.
- Sources and bootstrap tooling were retained under the non-root builder account.
- The successful SDK source-build used the locally prepared `10.0.113-fixed` bootstrap.
- Earlier MSBuild issues involved tool mapping from **18.0.35** to the validated **18.0.11** tasks; Razor task loading was checked.
- Earlier 10.0.113 build attempts were intermediate; the final successful output was SDK **10.0.115**.
- The runtime and ASP.NET Core runtime output versions are **10.0.15**.

The exact source commit, full build invocation, archive SHA256 digests and complete dependency manifest should be captured from the build host before declaring the artifacts formally reproducible or publishing a new GitHub release. Do not reuse the older 10.0.112 release hashes.

## Local artifacts

The successful build produced an SDK artifact identified as:

```text
dotnet-sdk-10.0.115-freebsd.15-x64
```

The builder also assembled separate .NET runtime 10.0.15 and ASP.NET Core runtime 10.0.15 outputs. Exact archive extensions, sizes and SHA256 digests should be taken from the archived files; they are intentionally not invented in this document.

## OPNsense runtime deployment

The 10.0.15 runtime was installed into a **versioned** path:

```text
/opt/dotnet-10.0.15
```

The transferred runtime archive was checksum-verified. A native executable smoke test passed process startup, ICU/globalization, SHA-256 and RSA checks. The versioned runtime was then used for the Technitium DNS Server 15.6.2 deployment. See the companion [Technitium FreeBSD deployment record](https://github.com/setsor/DnsServer/blob/master/FREEBSD-OPNSENSE-DEPLOYMENT.md).

These checks verify an operational subset of the runtime, not comprehensive coverage of every SDK or ASP.NET Core feature.

## Compatibility and maintenance

- This is a community FreeBSD port, **not** an official Microsoft build.
- Check FreeBSD release, dynamic-library requirements and native execution before installing on another machine.
- Keep a verified prior runtime/archive for rollback; do not overwrite the existing installation until the service using the new runtime has been tested.
- Any OpenSSL version override must be applied only when actually needed on the target and verified with cryptographic smoke tests.
- Exclude logs with tokens, internal host names or addresses, DNS configuration, passwords, certificate private keys and personal information from public commits.
- Do not publish new SDK binaries or tags without verifying source provenance, checksums, licenses and release assets.

## Earlier release

The existing [FreeBSD 15 / .NET SDK 10.0.112 release](https://github.com/setsor/dotnet/releases/tag/v10.0.112-freebsd15-x64) remains separate from this November native-build record. Its older installation instructions and SHA256 continue to apply **only** to that archived artifact.
