.. highlight:: sh

Debian
======

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

ZFS packages are included in the `contrib repository
<https://packages.debian.org/source/zfs-linux>`__. The
`backports repository <https://backports.debian.org/Instructions/>`__
often provides newer releases of ZFS. You can use it as follows.

Add the backports repository::

  vi /etc/apt/sources.list.d/buster-backports.list

.. code-block:: sourceslist

   deb http://deb.debian.org/debian buster-backports main contrib
   deb-src http://deb.debian.org/debian buster-backports main contrib

::

  vi /etc/apt/preferences.d/90_zfs

.. code-block:: control

  Package: libnvpair1linux libnvpair3linux libuutil1linux libuutil3linux libzfs2linux libzfs4linux libzpool2linux libzpool4linux spl-dkms zfs-dkms zfs-test zfsutils-linux zfsutils-linux-dev zfs-zed
  Pin: release n=buster-backports
  Pin-Priority: 990

Install the packages::

  apt update
  apt install dpkg-dev linux-headers-$(uname -r) linux-image-amd64
  apt install zfs-dkms zfsutils-linux

**Caution**: If you are in a poorly configured environment (e.g. certain VM or container consoles), when apt attempts to pop up a message on first install, it may fail to notice a real console is unavailable, and instead appear to hang indefinitely. To circumvent this, you can prefix the `apt install` commands with ``DEBIAN_FRONTEND=noninteractive``, like this::

  DEBIAN_FRONTEND=noninteractive apt install zfs-dkms zfsutils-linux

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS

Related topics
--------------
.. toctree::
  :maxdepth: 1

  Debian GNU Linux initrd documentation
