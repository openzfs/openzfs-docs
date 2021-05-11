.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

#. Download 2021.05.01 build and signature.

#. Follow `installation guide on Arch wiki <https://wiki.archlinux.org/title/Installation_guide>`__
   up to **Update the system clock**.

#. Set root password or ``/root/authorized_keys``.
#. Start SSH server::

    systemctl start sshd

#. Connect from another computer
   and enter a bash shell::

    ssh root@192.168.1.19
    bash

#. `Add archzfs repo <../0-archzfs-repo.html>`__.

#.  Install ZFS::

     LIVE_ZFS_PKG="zfs-linux-2.0.4_5.11.16.arch1.1-1-x86_64.pkg.tar.zst"
     LIVE_ZFS_UTILS="zfs-utils-2.0.4-1-x86_64.pkg.tar.zst"
     LIVE_ZFS_MIRROR="https://mirror.sum7.eu/archlinux/archzfs"
     pacman -U --noconfirm ${LIVE_ZFS_MIRROR}/archzfs/x86_64/${LIVE_ZFS_UTILS} \
     || pacman -U --noconfirm ${LIVE_ZFS_MIRROR}/archive_archzfs/${LIVE_ZFS_UTILS}
     pacman -U --noconfirm ${LIVE_ZFS_MIRROR}/archzfs/x86_64/${LIVE_ZFS_PKG} \
     || pacman -U --noconfirm ${LIVE_ZFS_MIRROR}/archive_archzfs/${LIVE_ZFS_PKG}
     modprobe zfs

#. Timezone

   List available timezones with::

    ls /usr/share/zoneinfo/

   Store target timezone in a variable::

    INST_TZ=/usr/share/zoneinfo/Asia/Irkutsk

#. Host name

   Store the host name in a variable::

    INST_HOST='archonzfs'

#. Kernel variant

   Store the kernel variant in a variable.
   Available variants in official repo are:

   - linux
   - linux-lts
   - linux-zen
   - linux-hardened

   ::

    INST_LINVAR='linux'

   ``linux-hardened`` does not support hibernation.

#. Unique pool suffix. ZFS expects pool names to be
   unique, therefore it's recommended to create
   pools with a unique suffix::

    INST_UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-z0-9' | cut -c-6)

#. Identify this installation in ZFS filesystem path::

    INST_ID=arch

#. Target disk

   List available disks with::

    ls /dev/disk/by-id/*

   If using virtio as disk bus, use
   ``/dev/disk/by-path/*`` or ``/dev/vd*``.

   Declare disk array::

    DISK=(/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR)

   For single disk installation, use::

    DISK=(/dev/disk/by-id/disk1)

#. Choose a primary disk. This disk will be used
   for primary EFI partition and hibernation, default to
   first disk in the array::

    INST_PRIMARY_DISK=${DISK[0]}

   If disk path contains colon ``:``, this disk
   can not be used for hibernation. ``encrypt`` mkinitcpio
   hook treats ``:`` as argument separator without a means to
   escape this character.

#. Set vdev specification, possible values are:

   - (not set, single disk)
   - mirror
   - raidz1
   - raidz2
   - raidz3

   ::

    INST_VDEV=

#. Set partition size:

   Set ESP size. ESP contains Live ISO for recovery,
   as described in `optional configurations <4-optional-configuration.html>`__::

    INST_PARTSIZE_ESP=4 # in GB
    #INST_PARTSIZE_ESP=1 # if local recovery is not needed

   Set boot pool size. To avoid running out of space while using
   boot environments, the minimum is 4GB. Adjust the size if you
   intend to use multiple kernel/distros::

    INST_PARTSIZE_BPOOL=4

   Set swap size. It's `recommended <https://chrisdown.name/2018/01/02/in-defence-of-swap.html>`__
   to setup a swap partition. If you intend to use hibernation,
   the minimum should be no less than RAM size. Skip if swap is not needed::

    INST_PARTSIZE_SWAP=8

   Root pool size, use all remaining disk space if not set::

    INST_PARTSIZE_RPOOL=
