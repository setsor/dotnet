# .NET 10.0.115 — FreeBSD 15.1 amd64

## Purpose and status

**Status: preparation; native build not yet run or validated.**

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
