.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

#. Disable Secure Boot. ZFS modules can not be loaded if Secure Boot is enabled.
#. Download latest `Arch Linux live image  <https://archlinux.org/download/>`__ and boot from it.
#. Connect to the Internet.
#. Set root password or ``/root/.ssh/authorized_keys``.
#. Start SSH server::

    systemctl restart sshd

#. Connect from another computer::

    ssh root@192.168.1.19

#. Use bash shell.  Other shell not tested::

     bash

#. Target disk

   List available disks with::

    ls /dev/disk/by-id/*

   If using virtio as disk bus, use ``/dev/disk/by-path/*``.

   Declare disk array::

    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'

   For single disk installation, use::

    DISK='/dev/disk/by-id/disk1'

#. Set partition size:

   Set swap size. It's `recommended <https://chrisdown.name/2018/01/02/in-defence-of-swap.html>`__
   to setup a swap partition. If you intend to use hibernation,
   the minimum should be no less than RAM size. Skip if swap is not needed::

    INST_PARTSIZE_SWAP=8

   Root pool size, use all remaining disk space if not set::

    INST_PARTSIZE_RPOOL=

#. Add ZFS repo::

     curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
     pacman-key --lsign-key $(curl -L https://git.io/JsfVS)
     curl -L https://git.io/Jsfw2 > /etc/pacman.d/mirrorlist-archzfs

     tee -a /etc/pacman.conf <<- 'EOF'

     #[archzfs-testing]
     #Include = /etc/pacman.d/mirrorlist-archzfs

     [archzfs]
     Include = /etc/pacman.d/mirrorlist-archzfs
     EOF

#. Check kernel version::

     uname -r
     #5.18.7-arch1-1

#. Find a ZFS package compatible with the kernel:

   Search kernel version string (e.g. 5.18.7) in both pages:

   * https://archzfs.com/archive_archzfs/
   * https://archzfs.com/archzfs/x86_64/

   Result: https/.../archive_archzfs/zfs-linux-2.1.5_5.18.7.arch1.1-1-x86_64.pkg.tar.zst

#. Find compatible zfs-utils package:

   Search ZFS version string (e.g. 2.1.5) in both pages above.

   Result: https/.../archzfs/x86_64/zfs-utils-2.1.5-2-x86_64.pkg.tar.zst

#. Download both then install::

     pacman -U link-to-zfs.zst link-to-utils.zst

#. Load kernel modules::

    modprobe zfs
