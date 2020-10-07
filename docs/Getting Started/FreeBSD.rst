|img|

OpenZFS is an advanced file system and volume manager which was
originally developed for Solaris and is now maintained by the OpenZFS
community.

Official Resources
==================

-  `ZoF GitHub Site <https://zfsonfreebsd.github.io/ZoF/>`__
-  `OpenZFS site <http://open-zfs.org/>`__
-  `OpenZFS repo <https://github.com/openzfs/zfs>`__

Installation on FreeBSD
=======================

OpenZFS is available in the FreeBSD ports tree as sysutils/openzfs and
sysutils/openzfs-kmod. It can be installed on FreeBSD stable/12 or
later.

The ZFS utilities will be installed in /usr/local/sbin/, so make sure
your PATH gets adjusted accordingly.

To load the module at boot, put ``openzfs_load="YES"`` in
/boot/loader.conf, and remove ``zfs_load="YES"`` if migrating a ZFS
install.

Beware that the FreeBSD boot loader does not allow booting from root
pools with encryption active (even if it is not in use), so do not try
encryption on a pool you boot from.

Development on FreeBSD
======================

The following dependencies are required to build OpenZFS on FreeBSD:

-  FreeBSD sources in /usr/src or elsewhere specified by SYSDIR in env
-  Packages for build:
   ::

      pkg install \
          autoconf \
          automake \
          autotools \
          bash \
          git \
          gmake \

-  Optional packages for build:
   ::

      pkg install python37 # or your preferred Python version

-  Packages for checks and tests:
   ::

      pkg install \
          base64 \
          checkbashisms \
          fio \
          hs-ShellCheck \
          ksh93 \
          pamtester \
          py37-flake8 \
      python37 \
          sudo

   Your preferred python version may be substituted. The user for
   running tests must have NOPASSWD sudo permission.

To build and install:

::

   # as user
   git clone https://github.com/openzfs/zfs
   cd zfs
   ./autogen.sh
   ./configure
   gmake -j$(sysctl -n hw.ncpu)
   # as root
   gmake install

Though not required, ``WITHOUT_ZFS`` is a useful build option in FreeBSD
to avoid building and installing the legacy zfs tools and kmod - see
``src.conf(5)``.

For rapid development it can be convenient to do a UFS install instead
of ZFS when setting up the work environment. That way the module can be
unloaded and loaded without rebooting.

Contributing
============

Submit changes to the `openzfs/zfs <https://github.com/openzfs/zfs>`__
repo.

Issues
======

Issues can be reported via GitHub's `Issue
Tracker <https://github.com/openzfs/zfs>`__.

.. |img| image:: https://github.com/zfsonfreebsd/ZoF/raw/gh-pages/zof-logo.png
