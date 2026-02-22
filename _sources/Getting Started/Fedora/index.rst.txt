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

    dnf install -y https://zfsonlinux.org/fedora/zfs-release-3-0$(rpm --eval "%{dist}").noarch.rpm

   List of old zfs-release RPMs are available `here <https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/fedora>`__.

#. Install kernel headers::

     dnf install -y kernel-devel-$(uname -r | awk -F'-' '{print $1}')

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

Latest Repositories (Fedora 41+)
--------------------------------

*zfs-latest* repository contains the latest released version of OpenZFS which
is under active development. It will contain the newest features, and is
considered stable, but will have less real-world testing use than
*zfs-legacy*. 
This repository is equivalent to the default *zfs* repository for Fedora.
Packages from the latest repository can be installed as follows.

For Fedora 41 and newer run::

 sudo dnf config-manager setopt zfs*.enabled=0
 sudo dnf config-manager setopt zfs-latest.enabled=1
 sudo dnf install zfs

Legacy Repositories (Fedora 41+)
--------------------------------

*zfs-legacy* repository contains the previous released version of OpenZFS which
is still being actively updated.
Typically, this repository provides same packages as primary *zfs* repository
for RHEL- and CentOS-based distribution.
Packages from the legacy repository can be installed as follows.

For Fedora 41 and newer run::

 sudo dnf config-manager setopt zfs*.enabled=0
 sudo dnf config-manager setopt zfs-legacy.enabled=1
 sudo dnf install zfs

Version Specific Repositories (Fedora 41+)
------------------------------------------

Version specific repositories are provided for users who wants to run a specific
branch (e.g. `2.3.x`) of ZFS.
Packages from the version specific repository can be installed as follows.

For Fedora 41 and newer, to enable version specific repository for ZFS branch x.y, run::

 sudo dnf config-manager setopt zfs*.enabled=0
 sudo dnf config-manager setopt zfs-x.y.enabled=1
 sudo dnf install zfs

Testing Repository (DEPRECATED)
-------------------------------

*zfs-testing* repository is DEPRECATED in favor of 'zfs-latest'.


Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *
