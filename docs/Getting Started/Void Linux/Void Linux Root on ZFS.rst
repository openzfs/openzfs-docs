.. highlight:: sh

Void Linux Root on ZFS
=======================

.. contents:: Table of Contents
   :local:

Overview
--------

Caution
~~~~~~~

- This guide uses entire physical disks.
- Multiple systems on one disk is not supported.
- Target disk will be wiped. Back up your data before continuing.
- The target system, virtual or physical, must have at least 4GB RAM,
  or the DKMS module will fail to build.

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <irc://irc.freenode.net/#zfsonlinux>`__ on `freenode
<https://freenode.net/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @ne9z
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Void%20Linux%20Root%20on%20ZFS%20HOWTO:>`__.

Contributing
~~~~~~~~~~~~

#. Fork and clone: https://github.com/openzfs/openzfs-docs

#. Install the tools::

    sudo xbps-install python3-pip

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

#. Visit `Void Linux mirror <https://alpha.de.repo.voidlinux.org/live/>`__,
   choose the most recent directory,
   download
   ``void-live-x86_64-musl-DATE.iso`` or
   ``void-live-x86_64-DATE.iso``
   and write it to a USB drive or an optical disc.

   Do not download from ``current`` or the version listed on the official
   `Download page <https://voidlinux.org/download/>`__.

   They contain outdated kernel and require
   an update to install headers, which is not doable in live environment.

#. Boot the target computer from the prepared live medium.

#. Connect to the internet. 
   If the target computer aquires IP address with DHCP, 
   no further steps need to be taken. 
   Otherwise, refer to 
   `Void Linux Handbook <https://docs.voidlinux.org/config/network/index.html>`__ 

#. Login as root. Instructions are available in MOTD.


#. Start SSH server.

    - Permit root login with password::

       echo PermitRootLogin yes >> /etc/ssh/sshd_config

    - Restart SSH server::

       sv restart sshd

    - Find the IP address of the target computer::

       ip -4 address show scope global

    - On another computer, connect to the target computer with::

       ssh root@192.168.1.10

#. Enter a bash shell::

     bash

#. Optional: Configure a mirror

   See `Changing Mirror <https://docs.voidlinux.org/xbps/repositories/mirrors/changing.html>`__
   chapter of the Void Linux Handbook.

#. Install ZFS and tools in live environment::

    xbps-install -Sy linux-headers dkms zfs gptfdisk

#. Load kernel module::

    modprobe zfs

Installation Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Timezone

   List the available timezones with::

    ls /usr/share/zoneinfo/posix/

   Store the target timezone in a variable::

    INST_TZ=Asia/Irkutsk

#. Host name

   Store the host name in a variable::

    INST_HOST='localhost'

#. Target disk

   List the available disks with::

     ls -d /dev/disk/by-id/* | grep -v part

   If the disk is connected with VirtIO, use ``/dev/vd*``.
   And replace ``${DISK}-part`` in this guide with ``${DISK}``

   Store the target disk in a variable::

     DISK=/dev/disk/by-id/nvme-foo_NVMe_bar_512GB

   For multi-disk setups, repeat the formatting and
   partitioning commands for other disks.

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

   If you want to create a multi-disk pool, replace ``${DISK}-partX`` with the topology and the disk path.

   For example, change::

    zpool create \
      ... \
      ${DISK}-part2

   to::

    zpool create \
      ... \
      mirror \
      /dev/disk/by-id/ata-disk1-part2
      /dev/disk/by-id/ata-disk2-part2

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
        ${DISK}-part2

#. Create root pool:

   - Unencrypted::

      zpool create \
        -o ashift=12 \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=zstd \
        -O dnodesize=auto \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/ \
        -R $INST_MNT \
        rpool_$INST_UUID \
        ${DISK}-part3

   - Encrypted::

       zpool create \
        -o ashift=12 \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=zstd \
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
        ${DISK}-part3

Create Datasets
~~~~~~~~~~~~~~~~~~~~~~

#. Create container datasets::

    zfs create -o canmount=off -o mountpoint=none bpool_$INST_UUID/BOOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/ROOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/DATA

#. Create root and boot filesystem datasets::

     zfs create -o mountpoint=legacy -o canmount=noauto bpool_$INST_UUID/BOOT/default
     zfs create -o mountpoint=/      -o canmount=noauto rpool_$INST_UUID/ROOT/default

   Note: these properties are compatible with boot environment

    - ``canmount=noauto`` prevents ZFS from automatically
      mounting datasets.

    - Root dataset, specified with ``root=ZFS=rpool/ROOT/dataset`` at boot,
      will be mounted regardless of other properties.

    - Boot dataset is mounted with ``/etc/fstab``.
      Its ``fstab`` entry will be updated upon the creation of
      a new boot environment.

    - ``zfs-mount-generator`` does not mount datasets
      with ``canmount=noauto``.

#. Mount root and boot filesystem datasets::

    zfs mount rpool_$INST_UUID/ROOT/default
    mkdir $INST_MNT/boot
    mount -t zfs bpool_$INST_UUID/BOOT/default $INST_MNT/boot

#. Create datasets to separate user data from root filesystem::

    zfs create -o mountpoint=/ -o canmount=off rpool_$INST_UUID/DATA/default

    for i in {usr,var,var/lib};
    do
        zfs create -o canmount=off rpool_$INST_UUID/DATA/default/$i
    done

    for i in {home,root,srv,usr/local,var/log,var/spool,var/tmp};
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

 mkfs.vfat -n EFI ${DISK}-part1
 mkdir $INST_MNT/boot/efi
 mount -t vfat ${DISK}-part1 $INST_MNT/boot/efi

If you are using a multi-disk setup, this step will only install
bootloader to the first disk. Other disks will be handled later.


Package Installation
~~~~~~~~~~~~~~~~~~~~

#. Select a mirror for xbps::

    REPO=https://alpha.de.repo.voidlinux.org/current/musl

#. Set architecture::

    ARCH=x86_64-musl
    # or x86_64, also change the repo URL

#. Install base packages::
    
     XBPS_ARCH=$ARCH xbps-install -Sy -r $INST_MNT -R "$REPO" \
        base-system connman grub-x86_64-efi linux-headers dkms zfs

   DKMS build will fail::

    zfs-2.0.1_1: configuring ...
    Added DKMS module 'zfs-2.0.1'.
    Building DKMS module 'zfs-2.0.1' for kernel-5.9.16_1... FAILED!
    DKMS module 'zfs-2.0.1' failed to build, please check /var/lib/dkms
    for errors in the log file.
    ...
    zfs-2.0.1_1: installed successfully.

   We will fix this in chroot.

System Configuration
--------------------

#. Generate fstab::

     echo bpool_$INST_UUID/BOOT/default /boot zfs rw,xattr,posixacl 0 0 >> $INST_MNT/etc/fstab
     echo UUID=$(blkid -s UUID -o value ${DISK}-part1) /boot/efi vfat umask=0022,fmask=0022,dmask=0022 0 1 >> $INST_MNT/etc/fstab

   If a swap partition has been created::

       echo crypt-swap ${DISK}-part4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256 >> $INST_MNT/etc/crypttab
       echo /dev/mapper/crypt-swap none swap defaults 0 0 >> $INST_MNT/etc/fstab


#. Configure dracut::

     echo 'add_dracutmodules+="zfs"' >> $INST_MNT/etc/dracut.conf.d/zfs.conf

#. Host name::

    echo $INST_HOST > $INST_MNT/etc/hostname

#. Timezone::

     echo TIMEZONE=\"$INST_TZ\" >> $INST_MNT/etc/rc.conf

#. If you are using glibc, set locale::

    echo "en_US.UTF-8 UTF-8" >> $INST_MNT/etc/default/libc-locales
    echo "LANG=en_US.UTF-8" >> $INST_MNT/etc/default/libc-locales

   Other locales should be added after reboot, not here.

#. Copy resolve.conf::

    cp -p /etc/resolv.conf $INST_MNT/etc/

#. Copy mirror configuration::

    cp -r /etc/xbps.d/ $INST_MNT/etc/

#. Chroot::

    m='dev proc sys'
    for i in $m; do
       mount --rbind /$i $INST_MNT/$i
    done
    chroot $INST_MNT /usr/bin/env DISK=$DISK INST_UUID=$INST_UUID /bin/bash

#. Build ZFS kernel module::

    dkms install --no-depmod -m zfs -v $(ls -1 /var/lib/dkms/zfs/) -k $(ls -1 /lib/modules/)

#. If a swap partition has been created, install cryptsetup::
   
    xbps-install -Sy cryptsetup

#. If you are using glibc, apply locales::

    xbps-reconfigure -f glibc-locales

#. Enable networking::

    ln -s /etc/sv/connmand /etc/runit/runsvdir/default/

#. Generate zpool.cache

   Pools are imported by initramfs with the information stored in ``/etc/zfs/zpool.cache``.
   This cache file will be embedded in ``initramfs``.

   ::

     zpool set cachefile=/etc/zfs/zpool.cache rpool_$INST_UUID
     zpool set cachefile=/etc/zfs/zpool.cache bpool_$INST_UUID

#. Set root password::

     passwd

#. Generate initramfs::

     linver=$(ls -1 /lib/modules)
     xbps-reconfigure -f linux${linver%.*}

GRUB Installation
-----------------

Currently GRUB has multiple compatibility problems with ZFS, 
especially with regards to newer ZFS features. 
Workarounds have to be applied.

grub-probe fails to get canonical path of root partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When persistent device names ``/dev/disk/by-id/*`` are used
with ZFS, GRUB will fail to resolve the path of the boot pool
device. Error::

  # /usr/bin/grub-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.0-part3'.

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
the ZFS script in initramfs, used to tell 
the kernel the real root filesystem.

``zfs=bootfs`` kernel command line and 
``zpool set bootfs=pool/dataset pool`` is not used due to its inflexibility.


GRUB Installation
~~~~~~~~~~~~~~~~~

- If you use EFI::

   grub-install

  This will only install boot loader to $DISK. 
  If you use multi-disk setup, other disks are  dealt with later.

  Some motherboards does not properly recognize 
  GRUB boot entry, to ensure that your computer will boot,
  also install GRUB to fallback location with::

   grub-install --removable

- If you use BIOS booting::

    grub-install $DISK

Generate GRUB Boot Menu
~~~~~~~~~~~~~~~~~~~~~~~

::

   grub-mkconfig -o /boot/grub/grub.cfg

Ignore ``cannot find a GRUB drive for ...``.

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
#. Mirror EFI system partition

   #. Format redundant EFI partitions::

        mkfs.vfat -n EFI2 /dev/disk/by-id/target_disk2-part1
        mkfs.vfat -n EFI3 /dev/disk/by-id/target_disk3-part1

   #. Create mountpoints::

        mkdir -p /boot/efis/{2,3}

   #. Mount redundant EFI partitions::

        mount -o umask=0022,fmask=0022,dmask=0022 /dev/disk/by-id/target_disk2-part1 /boot/efis/2
        mount -o umask=0022,fmask=0022,dmask=0022 /dev/disk/by-id/target_disk3-part1 /boot/efis/3

   #. Add fstab entries::

        pacman -S --needed artools-base

        fstabgen / | grep efis >> /etc/fstab

   #. Sync EFI system partition contents::

        for i in /boot/efis/*; do 
           /usr/bin/cp -r /boot/efi/* /boot/efis/$i; 
        done

   #. Add EFI boot entries::

       efibootmgr -c -g -d /dev/disk/by-id/target_disk2-part1 \
          -p 2 -L "artix-2" -l "\EFI\arch\grubx64.efi"
       efibootmgr -c -g -d /dev/disk/by-id/target_disk3-part1 \
          -p 3 -L "artix-3" -l "\EFI\arch\grubx64.efi"

Recovery
--------

Load grub.cfg in GRUB command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Boot environment menu is stored in ``/boot/grub.cfg``. But the absolute path of ``grub.cfg`` will
change when you enter another boot environment, from ``bpool/BOOT/default/@/boot/grub.cfg`` to 
``bpool/BOOT/bootenv1/@/boot/grub.cfg``.

This absolute path is stored in the bootloader file:
``grubx64.efi`` for EFI booting, or inside the first sector of the 
disk for BIOS booting.

GRUB will load the wrong ``grub.cfg`` if the 
bootloader file has not been updated upon
entering another boot environment. 
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

   To load from ``default`` boot environment,
   append ``default/@/grub/grub.cfg`` to the last ``ls`` command.

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

    m='dev proc sys'
    for i in $m; do
       mount --rbind /$i $INST_MNT/$i
    done
    chroot $INST_MNT /usr/bin/env DISK=$DISK INST_UUID=$INST_UUID /bin/bash

    mount /boot
    mount /boot/efi
    zfs mount -a

#. Finish rescue::

    exit
    umount $INST_MNT/boot/efi
    umount -lf $INST_MNT/dev
    umount -lf $INST_MNT/proc
    umount -lf $INST_MNT/sys
    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID
    reboot
