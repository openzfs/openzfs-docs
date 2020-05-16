Debian
======

`DKMS <https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support>`__
style packages are available from the `Debian GNU/Linux
repository <https://tracker.debian.org/pkg/zfs-linux>`__ for the
following configurations. The packages previously hosted at
archive.zfsonlinux.org will not be updated and are not recommended for
new installations.

**Debian Releases:** Stretch (oldstable), Buster (stable), and newer
(testing, sid) **Architectures:** amd64

.. contents:: Table of Contents
   :local:

Installation
------------

For Debian Buster, ZFS packages are included in the `contrib
repository <https://packages.debian.org/source/buster/zfs-linux>`__.

If you want to boot from ZFS, see
:doc:`Debian Buster Root on ZFS <./Debian Buster Root on ZFS>`
instead.
For troubleshooting existing installations on Stretch, see
:doc:`Debian Stretch Root on ZFS <./Debian Stretch Root on ZFS>`.

The `backports
repository <https://backports.debian.org/Instructions/>`__ often
provides newer releases of ZFS. You can use it as follows:

Add the backports repository:

::

   # vi /etc/apt/sources.list.d/buster-backports.list
   deb http://deb.debian.org/debian buster-backports main contrib
   deb-src http://deb.debian.org/debian buster-backports main contrib

   # vi /etc/apt/preferences.d/90_zfs
   Package: libnvpair1linux libuutil1linux libzfs2linux libzpool2linux spl-dkms zfs-dkms zfs-test zfsutils-linux zfsutils-linux-dev zfs-zed
   Pin: release n=buster-backports
   Pin-Priority: 990

Update the list of packages:

::

   # apt update

Install the kernel headers and other dependencies:

::

   # apt install --yes dpkg-dev linux-headers-$(uname -r) linux-image-amd64

Install the zfs packages:

::

   # apt-get install zfs-dkms zfsutils-linux

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