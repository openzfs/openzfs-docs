#!/usr/bin/env bash
# working directory: root of repo
set -vxuef

distro="${1}"

# clean up previous tests
find /dev/mapper/ -name '*-part4' -print0 \
     | xargs -t -0I'{}' sh -vxc "swapoff '{}' && cryptsetup close '{}'"

find . -mindepth 1 -maxdepth 1 -type d -name 'rootfs-*' \
    | while read -r dir; do
    grep "$(pwd || true)/${dir##./}" /proc/mounts \
        | cut -f2 -d' ' | sort | tac \
        | xargs -t -I '{}' sh -vxc "if test -d '{}'; then umount -Rl '{}'; fi"
done
find /dev -mindepth 1 -maxdepth 1 -type l -name 'loop*' -exec rm {} +
zpool export -a
losetup --detach-all

# download alpine linux chroot
# it is easier to install rhel with Alpine Linux live media
# which has native zfs support
if ! test -f rootfs.tar.gz; then
    curl --fail-early --fail -Lo rootfs.tar.gz https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.0-x86_64.tar.gz
    curl --fail-early --fail -Lo rootfs.tar.gz.sig https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.0-x86_64.tar.gz.asc
    gpg --auto-key-retrieve --keyserver hkps://keyserver.ubuntu.com --verify rootfs.tar.gz.sig
fi
mkdir rootfs-"${distro}"
tar --auto-compress --extract --file rootfs.tar.gz --directory ./rootfs-"${distro}"

# Create empty disk image
qemu-img create -f raw "${distro}"_disk1.img 16G
qemu-img create -f raw "${distro}"_disk2.img 16G
losetup --partscan "$(losetup -f || true)"  "${distro}"_disk1.img
losetup --partscan "$(losetup -f || true)" "${distro}"_disk2.img

run_test () {
    local path="${1}"
    local distro="${2}"
    sed 's|.. ifconfig:: zfs_root_test|::|g' \
	"${path}" > "${distro}".rst
    sed -i '/highlight:: sh/d' "${distro}".rst

    # Generate installation script from documentation
    python scripts/zfs_root_gen_bash.py "${distro}".rst "${distro}".sh

    # Postprocess script for bash
    sed -i 's|^ *::||g' "${distro}".sh
    # ensure heredocs work
    sed -i 's|^ *ZFS_ROOT_GUIDE_TEST|ZFS_ROOT_GUIDE_TEST|g' "${distro}".sh
    sed -i 's|^ *ZFS_ROOT_NESTED_CHROOT|ZFS_ROOT_NESTED_CHROOT|g' "${distro}".sh
    sed -i 's|^ *EOF|EOF|g' "${distro}".sh

    # check whether nixos.sh have syntax errors
    sh -n "${distro}".sh

    ## !shellcheck does not handle nested chroots
    # create another file with <<EOF construct removed
    sed 's|<<.*||g' "${distro}".sh > "${distro}"-shellcheck.sh
    shellcheck \
        --check-sourced \
        --enable=all \
        --shell=dash \
        --severity=style \
        --format=tty \
        "${distro}"-shellcheck.sh

    # Make the installation script executable and run
    chmod a+x "${distro}".sh
    ./"${distro}".sh "${distro}"
}


case "${distro}" in
    ("nixos")
        run_test 'docs/Getting Started/NixOS/Root on ZFS.rst'  "${distro}"
        ;;

    ("rhel")
        run_test 'docs/Getting Started/RHEL-based distro/Root on ZFS.rst'  "${distro}"
        ;;
    ("alpine")
        run_test 'docs/Getting Started/Alpine Linux/Root on ZFS.rst'  "${distro}"
        ;;

    ("archlinux")
        run_test 'docs/Getting Started/Arch Linux/Root on ZFS.rst' "${distro}"
        ;;

    ("fedora")
        run_test 'docs/Getting Started/Fedora/Root on ZFS.rst' "${distro}"
        ;;

    ("maintenance")
        grep -B1000 'MAINTENANCE SCRIPT ENTRY POINT' 'docs/Getting Started/Alpine Linux/Root on ZFS.rst' > test_maintenance.rst
        cat 'docs/Getting Started/zfs_root_maintenance.rst' >> test_maintenance.rst
        grep -A1000 'MAINTENANCE SCRIPT ENTRY POINT' 'docs/Getting Started/Alpine Linux/Root on ZFS.rst' >> test_maintenance.rst
        run_test './test_maintenance.rst' "${distro}"
        ;;
    (*)
        echo "no distro specified"
        exit 1
        ;;
esac
