.. highlight:: sh

Arch Linux
============

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

Add archzfs repo
~~~~~~~~~~~~~~~~

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

Prebuilt zfs package
~~~~~~~~~~~~~~~~~~~~

This only applies to vanilla Arch Linux kernels.
For other kernels, use `archzfs-dkms package`_.
You can also switch between DKMS and prebuilt
packages with instructions on this page.

Check kernel variant::

 INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | awk '{ print $1 }')

Install compatible package::

 pacman -Sy archzfs-${INST_LINVAR}

If kernel dependency failed, you can either:

* Install `archzfs-dkms package`_, or

* Downgrade kernel
  to a compatible version:

Downgrade to compatible kernel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check compatible kernel version::

 INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} \
 | grep 'Depends On' \
 | sed "s|.*${INST_LINVAR}=||" \
 | awk '{ print $1 }')

Install compatible kernel::

 pacman -U \
 https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst

Install archzfs::

 pacman -Sy archzfs-${INST_LINVAR}

Ignore kernel update when dependency fails
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes archzfs prebuilt package might lag behind
kernel updates::

 pacman -Syu
 # error: failed to prepare transaction (could not satisfy dependencies)
 # :: installing linux-lts (5.4.93-2) breaks dependency 'linux-lts=5.4.92-1' required by zfs-linux-lts

Temporarily ignore kernel update to upgrade other packages::

 pacman -Syu --ignore=linux-lts

archzfs-dkms package
~~~~~~~~~~~~~~~~~~~~

This package will dynamically build ZFS modules for
supported kernels. Both Arch Linux and derivatives
are supported.

Check OpenZFS compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check kernel version::

  uname -r
  # 5.4.92-1-lts

Check newer archzfs-dkms package version::

 DKMS_VER=$(pacman -Si zfs-dkms \
 | grep 'Version' \
 | awk '{ print $3 }' \
 | sed 's|-.*||')

Visit OpenZFS release page ::

 curl https://github.com/openzfs/zfs/releases/zfs-${DKMS_VER} \
 | grep Linux
 # Linux: compatible with 3.10 - 5.10 kernels

If it's not supported, see `Install alternative kernel`_.
Otherwise, continue to next step.

Normal installation
^^^^^^^^^^^^^^^^^^^

Check kernel variant::

  INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | awk '{ print $1 }')

Check kernel version::

  INST_LINVER=$(pacman -Qi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

Install kernel headers::

  pacman -U https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst
  # for artix
  pacman -U https://archive.artixlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

Install archzfs-dkms::

  pacman -Sy archzfs-dkms

Hold kernel package from updates::

  sed -i 's/#.*IgnorePkg/IgnorePkg/' /etc/pacman.conf
  sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

Kernel must be manually updated, see `Kernel update`_.

Install alternative kernel
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the kernel is not yet supported, install a supported kernel:

Choose kernel variant. Available variants are:

* linux
* linux-lts

For Artix, replace ``archlinux.org`` with ``artixlinux.org``.

::

  INST_LINVAR=linux

Check build date::

  DKMS_DATE=$(pacman -Syi zfs-dkms \
  | grep 'Build Date' \
  | sed 's/.*: //' \
  | LC_ALL=C xargs -i{} date -d {}  +%Y/%m/%d)

Check kernel version::

  curl https://archive.archlinux.org/repos/${DKMS_DATE}/core/os/x86_64/ \
  | grep \"${INST_LINVAR}-'[0-9]' \
  | grep -v sig
  # <a href="linux-5.10.3.arch1-1-x86_64.pkg.tar.zst">

Set kernel version in a variable::

  # <a href="linux-5.10.3.arch1-1-x86_64.pkg.tar.zst">
  INST_LINVER=5.10.3.arch1-1

Install kernel and headers::

  pacman -U \
  https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst \
  https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

Install archzfs-dkms::

  pacman -Sy archzfs-dkms

Hold kernel package from updates::

  sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
  sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

Kernel must be manually updated, see `Kernel update`_.

Kernel update
^^^^^^^^^^^^^

This applies to archzfs-dkms package.

Check kernel variant::

 INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | awk '{ print $1 }')

Check newer kernel version::

 pacman -Syi $INST_LINVAR \
 | grep 'Version' \
 | awk '{ print $3 }'
 # 5.10.1.1-1

Check newer archzfs-dkms package version::

 DKMS_VER=$(pacman -Si zfs-dkms \
 | grep 'Version' \
 | awk '{ print $3 }' \
 | sed 's|-.*||')

Visit OpenZFS release page ::

 curl https://github.com/openzfs/zfs/releases/zfs-${DKMS_VER} \
 | grep Linux
 # Linux: compatible with 3.10 - 5.10 kernels

If compatible, update kernel with::

 pacman -S $INST_LINVAR $INST_LINVAR-headers archzfs-dkms

Do not update if the kernel is not compatible
with OpenZFS.

glibc version mismatch
^^^^^^^^^^^^^^^^^^^^^^
As of Feb 6th, 2021, latest glibc release is ``2.33``.
glibc in Arch Linux repo is ``2.32``.

When updating ``linux-lts (5.4.94-1 -> 5.4.95-1)``,
``linux-lts-headers`` will depend on the unavailable glibc ``2.33``
::

 # /var/lib/dkms/zfs/2.0.2/build/config.log
 
 configure:18576: checking whether modules can be built
 configure:18746:
             KBUILD_MODPOST_NOFINAL= KBUILD_MODPOST_WARN=
             make modules -k -j4 -C /usr/lib/modules/5.4.95-1-lts/build
             M=/var/lib/dkms/zfs/2.0.2/build/build/conftest >build/conftest/build.log 2>&1
 configure:18749: $? = 2
 configure:18752: test -f build/conftest/conftest.ko
 configure:18755: $? = 1
 configure:18764: result: no
 configure:18767: error:
         *** Unable to build an empty module.

::

 # /var/lib/dkms/zfs/2.0.2/build/build/conftest/build.log
 
 make: Entering directory '/usr/lib/modules/5.4.95-1-lts/build'
   CC [M]  /var/lib/dkms/zfs/2.0.2/build/build/conftest/conftest.o
 scripts/basic/fixdep: /usr/lib/libc.so.6: version `GLIBC_2.33' not found (required by scripts/basic/fixdep)
 make[1]: *** [scripts/Makefile.build:262: /var/lib/dkms/zfs/2.0.2/build/build/conftest/conftest.o] Error 1
 make[1]: *** Deleting file '/var/lib/dkms/zfs/2.0.2/build/build/conftest/conftest.o'

::

 pacman -Qo /usr/lib/modules/5.4.95-1-lts/build/scripts/basic/fixdep
 /usr/lib/modules/5.4.95-1-lts/build/scripts/basic/fixdep is owned by linux-lts-headers 5.4.95-1

To solve the problem, rollback kernel update
and postpone kernel updates
until glibc ``2.33`` becomes available.

::

 cd /var/cache/pacman/pkg/
 pacman -U linux-lts-5.4.94-1-x86_64.pkg.tar.zst linux-lts-headers-5.4.94-1-x86_64.pkg.tar.zst

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

#. Check latest archzfs package version::

    https://archzfs.com/archzfs/x86_64/
    # zfs-dkms-2.0.1-1-x86_64.pkg.tar.zst
    # zfs-linux-2.0.1_5.10.10.arch1.1-1-x86_64.pkg.tar.zst

#. Visit OpenZFS release page https://github.com/openzfs/zfs/releases/tag/zfs-2.0.1::

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
