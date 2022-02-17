Ubuntu
======

.. contents:: Table of Contents
  :local:

Installation
------------

.. note::
  If you want to use ZFS as your root filesystem, see the
  `Root on ZFS`_ links below instead.

.. note::
  Steps in this guide apply to most Ubuntu-based distributions.

Since Ubuntu 16.04 ("Xenial Xerus"), ZFS is included in the default
Linux kernel packages. Due to license issues, ZFS kernel modules
must be built from sources by dkms.

To install the ZFS first make sure ``universe`` component is enabled
in ``/etc/apt/sources.list``:

::

  deb http://archive.ubuntu.com/ubuntu <UBUNTU CODE NAME> main universe

Install ``zfsutils-linux`` (user land tools) and ``zfs-dkms`` (kernel modules) components:

::

  apt update
  apt install zfsutils-linux zfs-dkms

Load the ``zfs`` kernel module and list pools to check if installation was successful:

::

  modprobe zfs
  zpool list

The list reported will be empty. No obvious errors in the process
indicate that ZFS was installed successfully.

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *
