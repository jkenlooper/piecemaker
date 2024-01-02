#!/usr/bin/env sh

set -o errexit

# UPKEEP due: "2025-03-11" label: "libspatialindex for Python Rtree" interval: "+2 years"
# Alpine Linux currently doesn't have spatialindex available as a package.
# Opting to install manually at this point.
# https://github.com/libspatialindex/libspatialindex/releases
spatialindex_sha512sum="519d1395de01ffc057a0da97a610c91b1ade07772f54fce521553aafd1d29b58df9878bb067368fd0a0990049b6abce0b054af7ccce6bf123b835f5c7ed80eec"
spatialindex_version="1.9.3"
spatialindex_release_url="https://github.com/libspatialindex/libspatialindex/releases/download/$spatialindex_version/spatialindex-src-$spatialindex_version.tar.gz"
spatialindex_tar="$(basename "$spatialindex_release_url")"
spatialindex_install_dir="$(mktemp -d)"
wget -P "$spatialindex_install_dir" -O "$spatialindex_install_dir/$spatialindex_tar" "$spatialindex_release_url"
sha512sum "$spatialindex_install_dir/$spatialindex_tar"
echo "$spatialindex_sha512sum  $spatialindex_install_dir/$spatialindex_tar" | sha512sum -c \
  || ( \
    echo "Cleaning up in case errexit is not set." \
    && mv --verbose "$spatialindex_install_dir/$spatialindex_tar" "$spatialindex_install_dir/$spatialindex_tar.INVALID" \
    && exit 1 \
    )
tar x -o -f "$spatialindex_install_dir/$spatialindex_tar" -C "$spatialindex_install_dir" --strip-components 1
(cd "$spatialindex_install_dir"
  cmake -B build \
    -DCMAKE_BUILD_TYPE=MinSizeRel \
    -DCMAKE_PREFIX_PATH=/usr \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DBUILD_TESTING=ON
  cmake --build build
  cmake --build build --target install
)
