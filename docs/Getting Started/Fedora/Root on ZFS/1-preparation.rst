.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

#. Download a variant of Fedora 34 live image
   and boot from it.

#. Disable Secure Boot. ZFS modules can not be loaded of Secure Boot is enabled.
#. Set root password or ``/root/authorized_keys``.
#. Start SSH server::

    echo PermitRootLogin yes >> /etc/ssh/sshd_config
    systemctl start sshd

#. Connect from another computer::

    ssh root@192.168.1.19

#. Set SELinux to persmissive::

    setenforce 0

#. Install ``kernel-devel``::

    source /etc/os-release
    dnf install -y https://dl.fedoraproject.org/pub/fedora/linux/releases/${VERSION_ID}/Everything/x86_64/os/Packages/k/kernel-devel-$(uname -r).rpm

#. Add ZFS repo::

    dnf install -y https://zfsonlinux.org/fedora/zfs-release.fc${VERSION_ID}.noarch.rpm

#. Install ZFS packages::

    dnf install -y zfs

#. Load kernel modules::

    modprobe zfs

#. Install helper script and partition tool::

    dnf install -y arch-install-scripts gdisk

#. Target Fedora version::

    INST_FEDORA_VER='34'

#. Unique pool suffix. ZFS expects pool names to be
   unique, therefore it's recommended to create
   pools with a unique suffix::

    INST_UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-z0-9' | cut -c-6)

#. Identify this installation in ZFS filesystem path::

    INST_ID=fedora

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

#. Set vdev topology, possible values are:

   - (not set, single disk or striped; no redundancy)
   - mirror
   - raidz1
   - raidz2
   - raidz3

   ::

    INST_VDEV=

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
