Alpine Linux
============

Contents
--------
.. toctree::
  :maxdepth: 1
  :glob:

  *

Installation
------------

Note: this is for installing ZFS on an existing Alpine
installation. To use ZFS as root file system,
see below.

#. Install ZFS package::

    apk add zfs zfs-lts

#. Load kernel module::

    modprobe zfs

Automatic zpool importing and mount
-----------------------------------

To avoid needing to manually import and mount zpools
after the system boots, be sure to enable the
related services.

#. Import pools on boot::

    rc-update add zfs-import default

#. Mount pools on boot::

    rc-update add zfs-mount default

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *
