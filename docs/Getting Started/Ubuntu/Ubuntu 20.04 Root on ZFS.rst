.. highlight:: sh

Ubuntu 20.04 Root on ZFS
========================

.. contents:: Table of Contents
  :local:

Errata
------

If you previously installed using this guide, please apply these fixes if
applicable:

/boot/grub Not Mounted
~~~~~~~~~~~~~~~~~~~~~~

| **Severity:** Normal (previously Grave)
| **Fixed:** 2020-12-05 (previously 2020-05-30)

For a mirror or raidz topology, ``/boot/grub`` is on a separate dataset. This
was originally ``bpool/grub``, then changed on 2020-05-30 to
``bpool/BOOT/ubuntu_UUID/grub`` to work-around zsys setting ``canmount=off``
which would result in ``/boot/grub`` not mounting.  This work-around lead to
`issues with snapshot restores
<https://github.com/openzfs/openzfs-docs/issues/55>`__.  The underlying `zsys
issue <https://github.com/ubuntu/zsys/issues/164>`__ was fixed and backported
to 20.04, so it is now back to being ``bpool/grub``.

* If you never applied the 2020-05-30 errata fix, then ``/boot/grub`` is
  probably not mounting.  Check that::

    mount | grep /boot/grub

  If it is mounted, everything is fine. Stop. Otherwise::

    zfs set canmount=on bpool/boot/grub
    update-initramfs -c -k all
    update-grub

    grub-install --target=x86_64-efi --efi-directory=/boot/efi \
        --bootloader-id=ubuntu --recheck --no-floppy

  Run this for the additional disk(s), incrementing the “2” to “3” and so on
  for both ``/boot/efi2`` and ``ubuntu-2``::

    cp -a /boot/efi/EFI /boot/efi2
    grub-install --target=x86_64-efi --efi-directory=/boot/efi2 \
        --bootloader-id=ubuntu-2 --recheck --no-floppy

  Check that these have ``set prefix=($root)'/BOOT/ubuntu_UUID/grub@'``::

    grep prefix= \
        /boot/efi/EFI/ubuntu/grub.cfg \
        /boot/efi2/EFI/ubuntu-2/grub.cfg

* If you applied the 2020-05-30 errata fix, then you should revert the dataset
  rename::

    umount /boot/grub
    zfs rename bpool/BOOT/ubuntu_UUID/grub bpool/grub
    zfs set com.ubuntu.zsys:bootfs=no bpool/grub
    zfs mount bpool/grub

AccountsService Not Mounted
~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Severity:** Normal
| **Fixed:** 2020-05-28

The HOWTO previously had a typo in AccountsService (where Accounts is plural)
as AccountServices (where Services is plural). This means that AccountsService
data will be written to the root filesystem. This is only harmful in the event
of a rollback of the root filesystem that does not include a rollback of the
user data. Check it::

  zfs list | grep Account

If the “s” is on “Accounts”, you are good. If it is on “Services”, fix it::

  mv /var/lib/AccountsService /var/lib/AccountsService-old
  zfs list -r rpool
  # Replace the UUID twice below:
  zfs rename rpool/ROOT/ubuntu_UUID/var/lib/AccountServices \
             rpool/ROOT/ubuntu_UUID/var/lib/AccountsService
  mv /var/lib/AccountsService-old/* /var/lib/AccountsService
  rmdir /var/lib/AccountsService-old

Overview
--------

Ubuntu Installer
~~~~~~~~~~~~~~~~

The Ubuntu installer has `support for root-on-ZFS
<https://arstechnica.com/gadgets/2020/03/ubuntu-20-04s-zsys-adds-zfs-snapshots-to-package-management/>`__.
This HOWTO produces nearly identical results as the Ubuntu installer because of
`bidirectional collaboration
<https://ubuntu.com/blog/enhancing-our-zfs-support-on-ubuntu-19-10-an-introduction>`__.

If you want a single-disk, unencrypted, desktop install, use the installer. It
is far easier and faster than doing everything by hand.

If you want a ZFS native encrypted, desktop install, you can `trivially edit
the installer
<https://linsomniac.gitlab.io/post/2020-04-09-ubuntu-2004-encrypted-zfs/>`__.
The ``-o recordsize=1M`` there is unrelated to encryption; omit that unless
you understand it. Make sure to use a password that is at least 8 characters
or this hack will crash the installer. Additionally, once the system is
installed, you should switch to encrypted swap::

  swapon -v
  # Note the device, including the partition.

  ls -l /dev/disk/by-id/
  # Find the by-id name of the disk.

  sudo swapoff -a
  sudo vi /etc/fstab
  # Remove the swap entry.

  sudo apt install --yes cryptsetup curl patch

  curl https://launchpadlibrarian.net/478315221/2150-fix-systemd-dependency-loops.patch | \
      sed "s|/etc|/lib|;s|\.in$||" | (cd / ; sudo patch -p1)

  # Replace DISK-partN as appropriate from above:
  echo swap /dev/disk/by-id/DISK-partN /dev/urandom \
      swap,cipher=aes-xts-plain64:sha256,size=512 | sudo tee -a /etc/crypttab
  echo /dev/mapper/swap none swap defaults 0 0 | sudo tee -a /etc/fstab

`Hopefully the installer will gain encryption support in
the future
<https://bugs.launchpad.net/ubuntu/+source/ubiquity/+bug/1857398>`__.

If you want to setup a mirror or raidz topology, use LUKS encryption, and/or
install a server (no desktop GUI), use this HOWTO.

Raspberry Pi
~~~~~~~~~~~~

If you are looking to install on a Raspberry Pi, see
:doc:`Ubuntu 20.04 Root on ZFS for Raspberry Pi`.

Caution
~~~~~~~

- This HOWTO uses a whole physical disk.
- Do not use these instructions for dual-booting.
- Backup your data. Any existing data will be lost.

System Requirements
~~~~~~~~~~~~~~~~~~~

- `Ubuntu 20.04.2 (“Focal”) Desktop CD
  <https://releases.ubuntu.com/20.04/ubuntu-20.04.2-desktop-amd64.iso>`__
  (*not* any server images)
- Installing on a drive which presents 4 KiB logical sectors (a “4Kn” drive)
  only works with UEFI booting. This not unique to ZFS. `GRUB does not and
  will not work on 4Kn with legacy (BIOS) booting.
  <http://savannah.gnu.org/bugs/?46700>`__

Computers that have less than 2 GiB of memory run ZFS slowly. 4 GiB of memory
is recommended for normal performance in basic workloads. If you wish to use
deduplication, you will need `massive amounts of RAM
<http://wiki.freebsd.org/ZFSTuningGuide#Deduplication>`__. Enabling
deduplication is a permanent change that cannot be easily reverted.

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <ircs://irc.libera.chat/#zfsonlinux>`__ on `Libera Chat
<https://libera.chat/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @rlaager
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Ubuntu%2020.04%20Root%20on%20ZFS%20HOWTO:>`__.

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

Step 1: Prepare The Install Environment
---------------------------------------

#. Boot the Ubuntu Live CD. Select Try Ubuntu. Connect your system to the
   Internet as appropriate (e.g. join your WiFi network). Open a terminal
   (press Ctrl-Alt-T).

#. Setup and update the repositories::

     sudo apt update

#. Optional: Install and start the OpenSSH server in the Live CD environment:

   If you have a second system, using SSH to access the target system can be
   convenient::

     passwd
     # There is no current password.
     sudo apt install --yes openssh-server vim

   Installing the full ``vim`` package fixes terminal problems that occur when
   using the ``vim-tiny`` package (that ships in the Live CD environment) over
   SSH.

   **Hint:** You can find your IP address with
   ``ip addr show scope global | grep inet``. Then, from your main machine,
   connect with ``ssh ubuntu@IP``.

#. Disable automounting:

   If the disk has been used before (with partitions at the same offsets),
   previous filesystems (e.g. the ESP) will automount if not disabled::

     gsettings set org.gnome.desktop.media-handling automount false

#. Become root::

     sudo -i

#. Install ZFS in the Live CD environment::

     apt install --yes debootstrap gdisk zfs-initramfs

     systemctl stop zed

Step 2: Disk Formatting
-----------------------

#. Set a variable with the disk name::

     DISK=/dev/disk/by-id/scsi-SATA_disk1

   Always use the long ``/dev/disk/by-id/*`` aliases with ZFS. Using the
   ``/dev/sd*`` device nodes directly can cause sporadic import failures,
   especially on systems that have more than one storage pool.

   **Hints:**

   - ``ls -la /dev/disk/by-id`` will list the aliases.
   - Are you doing this in a virtual machine? If your virtual disk is missing
     from ``/dev/disk/by-id``, use ``/dev/vda`` if you are using KVM with
     virtio; otherwise, read the `troubleshooting <#troubleshooting>`__
     section.

#. If you are re-using a disk, clear it as necessary:

   Ensure swap partitions are not in use::
   
     swapoff --all

   If the disk was previously used in an MD array::

     apt install --yes mdadm

     # See if one or more MD arrays are active:
     cat /proc/mdstat
     # If so, stop them (replace ``md0`` as required):
     mdadm --stop /dev/md0

     # For an array using the whole disk:
     mdadm --zero-superblock --force $DISK
     # For an array using a partition (e.g. a swap partition per this HOWTO):
     mdadm --zero-superblock --force ${DISK}-part2

   Clear the partition table::

     sgdisk --zap-all $DISK

   If you get a message about the kernel still using the old partition table,
   reboot and start over (except that you can skip this step).

#. Create bootloader partition(s)::

     sgdisk     -n1:1M:+512M   -t1:EF00 $DISK

     # For legacy (BIOS) booting:
     sgdisk -a1 -n5:24K:+1000K -t5:EF02 $DISK

   **Note:** While the Ubuntu installer uses an MBR label for legacy (BIOS)
   booting, this HOWTO uses GPT partition labels for both UEFI and legacy
   (BIOS) booting. This is simpler than having two options.  It is also
   provides forward compatibility (future proofing).  In other words, for
   legacy (BIOS) booting, this will allow you to move the disk(s) to a new
   system/motherboard in the future without having to rebuild the pool (and
   restore your data from a backup). The ESP is created in both cases for
   similar reasons.  Additionally, the ESP is used for ``/boot/grub`` in
   single-disk installs, as :ref:`discussed below <boot-grub-esp>`.

#. Create a partition for swap:

   Previous versions of this HOWTO put swap on a zvol. `Ubuntu recommends
   against this configuration due to deadlocks.
   <https://bugs.launchpad.net/ubuntu/+source/zfs-linux/+bug/1847628>`__ There
   is `a bug report upstream
   <https://github.com/zfsonlinux/zfs/issues/7734>`__.

   Putting swap on a partition gives up the benefit of ZFS checksums (for your
   swap). That is probably the right trade-off given the reports of ZFS
   deadlocks with swap. If you are bothered by this, simply do not enable
   swap.

   Choose one of the following options if you want swap:

   - For a single-disk install::

       sgdisk     -n2:0:+500M    -t2:8200 $DISK

   - For a mirror or raidz topology::

       sgdisk     -n2:0:+500M    -t2:FD00 $DISK

   Adjust the swap swize to your needs.  If you wish to enable hiberation
   (which only works for unencrypted installs), the swap partition must be
   at least as large as the system's RAM.

#. Create a boot pool partition::

     sgdisk     -n3:0:+2G      -t3:BE00 $DISK

   The Ubuntu installer uses 5% of the disk space constrained to a minimum of
   500 MiB and a maximum of 2 GiB. `Making this too small (and 500 MiB might
   be too small) can result in an inability to upgrade the kernel.
   <https://medium.com/@andaag/how-i-moved-a-ext4-ubuntu-install-to-encrypted-zfs-62af1170d46c>`__

#. Create a root pool partition:

   Choose one of the following options:

   - Unencrypted or ZFS native encryption::

       sgdisk     -n4:0:0        -t4:BF00 $DISK

   - LUKS::

       sgdisk     -n4:0:0        -t4:8309 $DISK

   If you are creating a mirror or raidz topology, repeat the partitioning
   commands for all the disks which will be part of the pool.

#. Create the boot pool::

     zpool create \
         -o cachefile=/etc/zfs/zpool.cache \
         -o ashift=12 -o autotrim=on -d \
         -o feature@async_destroy=enabled \
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
         -O acltype=posixacl -O canmount=off -O compression=lz4 \
         -O devices=off -O normalization=formD -O relatime=on -O xattr=sa \
         -O mountpoint=/boot -R /mnt \
         bpool ${DISK}-part3

   You should not need to customize any of the options for the boot pool.

   GRUB does not support all of the zpool features. See ``spa_feature_names``
   in `grub-core/fs/zfs/zfs.c
   <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
   This step creates a separate boot pool for ``/boot`` with the features
   limited to only those that GRUB supports, allowing the root pool to use
   any/all features. Note that GRUB opens the pool read-only, so all
   read-only compatible features are “supported” by GRUB.

   **Hints:**

   - If you are creating a mirror topology, create the pool using::

       zpool create \
           ... \
           bpool mirror \
           /dev/disk/by-id/scsi-SATA_disk1-part3 \
           /dev/disk/by-id/scsi-SATA_disk2-part3

   - For raidz topologies, replace ``mirror`` in the above command with
     ``raidz``, ``raidz2``, or  ``raidz3`` and list the partitions from
     additional disks.
   - The boot pool name is no longer arbitrary.  It _must_ be ``bpool``.
     If you really want to rename it, edit ``/etc/grub.d/10_linux_zfs`` later,
     after GRUB is installed (and run ``update-grub``).

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

#. Create the root pool:

   Choose one of the following options:

   - Unencrypted::

       zpool create \
           -o ashift=12 -o autotrim=on \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part4

   - ZFS native encryption::

       zpool create \
           -o ashift=12 -o autotrim=on \
           -O encryption=aes-256-gcm \
           -O keylocation=prompt -O keyformat=passphrase \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part4

   - LUKS::

       cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part4
       cryptsetup luksOpen ${DISK}-part4 luks1
       zpool create \
           -o ashift=12 -o autotrim=on \
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

   **Hints:**

   - If you are creating a mirror topology, create the pool using::

       zpool create \
           ... \
           rpool mirror \
           /dev/disk/by-id/scsi-SATA_disk1-part4 \
           /dev/disk/by-id/scsi-SATA_disk2-part4

   - For raidz topologies, replace ``mirror`` in the above command with
     ``raidz``, ``raidz2``, or  ``raidz3`` and list the partitions from
     additional disks.
   - When using LUKS with mirror or raidz topologies, use
     ``/dev/mapper/luks1``, ``/dev/mapper/luks2``, etc., which you will have
     to create using ``cryptsetup``.
   - The pool name is arbitrary. If changed, the new name must be used
     consistently. On systems that can automatically install to ZFS, the root
     pool is named ``rpool`` by default.

Step 3: System Installation
---------------------------

#. Create filesystem datasets to act as containers::

     zfs create -o canmount=off -o mountpoint=none rpool/ROOT
     zfs create -o canmount=off -o mountpoint=none bpool/BOOT

#. Create filesystem datasets for the root and boot filesystems::

     UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null |
         tr -dc 'a-z0-9' | cut -c-6)

     zfs create -o mountpoint=/ \
         -o com.ubuntu.zsys:bootfs=yes \
         -o com.ubuntu.zsys:last-used=$(date +%s) rpool/ROOT/ubuntu_$UUID

     zfs create -o mountpoint=/boot bpool/BOOT/ubuntu_$UUID

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
     chmod 700 /mnt/root

   For a mirror or raidz topology, create a dataset for ``/boot/grub``::

     zfs create -o com.ubuntu.zsys:bootfs=no bpool/grub

   Mount a tmpfs at /run::

     mkdir /mnt/run
     mount -t tmpfs tmpfs /mnt/run
     mkdir /mnt/run/lock

   A tmpfs is recommended later, but if you want a separate dataset for
   ``/tmp``::

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

#. Install the minimal system::

     debootstrap focal /mnt

   The ``debootstrap`` command leaves the new system in an unconfigured state.
   An alternative to using ``debootstrap`` is to copy the entirety of a
   working system into the new ZFS root.

#. Copy in zpool.cache::

     mkdir /mnt/etc/zfs
     cp /etc/zfs/zpool.cache /mnt/etc/zfs/

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

#. Configure the network interface:

   Find the interface name::

     ip addr show

   Adjust ``NAME`` below to match your interface name::

     vi /mnt/etc/netplan/01-netcfg.yaml

   .. code-block:: yaml

     network:
       version: 2
       ethernets:
         NAME:
           dhcp4: true

   Customize this file if the system is not a DHCP client.

#. Configure the package sources::

     vi /mnt/etc/apt/sources.list

   .. code-block:: sourceslist

     deb http://archive.ubuntu.com/ubuntu focal main restricted universe multiverse
     deb http://archive.ubuntu.com/ubuntu focal-updates main restricted universe multiverse
     deb http://archive.ubuntu.com/ubuntu focal-backports main restricted universe multiverse
     deb http://security.ubuntu.com/ubuntu focal-security main restricted universe multiverse

#. Bind the virtual filesystems from the LiveCD environment to the new
   system and ``chroot`` into it::

     mount --rbind /dev  /mnt/dev
     mount --rbind /proc /mnt/proc
     mount --rbind /sys  /mnt/sys
     chroot /mnt /usr/bin/env DISK=$DISK UUID=$UUID bash --login

   **Note:** This is using ``--rbind``, not ``--bind``.

#. Configure a basic system environment::

     apt update

   Even if you prefer a non-English system language, always ensure that
   ``en_US.UTF-8`` is available::

     dpkg-reconfigure locales tzdata keyboard-configuration console-setup

   Install your preferred text editor::

     apt install --yes nano

     apt install --yes vim

   Installing the full ``vim`` package fixes terminal problems that occur when
   using the ``vim-tiny`` package (that is installed by ``debootstrap``) over
   SSH.

#. For LUKS installs only, setup ``/etc/crypttab``::

     apt install --yes cryptsetup

     echo luks1 /dev/disk/by-uuid/$(blkid -s UUID -o value ${DISK}-part4) \
         none luks,discard,initramfs > /etc/crypttab

   The use of ``initramfs`` is a work-around for `cryptsetup does not support
   ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

   **Hint:** If you are creating a mirror or raidz topology, repeat the
   ``/etc/crypttab`` entries for ``luks2``, etc. adjusting for each disk.

#. Create the EFI filesystem:

   Perform these steps for both UEFI and legacy (BIOS) booting::

     apt install --yes dosfstools

     mkdosfs -F 32 -s 1 -n EFI ${DISK}-part1
     mkdir /boot/efi
     echo /dev/disk/by-uuid/$(blkid -s UUID -o value ${DISK}-part1) \
         /boot/efi vfat defaults 0 0 >> /etc/fstab
     mount /boot/efi

   For a mirror or raidz topology, repeat the `mkdosfs` for the additional
   disks, but do not repeat the other commands.

   **Note:** The ``-s 1`` for ``mkdosfs`` is only necessary for drives which
   present 4 KiB logical sectors (“4Kn” drives) to meet the minimum cluster
   size (given the partition size of 512 MiB) for FAT32. It also works fine on
   drives which present 512 B sectors.

#. Put ``/boot/grub`` on the EFI System Partition:

   .. _boot-grub-esp:

   For a single-disk install only::

     mkdir /boot/efi/grub /boot/grub
     echo /boot/efi/grub /boot/grub none defaults,bind 0 0 >> /etc/fstab
     mount /boot/grub

   This allows GRUB to write to ``/boot/grub`` (since it is on a FAT-formatted
   ESP instead of on ZFS), which means that ``/boot/grub/grubenv`` and the
   ``recordfail`` feature works as expected: if the boot fails, the normally
   hidden GRUB menu will be shown on the next boot. For a mirror or raidz
   topology, we do not want GRUB writing to the EFI System Partition. This is
   because we duplicate it at install without a mechanism to update the copies
   when the GRUB configuration changes (e.g. as the kernel is upgraded). Thus,
   we keep ``/boot/grub`` on the boot pool for the mirror or raidz topologies.
   This preserves correct mirroring/raidz behavior, at the expense of being
   able to write to ``/boot/grub/grubenv`` and thus the ``recordfail``
   behavior.

#. Install GRUB/Linux/ZFS in the chroot environment for the new system:

   Choose one of the following options:

   - Install GRUB/Linux/ZFS for legacy (BIOS) booting::

       apt install --yes grub-pc linux-image-generic zfs-initramfs zsys

     Select (using the space bar) all of the disks (not partitions) in your
     pool.

   - Install GRUB/Linux/ZFS for UEFI booting::

       apt install --yes \
           grub-efi-amd64 grub-efi-amd64-signed linux-image-generic \
           shim-signed zfs-initramfs zsys

     **Notes:**

     - Ignore any error messages saying ``ERROR: Couldn't resolve device`` and
       ``WARNING: Couldn't determine root device``.  `cryptsetup does not
       support ZFS
       <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

     - Ignore any error messages saying ``Module zfs not found`` and
       ``couldn't connect to zsys daemon``.  The first seems to occur due to a
       version mismatch between the Live CD kernel and the chroot environment,
       but this is irrelevant since the module is already loaded.  The second
       may be caused by the first but either way is irrelevant since ``zed``
       is started manually later.

     - For a mirror or raidz topology, this step only installs GRUB on the
       first disk. The other disk(s) will be handled later.  For some reason,
       grub-efi-amd64 does not prompt for ``install_devices`` here, but does
       after a reboot.

#. Optional: Remove os-prober::

     apt remove --purge os-prober

   This avoids error messages from ``update-grub``.  ``os-prober`` is only
   necessary in dual-boot configurations.

#. Set a root password::

     passwd

#. Configure swap:

   Choose one of the following options if you want swap:

   - For an unencrypted single-disk install::

       mkswap -f ${DISK}-part2
       echo /dev/disk/by-uuid/$(blkid -s UUID -o value ${DISK}-part2) \
           none swap discard 0 0 >> /etc/fstab
       swapon -a

   - For an unencrypted mirror or raidz topology::

       apt install --yes mdadm

       # Adjust the level (ZFS raidz = MD raid5, raidz2 = raid6) and
       # raid-devices if necessary and specify the actual devices.
       mdadm --create /dev/md0 --metadata=1.2 --level=mirror \
           --raid-devices=2 ${DISK1}-part2 ${DISK2}-part2
       mkswap -f /dev/md0
       echo /dev/disk/by-uuid/$(blkid -s UUID -o value /dev/md0) \
           none swap discard 0 0 >> /etc/fstab

   - For an encrypted (LUKS or ZFS native encryption) single-disk install::

       apt install --yes cryptsetup

       echo swap ${DISK}-part2 /dev/urandom \
             swap,cipher=aes-xts-plain64:sha256,size=512 >> /etc/crypttab
       echo /dev/mapper/swap none swap defaults 0 0 >> /etc/fstab

   - For an encrypted (LUKS or ZFS native encryption) mirror or raidz
     topology::

       apt install --yes cryptsetup mdadm

       # Adjust the level (ZFS raidz = MD raid5, raidz2 = raid6) and
       # raid-devices if necessary and specify the actual devices.
       mdadm --create /dev/md0 --metadata=1.2 --level=mirror \
           --raid-devices=2 ${DISK1}-part2 ${DISK2}-part2
       echo swap /dev/md0 /dev/urandom \
             swap,cipher=aes-xts-plain64:sha256,size=512 >> /etc/crypttab
       echo /dev/mapper/swap none swap defaults 0 0 >> /etc/fstab

#. Optional (but recommended): Mount a tmpfs to ``/tmp``

   If you chose to create a ``/tmp`` dataset above, skip this step, as they
   are mutually exclusive choices. Otherwise, you can put ``/tmp`` on a
   tmpfs (RAM filesystem) by enabling the ``tmp.mount`` unit.

   ::

     cp /usr/share/systemd/tmp.mount /etc/systemd/system/
     systemctl enable tmp.mount

#. Setup system groups::

     addgroup --system lpadmin
     addgroup --system lxd
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

#. Optional: Install SSH::

     apt install --yes openssh-server

     vi /etc/ssh/sshd_config
     # Set: PermitRootLogin yes

Step 5: GRUB Installation
-------------------------

#. Verify that the ZFS boot filesystem is recognized::

     grub-probe /boot

#. Refresh the initrd files::

     update-initramfs -c -k all

   **Note:** Ignore any error messages saying ``ERROR: Couldn't resolve
   device`` and ``WARNING: Couldn't determine root device``.  `cryptsetup
   does not support ZFS
   <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

#. Disable memory zeroing::

     vi /etc/default/grub
     # Add init_on_alloc=0 to: GRUB_CMDLINE_LINUX_DEFAULT
     # Save and quit (or see the next step).

   This is to address `performance regressions
   <https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1862822>`__.

#. Optional (but highly recommended): Make debugging GRUB easier::

     vi /etc/default/grub
     # Comment out: GRUB_TIMEOUT_STYLE=hidden
     # Set: GRUB_TIMEOUT=5
     # Below GRUB_TIMEOUT, add: GRUB_RECORDFAIL_TIMEOUT=5
     # Remove quiet and splash from: GRUB_CMDLINE_LINUX_DEFAULT
     # Uncomment: GRUB_TERMINAL=console
     # Save and quit.

   Later, once the system has rebooted twice and you are sure everything is
   working, you can undo these changes, if desired.

#. Update the boot configuration::

     update-grub

   **Note:** Ignore errors from ``osprober``, if present.

#. Install the boot loader:

   Choose one of the following options:

   - For legacy (BIOS) booting, install GRUB to the MBR::

       grub-install $DISK

     Note that you are installing GRUB to the whole disk, not a partition.

     If you are creating a mirror or raidz topology, repeat the
     ``grub-install`` command for each disk in the pool.

   - For UEFI booting, install GRUB to the ESP::

       grub-install --target=x86_64-efi --efi-directory=/boot/efi \
           --bootloader-id=ubuntu --recheck --no-floppy

#. Disable grub-initrd-fallback.service

   For a mirror or raidz topology::

     systemctl mask grub-initrd-fallback.service

   This is the service for ``/boot/grub/grubenv`` which does not work on
   mirrored or raidz topologies. Disabling this keeps it from blocking
   subsequent mounts of ``/boot/grub`` if that mount ever fails.

   Another option would be to set ``RequiresMountsFor=/boot/grub`` via a
   drop-in unit, but that is more work to do here for no reason. Hopefully
   `this bug <https://bugs.launchpad.net/ubuntu/+source/grub2/+bug/1881442>`__
   will be fixed upstream.

#. Fix filesystem mount ordering:

   We need to activate ``zfs-mount-generator``. This makes systemd aware of
   the separate mountpoints, which is important for things like ``/var/log``
   and ``/var/tmp``. In turn, ``rsyslog.service`` depends on ``var-log.mount``
   by way of ``local-fs.target`` and services using the ``PrivateTmp`` feature
   of systemd automatically use ``After=var-tmp.mount``.

   ::

     mkdir /etc/zfs/zfs-list.cache
     touch /etc/zfs/zfs-list.cache/bpool
     touch /etc/zfs/zfs-list.cache/rpool
     ln -s /usr/lib/zfs-linux/zed.d/history_event-zfs-list-cacher.sh /etc/zfs/zed.d
     zed -F &

   Verify that ``zed`` updated the cache by making sure these are not empty::

     cat /etc/zfs/zfs-list.cache/bpool
     cat /etc/zfs/zfs-list.cache/rpool

   If either is empty, force a cache update and check again::

     zfs set canmount=on bpool/BOOT/ubuntu_$UUID
     zfs set canmount=on rpool/ROOT/ubuntu_$UUID

   If they are still empty, stop zed (as below), start zed (as above) and try
   again.

   Once the files have data, stop ``zed``::

     fg
     Press Ctrl-C.

   Fix the paths to eliminate ``/mnt``::

     sed -Ei "s|/mnt/?|/|" /etc/zfs/zfs-list.cache/*

#. Exit from the ``chroot`` environment back to the LiveCD environment::

     exit

#. Run these commands in the LiveCD environment to unmount all
   filesystems::

     mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
         xargs -i{} umount -lf {}
     zpool export -a

#. Reboot::

     reboot

   Wait for the newly installed system to boot normally. Login as root.

Step 6: First Boot
------------------

#. Install GRUB to additional disks:

   For a UEFI mirror or raidz topology only::

     dpkg-reconfigure grub-efi-amd64

     Select (using the space bar) all of the ESP partitions (partition 1 on
     each of the pool disks).

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

Step 7: Full Software Installation
----------------------------------

#. Upgrade the minimal system::

     apt dist-upgrade --yes

#. Install a regular set of software:

   Choose one of the following options:

   - Install a command-line environment only::

       apt install --yes ubuntu-standard

   - Install a full GUI environment::

       apt install --yes ubuntu-desktop

     **Hint**: If you are installing a full GUI environment, you will likely
     want to manage your network with NetworkManager::

       rm /etc/netplan/01-netcfg.yaml
       vi /etc/netplan/01-network-manager-all.yaml

     .. code-block:: yaml

       network:
         version: 2
         renderer: NetworkManager

#. Optional: Disable log compression:

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

Step 8: Final Cleanup
---------------------

#. Wait for the system to boot normally. Login using the account you
   created. Ensure the system (including networking) works normally.

#. Optional: Disable the root password::

     sudo usermod -p '*' root

#. Optional (but highly recommended): Disable root SSH logins:

   If you installed SSH earlier, revert the temporary change::

     sudo vi /etc/ssh/sshd_config
     # Remove: PermitRootLogin yes

     sudo systemctl restart ssh

#. Optional: Re-enable the graphical boot process:

   If you prefer the graphical boot process, you can re-enable it now. If
   you are using LUKS, it makes the prompt look nicer.

   ::

     sudo vi /etc/default/grub
     # Uncomment: GRUB_TIMEOUT_STYLE=hidden
     # Add quiet and splash to: GRUB_CMDLINE_LINUX_DEFAULT
     # Comment out: GRUB_TERMINAL=console
     # Save and quit.

     sudo update-grub

   **Note:** Ignore errors from ``osprober``, if present.

#. Optional: For LUKS installs only, backup the LUKS header::

     sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
         --header-backup-file luks1-header.dat

   Store that backup somewhere safe (e.g. cloud storage). It is protected by
   your LUKS passphrase, but you may wish to use additional encryption.

   **Hint:** If you created a mirror or raidz topology, repeat this for each
   LUKS volume (``luks2``, etc.).

Troubleshooting
---------------

Rescuing using a Live CD
~~~~~~~~~~~~~~~~~~~~~~~~

Go through `Step 1: Prepare The Install Environment
<#step-1-prepare-the-install-environment>`__.

For LUKS, first unlock the disk(s)::

  cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
  # Repeat for additional disks, if this is a mirror or raidz topology.

Mount everything correctly::

  zpool export -a
  zpool import -N -R /mnt rpool
  zpool import -N -R /mnt bpool
  zfs load-key -a
  # Replace “UUID” as appropriate; use zfs list to find it:
  zfs mount rpool/ROOT/ubuntu_UUID
  zfs mount bpool/BOOT/ubuntu_UUID
  zfs mount -a

If needed, you can chroot into your installed environment::

  mount --rbind /dev  /mnt/dev
  mount --rbind /proc /mnt/proc
  mount --rbind /sys  /mnt/sys
  mount -t tmpfs tmpfs /mnt/run
  mkdir /mnt/run/lock
  chroot /mnt /bin/bash --login
  mount -a

Do whatever you need to do to fix your system.

When done, cleanup::

  exit
  mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
      xargs -i{} umount -lf {}
  zpool export -a
  reboot

Areca
~~~~~

Systems that require the ``arcsas`` blob driver should add it to the
``/etc/initramfs-tools/modules`` file and run ``update-initramfs -c -k all``.

Upgrade or downgrade the Areca driver if something like
``RIP: 0010:[<ffffffff8101b316>]  [<ffffffff8101b316>] native_read_tsc+0x6/0x20``
appears anywhere in kernel log. ZoL is unstable on systems that emit this
error message.

MPT2SAS
~~~~~~~

Most problem reports for this tutorial involve ``mpt2sas`` hardware that does
slow asynchronous drive initialization, like some IBM M1015 or OEM-branded
cards that have been flashed to the reference LSI firmware.

The basic problem is that disks on these controllers are not visible to the
Linux kernel until after the regular system is started, and ZoL does not
hotplug pool members. See `https://github.com/zfsonlinux/zfs/issues/330
<https://github.com/zfsonlinux/zfs/issues/330>`__.

Most LSI cards are perfectly compatible with ZoL. If your card has this
glitch, try setting ``ZFS_INITRD_PRE_MOUNTROOT_SLEEP=X`` in
``/etc/default/zfs``. The system will wait ``X`` seconds for all drives to
appear before importing the pool.

QEMU/KVM/XEN
~~~~~~~~~~~~

Set a unique serial number on each virtual disk using libvirt or qemu
(e.g. ``-drive if=none,id=disk1,file=disk1.qcow2,serial=1234567890``).

To be able to use UEFI in guests (instead of only BIOS booting), run
this on the host::

  sudo apt install ovmf
  sudo vi /etc/libvirt/qemu.conf

Uncomment these lines:

.. code-block:: text

  nvram = [
     "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd",
     "/usr/share/OVMF/OVMF_CODE.secboot.fd:/usr/share/OVMF/OVMF_VARS.fd",
     "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd",
     "/usr/share/AAVMF/AAVMF32_CODE.fd:/usr/share/AAVMF/AAVMF32_VARS.fd",
     "/usr/share/OVMF/OVMF_CODE.ms.fd:/usr/share/OVMF/OVMF_VARS.ms.fd"
  ]

::

  sudo systemctl restart libvirtd.service

VMware
~~~~~~

- Set ``disk.EnableUUID = "TRUE"`` in the vmx file or vsphere configuration.
  Doing this ensures that ``/dev/disk`` aliases are created in the guest.
