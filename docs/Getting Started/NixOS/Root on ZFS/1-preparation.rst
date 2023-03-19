.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

This guide supports x86_64 and arm64-efi architectures.

**Note for Tow-Boot**

`Tow-Boot firmware <https://tow-boot.org/>`__
enables UEFI boot on many affordable arm64 based computers.  If
using Tow-Boot, NixOS and Tow-Boot must be on separate disks.
Example, Tow-Boot is installed to an SD card.  Then the SD card
should not be also shared with NixOS.  Install NixOS to an external
disk instead.

#. Disable Secure Boot. ZFS modules can not be loaded if Secure Boot is enabled.
#. Download `NixOS Live Image
   <https://nixos.org/download.html#download-nixos>`__ and boot from it.
#. Connect to the Internet.
#. Set root password or ``/root/.ssh/authorized_keys``.
#. Start SSH server::

    systemctl restart sshd

#. Connect from another computer::

    ssh root@192.168.1.91

#. Target disk

   List available disks with::

    find /dev/disk/by-id/

   If using virtio as disk bus, use ``/dev/disk/by-path/``.

   Declare disk array::

    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'

   For single disk installation, use::

    DISK='/dev/disk/by-id/disk1'

#. Set partition size:

   Set swap size, set to 1 if you don't want swap to
   take up too much space::

    INST_PARTSIZE_SWAP=4

   It is recommeneded to set this value higher if your computer has
   less than 8GB of memory, otherwise ZFS might fail to build.

   Root pool size, use all remaining disk space if not set::

    INST_PARTSIZE_RPOOL=
