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

Overview
--------

Due to license incompatibility,
ZFS support is provided by out-of-tree kernel modules.

Kernel modules are specific to each kernel package, i.e.,
ZFS kernel module built for ``linux-5.11.1.arch1-1`` is incompatible
with ``linux-5.11.2.arch1-1`` kernel.

ZFS kernel modules can be obtained by

- installing ``zfs-linux*``, which contains prebuilt ZFS kernel modules;
- installing ``zfs-dkms`` and build ZFS kernel modules on-the-fly.

``zfs-linux*`` packages are the easiest and
most risk-free way to obtain ZFS support.
However, they hard-depend on a specific kernel
and will block kernel updates if the corresponding
``zfs-linux*`` package is not available.

``zfs-dkms`` package is the more versatile choice.
After installation, Dynamic Kernel Module Support
will automatically build ZFS kernel modules for installed
kernels and not interfere with kernel updates.
However, the modules are somewhat slow to build and more
importantly, there will be little warning message when the
build fails. Also, as ``zfs-dkms`` does not perform checks against
kernel version, this must be done by user themselves for major kernel updates
such as ``5.10 -> 5.11``.

``zfs-linux*`` is recommended for users who are using stock kernels
from official Arch Linux repo and can accept kernel update delays.
Such delays should be no more than a few days.

``zfs-dkms`` is required for experienced users who are using custom kernels or
want to follow the latest kernel updates. This package is also required for derivative
distros such as `Artix Linux <https://artixlinux.org>`__.

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

archzfs repo
~~~~~~~~~~~~

ZFS packages are provided by the third-party
`archzfs repository <https://github.com/archzfs/archzfs>`__.
You can use it as follows.

#. Import keys of archzfs repository::

    curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
    curl -L https://git.io/JtQpl | xargs -i{} pacman-key --lsign-key {}
    curl -L https://git.io/JtQp4 > /etc/pacman.d/mirrorlist-archzfs

#. Add archzfs repository::

    tee -a /etc/pacman.conf <<- 'EOF'

    #[archzfs-testing]
    #Include = /etc/pacman.d/mirrorlist-archzfs
 
    [archzfs]
    Include = /etc/pacman.d/mirrorlist-archzfs
    EOF

#. Update pacman database::

     pacman -Sy

zfs-linux* package
~~~~~~~~~~~~~~~~~~

When using unmodified Arch Linux kernels,
prebuilt ``zfs-linux*`` packages are available.
You can also switch between ``zfs-linux*`` and ``zfs-dkms``
packages later.

For other kernels or Arch-based distros, use zfs-dkms package.

#. Check kernel variant::

    INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

#. Check compatible kernel version::

    INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} | grep 'Depends On' | sed "s|.*${INST_LINVAR}=||" | awk '{ print $1 }')

#. Install kernel. Download from archive if kernel is not available::

    if [ ${INST_LINVER} == \
    $(pacman -Si ${INST_LINVAR} | grep Version | awk '{ print $3 }') ]; then
     pacman -S --noconfirm --needed ${INST_LINVAR}
    else
     pacman -U --noconfirm --needed \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst
    fi

#. Install zfs-linux*::

    pacman -Sy zfs-${INST_LINVAR}

#. Ignore kernel updates::

     sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
     sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR} zfs-utils/" /etc/pacman.conf

#. To update kernel, run::

     INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')
     pacman -Sy --needed --noconfirm ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR}

zfs-dkms package
~~~~~~~~~~~~~~~~

Check kernel compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Check kernel variant::

    INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

#. Check kernel version::

    INST_LINVER=$(pacman -Qi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

#. Check zfs-dkms package version::

    DKMS_VER=$(pacman -Syi zfs-dkms | grep 'Version' | awk '{ print $3 }' | sed 's|-.*||')

#. Visit OpenZFS release page ::

    curl -L https://github.com/openzfs/zfs/raw/zfs-${DKMS_VER}/META \
    | grep Linux
    # Linux-Maximum: 5.10
    # Linux-Minimum: 3.10
    # compare with the output of the following command
    echo ${INST_LINVER%%-*}
    # 5.10.17 # supported

   If it's not supported, see `Install zfs-dkms compatible kernel`_.
   Otherwise, continue to next step.

#. Install kernel headers::

     pacman -U \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

#. Install zfs-dkms::

     pacman -Sy zfs-dkms

#. Ignore kernel package from updates::

     sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
     sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

Kernel must be manually updated, see `Kernel update`_.

Install zfs-dkms compatible kernel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Choose kernel variant. Available variants are:

   * linux
   * linux-lts

   ::

     INST_LINVAR=linux

#. Install kernels available when the package was built. Check build date::

     DKMS_DATE=$(pacman -Syi zfs-dkms \
     | grep 'Build Date' \
     | sed 's/.*: //' \
     | LC_ALL=C xargs -i{} date -d {} -u +%Y/%m/%d)

#. Check kernel version::

     INST_LINVER=$(curl https://archive.archlinux.org/repos/${DKMS_DATE}/core/os/x86_64/ \
     | grep \"${INST_LINVAR}-'[0-9]' \
     | grep -v sig \
     | sed "s|.*$INST_LINVAR-||" \
     | sed "s|-x86_64.*||")

#. Install compatible kernel and headers::

     pacman -U \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

#. Install zfs-dkms::

     pacman -Sy zfs-dkms

#. Hold kernel package from updates::

     sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
     sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

   Kernel must be manually updated, see `Kernel update`_.

Kernel update
^^^^^^^^^^^^^

#. `Check kernel compatibility`_.

#. Replace check kernel version with ``-Syi``::

    INST_LINVER=$(pacman -Syi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

#. If compatible, update kernel and headers with::

    pacman -Sy $INST_LINVAR $INST_LINVAR-headers

   Do not update if the kernel is not compatible
   with OpenZFS.

Check Live Image Compatibility
------------------------------
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

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS
