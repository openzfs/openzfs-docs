.. highlight:: sh

Preparation
======================

.. contents:: Table of Contents
   :local:

#. Disable Secure Boot. ZFS modules can not be loaded if Secure Boot is enabled.
#. Download a variant of `Fedora live image
   <https://download.fedoraproject.org/pub/fedora/linux/releases/>`__ and boot from it.
#. Connect to the Internet.
#. Set root password or ``/root/.ssh/authorized_keys``.
#. Start SSH server::

    echo PermitRootLogin yes >> /etc/ssh/sshd_config
    systemctl restart sshd

#. Connect from another computer::

    ssh root@192.168.1.19

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

#. Temporarily set SELinux to permissive in live environment::

    setenforce 0

   SELinux will be enabled on the installed system.

#. Add ZFS repo::

    dnf install -y https://zfsonlinux.org/fedora/zfs-release-2-2$(rpm --eval "%{dist}").noarch.rpm

#. Check available repos::

     dnf repolist --all

#. Install ZFS packages::

    rpm -e --nodeps zfs-fuse
    dnf install -y https://dl.fedoraproject.org/pub/fedora/linux/releases/$(source /etc/os-release; echo $VERSION_ID)/Everything/x86_64/os/Packages/k/kernel-devel-$(uname -r).rpm
    dnf install -y zfs

#. Load kernel modules::

    modprobe zfs

#. Install partition tool::

    dnf install -y gdisk dosfstools
