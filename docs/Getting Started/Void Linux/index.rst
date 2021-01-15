.. highlight:: sh

Void Linux
==========

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

ZFS packages are included in the official repository. 
You can use it as follows.

Check current kernel version::

 $ uname -r
 5.9.16_1

Check if kernel headers are available::

  $ xbps-query -Rs -headers-
  [*] linux-headers-5.9_2       # meta package
  ...
  [-] linux5.8-headers-5.8.18_1
  [*] linux5.9-headers-5.9.16_1

 If not available for the kernel version on your machine,
 you need to upgrade the kernel first before continuing.

Install ZFS::

 xbps-install linux-headers dkms zfs

Note: on systems with less than 2G available RAM, DKMS module
might fail to build.

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS
