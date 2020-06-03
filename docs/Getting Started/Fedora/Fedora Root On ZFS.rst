.. highlight:: sh

Fedora Root on ZFS
==================

.. contents:: Table of Contents
  :local:

Overview
--------

Caution
~~~~~~~

- This HOWTO uses a whole physical disk.
- Do not use these instructions for dual-booting.
- Backup your data. Any existing data will be lost.

System Requirements
~~~~~~~~~~~~~~~~~~~

- `64-bit Fedora Workstation (spins are not yet tested yet)
  <https://getfedora.org/en/workstation/download/>`__
- `A 64-bit kernel is strongly encouraged.
  <https://github.com/zfsonlinux/zfs/wiki/FAQ#32-bit-vs-64-bit-systems>`__
- Installing on a drive which presents 4 KiB logical sectors (a “4Kn” drive)
  only works with UEFI booting. This not unique to ZFS. `GRUB does not and
  will not work on 4Kn with legacy (BIOS) booting.
  <http://savannah.gnu.org/bugs/?46700>`__
- You MUST use a UEFI system for this guide as GRUB is not yet supported. To verify UEFI, go to /sys/firmware/efi/efivars and make sure it is not empty.

Computers that have less than 2 GiB of memory run ZFS slowly. 4 GiB of memory
is recommended for normal performance in basic workloads. If you wish to use
deduplication, you will need `massive amounts of RAM
<http://wiki.freebsd.org/ZFSTuningGuide#Deduplication>`__. Enabling
deduplication is a permanent change that cannot be easily reverted.

Support
~~~~~~~

If you need help, reach out to the community using the :doc:`zfs-discuss
mailing list <../../Project and Community/Mailing Lists>` or IRC at
`#zfsonlinux <irc://irc.freenode.net/#zfsonlinux>`__ on `freenode
<https://freenode.net/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @rlaager
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Debian%20Buster%20Root%20on%20ZFS%20HOWTO:>`__.

Contributing
~~~~~~~~~~~~

#. Fork and clone: https://github.com/openzfs/openzfs-docs

#. Install the tools::

    sudo dnf install python3-pip sensible-utils
    cd openzfs-docs/docs
    pip3 install -r requirements.txt
    # Add ~/.local/bin to your $PATH, e.g. by adding this to ~/.bashrc:
    PATH=$HOME/.local/bin:$PATH

#. Make your changes.

#. Test::

    cd docs # If you aren't already in the docs folder
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
encrypted once per disk. Note that I (cheesycod) do not use LUKS and that you are using this at your own risk.

Step 1: Prepare The Install Environment
---------------------------------------

#. Create a Fedora Workstation Live CD or USB. Note that you can do this through either Fedora Media Writer or using any other DVD or USB writing software.

#. Boot the Fedora Workstation Live CD or USB that you made in Step 1.

#. Connect your system to the Internet as appropriate (e.g. join your WiFi network). Once you have connected to the internet, open a terminal.

#. Optional: Install and start the OpenSSH server in the Live CD environment:

   If you have a second system, using SSH to access the target system can be
   convenient::

     sudo dnf install openssh-server
     sudo systemctl restart sshd

   **Hint:** You can find your IP address with
   ``ip addr show scope global | grep inet``. Then, from your main machine,
   connect with ``ssh user@IP``.

#. Become root using ``sudo -i`` OR ``su root``

.. note::
   From here on out, all commands will assert that you are root unless previously specified

#. Install the zfs-release rpm. You can do this by running the following command: ``dnf install http://download.zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm``. It is also recommended to check the PGP keys to verify that the RPM has not been tampered.

#. Install the kernel headers using ``dnf install kernel-devel-$(uname -r)``. Note that you may need to use Bodhi if the kernel your version of Fedora is using is too old.

#. Next swap the zfs FUSE with the openZFS kernel module: ``dnf swap zfs-fuse zfs``

#. Finally ensure that the zfs kernel module is loaded by running ``sudo modprobe zfs``.

Step 2: Disk Formatting
-----------------------
.. note::
   Note that if you want to use systemd-boot instead of GRUB, you should not create a boot pool. This only applies to systemd-boot users. Also note that GRUB is not yet supported (I have not yet gotten it to work correctly). For now, please use systemd-boot with Fedora. Also note that systemd-boot is easier than GRUB to setup with Fedora.

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

   If the disk was previously used in an MD array::

     # See if one or more MD arrays are active:
     cat /proc/mdstat
     # If so, stop them (replace ``md0`` as required):
     mdadm --stop /dev/md0

     # For an array using the whole disk:
     mdadm --zero-superblock --force $DISK
     # For an array using a partition:
     mdadm --zero-superblock --force ${DISK}-part2

   Clear the partition table::

     sgdisk --zap-all $DISK

   If you get a message about the kernel still using the old partition table,
   reboot and start over (except that you can skip this step).


#. Partition your disk(s):

   Run this if you need legacy (BIOS) booting::

     sgdisk -a1 -n1:24K:+1000K -t1:EF02 $DISK

   Run this for UEFI booting (for use now or in the future). Note that you should increase the size of this to 1G if you are bot going to use a boot pool (systemd-boot)::

     sgdisk     -n2:1M:+512M   -t2:EF00 $DISK

   Run this for the boot pool (if you are using GRUB, not yet supported on Fedora)::

     sgdisk     -n3:0:+1G      -t3:BF01 $DISK

   (Optional, but recommended if you have high memory pressure): Create a swap partition (change the -n4 and -t4 if you are using systemd-boot)::

     sgdisk     -n4:0:+<size>G  -t4:8200 $DISK # Make sure you replace <size> with the size of your swap partition.
     mkswap     $DISK-part4
     swapon     $DISK-part4
   
   Choose one of the following options:

   - Unencrypted or ZFS native encryption (change the -n4 and -t4 if you added a swap partition)::

       sgdisk     -n4:0:0        -t4:BF00 $DISK

   - LUKS (same warning as with Unencrypted and ZFS native encryption)::

       sgdisk     -n4:0:0        -t4:8309 $DISK

   If you are creating a mirror or raidz topology, repeat the partitioning
   commands for all the disks which will be part of the pool.

#. Create the boot pool (if you are using GRUB, not yet supported on Fedora)::

     zpool create \
         -o ashift=12 -d \
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
         -o feature@zpool_checkpoint=enabled \
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
   - The pool name is arbitrary. If changed, the new name must be used
     consistently. The ``bpool`` convention originated in this HOWTO.

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

#. Create the root pool (note that you might need to change the DISK depending on the options you choose:

   Choose one of the following options:

   - Unencrypted::

       zpool create \
           -o ashift=12 \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part4

   - ZFS native encryption::

       zpool create \
           -o ashift=12 \
           -O encryption=aes-256-gcm \
           -O keylocation=prompt -O keyformat=passphrase \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part4

   - LUKS::

       apt install --yes cryptsetup
       cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part4
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
     <http://open-zfs.org/wiki/Platform_code_differences>`__. If you move your
     ``xattr=sa`` pool to another OpenZFS implementation besides ZFS-on-Linux,
     extended attributes will not be readable (though your data will be). If
     portability of extended attributes is important to you, omit the
     ``-O xattr=sa`` above. Even if you do not want ``xattr=sa`` for the whole
     pool, it is probably fine to use it for ``/var/log``.
   - Make sure to include the ``-part4`` portion of the drive path. If you
     forget that, you are specifying the whole disk, which ZFS will then
     re-partition, and you will lose the bootloader partition(s).
   - ZFS native encryption `now
     <https://github.com/openzfs/zfs/commit/31b160f0a6c673c8f926233af2ed6d5354808393>`__
     defaults to ``aes-256-gcm``.
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
           bpool mirror \
           /dev/disk/by-id/scsi-SATA_disk1-part3 \
           /dev/disk/by-id/scsi-SATA_disk2-part3

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

#. Create filesystem datasets to act as containers (Again, omit the second line if you are using systemd-boot)::

     zfs create -o canmount=off -o mountpoint=none rpool/ROOT
     zfs create -o canmount=off -o mountpoint=none bpool/BOOT

   On Solaris systems, the root filesystem is cloned and the suffix is
   incremented for major system changes through ``pkg image-update`` or
   ``beadm``. Similar functionality has been implemented in Ubuntu 20.04 with
   the ``zsys`` tool, though its dataset layout is more complicated. Even
   without such a tool, the `rpool/ROOT` and `bpool/BOOT` containers can still
   be used for manually created clones. That said, this HOWTO assumes a single
   filesystem for ``/boot`` for simplicity.

#. Create filesystem datasets for the root and boot filesystems (again, omit the second two lines if you are using systemd-boot)::

     zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/fedora
     zfs mount rpool/ROOT/fedora

     zfs create -o mountpoint=/boot bpool/BOOT/fedora
     zfs mount bpool/BOOT/fedora

   With ZFS, it is not normally necessary to use a mount command (either
   ``mount`` or ``zfs mount``). This situation is an exception because of
   ``canmount=noauto``.

#. Create datasets::

     zfs create                                 rpool/home
     zfs create -o mountpoint=/root             rpool/home/root
     zfs create -o canmount=off                 rpool/var
     zfs create -o canmount=off                 rpool/var/lib
     zfs create                                 rpool/var/log
     zfs create                                 rpool/var/spool

   The datasets below are optional, depending on your preferences and/or
   software choices.

   If you wish to exclude these from snapshots::

     zfs create -o com.sun:auto-snapshot=false  rpool/var/cache
     zfs create -o com.sun:auto-snapshot=false  rpool/var/tmp
     chmod 1777 /mnt/var/tmp

   If this system will use Docker (which manages its own datasets &
   snapshots)::

     zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/docker

   If this system will use NFS (locking)::

     zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/nfs

   A tmpfs is recommended later, but if you want a separate dataset for
   ``/tmp``::

     zfs create -o com.sun:auto-snapshot=false  rpool/tmp
     chmod 1777 /mnt/tmp
   
   Note that the reason why we are not fully seperating everything like we did in Ubuntu is because dnf will fail to install or update certain packages if we create too many datasets.

   The primary goal of this dataset layout is to separate the OS from user
   data. This allows the root filesystem to be rolled back without rolling
   back user data.

   If you do nothing extra, ``/tmp`` will be stored as part of the root
   filesystem. Alternatively, you can create a separate dataset for ``/tmp``,
   as shown above. This keeps the ``/tmp`` data out of snapshots of your root
   filesystem. It also allows you to set a quota on ``rpool/tmp``, if you want
   to limit the maximum space used. Otherwise, you can use a tmpfs (RAM
   filesystem) later.

#. Copy the LiveCD to your HDD/SDD::

     rsync -avxHASX / /sysroot/
   
   It is important to not forget the trailing /.
   This command copies the LiveCD to our new zfs datasets and this is the only way I have found to reliably install and boot Fedora Workstation

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

   **Hint:** Use ``nano`` or ``vim`` if you find ``vi`` confusing.

#. Configure the network interface:

   Find the interface name::

     ip addr show

   Adjust ``NAME`` below to match your interface name::

     vi /mnt/etc/network/interfaces.d/NAME

   .. code-block:: text

     auto NAME
     iface NAME inet dhcp

   Customize this file if the system is not a DHCP client.

#. Bind the virtual filesystems from the LiveCD environment to the new
   system and ``chroot`` into it::

     mount --rbind /dev  /mnt/dev
     mount --rbind /proc /mnt/proc
     mount --rbind /sys  /mnt/sys
     chroot /mnt /usr/bin/env DISK=$DISK bash --login

   **Note:** This is using ``--rbind``, not ``--bind``.

#. Update the new system::

     dnf update

.. note::

   Note that the ZFS install we did outside in the LiveCD persists here. Hence, it is not needed to maunally install zfs-release and zfs again.i

#. For LUKS installs only, setup ``/etc/crypttab``::

     dnf install cryptsetup

     echo luks1 UUID=$(blkid -s UUID -o value ${DISK}-part4) none \
         luks,discard,initramfs > /etc/crypttab

   The use of ``initramfs`` is a work-around for `cryptsetup does not support
   ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

   **Hint:** If you are creating a mirror or raidz topology, repeat the
   ``/etc/crypttab`` entries for ``luks2``, etc. adjusting for each disk.

#. Install GRUB (note that this is not yet supported by this guide, use systemd-boot for now instead)

#. Install systemd-boot::

        rm -rvf /boot # Don't worry, we'll reinstall the kernel later
        mkdir boot # Create the boot folder
        dnf install dosfstools
        mkdosfs -F 32 -s 1 -n EFI ${DISK}-part2 # Change this if needed
        echo PARTUUID=$(blkid -s PARTUUID -o value ${DISK}-part2) \
           /boot vfat nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
        mount /boot
        bootctl install # Install systemd-boot to ESP
        sudo dnf reinstall kernel-core # Reinstall the kernel

      **Notes:**

     - The ``-s 1`` for ``mkdosfs`` is only necessary for drives which present
        4 KiB logical sectors (“4Kn” drives) to meet the minimum cluster size
        (given the partition size of 512 MiB) for FAT32. It also works fine on
        drives which present 512 B sectors.
     - For a mirror or raidz topology, this step only installs GRUB on the
       first disk. The other disk(s) will be handled later.

#. Remove stale packages::

     dnf remove --allowerasing --best anaconda-core anaconda-gui anaconda-gui grub* os-prober

   This avoids error messages from `update-grub`.  `os-prober` is only
   necessary in dual-boot configurations.
   Removal of anaconda and grub prevent issues such as the "Install Fedora" issue and dnf bootloader conflicts.

#. Set a root password::

     passwd

#. Enable importing bpool (only needed when using GRUB, not yet supported)

#. Optional (but recommended): Mount a tmpfs to ``/tmp``

   If you chose to create a ``/tmp`` dataset above, skip this step, as they
   are mutually exclusive choices. Otherwise, you can put ``/tmp`` on a
   tmpfs (RAM filesystem) by enabling the ``tmp.mount`` unit.

   ::

     cp /usr/share/systemd/tmp.mount /etc/systemd/system/
     systemctl enable tmp.mount

.. note::
   GRUB installation is not yet supported by this guide. The above steps should have already installed systemd-boot.

Step 6: First Boot
------------------
#. Rebuild initramfs one last time for certainty::

     dracut --kver $(uname -r) --force --add-drivers "zfs"

.. note::

   If you updated your kernel in this guide, you will need to change the $(uname -r) to your updated kernel version. You can find this in /lib/modules.

#. Optional: Install SSH (not needed if already done in the beginning)::

     dnf install --yes openssh-server

#. Optional: Snapshot the initial installation (omit the last one if you are using systemd-boot)::

     zfs snapshot bpool/BOOT/fedora@install
     zfs snapshot rpool/ROOT/fedora@install

   In the future, you will likely want to take snapshots before each
   upgrade, and remove old snapshots (including this one) at some point to
   save space.

#. Exit from the ``chroot`` environment back to the LiveCD environment::

     exit

#. Run these commands in the LiveCD environment to unmount all
   filesystems::

     mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
         xargs -i{} umount -lf {}
     zpool export -a

#. Reboot::

     reboot

   Wait for the newly installed system to boot normally (hopefully). You will/should automatically be logged in as liveuser.

#. Create a user account::
    
     1. Open GNOME Settings and navigate to User Accounts
     2. Click Unlock
     3. Click the Add User button
     4. Type in your user information. Make sure this user is an Administrator.
     5. Sign out of liveuser
     6. Login using your new user account
     7. Open GNOME settings again and navigate to User Accounts
     8. Click Unlock
     9. Click liveuser and click Delete User
     10. Set auto-login for your user account if you want
     11. Reboot

#. Mirror GRUB (not yet supported as GRUB is not yet supported)

Step 7: Optional: Configure ZVol Swap
-------------------------------------

**Caution**: On systems with extremely high memory pressure, using a
zvol for swap can result in lockup, regardless of how much swap is still
available. There is `a bug report upstream
<https://github.com/zfsonlinux/zfs/issues/7734>`__. On such systems, it is wise to create a swap partition and use that. This should have been covered in Partitioning.

#. Create a volume dataset (zvol) for use as a swap device::

     zfs create -V 4G -b $(getconf PAGESIZE) -o compression=zle \
         -o logbias=throughput -o sync=always \
         -o primarycache=metadata -o secondarycache=none \
         -o com.sun:auto-snapshot=false rpool/swap

   You can adjust the size (the ``4G`` part) to your needs.

   The compression algorithm is set to ``zle`` because it is the cheapest
   available algorithm. As this guide recommends ``ashift=12`` (4 kiB
   blocks on disk), the common case of a 4 kiB page size means that no
   compression algorithm can reduce I/O. The exception is all-zero pages,
   which are dropped by ZFS; but some form of compression has to be enabled
   to get this behavior.

#. Configure the swap device:

   **Caution**: Always use long ``/dev/zvol`` aliases in configuration
   files. Never use a short ``/dev/zdX`` device name.

   ::

     mkswap -f /dev/zvol/rpool/swap # Omit this if you already did it in partitioning with a swap partition
     echo /dev/zvol/rpool/swap none swap discard 0 0 >> /etc/fstab # Change this to your swap partition if you are using a swap partition
     echo RESUME=none > /etc/initramfs-tools/conf.d/resume # Omit this if you are using a swap partition and not a zvol.

   The ``RESUME=none`` is necessary to disable resuming from hibernation.
   This does not work, as the zvol is not present (because the pool has not
   yet been imported) at the time the resume script runs. If it is not
   disabled, the boot process hangs for 30 seconds waiting for the swap
   zvol to appear.

#. Enable the swap device::

     swapon -av

Step 8: Last Minute Fixes
-------------------------

#. Upgrade the system (if you haven't already done it)::

     dnf update

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

Step 9: Final Cleanup
---------------------

#. Wait for the system to boot normally. Login using the account you
   created. Ensure the system (including networking) works normally.

#. Optional: Delete the snapshots of the initial installation (omit the second one if you are not using GRUB)::

     sudo zfs destroy bpool/BOOT/fedora@install
     sudo zfs destroy rpool/ROOT/fedora@install

#. Optional (but highly recommended): Disable the root password::

     sudo usermod -p '*' root

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

  dnf install cryptsetup
  cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
  # Repeat for additional disks, if this is a mirror or raidz topology.

Mount everything correctly::

  zpool export -a
  zpool import -N -R /mnt rpool
  zpool import -N -R /mnt bpool
  zfs load-key -a
  zfs mount rpool/ROOT/fedora
  zfs mount -a

If needed, you can chroot into your installed environment::

  mount --rbind /dev  /mnt/dev
  mount --rbind /proc /mnt/proc
  mount --rbind /sys  /mnt/sys
  chroot /mnt /bin/bash --login
  mount /boot
  mount -a

Do whatever you need to do to fix your system.

When done, cleanup::

  exit
  mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
      xargs -i{} umount -lf {}
  zpool export -a
  reboot

QEMU/KVM/XEN
~~~~~~~~~~~~

Set a unique serial number on each virtual disk using libvirt or qemu
(e.g. ``-drive if=none,id=disk1,file=disk1.qcow2,serial=1234567890``).

To be able to use UEFI in guests (instead of only BIOS booting), run
this on the host::

  sudo apt install ovmf # or dnf install edk2-ovmf (if the host is Fedora)
  sudo vi /etc/libvirt/qemu.conf

Uncomment these lines:

.. code-block:: text

  nvram = [
     "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd",
     "/usr/share/OVMF/OVMF_CODE.secboot.fd:/usr/share/OVMF/OVMF_VARS.fd",
     "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd",
     "/usr/share/AAVMF/AAVMF32_CODE.fd:/usr/share/AAVMF/AAVMF32_VARS.fd"
  ]

::

  sudo systemctl restart libvirtd.service

VMware
~~~~~~

- Set ``disk.EnableUUID = "TRUE"`` in the vmx file or vsphere configuration.
  Doing this ensures that ``/dev/disk`` aliases are created in the guest.
