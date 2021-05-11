.. highlight:: sh

Live image
============

Latest live image might contain a kernel incompatible with
ZFS. Check the compatibility with the following procedure.

#. Choose a mirror::

    https://archlinux.org/mirrorlist/all/
    https://gitea.artixlinux.org/packagesA/artix-mirrorlist/src/branch/master/trunk/mirrorlist

#. Check the build date of the
   latest Arch Linux live image::

    https://mirrors.dotsrc.org/archlinux/iso/latest/
    https://mirrors.dotsrc.org/artix-linux/iso/
    # archlinux-2021.01.01-x86_64.iso

#. Check the kernel version of the live image::

    https://archive.archlinux.org/repos/2021/01/01/core/os/x86_64
    https://archive.artixlinux.org/repos/2021/01/01/system/os/x86_64
    # linux-5.10.3.arch1-1-x86_64.pkg.tar.zst

#. Check latest zfs-dkms package version::

    https://archzfs.com/archzfs/x86_64/
    # zfs-dkms-2.0.1-1-x86_64.pkg.tar.zst
    # zfs-linux-2.0.1_5.10.10.arch1.1-1-x86_64.pkg.tar.zst

#. Visit OpenZFS release page::

    curl -L https://github.com/openzfs/zfs/raw/zfs-2.0.1/META \
    | grep Linux
    # Linux-Maximum: 5.10
    # Linux-Minimum: 3.10

   - If compatible, download the latest live image::

      https://mirrors.dotsrc.org/archlinux/iso/latest/archlinux-2021.01.01-x86_64.iso
      https://mirrors.dotsrc.org/artix-linux/iso/artix-base-openrc-20210101-x86_64.iso

   - If not compatible, use an older live image and verify that it contains
     a supported kernel using the above method::

      https://mirrors.dotsrc.org/archlinux/iso/
      https://iso.artixlinux.org/archived-isos.php
