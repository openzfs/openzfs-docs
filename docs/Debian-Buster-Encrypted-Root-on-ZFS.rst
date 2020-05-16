This experimental guide has been made official at [[Debian Buster Root
on ZFS]].

If you have an existing system installed from the experimental guide,
adjust your sources:

::

   vi /etc/apt/sources.list.d/buster-backports.list
   deb http://deb.debian.org/debian buster-backports main contrib
   deb-src http://deb.debian.org/debian buster-backports main contrib

   vi /etc/apt/preferences.d/90_zfs
   Package: libnvpair1linux libuutil1linux libzfs2linux libzpool2linux zfs-dkms zfs-initramfs zfs-test zfsutils-linux zfs-zed
   Pin: release n=buster-backports
   Pin-Priority: 990

This will allow you to upgrade from the locally-built packages to the
official buster-backports packages.

You should set a root password before upgrading:

::

   passwd

Apply updates:

::

   apt update
   apt dist-upgrade

Reboot:

::

   reboot

If the bpool fails to import, then enter the rescue shell (which
requires a root password) and run:

::

   zpool import -f bpool
   zpool export bpool
   reboot
