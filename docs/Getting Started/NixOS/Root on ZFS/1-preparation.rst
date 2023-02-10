.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

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

   Root pool size, use all remaining disk space if not set::

    INST_PARTSIZE_RPOOL=
