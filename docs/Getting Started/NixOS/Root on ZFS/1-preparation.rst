.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

#. Download `Minimal ISO image
   <https://channels.nixos.org/nixos-21.11/latest-nixos-minimal-x86_64-linux.iso>`__ and boot from it.

#. Connect to network. See `NixOS manual <https://nixos.org/manual/nixos/stable/index.html#sec-installation-booting>`__.

#. SSH server is enabled by default. To connect, set root password with::

    sudo passwd

#. Connect from another computer::

    ssh root@192.168.1.19

#. Unique pool suffix. ZFS expects pool names to be
   unique, therefore it's recommended to create
   pools with a unique suffix::

    INST_UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-z0-9' | cut -c-6)

#. Identify this installation in ZFS filesystem path::

    INST_ID=nixos

#. Root on ZFS configuration file name::

    INST_CONFIG_FILE='zfs.nix'

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
   for primary EFI partition, default to
   first disk in the array::

    INST_PRIMARY_DISK=$(echo $DISK | cut -f1 -d\ )

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

   Set ESP size::

    INST_PARTSIZE_ESP=2 # in GB

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
