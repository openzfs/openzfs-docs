.. highlight:: sh

Alpine Linux Root on ZFS
========================

.. contents:: Table of Contents
   :local:

Overview
--------

Caution
~~~~~~~

- This guide uses entire physical disks.
- Multiple systems on one disk is not supported.
- Target disk will be wiped. Back up your data before continuing.
- Initramfs

  - Initramfs does not support persistent
    device names (``/dev/disk/by-*``).
    See `this merge request <https://gitlab.alpinelinux.org/alpine/mkinitfs/-/merge_requests/77/diffs>`__

    Multi-disk setup is therefore discouraged.
  - Init script has bug for encrypted ZFS pool,
    a variable is not enclosed in double quotes.
    See `this merge request <https://gitlab.alpinelinux.org/alpine/mkinitfs/-/merge_requests/76/diffs>`__

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <irc://irc.freenode.net/#zfsonlinux>`__ on `freenode
<https://freenode.net/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @ne9z
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Alpine%20Linux%20Root%20on%20ZFS%20HOWTO:>`__.

Contributing
~~~~~~~~~~~~

#. Fork and clone: https://github.com/openzfs/openzfs-docs

#. Enable community repo::

    vi /etc/apk/repositories
    # uncomment community line

#. Install the tools::

    sudo apk add py3-pip

    pip3 install -r docs/requirements.txt

    # Add ~/.local/bin to your $PATH, e.g. by adding this to ~/.bashrc:
    PATH=$HOME/.local/bin:$PATH

#. Make your changes.

#. Test::

    cd docs
    make html
    sensible-browser _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a pull
   request. Mention @rlaager.

Encryption
~~~~~~~~~~

This guide supports optional ZFS native encryption on the root pool.

Boot pool, where ``/boot`` is located, is not encrypted.

ZFS native encryption does not encrypt metadata. All datasets properties
are available immediately upon importing, without the key.

Preinstallation
----------------

Prepare the Live Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Download the latest extended x86_64 release 
   `from official website <https://www.alpinelinux.org/downloads/>`__ 
   and write it to a USB drive or an optical disc.

#. Boot the target computer from the prepared live medium.

#. Login. Default user name is ``root``
   , no password.

#. Setup live environment::

     setup-alpine

   See `wiki page <https://wiki.alpinelinux.org/wiki/Alpine_setup_scripts#setup-alpine>`__ for details.

   Settings given here will be copied to the
   target system.

   If asked which disk to use, enter ``none``.
   If asked where to store config, enter ``none``.

#. Allow SSH password login::

     echo PermitRootLogin yes >> /etc/ssh/sshd_config
     rc-service sshd restart

#. Show IP address::

     ip -4 address show scope global

#. Login from another computer::

     ssh root@192.168.1.10

#. Install ZFS and additional tools
   in the live environment::

    apk add zfs sgdisk grub-efi efibootmgr grub-bios

#. Load kernel module::

    modprobe zfs

Installation Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this part, we will set some variables to configure the system.

#. Target disk

   List the available disks with::

     ls -d /dev/*

   Store the target disk in a variable::

     DISK=/dev/vda

   For multi-disk setups, repeat the formatting and
   partitioning commands for other disks.

   Before persistent device naming become
   available in initramfs, multi-disk setup
   is discouraged.

#. Create a mountpoint with::

    INST_MNT=$(mktemp -d)

#. To avoid name conflict when importing pools on another computer,
   Give them a unique suffix::

    INST_UUID=$(dd if=/dev/urandom of=/dev/stdout bs=1 count=100 2>/dev/null |tr -dc 'a-z0-9' | cut -c-6)

System Installation
-------------------

Format and Partition the Target Disks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Clear the partition table::

    sgdisk --zap-all $DISK

#. Create EFI system partition ``esp``::

    sgdisk -n1:0:+1G -t1:EF00 $DISK

#. Create BIOS boot partition::

    sgdisk -a1 -n5:24K:+1000K -t5:EF02 $DISK

#. Create boot pool partition::

    sgdisk -n2:0:+4G -t2:BE00 $DISK

#. Create root pool partition

   - If you don't need a separate swap partition::

       sgdisk -n3:0:0 -t3:BF00 $DISK

   - If a separate swap partition is needed::

       sgdisk -n3:0:-8G -t3:BF00 $DISK
       sgdisk -n4:0:0 -t4:8308 $DISK

    Adjust the swap partition size to your needs.

#. Repeat the above steps for other target disks, if any.

Create Root and Boot Pools
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. For multi-disk setup

   If you want to create a multi-disk pool, replace ``${DISK}X`` 
   with the topology and the disk path.

   For example, change::

    zpool create \
      ... \
      ${DISK}2

   to::

    zpool create \
      ... \
      mirror \
      /dev/sda2
      /dev/sdb2

   replace ``mirror`` with ``raidz``, ``raidz2`` or ``raidz3``.

#. Create boot pool::

    zpool create \
        -o ashift=12 \
        -d -o feature@async_destroy=enabled \
        -o feature@bookmarks=enabled \
        -o feature@embedded_data=enabled \
        -o feature@empty_bpobj=enabled \
        -o feature@enabled_txg=enabled \
        -o feature@extensible_dataset=enabled \
        -o feature@filesystem_limits=enabled \
        -o feature@hole_birth=enabled \
        -o feature@large_blocks=enabled \
        -o feature@lz4_compress=enabled \
        -o feature@spacemap_histogram=enabled \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=lz4 \
        -O devices=off \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/boot \
        -R $INST_MNT \
        bpool_$INST_UUID \
        ${DISK}2

#. Create root pool:

   - Unencrypted::

      zpool create \
        -o ashift=12 \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=lz4 \
        -O dnodesize=auto \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/ \
        -R $INST_MNT \
        rpool_$INST_UUID \
        ${DISK}3

   - Encrypted::

       zpool create \
        -o ashift=12 \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=lz4 \
        -O dnodesize=auto \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/ \
        -R $INST_MNT \
        -O encryption=aes-256-gcm \
        -O keylocation=prompt \
        -O keyformat=passphrase \
        rpool_$INST_UUID \
        ${DISK}3

Create Datasets
~~~~~~~~~~~~~~~~~~~~~~

#. Create container datasets::

    zfs create -o canmount=off -o mountpoint=none bpool_$INST_UUID/BOOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/ROOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/DATA

#. Create root and boot filesystem datasets::

    zfs create -o mountpoint=legacy -o canmount=noauto bpool_$INST_UUID/BOOT/default
    zfs create -o mountpoint=/      -o canmount=noauto rpool_$INST_UUID/ROOT/default

#. Mount root and boot filesystem datasets::

    zfs mount rpool_$INST_UUID/ROOT/default
    mkdir $INST_MNT/boot
    mount -t zfs bpool_$INST_UUID/BOOT/default $INST_MNT/boot

#. Create datasets to separate user data from root filesystem::

    zfs create -o mountpoint=/ -o canmount=off rpool_$INST_UUID/DATA/default

    d='usr var var/lib'
    for i in $d;
    do
        zfs create -o canmount=off rpool_$INST_UUID/DATA/default/$i
    done

    d='home root srv usr/local var/log var/spool var/tmp'
    for i in $d;
    do
        zfs create -o canmount=on rpool_$INST_UUID/DATA/default/$i
    done

    chmod 750 $INST_MNT/root
    chmod 1777 $INST_MNT/var/tmp

#. Optional user data datasets:

   If you use /opt on this system::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/opt

   If this system will have games installed::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/games

   If you use /var/www on this system::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/www

   If this system will use GNOME::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/lib/AccountsService

   If this system will use Docker (which manages its own datasets &
   snapshots)::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/lib/docker

   If this system will use NFS (locking)::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/lib/nfs

   If this system will use Linux Containers::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/lib/lxc

Format and Mount EFI System Partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 mkfs.vfat -n EFI ${DISK}1
 mkdir $INST_MNT/boot/efi
 mount -t vfat ${DISK}1 $INST_MNT/boot/efi

If you are using a multi-disk setup, this step will only install
bootloader to the first disk. Other disks will be handled later.


Package Installation
~~~~~~~~~~~~~~~~~~~~

#. Fix GRUB root device path

   See below for more information::

    export ZPOOL_VDEV_NAME_PATH=YES

#. Add zfs to supported file systems::

    sed -i 's|supported="ext|supported="zfs ext|g' /sbin/setup-disk

#. Copy system from Live media::
    
      BOOTLOADER=grub USE_EFI=y setup-disk -v $INST_MNT

   Ignore GRUB error::

     /usr/sbin/grub-probe: error: failed to get canonical path of 
 
System Configuration
--------------------

#. Configure mkinitfs::

     echo 'features="ata base ide scsi usb virtio nvme zfs"'\
     > $INST_MNT/etc/mkinitfs/mkinitfs.conf

#. If a swap partition is created::

      echo 'features="ata base ide scsi usb virtio nvme crypttab zfs"'\
      > $INST_MNT/etc/mkinitfs/mkinitfs.conf

   Configure swap::

      echo crypt-swap ${DISK}4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256 >> /etc/crypttab
      echo /dev/mapper/crypt-swap none swap defaults 0 0 >> /etc/fstab

#. Fix init script for encryption

   #.  Open ``$INST_MNT/usr/share/mkinitfs/initramfs-init``::

        vi $INST_MNT/usr/share/mkinitfs/initramfs-init

   #. Find this line::

       if [ $(zpool list -H -o feature@encryption $_root_pool) = "active" ]; then

   #. Enclose the variable with double quotes::

       if [ "$(zpool list -H -o feature@encryption $_root_pool)" = "active" ]; then 


#. Chroot::

    m='dev proc sys'
    for i in $m; do
       mount --rbind /$i $INST_MNT/$i
    done
    chroot $INST_MNT /usr/bin/env DISK=$DISK INST_UUID=$INST_UUID /bin/sh

#. Enable ZFS services::

    rc-update add zfs-mount sysinit

#. Generate zpool.cache

   Pools are imported by initramfs with the information stored in ``/etc/zfs/zpool.cache``.
   This cache file will be embedded in ``initramfs``.

   ::

     zpool set cachefile=/etc/zfs/zpool.cache rpool_$INST_UUID
     zpool set cachefile=/etc/zfs/zpool.cache bpool_$INST_UUID

#. If a swap partition was created::

     apk add cryptsetup

#. Generate initramfs::

     mkinitfs $(ls -1 /lib/modules/)

GRUB Installation
----------------------------

Currently GRUB has multiple compatibility problems with ZFS, especially with regards
to newer ZFS features. Workarounds have to be applied.

BusyBox stat does not support ZFS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because GRUB relies on ``stat`` to detect filesystem,
and the BusyBox builtin does not support ZFS,
``coreutils`` need to be installed.::

  apk add coreutils

grub-probe fails to get canonical path of root partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GRUB will fail to resolve the path of the boot pool
device. Error::

  # /usr/bin/grub-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.03'.

Solution::

 echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile
 source /etc/profile

Pool name missing if the pool has unsupported features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In ``/etc/grub.d/10_linux``::

  # rpool=`${grub_probe} --device ${GRUB_DEVICE} --target=fs_label 2>/dev/null || true`

``10_linux`` will return an empty result if the root pool has features
not supported by GRUB.

With this bug, the generated ``grub.cfg`` contains such lines::

 root=ZFS=/ROOT/default # root pool name missing; unbootable

Rendering the system unbootable.

A workaround is to replace the pool name detection with ``zdb``
command::

 sed -i "s|rpool=.*|rpool=\`zdb -l \${GRUB_DEVICE} \| grep -E '[[:blank:]]name' \| cut -d\\\' -f 2\`|"  /etc/grub.d/10_linux

This will replace the faulty line in ``10_linux`` with::

   # rpool=`zdb -l ${GRUB_DEVICE} | grep -E '[[:blank:]]name' | cut -d\' -f 2`

Note: Debian guide chose to hardcode ``root=ZFS=rpool/ROOT/default`` 
in ``GRUB_CMDLINE_LINUX`` in ``/etc/default/grub``
This is incompatible with the boot environment utility. 
The utility also uses this parameter to boot alternative
root filesystem datasets.

A boot environment entry::

  # root=ZFS=rpool_UUID/ROOT/bootenv_after-sysupdate

``root=ZFS=pool/dataset`` is processed by 
the ZFS script in initramfs, used to 
tell the kernel the real root filesystem.

``zfs=bootfs`` kernel command line 
and ``zpool set bootfs=pool/dataset pool`` 
is not used due to its inflexibility.


GRUB Installation
~~~~~~~~~~~~~~~~~

- If you use EFI::

   grub-install

  This will only install boot loader to $DISK. 
  If you use multi-disk setup, other disks are
  dealt with later.

  Some motherboards does not properly recognize GRUB 
  boot entry, to ensure that your computer will
  boot, also install GRUB to fallback location with::

   grub-install --removable

- If you use BIOS booting::

    grub-install $DISK

Generate GRUB Boot Menu
~~~~~~~~~~~~~~~~~~~~~~~

::

   grub-mkconfig -o /boot/grub/grub.cfg

Finish Installation
-------------------

#. Exit chroot::

    exit

#. Take a snapshot of the clean installation for future use::

    zfs snapshot -r rpool_$INST_UUID/ROOT/default@install
    zfs snapshot -r bpool_$INST_UUID/BOOT/default@install

#. Unmount EFI system partition and others::

    umount $INST_MNT/boot/efi
    umount -lf $INST_MNT/dev
    umount -lf $INST_MNT/proc
    umount -lf $INST_MNT/sys

#. Export pools::

    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID

 They must be exported, or else they will fail to be imported on reboot.

After Reboot
------------

Mounting rpool/ROOT/default on /sysroot failed: permission denied
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is because of a bug, the init script failed to
correctly parse the root pool name.

#. Load keys::

    zfs load-key -a

#. Manually mount root::

    mount -t zfs -o zfsutils rpool/ROOT/default /sysroot

#. Exit emergency shell::

    exit

   The system should boot normally.

#. After entering system, regenerate initramfs::

     mkinitfs

Disable root access
~~~~~~~~~~~~~~~~~~~
``/etc/ssh/sshd_config`` still contains the 
line allowing password-only root access.

Remove it to secure your system.

Recovery
--------

Load grub.cfg in GRUB command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Boot environment menu is stored in ``/boot/grub.cfg``. 
But the absolute path of ``grub.cfg`` will
change when you enter another boot environment, 
from ``bpool/BOOT/default/@/boot/grub.cfg`` to 
``bpool/BOOT/bootenv1/@/boot/grub.cfg``.

This absolute path is stored in the bootloader file:
``grubx64.efi`` for EFI booting, or inside the first sector of the 
disk for BIOS booting.

GRUB will load the wrong ``grub.cfg`` if the bootloader 
file has not been updated upon entering another boot environment. 
Following are the steps to load the correct ``grub.cfg``, 

#. Enter GRUB command line

   No additional steps if you are already in GRUB rescue. 
   Otherwise, press ``c`` at the GRUB menu.

#. List available partitions::

     grub > ls
     (hd0) (hd0,gpt4) (hd0,gpt3) (hd0,gpt2) (hd0,gpt1) (hd1) (hd1,gpt5) ...

   Boot pool is always ``(hdx,gpt2)``::

     grub > ls (hd0, # press tab after comma
     Possible partitions are:

         Partition hd0,gpt1: Filesystem type fat - Label 'EFI', UUID ...
         Partition hd0,gpt2: Filesystem type zfs - Label 'bpool' - Last modification time ...
         Partition hd0,gpt3: No known filesystem detected ...

#. List available boot environments::

     grub > ls (hd0,gpt2) # press tab after bracket
     Possible files are:

     @/ BOOT/

     grub > ls (hd0,gpt2)/BOOT # press tab after 'T'
     Possible files are:

     @/ default/ pac-multm2/

#. Load grub.cfg

   To load from ``default`` boot environment, append 
   ``default/@/grub/grub.cfg`` to the last ``ls`` command.

   Then press ``home`` on the keyboard to move 
   cursor to the start of the line.

   Change ``ls`` to ``configfile`` and press return::

    grub > configfile (hd0,gpt2)/BOOT/default/@/grub/grub.cfg

Rescue in Live Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Repeat `Prepare the Live Environment
   <#prepare-the-live-environment>`__.

#. Check the ``INST_UUID`` with ``zpool import``.

#. Set variables::

     INST_MNT=$(mktemp -d)
     INST_UUID=abc123
     RPOOL_PWD='rootpool'

#. Import and unlock root and boot pool::

     zpool import -N -R $INST_MNT rpool_$INST_UUID
     zpool import -N -R $INST_MNT bpool_$INST_UUID
     echo $RPOOL_PWD | zfs load-key rpool_$INST_UUID

#. Find the current boot environment::

     zfs list

#. Mount boot and root filesystem::

     zfs mount rpool_$INST_UUID/ROOT/$BE

#. chroot into the system::

     chroot $INST_MNT /bin/bash --login
     mount /boot
     mount /boot/efi
     zfs mount -a

#. Finish rescue::

    exit
    umount $INST_MNT/boot/efi
    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID
    reboot
