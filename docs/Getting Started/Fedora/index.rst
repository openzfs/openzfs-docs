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

    dnf remove -y zfs-fuse

#. Add ZFS repo::

    dnf install -y https://zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm

#. Install ZFS packages::

    dnf install -y kernel-devel zfs

#. Load kernel module::

    modprobe zfs

   If kernel module can not be loaded, your kernel version
   might be not yet supported by OpenZFS.

   An option is to an LTS kernel from COPR, provided by a third-party.
   Use it at your own risk::

    # kwizart/kernel-longterm-5.10
    # kwizart/kernel-longterm-4.19
    dnf copr enable -y kwizart/kernel-longterm-5.4
    dnf install -y kernel-longterm kernel-longterm-devel

   Reboot to new LTS kernel, then load kernel module::

    modprobe zfs

   It might be necessary to rebuild ZFS module::

    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      dkms autoinstall -k $kernel_version
    done

   If for some reason, ZFS kernel module is not successfully built,
   you can also run the above command to debug the problem.

#. By default ZFS kernel modules are loaded upon detecting a pool.
   To always load the modules at boot::

    echo zfs > /etc/modules-load.d/zfs.conf

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
ZFS can be used as root file system for Fedora.
An installation guide is available.

`Start here <Root%20on%20ZFS/0-overview.html>`__.

.. toctree::
  :maxdepth: 1
  :glob:

  Root on ZFS/*
