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

Root on ZFS
-----------
ZFS can be used as root file system for Fedora.
An installation guide is available.

Start from "Preparation".

.. toctree::
  :maxdepth: 1
  :glob:

  Root on ZFS/*
