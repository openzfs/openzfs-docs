.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

#. Download
   `2021.11.01 <https://mirrors.ocf.berkeley.edu/archlinux/iso/2021.11.01/archlinux-2021.11.01-x86_64.iso>`__
   Live ISO and `signature <https://archlinux.org/iso/2021.11.01/archlinux-2021.11.01-x86_64.iso.sig>`__.

#. Follow `installation guide on Arch wiki <https://wiki.archlinux.org/title/Installation_guide>`__
   up to **Update the system clock**.

#. Set root password or ``/root/.ssh/authorized_keys``.
#. Start SSH server::

    systemctl start sshd

#. Connect from another computer::

    ssh root@192.168.1.19

   and, most important, enter a bash shell::

    bash

   This guide is untested with the default shell ``zsh`` in live environment.

#. Expand live root filesystem::

    mount -o remount,size=2G /run/archiso/cowspace/

#. `Add archzfs repo <../0-archzfs-repo.html>`__.

#. `Install zfs-dkms in live environment <../2-zfs-dkms.html#installation>`__.

#. Load zfs kernel module::

    modprobe zfs

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
   ``/dev/disk/by-path/*``.

   Declare disk array::

    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'

   For single disk installation, use::

    DISK='/dev/disk/by-id/disk1'

#. Choose a primary disk. This disk will be used
   for primary EFI partition and hibernation, default to
   first disk in the array::

    INST_PRIMARY_DISK=$(echo $DISK | cut -f1 -d\ )

   If disk path contains colon ``:``, this disk
   can not be used for hibernation. ``encrypt`` mkinitcpio
   hook treats ``:`` as argument separator without a means to
   escape this character.

#. Set vdev topology, possible values are:

   - (not set, single disk or striped; no redundancy)
   - mirror
   - raidz1
   - raidz2
   - raidz3

   ::

    INST_VDEV=

   This will create a single vdev with the topology of your choice.
   It is also possible to manually create a pool with multiple vdevs, such as::

    zpool create --options \
          poolName \
          mirror sda sdb \
          raidz2 sdc ... \
          raidz3 sde ... \
          spare  sdf ...

   Notice the cost of parity when using RAID-Z. See
   `here <https://www.delphix.com/blog/delphix-engineering/zfs-raidz-stripe-width-or-how-i-learned-stop-worrying-and-love-raidz>`__
   and `here <https://docs.google.com/spreadsheets/d/1tf4qx1aMJp8Lo_R6gpT689wTjHv6CGVElrPqTA0w_ZY/>`__.

   For boot pool, which must be readable by GRUB, mirrored vdev should always be used for maximum redundancy.
   This guide will use mirrored bpool for multi-disk setup.

   Refer to `zpoolconcepts <https://openzfs.github.io/openzfs-docs/man/7/zpoolconcepts.7.html>`__
   and `zpool-create <https://openzfs.github.io/openzfs-docs/man/8/zpool-create.8.html>`__
   man pages for details.

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
