Fedora
======

Contents
--------
.. toctree::
  :maxdepth: 1
  :glob:

  *

Installation
------------

Note: this is for installing ZFS on an existing Fedora
installation. To use ZFS as root file system,
see below.

#. If ``zfs-fuse`` from official Fedora repo is installed,
   remove it first. It is not maintained and should not be used
   under any circumstance::

    rpm -e --nodeps zfs-fuse

#. Add ZFS repo::

    dnf install -y https://zfsonlinux.org/fedora/zfs-release-2-3$(rpm --eval "%{dist}").noarch.rpm

   List of repos is available `here <https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/fedora>`__.

#. Install kernel headers::

     dnf install -y kernel-devel

   ``kernel-devel`` package must be installed before ``zfs`` package.

#. Install ZFS packages::

    dnf install -y zfs

#. Load kernel module::

    modprobe zfs

   If kernel module can not be loaded, your kernel version
   might be not yet supported by OpenZFS.

   An option is to an LTS kernel from COPR, provided by a third-party.
   Use it at your own risk::

     # this is a third-party repo!
     # you have been warned.
     #
     # select a kernel from
     # https://copr.fedorainfracloud.org/coprs/kwizart/

     dnf copr enable -y kwizart/kernel-longterm-VERSION
     dnf install -y kernel-longterm kernel-longterm-devel

   Reboot to new LTS kernel, then load kernel module::

    modprobe zfs

#. By default ZFS kernel modules are loaded upon detecting a pool.
   To always load the modules at boot::

    echo zfs > /etc/modules-load.d/zfs.conf

#. By default ZFS may be removed by kernel package updates.
   To lock the kernel version to only ones supported by ZFS to prevent this::
    echo 'zfs' > /etc/dnf/protected.d/zfs.conf

   Pending non-kernel updates can still be applied::
    dnf update --exclude=kernel*

Testing Repo
--------------------

Testing repository, which is disabled by default, contains
the latest version of OpenZFS which is under active development.
These packages
**should not** be used on production systems.

::

   dnf config-manager --enable zfs-testing
   dnf install zfs

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *
