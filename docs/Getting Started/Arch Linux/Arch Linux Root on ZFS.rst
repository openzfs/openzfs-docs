.. highlight:: sh

Arch Linux Root on ZFS
======================

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
  or the DKMS module might fail to build.
- Installing on a drive which presents 4 KiB logical sectors (a “4Kn” drive)
  only works with UEFI booting. This not unique to ZFS. `GRUB does not and
  will not work on 4Kn with legacy (BIOS) booting.
  <http://savannah.gnu.org/bugs/?46700>`__

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <irc://irc.freenode.net/#zfsonlinux>`__ on `freenode
<https://freenode.net/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @ne9z
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Arch%20Linux%20Root%20on%20ZFS%20HOWTO:>`__.

Contributing
~~~~~~~~~~~~

#. Fork and clone: https://github.com/openzfs/openzfs-docs

#. Install the tools::

    sudo pacman -S python-pip

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

This guide supports optional ZFS native encryption on root pool.

Unencrypted does not encrypt anything, of course. With no encryption
happening, this option naturally has the best performance.

ZFS native encryption encrypts the data and most metadata in the root
pool. It does not encrypt dataset or snapshot names or properties. The
boot pool is not encrypted at all, but it only contains the bootloader,
kernel, and initrd. (Unless you put a password in ``/etc/fstab``, the
initrd is unlikely to contain sensitive data.) The system cannot boot
without the passphrase being entered at the console. Performance is
good. As the encryption happens in ZFS, even if multiple disks (mirror
or raidz topologies) are used, the data only has to be encrypted once.


Preinstallation
----------------
Download Arch Linux live image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Choose a mirror

    https://archlinux.org/mirrorlist/all/

#. Download Feb 2021 build. `File a new issue and mention @ne9z
   <https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20Update%20Live%20Image%20Arch%20Linux%20Root%20on
   %20ZFS%20HOWTO:>`__ if it's
   no longer available.

    https://mirrors.dotsrc.org/archlinux/iso/2021.02.01/archlinux-2021.02.01-x86_64.iso

#. Write the image to a USB drive or an optical disc.

#. Boot the target computer from the prepared live medium.

Prepare the Live Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Connect to the internet.
   If the target computer aquires IP address with DHCP,
   no further steps need to be taken.
   Otherwise, refer to
   `Network Configuration <https://wiki.archlinux.org/index.php/Network_configuration>`__
   wiki page.

#. Start SSH server.

   - Interactively set root password with::

      passwd

   - Start SSH server::

      systemctl start sshd

   - Find the IP address of the target computer::

      ip -4 address show scope global

   - On another computer, connect to the target computer with::

      ssh root@192.168.1.10

#. Enter a bash shell::

    bash

#. Import keys of archzfs repository::

    curl -O https://archzfs.com/archzfs.gpg
    pacman-key -a archzfs.gpg
    pacman-key --lsign-key DDF7DB817396A49B2A2723F7403BD972F75D9D76

#. Add archzfs repository::

    tee -a /etc/pacman.conf <<-'EOF'
    [archzfs]
    Server = https://archzfs.com/$repo/$arch
    Server = https://mirror.sum7.eu/archlinux/archzfs/$repo/$arch
    Server = https://mirror.biocrafting.net/archlinux/archzfs/$repo/$arch
    Server = https://mirror.in.themindsmaze.com/archzfs/$repo/$arch
    EOF

#. Select mirror:

   - Kill ``reflector``::

      killall -9 reflector

   - Edit the following files::

       /etc/pacman.d/mirrorlist

     Uncomment and move mirrors to
     the beginning of the file.

#. Install ZFS in the live environment::

    pacman -Sy --noconfirm archzfs-linux --ignore=linux

   Ignore ``ERROR: specified kernel image does not exist``.

   If this fails with ``unable to satisfy dependency``,
   install archzfs-dkms instead:

   - Check kernel variant::

       LIVE_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | awk '{ print $1 }')

   - Check kernel version::

       LIVE_LINVER=$(pacman -Qi ${LIVE_LINVAR} | grep Version | awk '{ print $3 }')

   - Install kernel headers::

       pacman -U https://archive.archlinux.org/packages/l/${LIVE_LINVAR}-headers/${LIVE_LINVAR}-headers-${LIVE_LINVER}-x86_64.pkg.tar.zst

   - Expand root filesystem::

       mount -o remount,size=1G /run/archiso/cowspace

   - Install archzfs-dkms::

       pacman -S archzfs-dkms

#. Load kernel module::

    modprobe zfs

Installation Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this part, we will set some variables to configure the system.

#. Timezone

   List the available timezones with::

    ls /usr/share/zoneinfo/

   Store the target timezone in a variable::

    INST_TZ=/usr/share/zoneinfo/Asia/Irkutsk

#. Host name

   Store the host name in a variable::

    INST_HOST='localhost'

#. Kernel variant

   Store the kernel variant in a variable.
   Available variants in official repo are:

   - linux
   - linux-lts
   - linux-zen
   - linux-hardened

   ::

    INST_LINVAR='linux'

#. Target disk

   List the available disks with::

     ls -d /dev/disk/by-id/* | grep -v part

   If the disk is not in the command output, use ``/dev/disk/by-path``.

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

#. Create EFI system partition (for use now or in the future)::

    sgdisk -n1:1M:+1G -t1:EF00 $DISK

#. Create BIOS boot partition::

    sgdisk -a1 -n5:24K:+1000K -t5:EF02 $DISK

#. Create boot pool partition::

    sgdisk -n2:0:+4G -t2:BE00 $DISK

#. Create root pool partition:

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

   If you want to create a multi-disk pool, replace ``${DISK}-partX``
   with the topology and the disk path.

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

   if needed, replace ``mirror`` with ``raidz1``, ``raidz2`` or ``raidz3``.

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

   You should not need to customize any of the options for the boot pool.

   GRUB does not support all of the zpool features. See ``spa_feature_names``
   in `grub-core/fs/zfs/zfs.c
   <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
   This step creates a separate boot pool for ``/boot`` with the features
   limited to only those that GRUB supports, allowing the root pool to use
   any/all features. Note that GRUB opens the pool read-only, so all
   read-only compatible features are “supported” by GRUB.

   **Feature Notes:**

   - The ``allocation_classes`` feature should be safe to use. However, unless
     one is using it (i.e. a ``special`` vdev), there is no point to enabling
     it. It is extremely unlikely that someone would use this feature for a
     boot pool. If one cares about speeding up the boot pool, it would make
     more sense to put the whole pool on the faster disk rather than using it
     as a ``special`` vdev.
   - The ``project_quota`` feature has been tested and is safe to use. This
     feature is extremely unlikely to matter for the boot pool.
   - The ``resilver_defer`` should be safe but the boot pool is small enough
     that it is unlikely to be necessary.
   - The ``spacemap_v2`` feature has been tested and is safe to use. The boot
     pool is small, so this does not matter in practice.
   - As a read-only compatible feature, the ``userobj_accounting`` feature
     should be compatible in theory, but in practice, GRUB can fail with an
     “invalid dnode type” error. This feature does not matter for ``/boot``
     anyway.

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

   **Notes:**

   - The use of ``ashift=12`` is recommended here because many drives
     today have 4 KiB (or larger) physical sectors, even though they
     present 512 B logical sectors. Also, a future replacement drive may
     have 4 KiB physical sectors (in which case ``ashift=12`` is desirable)
     or 4 KiB logical sectors (in which case ``ashift=12`` is required).
   - Setting ``-O acltype=posixacl`` enables POSIX ACLs globally. If you
     do not want this, remove that option, but later add
     ``-o acltype=posixacl`` (note: lowercase “o”) to the ``zfs create``
     for ``/var/log``, as `journald requires ACLs
     <https://askubuntu.com/questions/970886/journalctl-says-failed-to-search-journal-acl-operation-not-supported>`__
   - Setting ``normalization=formD`` eliminates some corner cases relating
     to UTF-8 filename normalization. It also implies ``utf8only=on``,
     which means that only UTF-8 filenames are allowed. If you care to
     support non-UTF-8 filenames, do not use this option. For a discussion
     of why requiring UTF-8 filenames may be a bad idea, see `The problems
     with enforced UTF-8 only filenames
     <http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames>`__.
   - ``recordsize`` is unset (leaving it at the default of 128 KiB). If you
     want to tune it (e.g. ``-o recordsize=1M``), see `these
     <https://jrs-s.net/2019/04/03/on-zfs-recordsize/>`__ `various
     <http://blog.programster.org/zfs-record-size>`__ `blog
     <https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSFileRecordsizeGrowth>`__
     `posts
     <https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSRecordsizeAndCompression>`__.
   - Setting ``relatime=on`` is a middle ground between classic POSIX
     ``atime`` behavior (with its significant performance impact) and
     ``atime=off`` (which provides the best performance by completely
     disabling atime updates). Since Linux 2.6.30, ``relatime`` has been
     the default for other filesystems. See `RedHat’s documentation
     <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/power_management_guide/relatime>`__
     for further information.
   - Setting ``xattr=sa`` `vastly improves the performance of extended
     attributes
     <https://github.com/zfsonlinux/zfs/commit/82a37189aac955c81a59a5ecc3400475adb56355>`__.
     Inside ZFS, extended attributes are used to implement POSIX ACLs.
     Extended attributes can also be used by user-space applications.
     `They are used by some desktop GUI applications.
     <https://en.wikipedia.org/wiki/Extended_file_attributes#Linux>`__
     `They can be used by Samba to store Windows ACLs and DOS attributes;
     they are required for a Samba Active Directory domain controller.
     <https://wiki.samba.org/index.php/Setting_up_a_Share_Using_Windows_ACLs>`__
     Note that ``xattr=sa`` is `Linux-specific
     <https://openzfs.org/wiki/Platform_code_differences>`__. If you move your
     ``xattr=sa`` pool to another OpenZFS implementation besides ZFS-on-Linux,
     extended attributes will not be readable (though your data will be). If
     portability of extended attributes is important to you, omit the
     ``-O xattr=sa`` above. Even if you do not want ``xattr=sa`` for the whole
     pool, it is probably fine to use it for ``/var/log``.
   - Make sure to include the ``-part3`` portion of the drive path. If you
     forget that, you are specifying the whole disk, which ZFS will then
     re-partition, and you will lose the bootloader partition(s).
   - ZFS native encryption `now
     <https://github.com/openzfs/zfs/commit/31b160f0a6c673c8f926233af2ed6d5354808393>`__
     defaults to ``aes-256-gcm``.
   - Your passphrase will likely be the weakest link. Choose wisely. See
     `section 5 of the cryptsetup FAQ
     <https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions#5-security-aspects>`__
     for guidance.

Create Datasets
~~~~~~~~~~~~~~~~~~~~~~

#. Create container datasets::

    zfs create -o canmount=off -o mountpoint=none bpool_$INST_UUID/BOOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/ROOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/DATA

#. Create root and boot filesystem datasets::

     zfs create -o mountpoint=legacy -o canmount=noauto bpool_$INST_UUID/BOOT/default
     zfs create -o mountpoint=/      -o canmount=noauto rpool_$INST_UUID/ROOT/default

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

   If this system will use libvirt::

     zfs create -o canmount=on rpool_$INST_UUID/DATA/default/var/lib/libvirt

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

#. Install base packages::

     pacstrap $INST_MNT base vi mandoc grub

#. Check compatible kernel version::

     INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} \
     | grep 'Depends On' \
     | sed "s|.*${INST_LINVAR}=||" \
     | awk '{ print $1 }')

#. Install kernel::

     pacstrap -U $INST_MNT \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst

#. Install archzfs package::

     pacstrap $INST_MNT archzfs-$INST_LINVAR

#. If your computer has hardware that requires firmware to run::

     pacstrap $INST_MNT linux-firmware

#. If you boot your computer with EFI::

     pacstrap $INST_MNT dosfstools efibootmgr

#. Microcode:

   - ``pacstrap $INST_MNT amd-ucode``
   - ``pacstrap $INST_MNT intel-ucode``

#. For other optional packages,
   see `ArchWiki <https://wiki.archlinux.org/index.php/Installation_guide#Installation>`__.

System Configuration
--------------------

#. Generate list of datasets for ``zfs-mount-generator`` to mount them at boot::

    # tab-separated zfs properties
    # see /etc/zfs/zed.d/history_event-zfs-list-cacher.sh
    export \
    PROPS="name,mountpoint,canmount,atime,relatime,devices,exec\
    ,readonly,setuid,nbmand,encroot,keylocation\
    ,org.openzfs.systemd:requires,org.openzfs.systemd:requires-mounts-for\
    ,org.openzfs.systemd:before,org.openzfs.systemd:after\
    ,org.openzfs.systemd:wanted-by,org.openzfs.systemd:required-by\
    ,org.openzfs.systemd:nofail,org.openzfs.systemd:ignore"

    mkdir -p $INST_MNT/etc/zfs/zfs-list.cache

    zfs list -H -t filesystem -o $PROPS -r rpool_$INST_UUID \
    > $INST_MNT/etc/zfs/zfs-list.cache/rpool_$INST_UUID

    sed -Ei "s|$INST_MNT/?|/|" $INST_MNT/etc/zfs/zfs-list.cache/*

#. Generate fstab::

     echo bpool_$INST_UUID/BOOT/default /boot zfs rw,xattr,posixacl 0 0 >> $INST_MNT/etc/fstab
     echo UUID=$(blkid -s UUID -o value ${DISK}-part1) /boot/efi vfat umask=0022,fmask=0022,dmask=0022 0 1 >> $INST_MNT/etc/fstab

   If a swap partition has been created::

       echo crypt-swap ${DISK}-part4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256 >> $INST_MNT/etc/crypttab
       echo /dev/mapper/crypt-swap none swap defaults 0 0 >> $INST_MNT/etc/fstab

#. Configure mkinitcpio::

    mv $INST_MNT/etc/mkinitcpio.conf $INST_MNT/etc/mkinitcpio.conf.original

    tee $INST_MNT/etc/mkinitcpio.conf <<EOF
    HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
    EOF

#. Host name::

    echo $INST_HOST > $INST_MNT/etc/hostname

#. Configure the network interface:

   Find the interface name::

     ip link

   Store it in a variable::

     INET=enp1s0

   Create network configuration::

     tee $INST_MNT/etc/systemd/network/20-default.network <<EOF

     [Match]
     Name=$INET

     [Network]
     DHCP=yes
     EOF

   Customize this file if the system is not a DHCP client.
   See `Network Configuration <https://wiki.archlinux.org/index.php/Network_configuration>`__.

#. Timezone::

    ln -sf $INST_TZ $INST_MNT/etc/localtime
    hwclock --systohc

#. archzfs repository::

    tee -a $INST_MNT/etc/pacman.conf <<-'EOF'
    [archzfs]
    Server = https://archzfs.com/$repo/$arch
    Server = https://mirror.sum7.eu/archlinux/archzfs/$repo/$arch
    Server = https://mirror.biocrafting.net/archlinux/archzfs/$repo/$arch
    Server = https://mirror.in.themindsmaze.com/archzfs/$repo/$arch
    EOF

#. Locale::

    echo "en_US.UTF-8 UTF-8" >> $INST_MNT/etc/locale.gen
    echo "LANG=en_US.UTF-8" >> $INST_MNT/etc/locale.conf

   Other locales should be added after reboot.

#. Chroot::

    arch-chroot $INST_MNT /usr/bin/env  DISK=$DISK \
      INST_UUID=$INST_UUID bash --login

#. Apply locales::

    locale-gen

#. Enable networking::

    systemctl enable systemd-networkd systemd-resolved

#. Enable ZFS services::

    systemctl enable zfs-import-cache zfs-import.target \
      zfs-mount zfs-zed zfs.target

#. Generate zpool.cache

   Pools are imported by initramfs with the information stored in ``/etc/zfs/zpool.cache``.
   This cache file will be embedded in ``initramfs``.

   ::

     zpool set cachefile=/etc/zfs/zpool.cache rpool_$INST_UUID
     zpool set cachefile=/etc/zfs/zpool.cache bpool_$INST_UUID

#. Set root password::

     passwd

#. Generate initramfs::

     mkinitcpio -P

Bootloader Installation
----------------------------

Currently GRUB has multiple compatibility problems with ZFS,
especially with regards to newer ZFS features.
Workarounds have to be applied.

grub-probe fails to get canonical path of root partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Solution::

 echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile
 source /etc/profile

**Notes:**

 When persistent device names ``/dev/disk/by-id/*`` are used
 with ZFS, GRUB will fail to resolve the path of the boot pool
 device. Error::

   # /usr/bin/grub-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.0-part3'.

Pool name missing if the pool has unsupported features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
See `this bug report <https://savannah.gnu.org/bugs/?59614>`__.
A workaround is to replace the pool name detection with ``zdb``
command::

 sed -i "s|rpool=.*|rpool=\`zdb -l \${GRUB_DEVICE} \| grep -E '[[:blank:]]name' \| cut -d\\\' -f 2\`|"  /etc/grub.d/10_linux

**Notes:**

 In ``/etc/grub.d/10_linux``::

   # rpool=`${grub_probe} --device ${GRUB_DEVICE} --target=fs_label 2>/dev/null || true`

 ``10_linux`` will return an empty result if the root pool has features
 not supported by GRUB.

 With this bug, the generated ``grub.cfg`` contains such lines::

   root=ZFS=/ROOT/default # root pool name missing; unbootable

 Rendering the system unbootable.

 This will replace the faulty line in ``10_linux`` with::

    # rpool=`zdb -l ${GRUB_DEVICE} | grep -E '[[:blank:]]name' | cut -d\' -f 2`

 Debian guide chose to hardcode ``root=ZFS=rpool/ROOT/default``
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

  If this is a multi-disk setup,
  install to other disks as well.

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

#. Unmount EFI system partition::

    umount $INST_MNT/boot/efi

#. Export pools::

    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID

 They must be exported, or else they will fail to be imported on reboot.

After Reboot
------------
Mirror EFI System Partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Format redundant EFI partitions::

     mkfs.vfat -n EFI2 /dev/disk/by-id/target_disk2-part1
     mkfs.vfat -n EFI3 /dev/disk/by-id/target_disk3-part1

#. Create mountpoints::

     mkdir -p /boot/efis/{2,3}

#. Mount redundant EFI partitions::

     mount -o umask=0022,fmask=0022,dmask=0022 /dev/disk/by-id/target_disk2-part1 /boot/efis/2
     mount -o umask=0022,fmask=0022,dmask=0022 /dev/disk/by-id/target_disk3-part1 /boot/efis/3

#. Add fstab entries::

     pacman -S --needed arch-install-scripts rsync

     genfstab / | grep efis >> /etc/fstab

#. Sync EFI system partition contents::

     for i in /boot/efis/*; do
        /usr/bin/rsync -a /boot/efi/ $i/
     done

#. Add EFI boot entries::

    efibootmgr -cgd /dev/disk/by-id/target_disk2-part1 \
       -p 1 -L "arch-2" -l "\EFI\arch\grubx64.efi"
    efibootmgr -cgd /dev/disk/by-id/target_disk3-part1 \
       -p 1 -L "arch-3" -l "\EFI\arch\grubx64.efi"

#. Create a service to monitor and sync EFI partitions::

    tee /usr/lib/systemd/system/boot/efis-sync.path << EOF
    [Unit]
    Description=Monitor changes in EFI system partition

    [Path]
    PathModified=/boot/efi/EFI/arch/

    [Install]
    WantedBy=multi-user.target
    EOF

    tee /usr/lib/systemd/system/boot/efis-sync.service << EOF
    [Unit]
    Description=Sync EFI system partition contents to backups

    [Service]
    Type=oneshot
    ExecStart=/usr/bin/bash -c 'for i in /boot/efis/*; do /usr/bin/rsync -a /boot/efi/ $i/; done'
    EOF

    systemctl enable --now efis-sync.path

Boot Environment Manager
~~~~~~~~~~~~~~~~~~~~~~~~
Optional: install ``rozb3-pac`` pacman hook and ``bieaz`` from AUR to
create boot environments.

Post installation
~~~~~~~~~~~~~~~~~
For post installation recommendations,
see `ArchWiki <https://wiki.archlinux.org/index.php/Installation_guide#Post-installation>`__.

Remember to create separate datasets for individual users.

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

     arch-chroot $INST_MNT /bin/bash --login
     mount /boot
     mount /boot/efi
     zfs mount -a

#. Finish rescue::

    exit
    umount $INST_MNT/boot/efi
    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID
    reboot
