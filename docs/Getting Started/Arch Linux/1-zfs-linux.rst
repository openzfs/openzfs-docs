.. highlight:: sh

zfs-linux
============

.. contents:: Table of Contents
  :local:

``zfs-linux*`` packages provides prebuilt modules.
Prebuilt modules are kernel-specific, i.e.,
module built for 5.11.1 is incompatible
with 5.11.2.
For this reason, ``zfs-linux*``
depends on a particular kernel version.

Example: if linux=5.11.2 is available, but
zfs-linux=5.11.2 is not available, you can not
upgrade to linux=5.11.2 until zfs-linux=5.11.2
came out.

``zfs-linux*`` is recommended for users who are using stock kernels
from Arch Linux repo and can accept kernel update delays.

You can also switch between ``zfs-linux*`` and ``zfs-dkms``
packages later.

For other kernels or Arch-based distros, use zfs-dkms package.

Available packages
~~~~~~~~~~~~~~~~~~~
* zfs-linux
* zfs-linux-lts
* zfs-linux-zen
* zfs-linux-hardened

Installation
~~~~~~~~~~~~

#. Check kernel variant::

    INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

#. Check compatible kernel version::

    INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} | grep 'Depends On' | sed "s|.*${INST_LINVAR}=||" | awk '{ print $1 }')

#. Install kernel. Download from archive if kernel is not available::

    if [ ${INST_LINVER} = \
    $(pacman -Si ${INST_LINVAR} | grep Version | awk '{ print $3 }') ]; then
     pacman -S --noconfirm --needed ${INST_LINVAR}
    else
     pacman -U --noconfirm --needed \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst
    fi

#. Install zfs-linux::

    pacman -Sy zfs-${INST_LINVAR}

#. Ignore kernel updates::

     sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
     sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR} zfs-utils/" /etc/pacman.conf

#. Load kernel module::

    modprobe zfs

Update kernel
~~~~~~~~~~~~~
To update kernel, run::

     INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')
     pacman -Sy --needed --noconfirm ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR} zfs-utils
