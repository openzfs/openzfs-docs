.. highlight:: sh

Ubuntu 20.04 Root on ZFS on external USB for Raspberry Pi
=========================================================

.. contents:: Table of Contents
  :local:

Overview
--------

Caution
~~~~~~~

- This HOWTO uses an external HDD or SSD connected via USB.
- Backup your data. Any existing data will be lost.

System Requirements
~~~~~~~~~~~~~~~~~~~

- A Raspberry Pi 4 B. (If you are looking to install on a regular PC, see
  :doc:`Ubuntu 20.04 Root on ZFS`.)
- `Ubuntu Server 20.04.2 (“Focal”) for Raspberry Pi 4
  <https://cdimage.ubuntu.com/releases/20.04.2/release/ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz>`__
- A microSD card. For recommendations, see Jeff Geerling's `performance
  comparison
  <https://www.jeffgeerling.com/blog/2019/raspberry-pi-microsd-card-performance-comparison-2019>`__.
- An Ubuntu system (with the ability to write to the SD card) other than the
  target Raspberry Pi.
- A USB-to-SATA Bridge ( see `James Achambers Guide <https://jamesachambers.com/new-raspberry-pi-4-bootloader-usb-network-boot-guide>`__ for types that work with Linux).
- Possibly an externally powered USB Hub. ( If using more than one SSD, or an HDD)
- One or more SSD's or HDD's.


4 GiB of memory is recommended. Do not use deduplication, as it needs `massive
amounts of RAM <http://wiki.freebsd.org/ZFSTuningGuide#Deduplication>`__.
Enabling deduplication is a permanent change that cannot be easily reverted.

A Raspberry Pi 3 B/B+ would probably work (as the Pi 3 is 64-bit, though it
has less RAM), but has not been tested.  Please report your results (good or
bad) using the issue link below.

Limitations
~~~~~~~~~~~

Support for an external USB Boot device is rather new. Since Ubuntu 20.04.2 support has been better integrated in Ubuntu (The firmware files do not need to be downloaded seperatly). 
As of right now it is impossible to have a seperate boot pool, as it is used in :doc:`Ubuntu 20.04 Root on ZFS`. 
The Raspberry Pi expects the boot firmware on the first (FAT formatted) partition. 
If you want to operate a Mirror or RaidZ setup, be aware, that this partition should exist on all USB devices and must be mirrored manually!

This guide will first create a ZFS filesystem on the USB devices and then copy the Ubuntu data to it.

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <ircs://irc.libera.chat/#zfsonlinux>`__ on `Libera Chat
<https://libera.chat/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @rlaager and @gador
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager%20and%20@gador,%20I%20have%20the%20following%20issue%20with%20the%20Ubuntu%2020.04%20Root%20on%20ZFS%20for%20Raspberry%20Pi%20HOWTO:>`__.

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

Step 1: Disk Formatting
-----------------------

The overall layout will be:

- Two partitions
  
  - First: Boot partition for the Raspberry Pi, including the firmware.
  - Second: ZFS

This layout will be the same for every connected external USB device. 
The commands in this step can be run from any computer with the USB disks attached. 

#. Download and unpack the official image::

    curl -O https://cdimage.ubuntu.com/releases/20.04.2/release/ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz
    xz -d ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz

    # or combine them to decompress as you download:
    curl https://cdimage.ubuntu.com/releases/20.04.2/release/ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz | \
        xz -d > ubuntu-20.04.2-preinstalled-server-arm64+raspi.img

#. Dump the partition table for the image::

     sfdisk -d ubuntu-20.04.2-preinstalled-server-arm64+raspi.img

   That will output this::

     label: dos
     label-id: 0x4ec8ea53
     device: ubuntu-20.04.2-preinstalled-server-arm64+raspi.img
     unit: sectors
     <name>.img1 : start=        2048, size=      524288, type=c, bootable
     <name>.img2 : start=      526336, size=     5839840, type=83

   The important number is 524288.  Store it in a variable::

     export BOOT=524288

#. Create a partition script::

     vi partitions.sh

   with the following contents:

   .. code-block:: sh

     cat << EOF
     label: dos
     unit: sectors
     
     1 : start=  2048,  size=$BOOT, type=c, bootable
     2 : start=$((2048+BOOT)), type=83
     EOF

#. Connect the external USB device:

   Store the disk label in a variable.::

     DISK=/dev/disk/by-id/ata-....

     # or, if you have multiple disks:
     DISK1=/dev/disk/by-id/ata-....
     DISK2=/dev/disk/by-id/ata-....
  
   For more than one DISK, use DISK1, DISK2 etc. For the subsequent steps, please be aware that all
   steps in formatting need to be done on all external disks you want to use. 

#. Install neccessary software::

    sudo apt install pv zfsutils-linux

#. Clear old ZFS labels::

     sudo zpool labelclear -f ${DISK}

     # or if you have more than one disk:
     sudo zpool labelclear -f ${DISK1}
     sudo zpool labelclear -f ${DISK2}
     # ...

   If a ZFS label still exists from a previous system/attempt, expanding the
   pool will result in an unbootable system. 


#. Delete existing partitions::

     echo "label: dos" | sudo sfdisk ${DISK}
     # or, if you have multiple disks:
     echo "label: dos" | sudo sfdisk ${DISK1}
     echo "label: dos" | sudo sfdisk ${DISK2}
     # ...
     sudo partprobe
     ls ${DISK}*
     # or:
     ls ${DISK1}*
     ls ${DISK2}*

   Make sure there are no partitions, just the file for the disk itself.  This
   step is not strictly necessary; it exists to catch problems. Again, use it on all disks.

#. Create the partitions::

     sh -u partitions.sh | sudo sfdisk $DISK
  
     #For more than one disk, repeat with $DISK1 etc.

#. Loopback mount the image::

     IMG=$(sudo losetup -fP --show \
               ubuntu-20.04.2-preinstalled-server-arm64+raspi.img)

#. Copy the bootloader data on all disks::

     sudo dd if=${IMG}p1 of=${DISK}-part1 bs=1M
     
     # or if you have more than one disk:
     sudo dd if=${IMG}p1 of=${DISK1}-part1 bs=1M
     sudo dd if=${IMG}p1 of=${DISK2}-part1 bs=1M
     # ...

#. Clear old label(s) from partition 2::

     sudo wipefs -a ${DISK}-part2

     # or if you have more than one disk:
     sudo wipefs -a ${DISK1}-part2
     sudo wipefs -a ${DISK2}-part2
     # ...

#. Mount the ubuntu root partiton of the image::

    sudo mkdir /root/hdd
    # mountpoint is not in /mnt because /mnt will be needed later for the ZFS filesystem
    sudo mount ${IMG}p2 /root/hdd/


All formatting steps are done now. Keep the IMG mounted for now and the disks attached.

Step 2: Setup ZFS
-----------------

#. Become root::

     sudo -i

#. Set the variable(s) with the disk name::

    DISK=/dev/disk/by-id/ata-....

    # or, if you have multiple disks:
    DISK1=/dev/disk/by-id/ata-....
    DISK2=/dev/disk/by-id/ata-....

#. Create the root pool:

   Choose one of the following options:

   - Unencrypted::

       zpool create \
           -o ashift=12 \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on -o feature@log_spacemap=disabled \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part2

   **WARNING:** Encryption has not yet been tested on the Raspberry Pi.

   - ZFS native encryption::

       zpool create \
           -o ashift=12 \
           -O encryption=aes-256-gcm \
           -O keylocation=prompt -O keyformat=passphrase \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on -o feature@log_spacemap=disabled \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part2

   - LUKS::

       cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part2
       cryptsetup luksOpen ${DISK}-part4 luks1
       zpool create \
           -o ashift=12 \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on -o feature@log_spacemap=disabled \
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
   - The feature flag ``log_spacemap`` must be disabled, because Ubuntu 20.04.2 cannot boot with it (unsupported flag and it will drop down in initramfs).

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
    
#. Copy the system into the ZFS filesystems::
   
        (cd /root/hdd/; tar -cf - --one-file-system --warning=no-file-ignored .) | \
        pv -p -bs $(du -sxm --apparent-size /root/hdd | cut -f1)m | \
        (cd /mnt ; tar -x)
        umount /root/hdd
   
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
   
#. Bind the virtual filesystems from the running environment to the new ZFS environment and ``chroot`` into it::
   
        # if you have more than one disk, only the firmware partition of the first disk should be mounted
        mount ${DISK}-part1 /mnt/boot/firmware # or use ${DISK1} if you have multiple disks
        mount --rbind /dev  /mnt/dev
        mount --rbind /proc /mnt/proc
        mount --rbind /run  /mnt/run
        mount --rbind /sys  /mnt/sys
        chroot /mnt /usr/bin/env DISK=$DISK UUID=$UUID bash --login
        # or for multiple disks:
        chroot /mnt /usr/bin/env DISK1=$DISK1 DISK2=$DISK2 UUID=$UUID bash --login
   
#. Configure a basic system environment::
   
        apt update
        apt install pv zfs-initramfs
   
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
   
#. Patch a dependency loop:
   
   .. note::

     This has been fixed as of 2021-08-04. Before applying the following patch,
     please check your version of zfs! The patch was applied on ``0.8.3-1ubuntu12.12``.
     You can check the version with ``apt show zfsutils-linux | grep 'Version'``

   
   For ZFS native encryption or LUKS::
   
      curl https://launchpadlibrarian.net/478315221/2150-fix-systemd-dependency-loops.patch | \
        sed "s|/etc|/lib|;s|\.in$||" | (cd / ; sudo patch -p1)
   
   This patch is from `Bug #1875577 Encrypted swap won't load on 20.04 with
   zfs root <https://bugs.launchpad.net/ubuntu/+source/zfs-linux/+bug/1875577>`__.
   
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
   
#. The Raspberry Pi can only boot from external USB devices with a decompressed vmlinux kernel::

      zcat -qf "/boot/firmware/vmlinuz" > "/boot/firmware/vmlinux"

#. Edit the config.txt file to conform to the following content:

   ::

      # Please DO NOT modify this file; if you need to modify the boot config, the
      # usercfg.txt file is the place to include user changes. Please refer to
      # the README file for a description of the various configuration files on
      # the boot partition.
      # The unusual ordering below is deliberate; older firmwares (in particular the
      # version initially shipped with bionic) don't understand the conditional
      # [sections] below and simply ignore them. The Pi4 doesn't boot at all with
      # firmwares this old so it's safe to place at the top. Of the Pi2 and Pi3, the
      # Pi3 uboot happens to work happily on the Pi2, so it needs to go at the bottom
      # to support old firmwares.
      [pi4]
      max_framebuffers=2
      dtoverlay=vc4-fkms-v3d
      boot_delay
      kernel=vmlinux
      initramfs initrd.img followkernel
      [pi2]
      boot_delay
      kernel=vmlinux
      initramfs initrd.img followkernel
      [pi3]
      boot_delay
      kernel=vmlinux
      initramfs initrd.img followkernel
      [all]
      arm_64bit=1
      device_tree_address=0x03000000
      # The following settings are defaults expected to be overridden by the
      # included configuration. The only reason they are included is, again, to
      # support old firmwares which don't understand the include command.
      enable_uart=1
      cmdline=cmdline.txt
      include syscfg.txt
      include usercfg.txt

#. Create auto-update script:

   This script will be run after every upgrade with apt. It checks, whether ``vmlinuz`` changed and will decompress it, if neccessary.

   Patch was adapted from `This github repo <https://github.com/TheRemote/Ubuntu-Server-raspi4-unofficial>`__.

   ::

        # Create script to automatically decompress kernel (source: https://www.raspberrypi.org/forums/viewtopic.php?t=278791)
        cat << \EOF | tee "/boot/firmware/auto_decompress_kernel">/dev/null
        #!/bin/bash -e
        # auto_decompress_kernel script
        BTPATH=/boot/firmware
        CKPATH=$BTPATH/vmlinuz
        DKPATH=$BTPATH/vmlinux
        # Check if compression needs to be done.
        if [ -e $BTPATH/check.md5 ]; then
          if md5sum --status --ignore-missing -c $BTPATH/check.md5; then
              echo -e "\e[32mFiles have not changed, Decompression not needed\e[0m"
              exit 0
          else
              echo -e "\e[31mHash failed, kernel will be compressed\e[0m"
          fi
        fi
        # Backup the old decompressed kernel
        mv $DKPATH $DKPATH.bak
        if [ ! $? == 0 ]; then
          echo -e "\e[31mDECOMPRESSED KERNEL BACKUP FAILED!\e[0m"
          exit 1
        else
          echo -e "\e[32mDecompressed kernel backup was successful\e[0m"
        fi
        # Decompress the new kernel
        echo "Decompressing kernel: "$CKPATH".............."
        zcat -qf $CKPATH > $DKPATH
        if [ ! $? == 0 ]; then
          echo -e "\e[31mKERNEL FAILED TO DECOMPRESS!\e[0m"
          exit 1
        else
          echo -e "\e[32mKernel Decompressed Succesfully\e[0m"
        fi
        # Hash the new kernel for checking
        md5sum $CKPATH $DKPATH > $BTPATH/check.md5
        if [ ! $? == 0 ]; then
          echo -e "\e[31mMD5 GENERATION FAILED!\e[0m"
        else
          echo -e "\e[32mMD5 generated Succesfully\e[0m"
        fi
        exit 0
        EOF
        chmod +x /boot/firmware/auto_decompress_kernel

        
   Call the script after upgrades:

   ::
     
     echo 'DPkg::Post-Invoke {"/bin/bash /boot/firmware/auto_decompress_kernel"; };' |  tee "/etc/apt/apt.conf.d/999_decompress_rpi_kernel" >/dev/null
     chmod +x /etc/apt/apt.conf.d/999_decompress_rpi_kernel

#. Preparing the Raspberry Pi:
   
   We are done with formating the disks and can leave the chroot::

      exit # to exit chroot
      exit # to logout of root
      sudo umount $IMG

   Due to the bind mounts, it is usually requiered to reboot the system to umount all of them::
      
      reboot
  
   After the reboot, the pool must be properly exported::

     zpool export rpool
   
   You can now detach the disks. Start the Raspberry Pi with e.g. `Raspberry Pi OS Lite <https://www.raspberrypi.org/software/operating-systems/>`__. 
   After login, enable USB booting:

   Run ``sudo raspi-conig`` --> Advanced Config (6) --> Boot Order (A6) --> Boot from USB, otherwise SD-Card (B2)
     
   Attach the USB-disk(s) and make sure, the Raspberry Pi recognizes them (Look for new scsi entries in the output of ``dmesg``).

   We can now continue with the first boot from ZFS. Leave the disks attached and reboot.


Step 5: First Boot
------------------

#. Wait for the newly installed system to boot normally. Login as ``ubuntu`` and become root with ``sudo -i``.

#. Create a user account:

   Replace ``username`` with your desired username::

     UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null |
         tr -dc 'a-z0-9' | cut -c-6)
     ROOT_DS=$(zfs list -o name | awk '/ROOT\/ubuntu_/{print $1;exit}')
     zfs create -o com.ubuntu.zsys:bootfs-datasets=$ROOT_DS \
         -o canmount=on -o mountpoint=/home/username \
         rpool/USERDATA/username_$UUID
     adduser username

     cp -a /etc/skel/. /home/username
     chown -R username:username /home/username
     usermod -a -G adm,cdrom,dip,lxd,plugdev,sudo username

#. Reboot::

     reboot

   Wait for the system to boot normally. Login with your username and become
   root with ``sudo -i``.

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

    rm /etc/netplan/50-cloud-init.yaml
    apt purge --autoremove ^cloud-init

#. Optional: Remove other storage packages::

     apt purge --autoremove bcache-tools btrfs-progs cloud-guest-utils lvm2 \
         mdadm multipath-tools open-iscsi overlayroot xfsprogs

#. Upgrade the minimal system::

     apt dist-upgrade --yes

#. Optional: Install a full GUI environment::

     apt install --yes ubuntu-desktop

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

Troubleshooting
---------------

Read errors with attached Disks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For me, the SATA-to-USB Bridge had ocasionally read errors. The system would reset the USB bus and cause read and chksum errors with ZFS.
For refference, this was tested with an Asmedia ASM1153 SATA-to-USB 3.0 converter on the USB 3.0 bus.

Reading `this issue on github <https://github.com/raspberrypi/linux/issues/3404>`__ I became aware of an USB quirk with some SATA-to-USB bridges. 
It is described in more detail `here <https://www.smartmontools.org/wiki/SAT-with-UAS-Linux>`__. I had to add ``usb_storage.quirks=174c:1153:u`` to the
cmdline.txt fine in /boot/firmware. Please note that the device address (here ``174c:1153``) is specific to the USB bridge used.
This causes the system to not use the (slightly faster) ``uas`` driver, but the older ``usb-storage`` driver. It also has the upside
that ``smartmontools`` work now, too. 

This reduced the ammount of read-errors, but they did still occur. From the issue linked above, other users reported that ``over_voltage=1`` added to 
``/boot/firmware/config.txt`` helped, too. I can confirm that. My complete working ``cmdline.txt`` is::

    net.ifnames=0 dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=ZFS=rpool/ROOT/ubuntu_abczkd elevator=deadline rootwait init_on_alloc=0 nosplash usb_storage.quirks=174c:1153:u

Drop to initramfs
~~~~~~~~~~~~~~~~~

This can have multiple reasons. Here are a few:

- ZFS not installed to initramfs

   When on the initramfs bootprompt, check whether zfs is installed by typing ``zpool status``. If it cannot find the binary, 
   you need to chroot in the enviroment again and install ``zfs-initramfs``

- Pool not imported

   When the pool was not exported before, zfs will not automatically import the pool. Run ``zpool import -f rpool`` and reboot. 
   Ubuntu should start now.

- Can't find root filesystem

   Make sure, that the ``UUID`` in the cmdline.txt file matches the zfs filesystem. If neccessary, correct the line im cmdline.txt and reboot.


It is always possible to detach the USB devices. The Raspberry Pi will then boot from the SD-card again. 





