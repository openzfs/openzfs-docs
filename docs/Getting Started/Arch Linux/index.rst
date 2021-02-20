.. highlight:: sh

Arch Linux
============

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

archzfs repo
~~~~~~~~~~~~

ZFS packages are provided by the third-party
`archzfs repository <https://github.com/archzfs/archzfs>`__.
You can use it as follows.

Import archzfs GPG key::

  curl -O https://archzfs.com/archzfs.gpg
  pacman-key -a archzfs.gpg
  pacman-key --lsign-key DDF7DB817396A49B2A2723F7403BD972F75D9D76

Add the archzfs repository::

  tee -a /etc/pacman.conf <<- 'EOF'
  [archzfs]
  Server = https://archzfs.com/$repo/$arch
  Server = https://mirror.sum7.eu/archlinux/archzfs/$repo/$arch
  Server = https://mirror.biocrafting.net/archlinux/archzfs/$repo/$arch
  Server = https://mirror.in.themindsmaze.com/archzfs/$repo/$arch
  EOF

Update pacman database::

  pacman -Sy

archzfs package
~~~~~~~~~~~~~~~

When using unmodified Arch Linux kernels,
prebuilt ``archzfs`` packages are available.
You can also switch between ``archzfs`` and ``zfs-dkms``
packages later.

For other kernels or distros, use `archzfs-dkms package`_.

Check kernel variant::

 INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | awk '{ print $1 }')

Check compatible kernel version::

 INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} | grep 'Depends On' | sed "s|.*${INST_LINVAR}=||" | awk '{ print $1 }')

Install compatible kernel::

 pacman -U \
 https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst

Install archzfs::

 pacman -Sy zfs-${INST_LINVAR}

archzfs-dkms package
~~~~~~~~~~~~~~~~~~~~

This package will dynamically build ZFS modules for
supported kernels.

Check kernel compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^

Check kernel variant::

 INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | awk '{ print $1 }')

Check kernel version::

 INST_LINVER=$(pacman -Qi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

Check zfs-dkms package version::

 DKMS_VER=$(pacman -Syi zfs-dkms | grep 'Version' | awk '{ print $3 }' | sed 's|-.*||')

Visit OpenZFS release page ::

 curl https://github.com/openzfs/zfs/releases/zfs-${DKMS_VER} \
 | grep Linux
 # Linux: compatible with 3.10 - 5.10 kernels
 echo $INST_LINVER

If it's not supported, see `Install zfs-dkms compatible kernel`_.
Otherwise, continue to next step.

Install kernel headers::

  pacman -U \
  https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

Install zfs-dkms::

  pacman -Sy zfs-dkms

Ignore kernel package from updates::

  sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
  sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

Kernel must be manually updated, see `Kernel update`_.

Install zfs-dkms compatible kernel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Choose kernel variant. Available variants are:

* linux
* linux-lts

::

  INST_LINVAR=linux

Install kernels available when the package was built. Check build date::

  DKMS_DATE=$(pacman -Syi zfs-dkms \
  | grep 'Build Date' \
  | sed 's/.*: //' \
  | LC_ALL=C xargs -i{} date -d {}  +%Y/%m/%d)

Check kernel version::

  INST_LINVER=$(curl https://archive.archlinux.org/repos/${DKMS_DATE}/core/os/x86_64/ \
  | grep \"${INST_LINVAR}-'[0-9]' \
  | grep -v sig \
  | sed "s|.*$INST_LINVAR-||" \
  | sed "s|-x86_64.*||")

Install compatible kernel and headers::

  pacman -U \
  https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst \
  https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

Install zfs-dkms::

  pacman -Sy zfs-dkms

Hold kernel package from updates::

  sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
  sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

Kernel must be manually updated, see `Kernel update`_.

Kernel update
^^^^^^^^^^^^^

`Check kernel compatibility`_.

Replace check kernel version with ``-Syi``::

 INST_LINVER=$(pacman -Syi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

If compatible, update kernel and headers with::

 pacman -Sy $INST_LINVAR $INST_LINVAR-headers

Do not update if the kernel is not compatible
with OpenZFS.

Check Live Image Compatibility
------------------------------
Choose a mirror::

 https://archlinux.org/mirrorlist/all/
 https://gitea.artixlinux.org/packagesA/artix-mirrorlist/src/branch/master/trunk/mirrorlist

Check the build date of the
latest Arch Linux live image::

 https://mirrors.dotsrc.org/archlinux/iso/latest/
 https://mirrors.dotsrc.org/artix-linux/iso/
 # archlinux-2021.01.01-x86_64.iso

Check the kernel version of the live image::

 https://archive.archlinux.org/repos/2021/01/01/core/os/x86_64
 https://archive.artixlinux.org/repos/2021/01/01/system/os/x86_64
 # linux-5.10.3.arch1-1-x86_64.pkg.tar.zst

Check latest archzfs package version::

 https://archzfs.com/archzfs/x86_64/
 # zfs-dkms-2.0.1-1-x86_64.pkg.tar.zst
 # zfs-linux-2.0.1_5.10.10.arch1.1-1-x86_64.pkg.tar.zst

Visit OpenZFS release page https://github.com/openzfs/zfs/releases/tag/zfs-2.0.1::

  # Linux: compatible with 3.10 - 5.10 kernels

- If compatible, download the latest live image::

   https://mirrors.dotsrc.org/archlinux/iso/latest/archlinux-2021.01.01-x86_64.iso
   https://mirrors.dotsrc.org/artix-linux/iso/artix-base-openrc-20210101-x86_64.iso

- If not compatible, use an older live image and verify that it contains
  a supported kernel using the above method::

   https://mirrors.dotsrc.org/archlinux/iso/
   https://iso.artixlinux.org/archived-isos.php

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS
