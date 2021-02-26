.. highlight:: sh

Artix Linux Root on ZFS
=======================

.. contents:: Table of Contents
   :local:

Overview
--------

`Artix Linux <https://artixlinux.org/>`__ is a systemd-free distribution based on Arch Linux.

OpenRC, runit and s6 are supported init systems.

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
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Artix%20Linux%20Root%20on%20ZFS%20HOWTO:>`__.

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

Preinstallation
----------------
Download Artix Linux live image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OpenRC is used throughout this guide.

Other init systems, runit and s6, are also supported.
Change the service commands to the equivalent commands.

#. Choose a mirror:

    `Mirrorlist <https://artixlinux.org/download.php>`__

#. Download January 2021 build and signature. `File a new issue and mention @ne9z
   <https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20Update%20Live%20Image%20Artix%20Linux%20Root%20on
   %20ZFS%20HOWTO:>`__ if it's
   no longer available.

    - `ISO (US mirror) <https://iso.artixlinux.org/iso/artix-base-openrc-20210101-x86_64.iso>`__
    - `Signature <https://iso.artixlinux.org/iso/artix-base-openrc-20210101-x86_64.iso.sig>`__

#. Check live image against signature::

    gpg --auto-key-retrieve --verify artix-base-openrc-20210101-x86_64.iso.sig

   If the file is authentic, output should be the following::

    gpg: Signature made Sun 03 Jan 2021 09:30:42 PM UTC
    gpg:                using RSA key A574A1915CEDE31A3BFF5A68606520ACB886B428
    gpg: Good signature from "Christos Nouskas <nous@artixlinux.org>" [unknown]
    ...
    Primary key fingerprint: A574 A191 5CED E31A 3BFF  5A68 6065 20AC B886 B428

   Ensure ``Good signature`` and last 8 digits are ``B886 B428``,
   as listed on `Artix Linux Download <https://artixlinux.org/download.php>`__ page.

#. Write the image to a USB drive or an optical disc.

#. Boot the target computer from the prepared live medium.

#. At GRUB menu, select "From ISO: artix x86_64".

Prepare the Live Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Connect to the internet.
   If the target computer aquires IP address with DHCP,
   no further steps need to be taken.
   Otherwise, refer to
   `Network Configuration <https://wiki.archlinux.org/index.php/Network_configuration>`__
   wiki page.

#. Become root::

    sudo -i

#. Start SSH server.

   - Interactively set root password with::

      passwd

   - Permit root login with password::

      echo PermitRootLogin yes >> /etc/ssh/sshd_config

   - Start SSH server::

      rc-service sshd start

   - Find the IP address of the target computer::

      ip -4 address show scope global

   - On another computer, connect to the target computer with::

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

   - Edit the following files::

       nano /etc/pacman.d/mirrorlist
       nano /etc/pacman.d/mirrorlist-arch

     Uncomment and move mirrors to
     the beginning of the file.

   - Update database::

       pacman -Sy

#. Install ZFS and tools in the live environment::

     pacman -Sy --noconfirm gdisk dosfstools zfs-dkms glibc

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

   ::

    INST_LINVAR='linux'

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
       sgdisk -n4:0:0   -t4:8308 $DISK

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
      /dev/disk/by-id/ata-disk1-part2 \
      /dev/disk/by-id/ata-disk2-part2

   if needed, replace ``mirror`` with ``raidz1``, ``raidz2`` or ``raidz3``.

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

#. Create root pool::

       zpool create \
        -o ashift=12 \
        -o autotrim=on \
        -R $INST_MNT \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=zstd \
        -O dnodesize=auto \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/ \
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
#. Create system boot container::

    zfs create \
     -o canmount=off \
     -o mountpoint=/boot \
     bpool_$INST_UUID/sys

#. Create system root container:

   Dataset encryption is set at creation and can not be altered later,
   but encrypted dataset can be created inside an unencrypted parent dataset.

   - Unencrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=/ \
       rpool_$INST_UUID/sys

   - Encrypted:

     #. Choose a strong password.

        Once the password is compromised,
        dataset and pool must be destroyed,
        disk wiped and system rebuilt from scratch to protect confidentiality.
        `Merely changing password is not enough <https://openzfs.github.io/openzfs-docs/man/8/zfs-change-key.8.html>`__.

        Example: generate passphrase with `xkcdpass <https://github.com/redacted/XKCD-password-generator>`_::

         pacman -S --noconfirm xkcdpass
         xkcdpass -Vn 10 -w /usr/lib/python*/site-packages/xkcdpass/static/eff-long

        Password can be supplied with SSH at boot time,
        see `Supply password with SSH <#supply-password-with-ssh>`__.

     #. Create dataset::

          zfs create \
           -o canmount=off \
           -o mountpoint=/ \
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
     zfs create -o mountpoint=/      -o canmount=noauto rpool_$INST_UUID/sys/ROOT/default

#. Mount root and boot filesystem datasets::

    zfs mount rpool_$INST_UUID/sys/ROOT/default
    mkdir $INST_MNT/boot
    mount -t zfs bpool_$INST_UUID/sys/BOOT/default $INST_MNT/boot

#. Create datasets to separate user data from root filesystem::

    zfs create -o mountpoint=/ -o canmount=off rpool_$INST_UUID/sys/DATA/default

    for i in {usr,var,var/lib};
    do
        zfs create -o canmount=off rpool_$INST_UUID/sys/DATA/default/$i
    done

    for i in {home,root,srv,usr/local,var/log,var/spool,var/tmp};
    do
        zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/$i
    done

    chmod 750 $INST_MNT/root
    chmod 1777 $INST_MNT/var/tmp

#. Optional user data datasets:

   If this system will have games installed::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/games

   If you use /var/www on this system::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/www

   If this system will use GNOME::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/AccountsService

   If this system will use Docker (which manages its own datasets &
   snapshots)::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/docker

   If this system will use NFS (locking)::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/nfs

   If this system will use Linux Containers::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/lxc

   If this system will use libvirt::

     zfs create -o canmount=on rpool_$INST_UUID/sys/DATA/default/var/lib/libvirt

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

     basestrap $INST_MNT base vi mandoc grub connman connman-openrc openrc elogind-openrc

#. Install kernel headers and zfs-dkms package:

   Check kernel version::

     INST_LINVER=$(pacman -Syi ${INST_LINVAR} | grep Version | awk '{ print $3 }')

   Check zfs-dkms package version::

    DKMS_VER=$(pacman -Si zfs-dkms \
    | grep 'Version' \
    | awk '{ print $3 }' \
    | sed 's|-.*||')

   Visit OpenZFS release page::

    curl -L https://github.com/openzfs/zfs/raw/zfs-${DKMS_VER}/META \
    | grep Linux
    # Linux-Maximum: 5.10
    # Linux-Minimum: 3.10
    # compare with the output of the following command
    echo ${INST_LINVER%%-*}
    # 5.10.17 # supported

   If the kernel is supported:

   - Install zfs-dkms::

       basestrap $INST_MNT zfs-dkms ${INST_LINVAR} ${INST_LINVAR}-headers

   If the kernel is not yet supported, install an older kernel:

   - Check build date::

      DKMS_DATE=$(pacman -Syi zfs-dkms \
      | grep 'Build Date' \
      | sed 's/.*: //' \
      | LC_ALL=C xargs -i{} date -d {} -u +%Y/%m/%d)

   - Check kernel version::

      INST_LINVER=$(curl https://archive.artixlinux.org/repos/${DKMS_DATE}/system/os/x86_64/ \
      | grep \"${INST_LINVAR}-'[0-9]' \
      | grep -v sig \
      | sed "s|.*$INST_LINVAR-||" \
      | sed "s|-x86_64.*||")

   - Install kernel and headers::

       basestrap -U $INST_MNT \
       https://archive.artixlinux.org/packages/l/${INST_LINVAR}/${INST_LINVAR}-${INST_LINVER}-x86_64.pkg.tar.zst \
       https://archive.artixlinux.org/packages/l/${INST_LINVAR}-headers/${INST_LINVAR}-headers-${INST_LINVER}-x86_64.pkg.tar.zst

   - Install zfs-dkms::

       basestrap $INST_MNT zfs-dkms

#. Hold kernel package from updates::

    sed -i 's/#IgnorePkg/IgnorePkg/' $INST_MNT/etc/pacman.conf
    sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers/" $INST_MNT/etc/pacman.conf

   Kernel must be manually updated, see kernel update section in Getting Started.

#. Install firmware::

     pacstrap $INST_MNT linux-firmware intel-ucode amd-ucode

#. If you boot your computer with EFI::

     basestrap $INST_MNT efibootmgr

#. If a swap partition has been created::

     basestrap $INST_MNT cryptsetup
     basestrap $INST_MNT cryptsetup-openrc

#. For other optional packages,
   see `ArchWiki <https://wiki.archlinux.org/index.php/Installation_guide#Installation>`__.

System Configuration
--------------------

#. Generate fstab::

      echo bpool_$INST_UUID/sys/BOOT/default /boot zfs rw,xattr,posixacl 0 0 >> $INST_MNT/etc/fstab
      echo UUID=$(blkid -s UUID -o value ${DISK}-part1) /boot/efi vfat umask=0022,fmask=0022,dmask=0022 0 1 >> $INST_MNT/etc/fstab

   ``tmpfs`` for ``/tmp`` is recommended::

      echo "tmpfs /tmp tmpfs nodev,nosuid 0 0" >> $INST_MNT/etc/fstab

   If a swap partition has been created::

       echo /dev/mapper/crypt-swap none swap defaults 0 0 >> $INST_MNT/etc/fstab
       echo swap=crypt-swap >> $INST_MNT/etc/conf.d/dmcrypt
       echo source=\'${DISK}-part4\' >> $INST_MNT/etc/conf.d/dmcrypt

#. Configure mkinitcpio::

    mv $INST_MNT/etc/mkinitcpio.conf $INST_MNT/etc/mkinitcpio.conf.original

    tee $INST_MNT/etc/mkinitcpio.conf <<EOF
    HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
    EOF

#. Host name::

    echo $INST_HOST > $INST_MNT/etc/hostname

#. Timezone::

    ln -sf $INST_TZ $INST_MNT/etc/localtime
    hwclock --systohc

#. Locale::

    echo "en_US.UTF-8 UTF-8" >> $INST_MNT/etc/locale.gen
    echo "LANG=en_US.UTF-8" >> $INST_MNT/etc/locale.conf

   Other locales should be added after reboot.

#. Chroot::

    artix-chroot $INST_MNT /usr/bin/env  DISK=$DISK INST_UUID=$INST_UUID bash --login

#. If a swap partition has been created,
   enable cryptsetup services for crypt-swap::

    rc-update add device-mapper boot
    rc-update add dmcrypt boot

#. Add and enable ZFS mount service::

    tee /etc/init.d/zfs-mount << 'EOF'
    #!/usr/bin/openrc-run

    start() {
    /usr/bin/zfs mount -a
    }
    EOF

    chmod +x /etc/init.d/zfs-mount

    rc-update add zfs-mount boot

   Other ZFS services, such as ``zed``
   can be ported from ``/usr/lib/systemd/system/zfs*``.

#. Apply locales::

    locale-gen

#. Import keys of archzfs repository::

    curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
    curl -L https://git.io/JtQpl | xargs -i{} pacman-key --lsign-key {}

#. Add archzfs repository::

    tee -a /etc/pacman.conf <<- 'EOF'

    [archzfs]
    Include = /etc/pacman.d/mirrorlist-archzfs
    EOF
    
    curl -L https://git.io/JtQp4 > /etc/pacman.d/mirrorlist-archzfs

#. Enable networking::

    rc-update add connmand default

#. Generate zpool.cache

   Pools are imported by initramfs with the information stored in ``/etc/zfs/zpool.cache``.
   This cache file will be embedded in initramfs.

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

grub-probe fails to get canonical path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When persistent device names ``/dev/disk/by-id/*`` are used
with ZFS, GRUB will fail to resolve the path of the boot pool
device. Error::

  # /usr/bin/grub-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.0-part3'.

Solution::

 echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile
 source /etc/profile

Pool name missing
~~~~~~~~~~~~~~~~~
See `this bug report <https://savannah.gnu.org/bugs/?59614>`__.
Root pool name is missing from ``root=ZFS=rpool/ROOT/default``
in generated ``grub.cfg`` file.

A workaround is to replace the pool name detection with ``zdb``
command::

 sed -i "s|rpool=.*|rpool=\`zdb -l \${GRUB_DEVICE} \| grep -E '[[:blank:]]name' \| cut -d\\\' -f 2\`|"  /etc/grub.d/10_linux

If you forgot to apply this workaround and
followed this guide to use ``rpool_$INST_UUID`` and ``bpool_$INST_UUID``,
``$INST_UUID`` can be found out with `Load grub.cfg in GRUB command line`_.

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
  install to other disks as well::

    for i in {target_disk2,target_disk3}; do
      grub-install /dev/disk/by-id/$i
    done

Generate GRUB Boot Menu
~~~~~~~~~~~~~~~~~~~~~~~

::

   grub-mkconfig -o /boot/grub/grub.cfg

Optional Configuration
----------------------

Supply password with SSH
~~~~~~~~~~~~~~~~~~~~~~~~

Optional:

#. Install mkinitcpio tools::

    pacman -S mkinitcpio-netconf mkinitcpio-dropbear openssh

#. Store authorized keys in ``/etc/dropbear/root_key``::

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

#. Regenerate initramfs::

    mkinitcpio -P

#. Update GRUB menu::

    grub-mkconfig -o /boot/grub/grub.cfg

Finish Installation
-------------------

#. Exit chroot::

    exit

#. Take a snapshot of the clean installation for future use::

    zfs snapshot -r rpool_$INST_UUID/sys/ROOT/default@install
    zfs snapshot -r bpool_$INST_UUID/sys/BOOT/default@install

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

#. Check disk name::

    ls -1 /dev/disk/by-id/ | grep -v '\-part[0-9]'

#. Mirror EFI ssystem partition::

    for i in {target_disk2,target_disk3}; do
     mkfs.vfat /dev/disk/by-id/$i-part1
     mkdir -p /boot/efis/$i
     echo UUID=$(blkid -s UUID -o value /dev/disk/by-id/$i-part1) /boot/efis/$i vfat \
     umask=0022,fmask=0022,dmask=0022 0 1 >> /etc/fstab
     mount /boot/efis/$i
     cp -r /boot/efi/EFI/ /boot/efis/$i
     efibootmgr -cgp 1 -l "\EFI\artix\grubx64.efi" \
     -L "artix-$i" -d /dev/disk/by-id/$i-part1
    done

#. Enable cron and set up cron job to sync EFI system partition contents::

    rc-update add cronie default
    crontab -u root -e
    # @hourly /usr/bin/bash -c 'for i in /boot/efis/*; do /usr/bin/cp -r /boot/efi/EFI/ $i/; done'

   Alternatively, monitor ``/boot/efi/EFI/artix`` with ``inotifywait``.

#. If EFI system partition failed, promote one backup
   to ``/boot/efi`` by editing ``/etc/fstab``.

Mirror BIOS boot sector
~~~~~~~~~~~~~~~~~~~~~~~

This need to be manually applied when GRUB is updated.

#. Check disk name::

    ls -1 /dev/disk/by-id/ | grep -v '\-part[0-9]'

#. Install GRUB to every disk::

    for i in {target_disk2,target_disk3}; do
      grub-install /dev/disk/by-id/$i
    done

Boot Environment Manager
~~~~~~~~~~~~~~~~~~~~~~~~

Optional: install
`rozb3-pac <https://gitlab.com/m_zhou/rozb3-pac/-/releases>`__
pacman hook and
`bieaz <https://gitlab.com/m_zhou/bieaz/-/releases>`__
from AUR to create boot environments.

Prebuilt packages are also available
in the links above.

Post installation
~~~~~~~~~~~~~~~~~
For post installation recommendations,
see `ArchWiki <https://wiki.archlinux.org/index.php/Installation_guide#Post-installation>`__.

Remember to create separate datasets for individual users.

Recovery
--------

Load grub.cfg in GRUB command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Press ``c`` at GRUB menu.

#. List available disks::

     grub > ls (hd # press tab after 'd'
     Possible devices are:

     hd0 hd1

#. List available boot environments::

     grub > ls (hd0,gpt2)/sys/BOOT # press tab after 'T'
     Possible files are:

     @/ default/ pac-multm2/

#. Load grub.cfg::

    grub > configfile (hd0,gpt2)/sys/BOOT/default@/grub/grub.cfg

Rescue in Live Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. `Download Artix Linux live image <#download-artix-linux-live-image>`__.

#. `Prepare the Live Environment <#prepare-the-live-environment>`__.

#. Check the ``INST_UUID`` with ``zpool import``.

#. Set variables::

     INST_MNT=$(mktemp -d)
     INST_UUID=abc123

#. Import and unlock root and boot pool::

     zpool import -N -R $INST_MNT rpool_$INST_UUID
     zpool import -N -R $INST_MNT bpool_$INST_UUID

   If using password::

     zfs load-key rpool_$INST_UUID

#. Find the current boot environment::

     zfs list
     BE=default

#. Mount root filesystem::

     zfs mount rpool_$INST_UUID/sys/ROOT/$BE

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
