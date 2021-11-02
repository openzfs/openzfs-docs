.. highlight:: sh

zfs-dkms
============

.. contents:: Table of Contents
  :local:

``zfs-dkms`` package provides Dynamic Kernel Module Support.
It will automatically build ZFS kernel modules for compatible
kernels.

However, there are several disadvantages:

- slow to build
- little warning when DKMS build fails

``zfs-dkms`` is required for users who are using custom kernels or
do not accept delays for kernel updates. This package is also required for derivative
distros such as `Artix Linux <https://artixlinux.org>`__.

Installation
~~~~~~~~~~~~

#. Check kernel variant::

    INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

  If you are using live image, use the hard-coded value::

    #INST_LINVAR=linux

#. Check kernel version::

    INST_LINVER=$(pacman -Qi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

#. Install kernel headers::

    if [ "${INST_LINVER}" = \
    "$(pacman -Si ${INST_LINVAR}-headers | grep Version | awk '{ print $3 }')" ]; then
     pacman -S --noconfirm --needed ${INST_LINVAR}-headers
    else
     pacman -U --noconfirm --needed \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst
    fi

#. Install zfs-dkms::

     pacman -Sy --needed --noconfirm zfs-dkms glibc

   If pacman output contains the following error message,
   then the kernel needs a `downgrade <#zfs-dkms-compatible-kernel>`__,
   or you can try ``zfs-dkms-git`` package::

    (3/4) Install DKMS modules
    ==> dkms install --no-depmod -m zfs -v 2.0.4 -k 5.12.0-rc5-1-git-00030-gd19cc4bfbff1
    configure: error:
    	*** None of the expected "capability" interfaces were detected.
    	*** This may be because your kernel version is newer than what is
    	*** supported, or you are using a patched custom kernel with
    	*** incompatible modifications.
    	***
    	*** ZFS Version: zfs-2.0.4-1
    	*** Compatible Kernels: 3.10 - 5.11

#. Ignore kernel package from updates::

     sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
     sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" /etc/pacman.conf

#. Load kernel module::

    modprobe zfs

Update kernel
~~~~~~~~~~~~~
#. Check kernel variant::

    INST_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

#. Install zfs-dkms::

     pacman -Sy --needed $INST_LINVAR $INST_LINVAR-headers zfs-dkms glibc

   If pacman output contains the following error message,
   then the kernel needs a `downgrade <#zfs-dkms-compatible-kernel>`__,
   or you can try ``zfs-dkms-git`` package::

    (3/4) Install DKMS modules
    ==> dkms install --no-depmod -m zfs -v 2.0.4 -k 5.12.0-rc5-1-git-00030-gd19cc4bfbff1
    configure: error:
    	*** None of the expected "capability" interfaces were detected.
    	*** This may be because your kernel version is newer than what is
    	*** supported, or you are using a patched custom kernel with
    	*** incompatible modifications.
    	***
    	*** ZFS Version: zfs-2.0.4-1
    	*** Compatible Kernels: 3.10 - 5.11

Install compatible kernel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the installed kernel is not
compatible with ZFS, a kernel downgrade
is needed.

#. Choose kernel variant. Available variants are:

   * linux
   * linux-lts
   * linux-zen
   * linux-hardened

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

#. Continue from `installation <#installation>`__.
