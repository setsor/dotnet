# .NET 10.0.115 — FreeBSD 15.1 amd64

## Purpose and status

**Status: native build environment prepared; the 10.0.112 bootstrap and matching previous source-built artifacts are SHA256-verified. Native builds of 10.0.113 and 10.0.115 have not yet run.**

Build .NET SDK **10.0.115**, Microsoft.NETCore.App **10.0.15** and
Microsoft.AspNetCore.App **10.0.15** natively on **FreeBSD 15.1 amd64**
inside a dedicated Parallels Desktop virtual machine.

This branch starts from the unmodified upstream Microsoft source release
`dotnet/dotnet@v10.0.115` (commit
`8e0f8ed2312954727f8919d7d1c2f78b483b4ee7`).
FreeBSD-specific source changes, if proven necessary, will be committed
separately with their reasons and tests.

## Previous validated release

- Branch: [`freebsd15-v10.0.112`](https://github.com/setsor/dotnet/tree/freebsd15-v10.0.112)
- Release: [`v10.0.112-freebsd15-x64`](https://github.com/setsor/dotnet/releases/tag/v10.0.112-freebsd15-x64)
- Previous method: **cross-build using a FreeBSD 15.1 rootfs**, not a native build.
- SDK: 10.0.112; runtimes: 10.0.12.
- Detailed original instructions: [`FREEBSD.md` on `main`](https://github.com/setsor/dotnet/blob/main/FREEBSD.md).

The previous branch is retained as a reproducible reference, not blindly merged
into the new upstream baseline.

## Native build environment

- VM: `dotnet-build.home.arpa`, Parallels Desktop, FreeBSD 15.1-RELEASE amd64.
- Resources allocated: 4 vCPU, 8 GiB RAM, 8 GiB swap, ZFS disk (approximately
  146 GiB free following installation).
- Source and build directories should remain inside this VM.
- Confirm a clean VM snapshot before installing additional build dependencies.
- Network access, DNS and HTTPS have been demonstrated in the VM.

## Bootstrap and known problem

Upstream `v10.0.115` declares SDK `10.0.113` in `global.json`
and previous source-built artifacts `10.0.113-servicing.26504.104`
in `eng/Versions.props`.

A community SDK 10.0.113 build produced on **FreeBSD 14.3** ran some .NET CLI
commands on FreeBSD 15.1 but crashed in `libcoreclr.so` (SIGSEGV,
.NET ThreadPool worker, fault address `0x108`) when executing
`dotnet build-server shutdown --msbuild`. This does **not** establish the
root cause or prove all FreeBSD 14 binaries incompatible with FreeBSD 15.

**Do not patch out MSBuild startup/shutdown calls merely to bypass this crash.**
Either validate a stable FreeBSD 15-compatible bootstrap or build one
reproducibly in the VM, using matching versioned artifacts.

The upstream `v10.0.113` source release itself declares 10.0.112 as
its previous bootstrap. Building that intermediate version is an available
fallback, **not the initial deliverable**.

## Execution gates

- [ ] Confirm the VM's FreeBSD version, architecture, ZFS free space and
      available RAM/swap.
- [ ] Record installed build-tool and native dependency versions.
- [ ] Establish a usable, provenance-checked SDK 10.0.113 bootstrap and
      matching previous source-built artifacts for the native build.
- [ ] Verify MSBuild version, a real console-project build, and
      `dotnet build-server shutdown --msbuild` without crashes.
- [ ] Document the exact native FreeBSD 15 build command, dependencies and
      any source changes, **before** running a full build.
- [ ] Build the 10.0.115 SDK and both 10.0.15 runtimes; keep logs.
- [ ] Verify output versions, dependency linkage, console-project execution
      and ASP.NET Core/Kestrel startup.
- [ ] Test Technitium against the candidate runtime in an isolated environment.
- [ ] Produce a release archive with SHA256, build provenance and restore notes.


## Verified bootstrap inputs (FreeBSD 15.1 VM, 2026-11-14)

Source Build requires two distinct inputs, whose versions must agree with
the upstream source tree's `global.json` and `eng/Versions.props`.

For intermediate upstream `dotnet/dotnet@v10.0.113`:
- Git tag resolves to `4099f83977f4d29604a9aeb971fb0a7bc1d5f699`.
- `global.json` requires SDK `10.0.112`.
- `eng/Versions.props` requires source-built packages
  `10.0.112-servicing.26422.108`.
- SDK `10.0.112` is downloaded from the project's
  [previous FreeBSD 15 release](https://github.com/setsor/dotnet/releases/tag/v10.0.112-freebsd15-x64).
  SHA256: `a24bbe5eda077eb89b0ea2e08a05595dc34ea7958e47e93ae396948c83936d48`.
- Source-built packages were downloaded from the official FreeBSD distfiles
  mirror (`pkg.freebsd.org/ports-distfiles/dotnet/`).
  SHA256: `7aab7f18a9db58684e6206f5958f065224633b8867133fb023df037f5080313a`.
- Packages extracted under `/home/builder/bootstrap/packages-10.0.112`.
- SDK extracted under `/home/builder/bootstrap/dotnet-10.0.112`.
- Native FreeBSD 15 `dotnet --info`, `dotnet msbuild -version`, and
  `dotnet build-server shutdown --msbuild` succeed with
  `DOTNET_OPENSSL_VERSION_OVERRIDE=35`. The override is needed because
  FreeBSD 15 base OpenSSL is `/usr/lib/libssl.so.35`.
- Build from upstream 10.0.113 is **not yet validated**; a real .NET console
  project and the native build remain to be executed.

For final upstream `v10.0.115`, `global.json` and `eng/Versions.props`
require SDK `10.0.113` and previously source-built artifacts
`10.0.113-servicing.26504.104`. Thus 10.0.113 is an explicit
intermediate bootstrap, not the final release deliverable.

## Release policy

No release or production upgrade is considered complete until all acceptance
checks above pass. Release binaries must be labeled **unofficial FreeBSD
community builds**, not official Microsoft binaries.

References: [Microsoft v10.0.115 source release](https://github.com/dotnet/dotnet/releases/tag/v10.0.115),
[FreeBSD build background](https://github.com/dotnet/runtime/blob/main/docs/workflow/requirements/freebsd-requirements.md).


## FreeBSD 15 source compatibility audit (2026-11-14)

Source basis: upstream `v10.0.115`, checked against the current
[FreeBSD Ports `lang/dotnet/files`](https://github.com/freebsd/freebsd-ports/tree/main/lang/dotnet/files).
The patches below are **candidates for review**, not applied changes.
No patch has been copied into this branch.

| Area | Observed in upstream v10.0.115 | FreeBSD Ports reference | Status |
|---|---|---|---|
| MSBuild node IPC | `NodeProviderOutOfProcBase.cs` uses one asynchronous header read; `NodeEndpointOutOfProcBase.cs` still checks short reads | FreeBSD Ports patches based on msbuild PR #14479 | Review whether upstream requires the partial-read fix before native build |
| MSBuild failure-node shutdown | Existing shutdown behavior differs from Ports' guarded shutdown | Ports `BuildManager.cs` patch based on PR #14479 | Review alongside IPC changes; never suppress command failures |
| CoreCLR PAL | `StackString()` does not initialize its NUL terminator | Ports `stackstring.hpp` patch | Review native correctness independently |
| Process enumeration | FreeBSD `Interop.Process.cs` still has original exception and native-buffer handling | Ports `Interop.Process.cs` patch | Review under FreeBSD 15 |
| Native socket event registration | kqueue/EV_RECEIPT code differs from Ports' socket patch | Ports `pal_networking.c` patch | Review under FreeBSD 15 |
| OpenSSL | FreeBSD Ports can force `OPENSSL_ROOT_DIR=/usr` for base SSL | Ports conditional `extra-patch-base-openssl` | **Conditional**, not automatically required if the selected SSL provider is in `/usr/local` |

The Ports recipe currently targets SDK 10.0.114 (not this release)
and builds using a previous SDK 10.0.112 bootstrap. It is a useful
implementation reference but does not establish that this older bootstrap
is sufficient for `v10.0.115`.

**Bootstrap acceptance rule:** resolve the version and provenance of
bootstrap SDK and matching source-built artifacts before running the
full build. A successful `dotnet --version` alone does not establish
that MSBuild and worker-process communication are stable.

Next investigation in the VM:
`pkg search` for existing native SDK packages, the bootstrap package
provenance, and missing FreeBSD-native development libraries. Record
the results before choosing any patch set or executing `build.sh`.


## Native 10.0.113 bootstrap build: first failure and documented upstream bug

On 2026-11-14, the **unmodified** upstream `v10.0.113` build was
started in the FreeBSD 15.1 VM with SDK 10.0.112 and the matching
verified source-built artifacts, using `--source-build --with-sdk
--with-packages`. Initial source-only toolset initialization,
SDK resolver build, and server shutdown all succeeded.

The later `source-build-assets` stage failed with `MSB4166`
(child MSBuild node exited) and follow-on `MSB4242`.
`/tmp/MSBuildTemp/MSBuild_pid-4835_a9c89349e85344ed845e64b28f73a4f6.failure.txt`
records `System.IO.IOException: Broken pipe`, socket error 32,
in `NodeEndpointOutOfProcBase.RunReadLoop`. No new core dump or
kernel signal was confirmed for this build. Do not confuse the earlier
OpenSSL SIGABRT tests with this failure.

This closely matches the documented FreeBSD 15 multicore issue
[dotnet/dotnet#4226](https://github.com/dotnet/dotnet/issues/4226).
The underlying MSBuild IPC bug assumes that one stream read receives
a complete message; the OS can return fewer bytes without error.
Upstream [dotnet/msbuild#14997](https://github.com/dotnet/msbuild/pull/14997)
merged a partial-read fix into MSBuild main on 2026-10-06; the
servicing-source snapshot in v10.0.113/v10.0.115 does not contain the
relevant fix. The separate abandoned PR #14479 was split into #14997
(merged) and #14998 (not merged at this audit).

**Next diagnostic gate:** verify that `DOTNET_PROCESSOR_COUNT=1`
is recognized by the FreeBSD bootstrap SDK, then perform one controlled
single-worker source-build attempt. This limits exposure to the
confirmed multicore IPC defect; it is not a code fix and must not
be presented as one. No fix has yet been applied to the source tree.



## Native 10.0.113: single-CPU diagnostic build (2026-11-14)

A subsequent attempt used `DOTNET_PROCESSOR_COUNT=1` and
`-maxcpucount:1` without applying patches. It passed the earlier
MSBuild node-failure point but **did not complete**. Unlike the first
run, this failed during NuGet restore in `source-build-assets`, with
22 errors and no new MSBuild failure report. The previous
`MSBuild_pid-4835_*.failure.txt` dated 17:24 belongs to the first run.

Primary errors:
- `NU1101`: missing platform-specific packages
  `runtime.freebsd-x64.microsoft.netcore.ilasm` and
  `runtime.freebsd-x64.microsoft.netcore.ildasm`.
- `NU1603`: `Microsoft.Build.Tasks.Core` and
  `Microsoft.Build.Utilities.Core` require version `18.0.11`
  but NuGet restored `18.0.35` instead (warning treated as error).
- `MSB3073` in the parent build only propagates the failing
  source-build-assets invocation.

The upstream v10.0.113 `src/source-build-assets/eng/Version.Details.props`
defines `MicrosoftNETCoreILAsmPackageVersion=10.0.13`,
`MicrosoftNETCoreILDAsmPackageVersion=10.0.13`, and MSBuild package
version `18.0.35`. The observed `18.0.11` requirement must therefore
be traced through the generated package/version props rather than
overriding versions blindly. FreeBSD is a community platform, so
native ILAsm/ILDAsm packages may not exist in Microsoft's public feeds.

**Next gate:** inspect exact package filenames and versions in
the verified 10.0.112 artifact archive and bootstrap SDK's
`library-packs`, then inspect the generated
`artifacts/obj/PackageVersions/PackageVersions.source-build-assets.props`.
Do not suppress `NU1603`, rename package versions, or restart the
full build until the package provenance/version mismatch is understood.
