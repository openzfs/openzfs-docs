#!/usr/bin/env bash
source_dir="$1"
build_dir="$2"

mkdir -p "$build_dir/tests/Root on ZFS"

sed 's|.. ifconfig:: zfs_root_test|::|g' \
    "$source_dir/Getting Started/NixOS/Root on ZFS.rst" \
    > "$build_dir/tests/Root on ZFS/nixos.rst"

python \
    ../scripts/my_pylit.py \
    "$build_dir/tests/Root on ZFS/nixos.rst" \
    "$build_dir/tests/Root on ZFS/nixos.sh"
