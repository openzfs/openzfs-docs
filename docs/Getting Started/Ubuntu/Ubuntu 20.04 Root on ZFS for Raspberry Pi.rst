.. highlight:: sh

Ubuntu 20.04 Root on ZFS for Raspberry Pi
=========================================

.. contents:: Table of Contents
  :local:

Overview
--------

Caution
~~~~~~~

- This HOWTO uses a whole physical disk.
- Backup your data. Any existing data will be lost.

System Requirements
~~~~~~~~~~~~~~~~~~~

- A Raspberry Pi 4 B. (If you are looking to install on a regular PC, see
  :doc:`Ubuntu 20.04 Root on ZFS`.)
- `Ubuntu Server 20.04.3 (“Focal”) for Raspberry Pi 4
  <https://cdimage.ubuntu.com/releases/20.04.3/release/ubuntu-20.04.3-preinstalled-server-arm64+raspi.img.xz>`__
- A microSD card or USB disk. For microSD card recommendations, see Jeff
  Geerling's `performance comparison
  <https://www.jeffgeerling.com/blog/2019/raspberry-pi-microsd-card-performance-comparison-2019>`__.
  When using a USB enclosure, `ensure it supports UASP
  <https://github.com/geerlingguy/turing-pi-cluster/issues/11#issuecomment-647726561>`__.
- An Ubuntu system (with the ability to write to the microSD card or USB disk)
  other than the target Raspberry Pi.

4 GiB of memory is recommended. Do not use deduplication, as it needs `massive
amounts of RAM <http://wiki.freebsd.org/ZFSTuningGuide#Deduplication>`__.
Enabling deduplication is a permanent change that cannot be easily reverted.

A Raspberry Pi 3 B/B+ would probably work (as the Pi 3 is 64-bit, though it
has less RAM), but has not been tested.  Please report your results (good or
bad) using the issue link below.

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <ircs://irc.libera.chat/#zfsonlinux>`__ on `Libera Chat
<https://libera.chat/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @rlaager
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Ubuntu%2020.04%20Root%20on%20ZFS%20for%20Raspberry%20Pi%20HOWTO:>`__.

Contributing
~~~~~~~~~~~~

#. Fork and clone: https://github.com/openzfs/openzfs-docs

#. Install the tools::

    sudo apt install python3-pip

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

**WARNING:** Encryption has not yet been tested on the Raspberry Pi.

This guide supports three different encryption options: unencrypted, ZFS
native encryption, and LUKS. With any option, all ZFS features are fully
available.

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

LUKS encrypts almost everything. The only unencrypted data is the bootloader,
kernel, and initrd. The system cannot boot without the passphrase being
entered at the console. Performance is good, but LUKS sits underneath ZFS, so
if multiple disks (mirror or raidz topologies) are used, the data has to be
encrypted once per disk.

USB Disks
~~~~~~~~~

The Raspberry Pi 4 runs much faster using a USB Solid State Drive (SSD) than
a microSD card. These instructions can also be used to install Ubuntu on a
USB-connected SSD or other USB disk. USB disks have three requirements that
do not apply to microSD cards:

#. The Raspberry Pi's Bootloader EEPROM must be dated 2020-09-03 or later.

   To check the bootloader version, power up the Raspberry Pi without an SD
   card inserted or a USB boot device attached; the date will be on the
   ``bootloader`` line. (If you do not see the ``bootloader`` line, the
   bootloader is too old.) Alternatively, run ``sudo rpi-eeprom-update``
   on an existing OS on the Raspberry Pi (which on Ubuntu requires
   ``apt install rpi-eeprom``).

   If needed, the bootloader can be updated from an existing OS on the
   Raspberry Pi using ``rpi-eeprom-update -a`` and rebooting.
   For other options, see `Updating the Bootloader
   <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#updating-the-bootloader>`_.

#. The Raspberry Pi must configured for USB boot. The bootloader will show a
   ``boot`` line; if ``order`` includes ``4``, USB boot is enabled.

   If not already enabled, it can be enabled from an existing OS on the
   Raspberry Pi using ``rpi-eeprom-config -e``: set ``BOOT_ORDER=0xf41``
   and reboot to apply the change. On subsequent reboots, USB boot will be
   enabled.

   Otherwise, it can be enabled without an existing OS as follows:

   - Download the `Raspberry Pi Imager Utility
     <https://www.raspberrypi.com/news/raspberry-pi-imager-imaging-utility/>`_.
   - Flash the ``USB Boot`` image to a microSD card. The ``USB Boot`` image is
     listed under ``Bootload`` in the ``Misc utility images`` folder.
   - Boot the Raspberry Pi from the microSD card. USB Boot should be enabled
     automatically.

#. U-Boot on Ubuntu 20.04 does not seem to support the Raspberry Pi USB.
   `Ubuntu 20.10 may work
   <https://forums.raspberrypi.com/viewtopic.php?t=295609>`_.  As a
   work-around, the Raspberry Pi bootloader is configured to directly boot
   Linux.  For this to work, the Linux kernel must not be compressed. These
   instructions decompress the kernel and add a script to
   ``/etc/kernel/postinst.d`` to handle kernel upgrades.

Step 1: Disk Formatting
-----------------------

The commands in this step are run on the system other than the Raspberry Pi.

This guide has you go to some extra work so that the stock ext4 partition can
be deleted.

#. Download and unpack the official image::

    curl -O https://cdimage.ubuntu.com/releases/20.04.3/release/ubuntu-20.04.3-preinstalled-server-arm64+raspi.img.xz
    xz -d ubuntu-20.04.3-preinstalled-server-arm64+raspi.img.xz

    # or combine them to decompress as you download:
    curl https://cdimage.ubuntu.com/releases/20.04.3/release/ubuntu-20.04.3-preinstalled-server-arm64+raspi.img.xz | \
        xz -d > ubuntu-20.04.3-preinstalled-server-arm64+raspi.img

#. Dump the partition table for the image::

     sfdisk -d ubuntu-20.04.3-preinstalled-server-arm64+raspi.img

   That will output this::

     label: dos
     label-id: 0xf66f0719
     device: ubuntu-20.04.3-preinstalled-server-arm64+raspi.img
     unit: sectors
     <name>.img1 : start=        2048, size=      524288, type=c, bootable
     <name>.img2 : start=      526336, size=     6052348, type=83

   The important numbers are 524288 and 6052348.  Store those in variables::

     BOOT=524288
     ROOT=6052348

#. Create a partition script::

     cat > partitions << EOF
     label: dos
     unit: sectors

     1 : start=  2048,  size=$BOOT,  type=c, bootable
     2 : start=$((2048+BOOT)),  size=$ROOT, type=83
     3 : start=$((2048+BOOT+ROOT)), size=$ROOT, type=83
     EOF

#. Connect the disk:

   Connect the disk to a machine other than the target Raspberry Pi.  If any
   filesystems are automatically mounted (e.g. by GNOME) unmount them.
   Determine the device name. For SD, the device name is almost certainly
   ``/dev/mmcblk0``. For USB SSDs, the device name is ``/dev/sdX``, where
   ``X`` is a lowercase letter. ``lsblk`` can help determine the device name.
   Set the ``DISK`` environment variable to the device name::

     DISK=/dev/mmcblk0    # microSD card
     DISK=/dev/sdX        # USB disk

   Because partitions are named differently for ``/dev/mmcblk0`` and ``/dev/sdX``
   devices, set a second variable used when working with partitions::

     export DISKP=${DISK}p # microSD card
     export DISKP=${DISK}  # USB disk ($DISKP == $DISK for /dev/sdX devices)

   **Hint**: microSD cards connected using a USB reader also have ``/dev/sdX``
   names.

   **WARNING**: The following steps destroy the existing data on the disk. Ensure
   ``DISK`` and ``DISKP`` are correct before proceeding.

#. Ensure swap partitions are not in use::

     swapon -v
     # If a partition is in use from the disk, disable it:
     sudo swapoff THAT_PARTITION

#. Clear old ZFS labels::

     sudo zpool labelclear -f ${DISK}

   If a ZFS label still exists from a previous system/attempt, expanding the
   pool will result in an unbootable system.

   **Hint:** If you do not already have the ZFS utilities installed, you can
   install them with: ``sudo apt install zfsutils-linux``  Alternatively, you
   can zero the entire disk with:
   ``sudo dd if=/dev/zero of=${DISK} bs=1M status=progress``

#. Delete existing partitions::

     echo "label: dos" | sudo sfdisk ${DISK}
     sudo partprobe
     ls ${DISKP}*

   Make sure there are no partitions, just the file for the disk itself.  This
   step is not strictly necessary; it exists to catch problems.

#. Create the partitions::

     sudo sfdisk $DISK < partitions

#. Loopback mount the image::

     IMG=$(sudo losetup -fP --show \
               ubuntu-20.04.3-preinstalled-server-arm64+raspi.img)

#. Copy the bootloader data::

     sudo dd if=${IMG}p1 of=${DISKP}1 bs=1M

#. Clear old label(s) from partition 2::

     sudo wipefs -a ${DISKP}2

   If a filesystem with the ``writable`` label from the Ubuntu image is still
   present in partition 2, the system will not boot initially.

#. Copy the root filesystem data::

     # NOTE: the destination is p3, not p2.
     sudo dd if=${IMG}p2 of=${DISKP}3 bs=1M status=progress conv=fsync

#. Unmount the image::

     sudo losetup -d $IMG

#. If setting up a USB disk:

   Decompress the kernel::

     sudo -sE

     MNT=$(mktemp -d /mnt/XXXXXXXX)
     mkdir -p $MNT/boot $MNT/root
     mount ${DISKP}1 $MNT/boot
     mount ${DISKP}3 $MNT/root

     zcat -qf $MNT/boot/vmlinuz >$MNT/boot/vmlinux

   Modify boot config::

     cat >> $MNT/boot/usercfg.txt << EOF
     kernel=vmlinux
     initramfs initrd.img followkernel
     boot_delay
     EOF

   Create a script to automatically decompress the kernel after an upgrade::

     cat >$MNT/root/etc/kernel/postinst.d/zz-decompress-kernel << 'EOF'
     #!/bin/sh

     set -eu

     echo "Updating decompressed kernel..."
     [ -e /boot/firmware/vmlinux ] && \
         cp /boot/firmware/vmlinux /boot/firmware/vmlinux.bak
     vmlinuxtmp=$(mktemp /boot/firmware/vmlinux.XXXXXXXX)
     zcat -qf /boot/vmlinuz > "$vmlinuxtmp"
     mv "$vmlinuxtmp" /boot/firmware/vmlinux
     EOF

     chmod +x $MNT/root/etc/kernel/postinst.d/zz-decompress-kernel

   Cleanup::

     umount $MNT/*
     rm -rf $MNT
     exit

#. Boot the Raspberry Pi.

   Move the SD/USB disk to the Raspberry Pi. Boot it and login (e.g. via SSH)
   with ``ubuntu`` as the username and password.  If you are using SSH, note
   that it takes a little bit for cloud-init to enable password logins on the
   first boot.  Set a new password when prompted and login again using that
   password.  If you have your local SSH configured to use ``ControlPersist``,
   you will have to kill the existing SSH process before logging in the second
   time.

Step 2: Setup ZFS
-----------------

#. Become root::

     sudo -i

#. Set the DISK and DISKP variables again::

     DISK=/dev/mmcblk0    # microSD card
     DISKP=${DISK}p       # microSD card

     DISK=/dev/sdX        # USB disk
     DISKP=${DISK}        # USB disk

   **WARNING:** Device names can change when moving a device to a different
   computer or switching the microSD card from a USB reader to a built-in
   slot. Double check the device name before continuing.

#. Install ZFS::

     apt update

     apt install pv zfs-initramfs

   **Note:** Since this is the first boot, you may get ``Waiting for cache
   lock`` because ``unattended-upgrades`` is running in the background.
   Wait for it to finish.

#. Create the root pool:

   Choose one of the following options:

   - Unencrypted::

       zpool create \
           -o ashift=12 \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISKP}2

   **WARNING:** Encryption has not yet been tested on the Raspberry Pi.

   - ZFS native encryption::

       zpool create \
           -o ashift=12 \
           -O encryption=aes-256-gcm \
           -O keylocation=prompt -O keyformat=passphrase \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISKP}2

   - LUKS::

       cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISKP}2
       cryptsetup luksOpen ${DISK}-part4 luks1
       zpool create \
           -o ashift=12 \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool /dev/mapper/luks1

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
     Also, `disabling ACLs apparently breaks umask handling with NFSv4
     <https://bugs.launchpad.net/ubuntu/+source/nfs-utils/+bug/1779736>`__.
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
   - Make sure to include the ``-part4`` portion of the drive path. If you
     forget that, you are specifying the whole disk, which ZFS will then
     re-partition, and you will lose the bootloader partition(s).
   - ZFS native encryption defaults to ``aes-256-ccm``, but `the default has
     changed upstream
     <https://github.com/openzfs/zfs/commit/31b160f0a6c673c8f926233af2ed6d5354808393>`__
     to ``aes-256-gcm``. `AES-GCM seems to be generally preferred over AES-CCM
     <https://crypto.stackexchange.com/questions/6842/how-to-choose-between-aes-ccm-and-aes-gcm-for-storage-volume-encryption>`__,
     `is faster now
     <https://github.com/zfsonlinux/zfs/pull/9749#issuecomment-569132997>`__,
     and `will be even faster in the future
     <https://github.com/zfsonlinux/zfs/pull/9749>`__.
   - For LUKS, the key size chosen is 512 bits. However, XTS mode requires two
     keys, so the LUKS key is split in half. Thus, ``-s 512`` means AES-256.
   - Your passphrase will likely be the weakest link. Choose wisely. See
     `section 5 of the cryptsetup FAQ
     <https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions#5-security-aspects>`__
     for guidance.

Step 3: System Installation
---------------------------

#. Create a filesystem dataset to act as a container::

     zfs create -o canmount=off -o mountpoint=none rpool/ROOT

#. Create a filesystem dataset for the root filesystem::

     UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null |
         tr -dc 'a-z0-9' | cut -c-6)

     zfs create -o canmount=noauto -o mountpoint=/ \
         -o com.ubuntu.zsys:bootfs=yes \
         -o com.ubuntu.zsys:last-used=$(date +%s) rpool/ROOT/ubuntu_$UUID
     zfs mount rpool/ROOT/ubuntu_$UUID

   With ZFS, it is not normally necessary to use a mount command (either
   ``mount`` or ``zfs mount``). This situation is an exception because of
   ``canmount=noauto``.

#. Create datasets::

     zfs create -o com.ubuntu.zsys:bootfs=no \
         rpool/ROOT/ubuntu_$UUID/srv
     zfs create -o com.ubuntu.zsys:bootfs=no -o canmount=off \
         rpool/ROOT/ubuntu_$UUID/usr
     zfs create rpool/ROOT/ubuntu_$UUID/usr/local
     zfs create -o com.ubuntu.zsys:bootfs=no -o canmount=off \
         rpool/ROOT/ubuntu_$UUID/var
     zfs create rpool/ROOT/ubuntu_$UUID/var/games
     zfs create rpool/ROOT/ubuntu_$UUID/var/lib
     zfs create rpool/ROOT/ubuntu_$UUID/var/lib/AccountsService
     zfs create rpool/ROOT/ubuntu_$UUID/var/lib/apt
     zfs create rpool/ROOT/ubuntu_$UUID/var/lib/dpkg
     zfs create rpool/ROOT/ubuntu_$UUID/var/lib/NetworkManager
     zfs create rpool/ROOT/ubuntu_$UUID/var/log
     zfs create rpool/ROOT/ubuntu_$UUID/var/mail
     zfs create rpool/ROOT/ubuntu_$UUID/var/snap
     zfs create rpool/ROOT/ubuntu_$UUID/var/spool
     zfs create rpool/ROOT/ubuntu_$UUID/var/www

     zfs create -o canmount=off -o mountpoint=/ \
         rpool/USERDATA
     zfs create -o com.ubuntu.zsys:bootfs-datasets=rpool/ROOT/ubuntu_$UUID \
         -o canmount=on -o mountpoint=/root \
         rpool/USERDATA/root_$UUID

   If you want a separate dataset for ``/tmp``::

     zfs create -o com.ubuntu.zsys:bootfs=no \
         rpool/ROOT/ubuntu_$UUID/tmp
     chmod 1777 /mnt/tmp

   The primary goal of this dataset layout is to separate the OS from user
   data. This allows the root filesystem to be rolled back without rolling
   back user data.

   If you do nothing extra, ``/tmp`` will be stored as part of the root
   filesystem. Alternatively, you can create a separate dataset for ``/tmp``,
   as shown above. This keeps the ``/tmp`` data out of snapshots of your root
   filesystem. It also allows you to set a quota on ``rpool/tmp``, if you want
   to limit the maximum space used. Otherwise, you can use a tmpfs (RAM
   filesystem) later.

#. Optional: Ignore synchronous requests:

   microSD cards are relatively slow.  If you want to increase performance
   (especially when installing packages) at the cost of some safety, you can
   disable flushing of synchronous requests (e.g. ``fsync()``, ``O_[D]SYNC``):

   Choose one of the following options:

   - For the root filesystem, but not user data::

       zfs set sync=disabled rpool/ROOT

   - For everything::

       zfs set sync=disabled rpool

   ZFS is transactional, so it will still be crash consistent.  However, you
   should leave ``sync`` at its default of ``standard`` if this system needs
   to guarantee persistence (e.g. if it is a database or NFS server).

#. Copy the system into the ZFS filesystems::

     (cd /; tar -cf - --one-file-system --warning=no-file-ignored .) | \
         pv -p -bs $(du -sxm --apparent-size / | cut -f1)m | \
         (cd /mnt ; tar -x)

Step 4: System Configuration
----------------------------

#. Configure the hostname:

   Replace ``HOSTNAME`` with the desired hostname::

     echo HOSTNAME > /mnt/etc/hostname
     vi /mnt/etc/hosts

   .. code-block:: text

     Add a line:
     127.0.1.1       HOSTNAME
     or if the system has a real name in DNS:
     127.0.1.1       FQDN HOSTNAME

   **Hint:** Use ``nano`` if you find ``vi`` confusing.

#. Stop ``zed``::

     systemctl stop zed

#. Bind the virtual filesystems from the running environment to the new
   ZFS environment and ``chroot`` into it::

     mount --rbind /boot/firmware /mnt/boot/firmware
     mount --rbind /dev  /mnt/dev
     mount --rbind /proc /mnt/proc
     mount --rbind /run  /mnt/run
     mount --rbind /sys  /mnt/sys
     chroot /mnt /usr/bin/env DISK=$DISK UUID=$UUID bash --login

#. Configure a basic system environment::

     apt update

   Even if you prefer a non-English system language, always ensure that
   ``en_US.UTF-8`` is available::

     dpkg-reconfigure locales
     dpkg-reconfigure tzdata

#. For LUKS installs only, setup ``/etc/crypttab``::

     # cryptsetup is already installed, but this marks it as manually
     # installed so it is not automatically removed.
     apt install --yes cryptsetup

     echo luks1 UUID=$(blkid -s UUID -o value ${DISK}-part4) none \
         luks,discard,initramfs > /etc/crypttab

   The use of ``initramfs`` is a work-around for `cryptsetup does not support
   ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

#. Optional: Mount a tmpfs to ``/tmp``

   If you chose to create a ``/tmp`` dataset above, skip this step, as they
   are mutually exclusive choices. Otherwise, you can put ``/tmp`` on a
   tmpfs (RAM filesystem) by enabling the ``tmp.mount`` unit.

   ::

     cp /usr/share/systemd/tmp.mount /etc/systemd/system/
     systemctl enable tmp.mount

#. Setup system groups::

     addgroup --system lpadmin
     addgroup --system sambashare

#. Patch a dependency loop:

   For ZFS native encryption or LUKS::

     apt install --yes curl patch

     curl https://launchpadlibrarian.net/478315221/2150-fix-systemd-dependency-loops.patch | \
         sed "s|/etc|/lib|;s|\.in$||" | (cd / ; patch -p1)

   Ignore the failure in Hunk #2 (say ``n`` twice).

   This patch is from `Bug #1875577 Encrypted swap won't load on 20.04 with
   zfs root
   <https://bugs.launchpad.net/ubuntu/+source/zfs-linux/+bug/1875577>`__.

#. Fix filesystem mount ordering:

   We need to activate ``zfs-mount-generator``. This makes systemd aware of
   the separate mountpoints, which is important for things like ``/var/log``
   and ``/var/tmp``. In turn, ``rsyslog.service`` depends on ``var-log.mount``
   by way of ``local-fs.target`` and services using the ``PrivateTmp`` feature
   of systemd automatically use ``After=var-tmp.mount``.

   ::

     mkdir /etc/zfs/zfs-list.cache
     touch /etc/zfs/zfs-list.cache/rpool
     ln -s /usr/lib/zfs-linux/zed.d/history_event-zfs-list-cacher.sh /etc/zfs/zed.d
     zed -F &

   Force a cache update::

     zfs set canmount=noauto rpool/ROOT/ubuntu_$UUID

   Verify that ``zed`` updated the cache by making sure this is not empty,
   which will take a few seconds::

     cat /etc/zfs/zfs-list.cache/rpool

   Stop ``zed``::

     fg
     Press Ctrl-C.

   Fix the paths to eliminate ``/mnt``::

     sed -Ei "s|/mnt/?|/|" /etc/zfs/zfs-list.cache/*

#. Remove old filesystem from ``/etc/fstab``::

     vi /etc/fstab
     # Remove the old root filesystem line:
     #   LABEL=writable / ext4 ...

#. Configure kernel command line::

     cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.bak
     sed -i "s|root=LABEL=writable rootfstype=ext4|root=ZFS=rpool/ROOT/ubuntu_$UUID|" \
         /boot/firmware/cmdline.txt
     sed -i "s| fixrtc||" /boot/firmware/cmdline.txt
     sed -i "s|$| init_on_alloc=0|" /boot/firmware/cmdline.txt

   The ``fixrtc`` script is not compatible with ZFS and will cause the boot
   to hang for 180 seconds.

   The ``init_on_alloc=0`` is to address `performance regressions
   <https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1862822>`__.

#. Optional (but highly recommended): Make debugging booting easier::

     sed -i "s|$| nosplash|" /boot/firmware/cmdline.txt

#. Reboot::

     exit
     reboot

   Wait for the newly installed system to boot normally. Login as ``ubuntu``.

Step 5: First Boot
------------------

#. Become root::

     sudo -i

#. Set the DISK variable again::

     DISK=/dev/mmcblk0    # microSD card

     DISK=/dev/sdX        # USB disk

#. Delete the ext4 partition and expand the ZFS partition::

     sfdisk $DISK --delete 3
     echo ", +" | sfdisk --no-reread -N 2 $DISK

   **Note:** This does not automatically expand the pool.  That will be happen
   on reboot.

#. Create a user account:

   Replace ``YOUR_USERNAME`` with your desired username::

     username=YOUR_USERNAME

     UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null |
         tr -dc 'a-z0-9' | cut -c-6)
     ROOT_DS=$(zfs list -o name | awk '/ROOT\/ubuntu_/{print $1;exit}')
     zfs create -o com.ubuntu.zsys:bootfs-datasets=$ROOT_DS \
         -o canmount=on -o mountpoint=/home/$username \
         rpool/USERDATA/${username}_$UUID
     adduser $username

     cp -a /etc/skel/. /home/$username
     chown -R $username:$username /home/$username
     usermod -a -G adm,cdrom,dip,lpadmin,lxd,plugdev,sambashare,sudo $username

#. Reboot::

     reboot

   Wait for the system to boot normally. Login using the account you
   created.

#. Become root::

     sudo -i

#. Expand the ZFS pool:

   Verify the pool expanded::

     zfs list rpool

   If it did not automatically expand, try to expand it manually::

     DISK=/dev/mmcblk0    # microSD card
     DISKP=${DISK}p       # microSD card

     DISK=/dev/sdX        # USB disk
     DISKP=${DISK}        # USB disk

     zpool online -e rpool ${DISKP}2

#. Delete the ``ubuntu`` user::

    deluser --remove-home ubuntu

Step 6: Full Software Installation
----------------------------------

#. Optional: Remove cloud-init::

    vi /etc/netplan/01-netcfg.yaml

   .. code-block:: yaml

    network:
      version: 2
      ethernets:
        eth0:
          dhcp4: true

   ::

    rm /etc/netplan/50-cloud-init.yaml
    apt purge --autoremove ^cloud-init
    rm -rf /etc/cloud

#. Optional: Remove other storage packages::

     apt purge --autoremove bcache-tools btrfs-progs cloud-guest-utils lvm2 \
         mdadm multipath-tools open-iscsi overlayroot xfsprogs

#. Upgrade the minimal system::

     apt dist-upgrade --yes

#. Optional: Install a full GUI environment::

     apt install --yes ubuntu-desktop
     echo dtoverlay=vc4-fkms-v3d >> /boot/firmware/usercfg.txt

   **Hint**: If you are installing a full GUI environment, you will likely
   want to remove cloud-init as discussed above but manage your network with
   NetworkManager::

     rm /etc/netplan/*.yaml
     vi /etc/netplan/01-network-manager-all.yaml

   .. code-block:: yaml

     network:
       version: 2
       renderer: NetworkManager

#. Optional (but recommended): Disable log compression:

   As ``/var/log`` is already compressed by ZFS, logrotate’s compression is
   going to burn CPU and disk I/O for (in most cases) very little gain. Also,
   if you are making snapshots of ``/var/log``, logrotate’s compression will
   actually waste space, as the uncompressed data will live on in the
   snapshot. You can edit the files in ``/etc/logrotate.d`` by hand to comment
   out ``compress``, or use this loop (copy-and-paste highly recommended)::

     for file in /etc/logrotate.d/* ; do
         if grep -Eq "(^|[^#y])compress" "$file" ; then
             sed -i -r "s/(^|[^#y])(compress)/\1#\2/" "$file"
         fi
     done

#. Reboot::

     reboot

Step 7: Final Cleanup
---------------------

#. Wait for the system to boot normally. Login using the account you
   created. Ensure the system (including networking) works normally.

#. Optional: For LUKS installs only, backup the LUKS header::

     sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
         --header-backup-file luks1-header.dat

   Store that backup somewhere safe (e.g. cloud storage). It is protected by
   your LUKS passphrase, but you may wish to use additional encryption.

   **Hint:** If you created a mirror or raidz topology, repeat this for each
   LUKS volume (``luks2``, etc.).
