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
- The target system, virtual or physical, must have at least 2GB RAM,
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

#. Fork and clone `this repo <https://github.com/openzfs/openzfs-docs>`__.

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

Boot pool can be optionally encrypted with LUKS,
Encrypted boot pool can protect initrd from tempering.

Preparations
----------------
#. Choose a mirror from `mirrorlist <https://archlinux.org/mirrorlist/all/>`__.

#. Download March 2021 build and signature. `File a new issue and mention @ne9z
   <https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20Update%20Live%20Image%20Arch%20Linux%20Root%20on
   %20ZFS%20HOWTO:>`__ if it's
   no longer available.

   - `ISO (US mirror) <https://mirrors.ocf.berkeley.edu/archlinux/iso/2021.03.01/archlinux-2021.03.01-x86_64.iso>`__
   - `Signature <https://archlinux.org/iso/2021.03.01/archlinux-2021.03.01-x86_64.iso.sig>`__

#. Check live image against signature::

    gpg --auto-key-retrieve --verify archlinux-2021.03.01-x86_64.iso.sig

   If the file is authentic, output should be the following::

    gpg: Signature made Mon 01 Feb 2021 03:23:39 PM UTC
    gpg:                using RSA key 4AA4767BBC9C4B1D18AE28B77F2D434B9741E8AC
    gpg: Good signature from "Pierre Schmitz <pierre@archlinux.de>" [unknown]
    ...
    Primary key fingerprint: 4AA4 767B BC9C 4B1D 18AE  28B7 7F2D 434B 9741 E8AC

   Ensure ``Good signature`` and last 8 digits are ``9741 E8AC``,
   as listed on `Arch Linux Developers <https://archlinux.org/people/developers/#pierre>`__ page.

#. Write the image to a USB drive or an optical disc.

#. Boot the target computer from the prepared live medium.

#. Connect to the internet.
   If the target computer aquires IP address with DHCP,
   no further steps need to be taken.
   Otherwise, refer to
   `Network Configuration <https://wiki.archlinux.org/index.php/Network_configuration>`__
   wiki page.

#. Start SSH server.

   Interactively set root password with::

      passwd

   Start SSH server::

      systemctl start sshd

   Find the IP address of the target computer::

      ip -4 address show scope global

   On another computer, connect to the target computer with::

      ssh root@192.168.1.10

#. Enter a bash shell::

    bash

#. Import keys of archzfs repository::

    curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
    curl -L https://git.io/JtQpl | xargs -i{} pacman-key --lsign-key {}

#. Add archzfs repository::

    tee -a /etc/pacman.conf <<- 'EOF'

    [archzfs]
    Include = /etc/pacman.d/mirrorlist-archzfs
    EOF

    curl -L https://git.io/JtQp4 > /etc/pacman.d/mirrorlist-archzfs

#. Select mirror:

   Kill ``reflector``::

      killall -9 reflector

   Edit the following files::

       nano /etc/pacman.d/mirrorlist

   Uncomment and move mirrors to
   the beginning of the file.

   Update database::

       pacman -Sy

#. Install ZFS in the live environment:

   Expand root filesystem::

    mount -o remount,size=1G /run/archiso/cowspace

   Check kernel variant::

    LIVE_LINVAR=$(sed 's|.*linux|linux|' /proc/cmdline | sed 's|.img||g' | awk '{ print $1 }')

   Check kernel version::

    LIVE_LINVER=$(pacman -Qi ${LIVE_LINVAR} | grep Version | awk '{ print $3 }')

   Install kernel headers::

    pacman -U https://archive.archlinux.org/packages/l/${LIVE_LINVAR}-headers/${LIVE_LINVAR}-headers-${LIVE_LINVER}-x86_64.pkg.tar.zst

   Install zfs-dkms::

    pacman -S --needed zfs-dkms glibc

#. Load kernel module::

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

#. Unique pool suffix. ZFS expects pool names to be
   unique, therefore it's recommended to create
   pools with a unique suffix::

    INST_UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-z0-9' | cut -c-6)

#. Target disk

   List available disks with::

     ls -1d /dev/disk/by-id/* | grep -v part

   If the disk is not in the command output, use ``/dev/disk/by-path``.

   Declare disk array::

    DISK=(/dev/disk/by-id/disk1 /dev/disk/by-id/disk2)

   For single disk installation, use::

    DISK=(/dev/disk/by-id/disk1)

System Installation
-------------------

#. Partition the disks::

     for i in ${DISK[@]}; do

     # clear partition table
     sgdisk --zap-all $i

     # EFI system partition; must be created
     sgdisk -n1:1M:+1G -t1:EF00 $i

     # Boot pool partition
     sgdisk -n2:0:+4G -t2:BE00 $i

     # with swap
     sgdisk -n3:0:-8G -t3:BF00 $i
     sgdisk -n4:0:0   -t4:8308 $i

     # without swap (not recommended)
     #sgdisk -n3:0:0 -t3:BF00 $i

     # with BIOS booting; can co-exist with EFI
     sgdisk -a1 -n5:24K:+1000K -t5:EF02 $i

     done

   It's `recommended <https://chrisdown.name/2018/01/02/in-defence-of-swap.html>`__
   to create a swap partition.

   Adjust the swap partition size to your needs.
   If hibernation is needed,
   swap size should be same or larger than RAM.
   Check RAM size with ``free -h``.

#. When creating pools, for single disk installation, omit topology specification
   ``mirror``::

    zpool create \
        ...
        rpool_$INST_UUID \
        # mirror \
        ...

#. When creating pools, for multi-disk installation, you can also use other topologies
   such as ``raidz1``, ``raidz2`` and ``raidz3``.

#. Create boot pool::

    zpool create \
        -o ashift=12 \
        -o autotrim=on \
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
        -R /mnt \
        bpool_$INST_UUID \
        mirror \
        $(for i in ${DISK[@]}; do
           printf "$i-part2 ";
          done)

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

#. Create root pool::

       zpool create \
        -o ashift=12 \
        -o autotrim=on \
        -R /mnt \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=zstd \
        -O dnodesize=auto \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/ \
        rpool_$INST_UUID \
        mirror \
       $(for i in ${DISK[@]}; do
          printf "$i-part3 ";
         done)

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

#. Create system boot container::

    zfs create \
     -o canmount=off \
     -o mountpoint=none \
     bpool_$INST_UUID/sys

#. Create system root container:

   Dataset encryption is set at creation and can not be altered later,
   but encrypted dataset can be created inside an unencrypted parent dataset.

   - Unencrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       rpool_$INST_UUID/sys

   - Encrypted:

     Choose a strong password.
     Due to the Copy-on-Write nature of ZFS,
     `merely changing password is not enough <https://openzfs.github.io/openzfs-docs/man/8/zfs-change-key.8.html>`__
     once the password is compromised.
     Dataset and pool must be destroyed,
     disk wiped and system rebuilt from scratch to protect confidentiality.
     Example: generate passphrase with `xkcdpass <https://github.com/redacted/XKCD-password-generator>`_::

      pacman -S --noconfirm xkcdpass
      xkcdpass -Vn 10 -w /usr/lib/python*/site-packages/xkcdpass/static/eff-long

     Root pool password can be supplied with SSH at boot time if boot pool is not encrypted,
     see optional configurations section.

     Encrypt boot pool.
     For mobile devices, it is strongly recommended to
     encrypt boot pool and enable Secure Boot, as described in
     the optional configuration section. This will prevent attacks to
     initrd.
     However, GRUB as of 2.04 requires interactively entering password,
     you must phsically type in the passwords at boot time,
     or else the computer will not boot.

     Create dataset::

       zfs create \
        -o canmount=off \
        -o mountpoint=none \
        -o encryption=on \
        -o keylocation=prompt \
        -o keyformat=passphrase \
        rpool_$INST_UUID/sys

#. Create container datasets::

    zfs create -o canmount=off -o mountpoint=none bpool_$INST_UUID/sys/BOOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/sys/ROOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/sys/DATA

#. Create root and boot filesystem datasets::

     zfs create -o mountpoint=legacy -o canmount=noauto bpool_$INST_UUID/sys/BOOT/default
     zfs create -o mountpoint=/      -o canmount=off    rpool_$INST_UUID/sys/DATA/default
     zfs create -o mountpoint=/      -o canmount=noauto rpool_$INST_UUID/sys/ROOT/default

#. Mount root and boot filesystem datasets::

    zfs mount rpool_$INST_UUID/sys/ROOT/default
    mkdir /mnt/boot
    mount -t zfs bpool_$INST_UUID/sys/BOOT/default /mnt/boot

#. Create datasets to separate user data from root filesystem::

    # create containers
    for i in {usr,var,var/lib};
    do
        zfs create -o canmount=off rpool_$INST_UUID/sys/DATA/default/$i
    done

    for i in {home,root,srv,usr/local,var/log,var/spool,var/tmp};
    do
        zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/$i
    done

    chmod 750 /mnt/root
    chmod 1777 /mnt/var/tmp

#. Create optional user data datasets to omit data from rollback::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/games
     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/www
     # for GNOME
     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/AccountsService
     # for Docker
     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/docker
     # for NFS
     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/nfs
     # for LXC
     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/lxc
     # for LibVirt
     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/libvirt

#. Format and mount EFI system partitions::

    for i in ${DISK[@]}; do
     mkfs.vfat -n EFI ${i}-part1
     mkdir -p /mnt/boot/efis/${i##*/}
     mount -t vfat ${i}-part1 /mnt/boot/efis/${i##*/}
    done

    mkdir -p /mnt/boot/efi
    mount -t vfat ${DISK[0]}-part1 /mnt/boot/efi

#. Install base packages::

     pacstrap /mnt base vi mandoc grub

#. Check compatible kernel version::

     INST_LINVER=$(pacman -Si zfs-${INST_LINVAR} \
     | grep 'Depends On' \
     | sed "s|.*${INST_LINVAR}=||" \
     | awk '{ print $1 }')

#. Install kernel. Download from archive if kernel is not available::

    if [ ${INST_LINVER} == \
    $(pacman -Si ${INST_LINVAR} | grep Version | awk '{ print $3 }') ]; then
     pacstrap /mnt ${INST_LINVAR}
    else
     pacstrap -U /mnt \
     https://archive.archlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst
    fi

#. Install archzfs package::

     pacstrap /mnt zfs-$INST_LINVAR

#. Install firmware::

     pacstrap /mnt linux-firmware intel-ucode amd-ucode

#. If you boot your computer with EFI::

     pacstrap /mnt efibootmgr

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

    mkdir -p /mnt/etc/zfs/zfs-list.cache

    zfs list -H -t filesystem -o $PROPS -r rpool_$INST_UUID > /mnt/etc/zfs/zfs-list.cache/rpool_$INST_UUID

    sed -Ei "s|/mnt/?|/|" /mnt/etc/zfs/zfs-list.cache/*

#. Generate fstab::

    echo bpool_$INST_UUID/sys/BOOT/default /boot zfs rw,xattr,posixacl 0 0 >> /mnt/etc/fstab

    for i in ${DISK[@]}; do
       echo UUID=$(blkid -s UUID -o value ${i}-part1) /boot/efis/${i##*/} vfat \
       x-systemd.idle-timeout=1min,x-systemd.automount,noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab
    done

    echo UUID=$(blkid -s UUID -o value ${DISK[0]}-part1) /boot/efi vfat \
    x-systemd.idle-timeout=1min,x-systemd.automount,noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab

   If a swap partition has been created::

    for i in ${DISK[@]}; do
     echo swap-${i##*/} ${i}-part4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256,discard >> /mnt/etc/crypttab
     echo /dev/mapper/swap-${i##*/} none swap defaults 0 0 >> /mnt/etc/fstab
    done

#. Configure mkinitcpio::

    mv /mnt/etc/mkinitcpio.conf /mnt/etc/mkinitcpio.conf.original

    tee /mnt/etc/mkinitcpio.conf <<EOF
    HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
    EOF

#. Host name::

    echo $INST_HOST > /mnt/etc/hostname

#. Configure the network interface:

   Find the interface name::

     ip link

   Store it in a variable::

     INET=enp1s0

   Create network configuration::

     tee /mnt/etc/systemd/network/20-default.network <<EOF

     [Match]
     Name=$INET

     [Network]
     DHCP=yes
     EOF

   Customize this file if the system is not a DHCP client.
   See `Network Configuration <https://wiki.archlinux.org/index.php/Network_configuration>`__.

#. Timezone::

    ln -sf $INST_TZ /mnt/etc/localtime
    hwclock --systohc

#. Locale::

    echo "en_US.UTF-8 UTF-8" >> /mnt/etc/locale.gen
    echo "LANG=en_US.UTF-8" >> /mnt/etc/locale.conf

   Other locales should be added after reboot.

#. Chroot::

    for i in ${DISK[@]}; do printf "$i "; done; printf '\n'
    # /dev/disk/by-id/disk1 /dev/disk/by-id/disk2
    arch-chroot /mnt /usr/bin/env INST_LINVAR=$INST_LINVAR INST_UUID=$INST_UUID bash --login

   Declare target disks::

    DISK=(/dev/disk/by-id/disk1 /dev/disk/by-id/disk2)

#. Apply locales::

    locale-gen

#. Import keys of archzfs repository::

    curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
    curl -L https://git.io/JtQpl | xargs -i{} pacman-key --lsign-key {}
    curl -L https://git.io/JtQp4 > /etc/pacman.d/mirrorlist-archzfs

#. Add archzfs repository::

    tee -a /etc/pacman.conf <<- 'EOF'

    #[archzfs-testing]
    #Include = /etc/pacman.d/mirrorlist-archzfs
    [archzfs]
    Include = /etc/pacman.d/mirrorlist-archzfs
    EOF

#. Ignore kernel updates::

    sed -i 's/#IgnorePkg/IgnorePkg/' /etc/pacman.conf
    sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR} zfs-utils/" /etc/pacman.conf

   Kernel will be manually updated, see Getting Started.

#. Enable networking::

    systemctl enable systemd-networkd systemd-resolved

#. Enable ZFS services::

    systemctl enable zfs-import-cache zfs-import.target zfs-mount zfs-zed zfs.target

#. Generate zpool.cache

   Pools are imported by initrd with the information stored in ``/etc/zfs/zpool.cache``.
   This cache file will be embedded in initrd.

   ::

     zpool set cachefile=/etc/zfs/zpool.cache rpool_$INST_UUID
     zpool set cachefile=/etc/zfs/zpool.cache bpool_$INST_UUID

#. Set root password::

     passwd

#. Generate initrd::

     mkinitcpio -P

Optional Configuration
~~~~~~~~~~~~~~~~~~~~~~~
- Boot Environment Manager

  A boot environment is a dataset which contains a bootable
  instance of an operating system. Within the context of this installation,
  boot environments can be created on-the-fly to preserve root file system
  states before pacman transactions.

  Install `rozb3-pac <https://gitlab.com/m_zhou/rozb3-pac/-/releases>`__
  pacman hook and
  `bieaz <https://gitlab.com/m_zhou/bieaz/-/releases>`__
  from AUR to create boot environments.
  Prebuilt packages are also available.

- Supply password with SSH

  #. Install mkinitcpio tools::

      pacman -S mkinitcpio-netconf mkinitcpio-dropbear openssh

  #. Store public keys in ``/etc/dropbear/root_key``::

      vi /etc/dropbear/root_key

     Note that dropbear only supports RSA keys.

  #. Edit mkinitcpio::

      tee /etc/mkinitcpio.conf <<- 'EOF'
      HOOKS=(base udev autodetect modconf block keyboard netconf dropbear zfsencryptssh zfs filesystems)
      EOF

  #. Add ``ip=`` to kernel command line::

      # example DHCP
      echo 'GRUB_CMDLINE_LINUX="ip=::::::dhcp"' >> /etc/default/grub

     Details for ``ip=`` can be found at
     `here <https://www.kernel.org/doc/html/latest/admin-guide/nfs/nfsroot.html#kernel-command-line>`__.

  #. Generate host keys::

      ssh-keygen -Am pem

  #. Regenerate initrd::

      mkinitcpio -P

- Encrypted boot pool.

  If encryption is enabled earlier, boot pool can be optionally encrypted.

  This step will reformat ``${DISK[@]}-part2`` as LUKS container and rebuild
  boot pool with ``/dev/mapper/*`` as vdev. Password must
  be entered interactively at GRUB and thus incompatible with
  `Supply password with SSH <#supply-password-with-ssh>`__.

  Encrypted boot pool protects initrd from
  malicious modification and supports hibernation
  and persistent encrypted swap.

  #. Create encryption keys::

      mkdir /etc/cryptkey.d/
      chmod 700 /etc/cryptkey.d/
      dd bs=32 count=1 if=/dev/urandom of=/etc/cryptkey.d/lukskey-bpool_$INST_UUID
      dd bs=32 count=1 if=/dev/urandom of=/etc/cryptkey.d/zfskey-rpool_$INST_UUID

  #. Backup boot pool::

      zfs snapshot -r bpool_$INST_UUID/sys@pre-luks
      zfs send -R bpool_$INST_UUID/sys@pre-luks > /root/bpool_$INST_UUID-pre-luks

  #. Unmount EFI partition::

      umount /boot/efi

      for i in ${DISK[@]}; do
       umount /boot/efis/${i##*/}
      done

  #. Destroy boot pool::

      zpool destroy bpool_$INST_UUID

  #. LUKS password::

      LUKS_PWD=secure-passwd

     You will need to enter the same password for
     each disk at boot. As root pool key is
     protected by this password, the previous warning
     about password strength still apply.

  #. Create LUKS containers::

      for i in ${DISK[@]}; do
       cryptsetup luksFormat -q --type luks1 --key-file /etc/cryptkey.d/lukskey-bpool_$INST_UUID $i-part2
       echo $LUKS_PWD | cryptsetup luksAddKey --key-file /etc/cryptkey.d/lukskey-bpool_$INST_UUID $i-part2
       cryptsetup open ${i}-part2 luks-bpool_$INST_UUID-${i##*/}-part2 --key-file /etc/cryptkey.d/lukskey-bpool_$INST_UUID
       echo luks-bpool_$INST_UUID-${i##*/}-part2 ${i}-part2 /etc/cryptkey.d/lukskey-bpool_$INST_UUID discard >> /etc/crypttab
      done

  #. Embed key file in initrd::

      tee -a /etc/mkinitcpio.conf <<EOF
      FILES=(/etc/cryptkey.d/lukskey-bpool_$INST_UUID /etc/cryptkey.d/zfskey-rpool_$INST_UUID)
      EOF

  #. Recreate boot pool with mappers as vdev.

     Example::

       zpool create \
       # reuse command here
       # without '-R /mnt'
       # ...
       bpool_$INST_UUID \
       mirror \
       $(for i in ${DISK[@]}; do
          printf "/dev/mapper/luks-bpool_$INST_UUID-${i##*/}-part2 ";
         done)

  #. Restore boot pool backup::

      cat /root/bpool_$INST_UUID-pre-luks | zfs recv bpool_$INST_UUID/sys
      rm /root/bpool_$INST_UUID-pre-luks

  #. Mount boot dataset and EFI partitions::

      mount /boot
      mount /boot/efi

      for i in ${DISK[@]}; do
       mount /boot/efis/${i##*/}
      done

  #. Change root pool password to key file::

      zfs change-key -l \
      -o keylocation=file:///etc/cryptkey.d/zfskey-rpool_$INST_UUID \
      -o keyformat=raw \
      rpool_$INST_UUID/sys

  #. Remove ``zfsencryptssh`` hook.
     Encrypted boot pool is incompatible with
     password by SSH::

      sed -i 's|zfsencryptssh||g' /etc/mkinitcpio.conf

     If ``zfsencryptssh`` is not removed, initrd will
     stuck at ``fail to load key material`` and fail to boot.

  #. Generate initrd::

      mkinitcpio -P

  #. As keys are stored in initrd,
     set secure permissions for ``/boot``::

      chmod 700 /boot

  #. Import boot pool after starting systemd::

       tee /etc/systemd/system/zfs-bpool_$INST_UUID-import-cache.service <<EOF
       [Unit]
       Description=Import boot pool by cache file
       Documentation=man:zpool(8)
       DefaultDependencies=no
       Requires=systemd-udev-settle.service
       After=zfs-import-cache.service
       After=zfs-import.target
       Before=boot.mount
       ConditionFileNotEmpty=/etc/zfs/zpool.cache
       ConditionPathIsDirectory=/sys/module/zfs

       [Service]
       Type=oneshot
       RemainAfterExit=yes
       ExecStart=/usr/bin/zpool import -c /etc/zfs/zpool.cache -aN

       [Install]
       WantedBy=zfs-import.target
       EOF

       systemctl enable zfs-bpool_$INST_UUID-import-cache.service

     initrd will still try to import boot pool
     before mapping LUKS containers. This will fail
     and delay boot for a few seconds.

  #. Enable GRUB cryptodisk::

       echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub

  #. **Important**: Back up root dataset key ``/etc/cryptkey.d/zfskey-rpool_$INST_UUID``
     to a secure location.

     In the possible event of LUKS container corruption,
     data on root set will only be available
     with this key.

Bootloader
----------------------------

Workarounds
~~~~~~~~~~~~~~~~~~~~
Currently GRUB has multiple compatibility problems with ZFS,
especially with regards to newer ZFS features.
Workarounds have to be applied.

#. grub-probe fails to get canonical path

   When persistent device names ``/dev/disk/by-id/*`` are used
   with ZFS, GRUB will fail to resolve the path of the boot pool
   device. Error::

     # /usr/bin/grub-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.0-part3'.

   Solution::

    echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile
    source /etc/profile

#. Pool name missing

   See `this bug report <https://savannah.gnu.org/bugs/?59614>`__.
   Root pool name is missing from ``root=ZFS=rpool_$INST_UUID/ROOT/default``
   kernel cmdline in generated ``grub.cfg`` file.

   A workaround is to replace the pool name detection with ``zdb``
   command::

     sed -i "s|rpool=.*|rpool=\`zdb -l \${GRUB_DEVICE} \| grep -E '[[:blank:]]name' \| cut -d\\\' -f 2\`|"  /etc/grub.d/10_linux

   If you forgot to apply this workaround, or GRUB package has been upgraded,
   initrd will fail to find root filesystem on reboot, ending in kernel panic.

Installation
~~~~~~~~~~~~~~~~~

#. Install GRUB:

   If you use EFI::

    grub-install && grub-install --removable

   If using multi-disk setup, mirror EFI system partitions::

    cp -r /boot/efi/EFI /tmp
    umount /boot/efi
    for i in ${DISK[@]}; do
     cp -r /tmp/EFI /boot/efis/${i##*/}
     efibootmgr -cgp 1 -l "\EFI\arch\grubx64.efi" \
     -L "arch-${i##*/}" -d ${i}-part1
    done
    mount /boot/efi

   If you use BIOS booting::

    for i in ${DISK[@]}; do
     grub-install --target=i386-pc $i
    done

#. Generate GRUB Menu::

    grub-mkconfig -o /boot/grub/grub.cfg

Finish Installation
-------------------

#. Exit chroot::

    exit

#. Take a snapshot of the clean installation for future use::

    zfs snapshot -r rpool_$INST_UUID/sys@install
    zfs snapshot -r bpool_$INST_UUID/sys@install

#. Unmount EFI system partition::

    umount /mnt/boot/efi
    for i in ${DISK[@]}; do
     umount /mnt/boot/efis/${i##*/}
    done

#. Export pools::

    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID

#. Reboot::

    reboot

GRUB Tips
-------------

- Switch prefix

  If GRUB has not been reinstalled after switching default boot environment,
  GRUB might fail to load configuration files or modules.

  We need to point prefix to the new boot environment and instruct GRUB
  to load configurations from there.

  #. Press ``c`` at GRUB menu. Skip this if you are in GRUB rescue.

  #. Check existing prefix::

       grub > set
       # ...
       # unencrypted bpool_$INST_UUID
       # prefix=(hd0,gpt2)/sys/BOOT/default@/grub
       # encrypted bpool_$INST_UUID
       # prefix=(cryptouuid/UUID)/sys/BOOT/default@/grub

  #. List available boot environments::

       # unencrypted bpool_$INST_UUID
       grub > ls (hd0,gpt2)/sys/BOOT
       # encrypted bpool_$INST_UUID
       grub > ls (crypto0)/sys/BOOT
       @/ default/ pac-multm2/

  #. Set new prefix::

      # unencrypted bpool_$INST_UUID
      grub > prefix=(hd0,gpt2)/sys/BOOT/pac-multm2@/grub
      # encrypted bpool_$INST_UUID
      grub > prefix=(crypto0)/sys/BOOT/pac-multm2@/grub

  #. Load config from new prefix::

      grub > insmod normal
      grub > normal

     New entries are shown below the old ones.

- Encrypted boot pool, if the password entered is wrong, GRUB
  will drop to ``grub-rescue`` instead of retrying::

   Attempting to decrypt master key...
   Enter passphrase for hd0,gpt2 (c0987ea1a51049e9b3056622804de62a):
   error: access denied.
   error: no such cryptodisk found.
   Entering rescue mode...
   grub rescue>

  Try entering the password again with::

   grub rescue> cryptomount hd0,gpt2
   Attempting to decrypt master key...
   Enter passphrase for hd0,gpt2 (c0987ea1a51049e9b3056622804de62a):
   Slot 1 opened
   grub rescue> insmod normal
   grub rescue> normal

  GRUB should then boot normally.

- Encrypted boot pool, when prefix disk failed, GRUB might fail to boot.

  .. code-block:: text

   Welcome to GRUB!

   error: no such cryptodisk found.
   Attempting to decrypt master key...
   Enter passphrase for hd0,gpt2 (c0987ea1a51049e9b3056622804de62a):
   Slot 1 opened
   error: disk `cryptouuid/47ed1b7eb0014bc9a70aede3d8714faf' not found.
   Entering rescue mode...
   grub rescue>

  Ensure ``Slot 1 opened`` message
  is shown. If ``error: access denied.`` is shown,
  the password entered is wrong.

  Check prefix::

      grub rescue > set
      # prefix=(cryptouuid/47ed1b7eb0014bc9a70aede3d8714faf)/sys/BOOT/default@/grub
      # root=cryptouuid/47ed1b7eb0014bc9a70aede3d8714faf

  Replace ``cryptouuid/UUID`` with ``crypto0``::

      grub rescue> prefix=(crypto0)/sys/BOOT/default@/grub
      grub rescue> root=crypto0

  Boot GRUB::

      grub rescue> insmod normal
      grub rescue> normal

  GRUB should then boot normally. After entering system,
  promote one backup to ``/boot/efi`` and reinstall GRUB with
  ``grub-install``.

Recovery
--------

#. Go through `preparations <#preparations>`__.

#. Import and unlock root and boot pool::

     zpool import -NR /mnt rpool_$INST_UUID
     zpool import -NR /mnt bpool_$INST_UUID

   If using password::

     zfs load-key rpool_$INST_UUID/sys

   If using keyfile::

     zfs load-key -L file:///path/to/keyfile rpool_$INST_UUID/sys

#. Find the current boot environment::

     zfs list
     BE=default

#. Mount root filesystem::

     zfs mount rpool_$INST_UUID/sys/ROOT/$BE

#. chroot into the system::

     arch-chroot /mnt /bin/bash --login
     zfs mount -a
     mount -a

#. Finish rescue. See `finish installation <#finish-installation>`__.
