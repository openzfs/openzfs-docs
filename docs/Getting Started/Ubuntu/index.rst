Ubuntu
======

.. contents:: Table of Contents
  :local:

Installation
------------

.. note::
  If you want to use ZFS as your root filesystem, see the
  `Root on ZFS`_ links below instead.

On Ubuntu, ZFS is included in the default Linux kernel packages.
To install the ZFS utilities, first make sure ``universe`` is enabled in
``/etc/apt/sources.list``::

  deb http://archive.ubuntu.com/ubuntu <CODENAME> main universe

Then install ``zfsutils-linux``::

  apt update
  apt install zfsutils-linux

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *
