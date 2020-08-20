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

- `64-bit Fedora Workstation ISO.
  <https://getfedora.org/en/workstation/download/>`__
  Note that spins have not been tested yet and we cannot guarantee that spins will work correctly.
- `A 64-bit kernel is strongly encouraged.
  <https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html#bit-vs-64-bit-systems>`__
- Installing on a drive which presents 4 KiB logical sectors (a “4Kn” drive)
  only works with UEFI booting. This not unique to ZFS. `GRUB does not and
  will not work on 4Kn with legacy (BIOS) booting.
  <http://savannah.gnu.org/bugs/?46700>`__
- You MUST use a UEFI system for this guide as GRUB is not supported and 
  will not be supported in the forseeable future. To verify that you are using
  UEFI, go to /sys/firmware/efi/efivars and make sure it is not empty. `It is 
  also worth noting that Fedora plans to drop support for legacy (BIOS) booting 
  support entirely in a future release.
  <https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/thread/QBANCA2UAJ5ZSMDVVARLIYAJE66TYTCD/>`__


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
related to this HOWTO, please `file a new issue and mention @cheesycod
<https://github.com/openzfs/openzfs-docs/issues/new?body=@cheesycod,%20I%20have%20the%20following%20issue%20with%20the%20Fedora%20Root%20on%20ZFS%20HOWTO:>`__.

Contributing
~~~~~~~~~~~~

#. Fork and clone: https://github.com/openzfs/openzfs-docs

#. Install the tools::

    sudo dnf install python3-pip
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
   request. Mention @cheesycod.

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
encrypted once per disk. This manual describes LUKS configuration only as an example, it wasn't tested on everyday basis usage.

.. note::
    Fedora doesn't have debootstrap and the only equivalent in Fedora (dnf --installroot) has weird issues when used with Gnome and other such desktop environments (Cinammon). One such issue is that the boot fails and the system hangs at "Starting GNOME Display Manager" with a broken TTY. 
    As a workaround, we copy the LiveCD on to a new partition and then remove the LiveCD-specific packages after finishing the install.

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

#. Install the zfs dracut module (needed for booting): ``dnf install zfs-dracut``

#. Ensure that the zfs kernel module is loaded by running ``sudo modprobe zfs``.

#. Define the hostid by running ``dd if=/dev/random of=/etc/hostid bs=1 count=4``. If you are curious to know your own hostid, you can run ``hostid | perl -e '$/=\2; $,="."; $\="\n"; print map { eval "0x$_" } (<>)[1,0,3,2];'``

Step 2: Disk Formatting
-----------------------
.. note::
   Note that if you want to use systemd-boot instead of GRUB, you should not create a boot pool. This only applies to systemd-boot users. Also note that GRUB is not supported and will not be supported in the forseeable future. Systemd-boot is much easier than GRUB to setup with Fedora.


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

   If you get a message about the kernel still using the old partition table of your target disk, reboot and restart this section. Note that this does not apply to other unrelated disks as we are running under a LiveCD and partprobe doesn't like that.

#. Partition your disk(s):

   Run this to create your ESP::

     sgdisk     -n0:1M:+1G   -t0:EF00 -c 0:boot $DISK

   (Optional, but recommended if you have high memory pressure): Create a swap partition::

     sgdisk     -n0:0:+<size>G  -t0:8200 -c 0:swap $DISK # Make sure you replace <size> with the size of your swap partition.
     mkswap     $DISK-part2
     swapon     $DISK-part2

   .. note::
      Creation of the swap partition shoud not be done if you plan on using ZFS for swap. Instead, please follow Step 8 instead

   Choose one of the following options:

   - Unencrypted or ZFS native encryption::

       sgdisk     -n3:0:0        -t3:BF00 -c 0:root $DISK

   - LUKS (same warning as with Unencrypted and ZFS native encryption, change the -n3 and -t3 to -n2 and -t2 if you are not adding swap)::

       sgdisk     -n3:0:0        -t3:8309 -c 0:root $DISK

   If you are creating a mirror or raidz topology, repeat the partitioning
   commands for all the disks which will be part of the pool.

#. Create the root pool (change the disk to ${DISK}-part2 if you added a swap partition in the previous step):

   Choose one of the following options:

   - Unencrypted::

       zpool create \
           -o ashift=12 \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part3

   - ZFS native encryption::

       zpool create \
           -o ashift=12 \
           -O encryption=aes-256-gcm \
           -O keylocation=prompt -O keyformat=passphrase \
           -O acltype=posixacl -O canmount=off -O compression=lz4 \
           -O dnodesize=auto -O normalization=formD -O relatime=on \
           -O xattr=sa -O mountpoint=/ -R /mnt \
           rpool ${DISK}-part3

   - LUKS::

       dnf install cryptsetup
       cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part3 # change -part 3 to -part2 if swap partition was not made during partitioning
       cryptsetup luksOpen ${DISK}-part3 luks1
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
           rpool mirror \
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

#. Create the filesystem datasets to act as containers::

     zfs create -o canmount=off -o mountpoint=none rpool/ROOT

   On Solaris systems, the root filesystem is cloned and the suffix is
   incremented for major system changes through ``pkg image-update`` or
   ``beadm``. Similar functionality has not yet been implemented into Fedora and will most likely never be added to Fedora in the forseeable future due to licensing issues.

#. Create filesystem datasets for the root and boot filesystems::

     zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/fedora
     zfs mount rpool/ROOT/fedora

   With ZFS, it is not normally necessary to use a mount command (either
   ``mount`` or ``zfs mount``). This situation is an exception because of
   ``canmount=noauto``.

#. Create datasets::

     zfs create                                 rpool/home
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
   
   Note that the reason why we are not fully seperating everything like we did in Ubuntu is because dnf will fail to install or update certain packages if we create too many datasets. An example of one such package is filesystem, which fails to install if other ZFS datasets are created. Another reason why is to make it easier to repair broken systems using the dracut emergency shell

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

     rsync -avxHASX / /mnt/
   
   It is important to not forget the trailing /.
   This command copies the LiveCD to our new zfs datasets and this is the only way I have found to reliably install and boot Fedora Workstation

Step 4: System Configuration
----------------------------

#. Configure the hostname:

   Replace ``HOSTNAME`` with the desired hostname::

     echo HOSTNAME > /mnt/etc/hostname
   
   Edit /mnt/etc/hosts using the text editor of your choice. 
   If the system does not have a real name in DNS, add this line::

     127.0.1.1       HOSTNAME
   
   Otherwise, if the system has a real name in DNS, add this line::

     127.0.1.1       FQDN HOSTNAME

   **Hint:** Use ``nano`` or ``vim`` if you find vi to be confusing

   .. note::
       NetworkManager, in most cases, will work without any additional configuration.

#. Bind the virtual filesystems from the LiveCD environment to the new
   system and ``chroot`` into it::

     mount --rbind /dev  /mnt/dev
     mount --rbind /proc /mnt/proc
     mount --rbind /sys  /mnt/sys
     sudo mount -o bind /run /mnt/run     
     chroot /mnt /usr/bin/env DISK=$DISK bash --login

   **Note:** This is using ``--rbind``, not ``--bind``.

#. Make sure that the output of ``echo $DISK`` is not blank. If it is, set the DISK variable like what we did in Step 2

#. Update the new system::

     dnf update --exclude=kernel* # Note: the --exclude=kernel* is optional in the majority of cases. You can remove it if you are OK with ZFS potentially (rarely) breaking due to a kernel update.

.. note::

   Note that the ZFS install we did outside in the LiveCD persists here. Hence, it is not needed to maunally install zfs-release, zfs-dracut and zfs again. Also note that cryptsetup is still extremely experimental and that the maintainer of this project does not use LUKS/cryptsetup whatsoever. Use at your own risk.

#. For LUKS installs only, setup ``/etc/crypttab``:: 

     dnf install cryptsetup

     echo luks1 UUID=$(blkid -s UUID -o value ${DISK}-part3) none \
         luks,discard,initramfs > /etc/crypttab

   The use of ``initramfs`` is a work-around for `cryptsetup does not support
   ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

   **Hint:** If you are creating a mirror or raidz topology, repeat the
   ``/etc/crypttab`` entries for ``luks2``, etc. adjusting for each disk.

#. Remove GRUB2 as it can cause problems in the future::

        rpm --nodeps -ve $(rpm -qa | grep "^grub2-") os-prober
        echo 'exclude=grub2-*,os-prober' >> /etc/dnf/dnf.conf
        rm -rf /boot

#. Install systemd-boot::

        rm -rvf /boot # Don't worry, we'll reinstall the kernel later
        mkdir boot # Create the boot folder
        dnf install dosfstools
        mkdosfs -F 32 -s 1 -n EFI ${DISK}-part1 # You should not need to change this
        # If you want to use partition UUID's (more stable, but longer to type and slightly harder to debug)
        echo PARTUUID=$(blkid -s PARTUUID -o value ${DISK}-part1) \
           /boot vfat umask=0777,shortname=lower,context=system_u:object_r:boot_t:s0,nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
        # If you want to use partition LABEL's (less stable, but shorter to type and slightly easier to debug)
        echo PARTLABEL=boot \
           /boot vfat umask=0777,shortname=lower,context=system_u:object_r:boot_t:s0,nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
        mount /boot
        uuidgen | tr -d '-' > /etc/machine-id
        mkdir -p /boot/$(</etc/machine-id)
        bootctl install # Install systemd-boot to ESP
        sudo dnf reinstall kernel-core # Reinstall the kernel
        sudo dnf reinstall zfs-dkms zfs-dracut # Reinstall the ZFS kernel module and dracut module as reinstalling the kernel can remove the ZFS kernel module

      **Notes:**

     - Use ``SYSTEMD_RELAX_XBOOTLDR_CHECKS=1 bootctl install --esp-path=/boot --boot-path=/boot`` instead of ``bootctl install`` if ``bootctl install`` fails.
     - The ``-s 1`` for ``mkdosfs`` is only necessary for drives which present
        4 KiB logical sectors (“4Kn” drives) to meet the minimum cluster size
        (given the partition size of 512 MiB) for FAT32. It also works fine on
        drives which present 512 B sectors.

#. Set a root password::

     passwd

#. Optional (but recommended): Mount a tmpfs to ``/tmp``

   If you chose to create a ``/tmp`` dataset above, skip this step, as they
   are mutually exclusive choices. Otherwise, you can put ``/tmp`` on a
   tmpfs (RAM filesystem) by enabling the ``tmp.mount`` unit.

   ::

     cp /usr/share/systemd/tmp.mount /etc/systemd/system/
     systemctl enable tmp.mount

.. note::
   GRUB installation is not supported by this guide and will not be supported in the forseeable future. The above steps should have installed systemd-boot, an alternative to GRUB which provides the majority of GRUBS features. If you still wish to use GRUB, it might be possible to chainload systemd-boot using GRUB and boot your Fedora installation that way. Instructions on how to do this will not be provided and this has not been tested to work. You are welcome to make a PR for this however

Step 6: Fixing systemd-boot config
----------------------------------

.. note:: 
   Note that dnf can sometimes mess up with configuring systemd-boot. Luckily this is very easy to fix

#. Firstly, change directory to /boot/loader/entries using ``cd /boot/loader/entries``.

#. Type ``ls``. You should see a bunch of files beginning with a random series of letters and numbers followed by a minus and then the kernel version or rescue (for example ``839fdb701b7c48d2b25ffc293bb7ee18-0-rescue.conf`` and ``839fdb701b7c48d2b25ffc293bb7ee18-5.7.0-0.rc3.1.fc33.x86_64.conf`` as examples)

#. Open each file using the text editor of your choice and look for a field called options. Delete everything you see in that line and replace it with ``options root=ZFS=rpool/ROOT/fedora``

.. note::
   Be sure to change the rpool/ROOT/fedora if you named it differently

#. Add any additional kernel options that you need and save and exit the file

Step 7: First Boot
------------------
#. Rebuild initramfs to be certain that the ZFS dracut module will be loaded on boot to mount our ZFS pools::

     dracut --kver $(uname -r) --force --add-drivers "zfs"

.. note::

   If you updated your kernel in this guide, you will need to change the $(uname -r) to your updated kernel version. You can find this in /lib/modules.

#. Optional: Snapshot the initial installation::

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

   Wait for the newly installed system to boot normally (hopefully). You will/should automatically be logged in as liveuser. Ignore any Install Fedora prompts you see for now. They will be removed when we remove the stale packages.

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

#. Remove stale packages::

     dnf remove --allowerasing --best anaconda-core anaconda-gui anaconda-widgets*

   Removal of anaconda and grub/os-prober prevent issues such as the "Install Fedora" issue and other such conflicts.


(Optional) Step 8: Configure ZVol Swap
--------------------------------------

**Caution**: On systems with extremely high memory pressure, using a
zvol for swap can result in lockup, regardless of how much swap is still
available. There is `a bug report upstream
<https://github.com/zfsonlinux/zfs/issues/7734>`__. On such systems, it is wise to create a swap partition and use that. This should have been covered in partitioning.

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

Step 9: Last Minute Fixes
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

#. (Optional, but highly recommended) Enable systemd-boot timeout menu in case latest kernel fails to boot::

     sed -i 's/#timeout.*/timeout 10/' /boot/loader/loader.conf

#. Reboot::

     reboot

Step 10: Final Cleanup
----------------------

#. Wait for the system to boot normally. Login using the account you
   created. Ensure the system (including networking) works normally.

#. Optional: Delete the snapshots of the initial installation::

     sudo zfs destroy rpool/ROOT/fedora@install

#. Optional: For LUKS installs only, backup the LUKS header::

     sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
         --header-backup-file luks1-header.dat

   Store that backup somewhere safe (e.g. cloud storage). It is protected by
   your LUKS passphrase, but you may wish to use additional encryption.

   **Hint:** If you created a mirror or raidz topology, repeat this for each
   LUKS volume (``luks2``, etc.).

#. Optional: If you want your boot partition synced between your disks, check out https://github.com/gregory-lee-bartholomew/bootsync

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

  sudo dnf install edk2-ovmf
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

For GRUB Users
~~~~~~~~~~~~~~

- If you still wish to use GRUB, you will need to set ZPOOL_VDEV_NAME_PATH=1 in environmental variables while installing and running grub-mkconfig. Instructions on how to install using GRUB will not be provided in the forseeable future. You can use the Ubuntu Root on ZFS guide as a reference on how to set that up however. PR's for GRUB support is welcome.

A Note On Kernel Updates
~~~~~~~~~~~~~~~~~~~~~~~~

Make sure to run `Step 6: Fixing systemd-boot config <#step-6-fixing-systemd-boot-config>`__. after kernel updates in case dnf messes up. 
