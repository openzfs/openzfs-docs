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

#. Add ZFS repo::

    dnf install -y https://zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm

#. Install ZFS packages::

    dnf install -y kernel-devel zfs

#. Load kernel module::

    modprobe zfs

   If kernel module can not be loaded, your kernel version
   might be not yet supported by OpenZFS. Try install
   an LTS kernel::

    dnf copr enable -y kwizart/kernel-longterm-5.4
    dnf install -y kernel-longterm kernel-longterm-devel
    # reboot to new LTS kernel
    modprobe zfs

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
