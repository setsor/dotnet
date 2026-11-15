# .NET SDK 10.0.113 — native FreeBSD 15.1 bootstrap

## Scope and baseline

This branch starts from Microsoft's **unmodified v10.0.113** source tag
(commit `4099f83977f4d29604a9aeb971fb0a7bc1d5f699`), plus two
separately committed upstream bug-fix backports:

1. `src/fsharp/FSharpBuild.Directory.Build.targets`: for
   `DotNetBuildSourceOnly=true`, set `UpdateXlfOnBuild=false` **after**
   the Arcade SDK targets import. Fixes the known intermittent
   `FSharp.Core.fsproj: MSB4057: target "UpdateXlf" does not exist` error
   on source-only builds. Source:
   https://github.com/dotnet/fsharp/issues/19961
   and the corresponding change in `dotnet/fsharp` main.
2. `src/msbuild/src/Build/BackEnd/Components/Communications/NodeProviderOutOfProcBase.cs`:
   accumulate partial header reads until the complete header is available
   or EOF occurs. Backported from merged
   https://github.com/dotnet/msbuild/pull/14997
   (adapted from current upstream's `_readStream` to this servicing
   snapshot's `_pipeStream`). This changes the MSBuild **being built**,
   not the pre-existing 10.0.112 bootstrap MSBuild.

**Status at 2026-11-15:** native 10.0.113 source builds have progressed
through `source-build-assets` and multiple components, but a complete
successful build has **not** been confirmed. The two source backports
have been committed to GitHub; no successful VM build after applying
both backports has been reported.

## Verified local prerequisites

- FreeBSD 15.1-RELEASE amd64, native build VM `dotnet-build.home.arpa`.
- Working FreeBSD 15.1 SDK 10.0.112 and source-built 10.0.112 package
  archive are prerequisites; the bootstrap SDK requires
  `DOTNET_OPENSSL_VERSION_OVERRIDE=35`.
- Bootstrap SDK:
  `/home/builder/bootstrap/dotnet-10.0.112`.
- Extracted previous source-built packages:
  `/home/builder/bootstrap/packages-10.0.112`.
- `libunwind-devel-g20261022` from FreeBSD Ports installs
  `libunwind-x86_64.so.11` and `libunwind.so.11`, both verified with
  `ldd` on the bootstrap `ilasm` tool; the existing
  `libunwind-20250904` coexists.
- `llvm21-lite` installed from FreeBSD packages, providing the verified
  executables `/usr/local/llvm21/bin/llvm-{ar,nm,ranlib,strings,link,objdump,readelf}`.
  Add `/usr/local/llvm21/bin` to the **build process** PATH to satisfy
  NativeAOT CMake detection. The FreeBSD `sh` shell does not expand
  Bash brace notation in interactive commands.
- While bootstrapping with MSBuild 10.0.112, use
  `DOTNET_PROCESSOR_COUNT=1` and `-maxcpucount:1` as a workaround
  for its FreeBSD partial stream-read issue.

## Native build command

Run as `builder` from the checkout that contains **this branch's
committed source changes**, in `tmux`:

```sh
cd /home/builder/src/dotnet-10.0.113
export PATH="/usr/local/llvm21/bin:$PATH"
export DOTNET_OPENSSL_VERSION_OVERRIDE=35
export DOTNET_PROCESSOR_COUNT=1

/usr/local/bin/bash -o pipefail -c '
./build.sh --source-build \
  --with-sdk /home/builder/bootstrap/dotnet-10.0.112 \
  --with-packages /home/builder/bootstrap/packages-10.0.112 \
  -- -maxcpucount:1 /p:MinimalConsoleLogOutput=false \
  2>&1 | tee /home/builder/bootstrap/build-10.0.113-next.log
'
echo "BUILD_EXIT=$?"
```

Do not infer success from an early nested `Build succeeded.`; require
`BUILD_EXIT=0` and the final VMR build summary.

## Previously diagnosed failures

1. **MSBuild MSB4166 / Broken pipe:** intermittent on FreeBSD 15,
   associated with short reads on pipe/socket stream. See
   https://github.com/dotnet/dotnet/issues/4226.
   `DOTNET_PROCESSOR_COUNT=1` allowed the next attempt to progress.
   Source patch above targets the eventually produced MSBuild.
2. **NU1101 / NU1603 in `source-build-assets`:** the initial generated
   `artifacts/obj/source-build-assets/NuGet.config` lacked the
   `previously-source-built` local feed even though the 10.0.112
   package archive contained the requested versions
   (`Microsoft.Build.Tasks.Core`/`Utilities.Core` 18.0.11,
   FreeBSD ILAsm/ILDAsm 10.0.12). The marker
   `artifacts/obj/source-build-assets/UpdateNuGetConfig.complete`
   was newer than the copied original config. Moving that generated
   marker aside caused the source-build target to recreate the config
   with `previously-source-built=/home/builder/bootstrap/packages-10.0.112/`.
   No package versions were renamed.
3. **Native ILAsm:** failed at execution with
   `libunwind-x86_64.so.11 not found`. Installing the correct ABI 11
   library resolved the loader issue.
4. **Application Insights:** the generated inner clone was recopied
   after the `ApplyPatches.complete` incremental marker, losing its
   two *already supplied* source-build patches. These are
   `0001-Eliminate-prebuilts.patch` (remove
   `Microsoft.SourceLink.GitHub 1.0.0`) and
   `0002-Update-System.Diagnostics.DiagnosticSource-to-elimin.patch`
   (use 8.0.0 rather than 5.0.0). Restore then requires the official
   `ApplyPatches` target to rerun on a fresh inner clone. Preserve
   unrelated package and build outputs. These changes belong to
   intermediate `artifacts/clone`, not the tracked upstream source.
5. **Retry5 NativeAOT:** `configuretools.cmake:38` reported
   `Unable to find toolchain executable. Name: 'link', Prefix: 'llvm-'`.
   `llvm21-lite` was installed afterwards; the next build must have
   its directory in PATH.
6. **Retry5 FSharp:** `FSharp.Core.fsproj` reported `MSB4057` for
   `UpdateXlf` and parent `MSB4181`. The backport above follows
   the published upstream source-only fix. A full successful build
   using this patch is not yet confirmed.

## Handoff to final version

The final target is `freebsd15-v10.0.115`, based on Microsoft's
v10.0.115 source tag. That version requires an SDK 10.0.113 bootstrap
and the matching 10.0.113 source-built artifacts. Do not claim that
the 10.0.115 build is bootstrappable until the 10.0.113 output has
been successfully built and verified.


### 2026-11-15 — retry6: generated NuGet feed staleness

The native v10.0.113 retry6 passed the previous LLVM tool detection;
its runtime bootstrap progressed into CMake probes and built for roughly
20 minutes. It then failed NuGet restore in the built Arcade SDK's
`tools/Tools.proj`: `NU1603` could not find
`Microsoft.DotNet.Build.Tasks.Feed 10.0.0-dev` and selected an unrelated
11.0.0 prerelease version.

The exact `Microsoft.DotNet.Build.Tasks.Feed.10.0.0-dev.nupkg`
exists under both `artifacts/packages/Release/NonShipping/arcade/`
and `src/arcade/artifacts/packages/Release/NonShipping/`; this is a
feed configuration problem, not an absent package. The generated
`artifacts/obj/runtime/NuGet.config` contained no Arcade or
`previously-source-built` feeds; its timestamp (2026-11-14 16:55)
predated `UpdateNuGetConfig.complete` (2026-11-15 00:26).
The `UpdateNuGetConfig` target previously had an incremental marker
whose freshness could not guarantee that `CopyNuGetConfig` had not
subsequently replaced the configured file with the original.

**Committed fix in `repo-projects/Directory.Build.targets`:**
remove incremental `Inputs`/`Outputs` from `UpdateNuGetConfig`,
keeping `CopyNuGetConfig` and the existing NuGet source mapping tasks.
Every invocation now reapplies the local source-built package feeds,
rather than trusting an outdated marker. This is a tracked code fix
in the source-build orchestration, **not yet verified** by a complete
successful retry. Preserve the compiled artifacts for incremental builds.
