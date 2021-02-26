.. highlight:: sh

Arch Linux
============

.. contents:: Table of Contents
  :local:

Support
-------

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <irc://irc.freenode.net/#zfsonlinux>`__ on `freenode
<https://freenode.net/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @ne9z
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Arch%20Linux%20ZFS%20HOWTO:>`__.

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

archzfs repo
~~~~~~~~~~~~

ZFS packages are provided by the third-party
`archzfs repository <https://github.com/archzfs/archzfs>`__.
You can use it as follows.

Import keys of archzfs repository::

 curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
 curl -L https://git.io/JtQpl | xargs -i{} pacman-key --lsign-key {}

Add archzfs repository::

 tee -a /etc/pacman.conf <<- 'EOF'

 [archzfs]
 Include = /etc/pacman.d/mirrorlist-archzfs
 EOF
 
 curl -L https://git.io/JtQp4 > /etc/pacman.d/mirrorlist-archzfs

Update pacman database::

  pacman -Sy

testing repo
^^^^^^^^^^^^
Testing repo provides newer packages than stable repo,
but may contain unknown bugs.
Use at your own risk::

 tee -a /etc/pacman.conf <<- 'EOF'
 
 # uncomment if you really want to use testing
 #[archzfs-testing]
 #Include = /etc/pacman.d/mirrorlist-archzfs
 EOF

archzfs package
~~~~~~~~~~~~~~~

When using unmodified Arch Linux kernels,
prebuilt ``archzfs`` packages are available.
You can also switch between ``archzfs`` and ``zfs-dkms``
packages later.

For other kernels or distros, use `archzfs-dkms package`_.

Check kernel variant::

 INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

Check compatible kernel version::

 INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} | grep 'Depends On' | sed "s|.*${INST_LINVAR}=||" | awk '{ print $1 }')

Install kernel. Download from archive if kernel is not available::

    if [ ${INST_LINVER} == \
    $(pacman -Si ${INST_LINVAR} | grep Version | awk '{ print $3 }') ]; then
     pacstrap $INST_MNT ${INST_LINVAR}
    else
     pacstrap -U $INST_MNT \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst
    fi

Install archzfs::

 pacman -Sy zfs-${INST_LINVAR}

archzfs-dkms package
~~~~~~~~~~~~~~~~~~~~

This package will dynamically build ZFS modules for
supported kernels.

Check kernel compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^

Check kernel variant::

 INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

Check kernel version::

 INST_LINVER=$(pacman -Qi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

Check zfs-dkms package version::

 DKMS_VER=$(pacman -Syi zfs-dkms | grep 'Version' | awk '{ print $3 }' | sed 's|-.*||')

Visit OpenZFS release page ::

 curl -L https://github.com/openzfs/zfs/raw/zfs-${DKMS_VER}/META \
 | grep Linux
 # Linux-Maximum: 5.10
 # Linux-Minimum: 3.10
 # compare with the output of the following command
 echo ${INST_LINVER%%-*}
 # 5.10.17 # supported

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
  | LC_ALL=C xargs -i{} date -d {} -u +%Y/%m/%d)

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

-git packages
~~~~~~~~~~~~~

Normal packages are built from
`latest OpenZFS stable release <https://github.com/openzfs/zfs/releases/latest>`__
which may not contain the newest features.

``-git`` packages are directly built from
`OpenZFS master branch <https://github.com/openzfs/zfs/commits/master>`__,
which may contain unknown bugs.

To use ``-git`` packages, attach ``-git`` suffix to package names, example::

 # zfs-dkms
 zfs-dkms-git

 # zfs-${INST_LINVAR}
 zfs-${INST_LINVAR}-git

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

Visit OpenZFS release page::

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

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS
