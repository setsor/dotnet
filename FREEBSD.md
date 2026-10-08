# .NET 10 for FreeBSD 15 x64

This fork publishes an **unofficial community build** of .NET 10 for FreeBSD 15 x64.

Current release:

- .NET SDK: **10.0.112**
- Microsoft.NETCore.App: **10.0.12**
- Microsoft.AspNetCore.App: **10.0.12**
- Architecture: **x86_64 / amd64**
- RID: **freebsd-x64**
- FreeBSD base used for the cross-build rootfs: **15.1-RELEASE**
- Source branch: `freebsd15-v10.0.112`
- Source commit: `e901d50bad`
- Release: [v10.0.112-freebsd15-x64](https://github.com/setsor/dotnet/releases/tag/v10.0.112-freebsd15-x64)

This is **not an official Microsoft binary distribution**.

## Download

Download:

`dotnet-sdk-10.0.112-freebsd-x64.tar.gz`

from the [GitHub release](https://github.com/setsor/dotnet/releases/tag/v10.0.112-freebsd15-x64).

SHA256:

```text
a24bbe5eda077eb89b0ea2e08a05595dc34ea7958e47e93ae396948c83936d48
```

A matching `.sha256` file is attached to the release.

## FreeBSD runtime dependencies

The build was validated with the following FreeBSD packages available:

```sh
pkg install -y \
  gettext-runtime \
  icu \
  krb5 \
  libinotify \
  libunwind \
  openssl \
  readline \
  terminfo-db
```

Some packages may already be present or installed as dependencies on a given FreeBSD system.

## Install

Example system-wide installation:

```sh
mkdir -p /opt/dotnet10
tar -xzf dotnet-sdk-10.0.112-freebsd-x64.tar.gz -C /opt/dotnet10
/opt/dotnet10/dotnet --info
```

For a per-user installation, extract to a directory such as `$HOME/dotnet10` instead.

### OPNsense / OpenSSL 3.5

On the tested OPNsense system, the base system provides OpenSSL 3.5 and .NET required the OpenSSL version override when invoked directly:

```sh
env DOTNET_OPENSSL_VERSION_OVERRIDE=35 \
  /opt/dotnet10/dotnet --info
```

For services, export the variable in the service runner:

```sh
export DOTNET_OPENSSL_VERSION_OVERRIDE="35"
```

Do not add this override on systems where `dotnet --info` already starts normally without it.

## Validation

The release archive was tested natively on FreeBSD 15.1-RELEASE amd64.

Validated scenarios include:

- `dotnet --info`
- .NET console project creation, restore, build and execution
- ASP.NET Core / Kestrel HTTP serving
- Technitium DNS Server 15.6
- DNS resolution through Technitium
- OPNsense production deployment
- dnsdist -> Technitium DNS backend operation
- service restart and post-reboot operation

The same release archive was deployed on OPNsense 26.7.4_1 / FreeBSD 15 and validated after reboot.

## Source change

The FreeBSD 15 support change is intentionally small. It extends `eng/common/cross/build-rootfs.sh` with:

```sh
freebsd15)
    __CodeName=freebsd
    __FreeBSDBase="15.1-RELEASE"
    __FreeBSDABI="15"
    __SkipUnmount=1
    ;;
```

and adds `freebsd15` to the usage text.

## Building from source

Clone the FreeBSD branch:

```sh
git clone --branch freebsd15-v10.0.112 --single-branch \
  https://github.com/setsor/dotnet.git dotnet-10.0.112

cd dotnet-10.0.112
```

Create the FreeBSD 15 x64 rootfs:

```sh
sudo ./eng/common/cross/build-rootfs.sh \
  x64 freebsd15 \
  --rootfsdir "$HOME/cross_root_15_x64" \
  --skipemulation
```

Then run the source-build:

```sh
ROOTFS_DIR="$HOME/cross_root_15_x64" \
./build.sh \
  --prep \
  --configuration Release \
  --target-os freebsd \
  --target-arch x64 \
  --target-rid freebsd-x64 \
  --source-build \
  -p:PortableBuild=true \
  -p:PortableTargetRid=freebsd-x64 \
  -p:CrossBuild=true \
  -p:SkipUsingCrossgen=true \
  -p:BundleCrossgen2=true \
  --ci \
  --official-build-id 20260822.8
```

The validated build was produced from upstream `dotnet/dotnet` tag `v10.0.112`.

### Ubuntu 26.04 note

On the Ubuntu 26.04 build host used for this release, the default `sort` / `comm` implementation caused source-build sort-order errors. GNU coreutils `sort` and `comm`, with `LC_ALL=C`, were used for the successful build.

This is a build-host-specific note, not a FreeBSD runtime requirement.

## License and upstream

This repository is a fork of [dotnet/dotnet](https://github.com/dotnet/dotnet). Upstream licensing and component licenses continue to apply.
