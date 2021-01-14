.. highlight:: sh

Alpine Linux
============

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

ZFS packages are included in the official repository.
You can use it as follows.

Install ZFS::

  apk add zfs

Load kernel module::

  modprobe zfs

For persistent device naming 
(``/dev/disk/by-*``), 
``eudev`` is needed::

  apk add eudev
  setup-udev

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS
