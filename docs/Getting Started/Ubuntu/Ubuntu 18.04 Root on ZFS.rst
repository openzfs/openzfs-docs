.. highlight:: sh

Ubuntu 18.04 Root on ZFS
========================

.. contents:: Table of Contents
  :local:

Overview
--------

Newer release available
~~~~~~~~~~~~~~~~~~~~~~~

- See :doc:`Ubuntu 20.04 Root on ZFS <./Ubuntu 20.04 Root on ZFS>` for new
  installs.

Caution
~~~~~~~

- This HOWTO uses a whole physical disk.
- Do not use these instructions for dual-booting.
- Backup your data. Any existing data will be lost.

System Requirements
~~~~~~~~~~~~~~~~~~~

- `Ubuntu 18.04.3 ("Bionic") Desktop
  CD <https://releases.ubuntu.com/18.04.3/ubuntu-18.04.3-desktop-amd64.iso>`__
  (*not* any server images)
- Installing on a drive which presents 4 KiB logical sectors (a “4Kn”
  drive) only works with UEFI booting. This not unique to ZFS. `GRUB
  does not and will not work on 4Kn with legacy (BIOS)
  booting. <http://savannah.gnu.org/bugs/?46700>`__

Computers that have less than 2 GiB of memory run ZFS slowly. 4 GiB of
memory is recommended for normal performance in basic workloads. If you
wish to use deduplication, you will need `massive amounts of
RAM <http://wiki.freebsd.org/ZFSTuningGuide#Deduplication>`__. Enabling
deduplication is a permanent change that cannot be easily reverted.

Support
~~~~~~~

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <ircs://irc.libera.chat/#zfsonlinux>`__ on `Libera Chat
<https://libera.chat/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @rlaager
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Ubuntu%2018.04%20Root%20on%20ZFS%20HOWTO:>`__.

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

This guide supports two different encryption options: unencrypted and
LUKS (full-disk encryption). With either option, all ZFS features are fully
available. ZFS native encryption is not available in Ubuntu 18.04.

Unencrypted does not encrypt anything, of course. With no encryption
happening, this option naturally has the best performance.

LUKS encrypts almost everything. The only unencrypted data is the bootloader,
kernel, and initrd. The system cannot boot without the passphrase being
entered at the console. Performance is good, but LUKS sits underneath ZFS, so
if multiple disks (mirror or raidz topologies) are used, the data has to be
encrypted once per disk.

Step 1: Prepare The Install Environment
---------------------------------------

1.1 Boot the Ubuntu Live CD. Select Try Ubuntu. Connect your system to
the Internet as appropriate (e.g. join your WiFi network). Open a
terminal (press Ctrl-Alt-T).

1.2 Setup and update the repositories::

  sudo apt-add-repository universe
  sudo apt update

1.3 Optional: Install and start the OpenSSH server in the Live CD
environment:

If you have a second system, using SSH to access the target system can
be convenient::

  passwd
  # There is no current password; hit enter at that prompt.
  sudo apt install --yes openssh-server

**Hint:** You can find your IP address with
``ip addr show scope global | grep inet``. Then, from your main machine,
connect with ``ssh ubuntu@IP``.

1.4 Become root::

  sudo -i

1.5 Install ZFS in the Live CD environment::

  apt install --yes debootstrap gdisk zfs-initramfs

Step 2: Disk Formatting
-----------------------

2.1 Set a variable with the disk name::

  DISK=/dev/disk/by-id/scsi-SATA_disk1

Always use the long ``/dev/disk/by-id/*`` aliases with ZFS. Using the
``/dev/sd*`` device nodes directly can cause sporadic import failures,
especially on systems that have more than one storage pool.

**Hints:**

- ``ls -la /dev/disk/by-id`` will list the aliases.
- Are you doing this in a virtual machine? If your virtual disk is
  missing from ``/dev/disk/by-id``, use ``/dev/vda`` if you are using
  KVM with virtio; otherwise, read the
  `troubleshooting <#troubleshooting>`__ section.

2.2 If you are re-using a disk, clear it as necessary:

If the disk was previously used in an MD array, zero the superblock::

  apt install --yes mdadm
  mdadm --zero-superblock --force $DISK

Clear the partition table::

  sgdisk --zap-all $DISK

2.3 Partition your disk(s):

Run this if you need legacy (BIOS) booting::

  sgdisk -a1 -n1:24K:+1000K -t1:EF02 $DISK

Run this for UEFI booting (for use now or in the future)::

  sgdisk     -n2:1M:+512M   -t2:EF00 $DISK

Run this for the boot pool::

  sgdisk     -n3:0:+1G      -t3:BF01 $DISK

Choose one of the following options:

2.3a Unencrypted::

  sgdisk     -n4:0:0        -t4:BF01 $DISK

2.3b LUKS::

  sgdisk     -n4:0:0        -t4:8300 $DISK

If you are creating a mirror or raidz topology, repeat the partitioning
commands for all the disks which will be part of the pool.

2.4 Create the boot pool::

  zpool create -o ashift=12 -d \
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
      -O acltype=posixacl -O canmount=off -O compression=lz4 -O devices=off \
      -O normalization=formD -O relatime=on -O xattr=sa \
      -O mountpoint=/ -R /mnt bpool ${DISK}-part3

You should not need to customize any of the options for the boot pool.

GRUB does not support all of the zpool features. See
``spa_feature_names`` in
`grub-core/fs/zfs/zfs.c <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
This step creates a separate boot pool for ``/boot`` with the features
limited to only those that GRUB supports, allowing the root pool to use
any/all features. Note that GRUB opens the pool read-only, so all
read-only compatible features are “supported” by GRUB.

**Hints:**

- If you are creating a mirror or raidz topology, create the pool using
  ``zpool create ... bpool mirror /dev/disk/by-id/scsi-SATA_disk1-part3 /dev/disk/by-id/scsi-SATA_disk2-part3``
  (or replace ``mirror`` with ``raidz``, ``raidz2``, or ``raidz3`` and
  list the partitions from additional disks).
- The pool name is arbitrary. If changed, the new name must be used
  consistently. The ``bpool`` convention originated in this HOWTO.

**Feature Notes:**

- As a read-only compatible feature, the ``userobj_accounting`` feature should
  be compatible in theory, but in practice, GRUB can fail with an “invalid
  dnode type” error. This feature does not matter for ``/boot`` anyway.

2.5 Create the root pool:

Choose one of the following options:

2.5a Unencrypted::

  zpool create -o ashift=12 \
      -O acltype=posixacl -O canmount=off -O compression=lz4 \
      -O dnodesize=auto -O normalization=formD -O relatime=on -O xattr=sa \
      -O mountpoint=/ -R /mnt rpool ${DISK}-part4

2.5b LUKS::

  cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part4
  cryptsetup luksOpen ${DISK}-part4 luks1
  zpool create -o ashift=12 \
      -O acltype=posixacl -O canmount=off -O compression=lz4 \
      -O dnodesize=auto -O normalization=formD -O relatime=on -O xattr=sa \
      -O mountpoint=/ -R /mnt rpool /dev/mapper/luks1

**Notes:**

- The use of ``ashift=12`` is recommended here because many drives
  today have 4 KiB (or larger) physical sectors, even though they
  present 512 B logical sectors. Also, a future replacement drive may
  have 4 KiB physical sectors (in which case ``ashift=12`` is desirable)
  or 4 KiB logical sectors (in which case ``ashift=12`` is required).
- Setting ``-O acltype=posixacl`` enables POSIX ACLs globally. If you
  do not want this, remove that option, but later add
  ``-o acltype=posixacl`` (note: lowercase “o”) to the ``zfs create``
  for ``/var/log``, as `journald requires
  ACLs <https://askubuntu.com/questions/970886/journalctl-says-failed-to-search-journal-acl-operation-not-supported>`__
- Setting ``normalization=formD`` eliminates some corner cases relating
  to UTF-8 filename normalization. It also implies ``utf8only=on``,
  which means that only UTF-8 filenames are allowed. If you care to
  support non-UTF-8 filenames, do not use this option. For a discussion
  of why requiring UTF-8 filenames may be a bad idea, see `The problems
  with enforced UTF-8 only
  filenames <http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames>`__.
- ``recordsize`` is unset (leaving it at the default of 128 KiB). If you want to
  tune it (e.g. ``-o recordsize=1M``), see `these
  <https://jrs-s.net/2019/04/03/on-zfs-recordsize/>`__ `various
  <http://blog.programster.org/zfs-record-size>`__ `blog
  <https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSFileRecordsizeGrowth>`__
  `posts
  <https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSRecordsizeAndCompression>`__.
- Setting ``relatime=on`` is a middle ground between classic POSIX
  ``atime`` behavior (with its significant performance impact) and
  ``atime=off`` (which provides the best performance by completely
  disabling atime updates). Since Linux 2.6.30, ``relatime`` has been
  the default for other filesystems. See `RedHat’s
  documentation <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/power_management_guide/relatime>`__
  for further information.
- Setting ``xattr=sa`` `vastly improves the performance of extended
  attributes <https://github.com/zfsonlinux/zfs/commit/82a37189aac955c81a59a5ecc3400475adb56355>`__.
  Inside ZFS, extended attributes are used to implement POSIX ACLs.
  Extended attributes can also be used by user-space applications.
  `They are used by some desktop GUI
  applications. <https://en.wikipedia.org/wiki/Extended_file_attributes#Linux>`__
  `They can be used by Samba to store Windows ACLs and DOS attributes;
  they are required for a Samba Active Directory domain
  controller. <https://wiki.samba.org/index.php/Setting_up_a_Share_Using_Windows_ACLs>`__
  Note that ``xattr=sa`` is
  `Linux-specific <https://openzfs.org/wiki/Platform_code_differences>`__.
  If you move your ``xattr=sa`` pool to another OpenZFS implementation
  besides ZFS-on-Linux, extended attributes will not be readable
  (though your data will be). If portability of extended attributes is
  important to you, omit the ``-O xattr=sa`` above. Even if you do not
  want ``xattr=sa`` for the whole pool, it is probably fine to use it
  for ``/var/log``.
- Make sure to include the ``-part4`` portion of the drive path. If you
  forget that, you are specifying the whole disk, which ZFS will then
  re-partition, and you will lose the bootloader partition(s).
- For LUKS, the key size chosen is 512 bits. However, XTS mode requires
  two keys, so the LUKS key is split in half. Thus, ``-s 512`` means
  AES-256.
- Your passphrase will likely be the weakest link. Choose wisely. See
  `section 5 of the cryptsetup
  FAQ <https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions#5-security-aspects>`__
  for guidance.

**Hints:**

- If you are creating a mirror or raidz topology, create the pool using
  ``zpool create ... rpool mirror /dev/disk/by-id/scsi-SATA_disk1-part4 /dev/disk/by-id/scsi-SATA_disk2-part4``
  (or replace ``mirror`` with ``raidz``, ``raidz2``, or ``raidz3`` and
  list the partitions from additional disks). For LUKS, use
  ``/dev/mapper/luks1``, ``/dev/mapper/luks2``, etc., which you will
  have to create using ``cryptsetup``.
- The pool name is arbitrary. If changed, the new name must be used
  consistently. On systems that can automatically install to ZFS, the
  root pool is named ``rpool`` by default.

Step 3: System Installation
---------------------------

3.1 Create filesystem datasets to act as containers::

  zfs create -o canmount=off -o mountpoint=none rpool/ROOT
  zfs create -o canmount=off -o mountpoint=none bpool/BOOT

On Solaris systems, the root filesystem is cloned and the suffix is
incremented for major system changes through ``pkg image-update`` or
``beadm``. Similar functionality has been implemented in Ubuntu 20.04 with the
``zsys`` tool, though its dataset layout is more complicated. Even without
such a tool, the `rpool/ROOT` and `bpool/BOOT` containers can still be used
for manually created clones.

3.2 Create filesystem datasets for the root and boot filesystems::

  zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/ubuntu
  zfs mount rpool/ROOT/ubuntu

  zfs create -o canmount=noauto -o mountpoint=/boot bpool/BOOT/ubuntu
  zfs mount bpool/BOOT/ubuntu

With ZFS, it is not normally necessary to use a mount command (either
``mount`` or ``zfs mount``). This situation is an exception because of
``canmount=noauto``.

3.3 Create datasets::

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

If you use /opt on this system::

  zfs create                                 rpool/opt

If you use /srv on this system::

  zfs create                                 rpool/srv

If you use /usr/local on this system::

  zfs create -o canmount=off                 rpool/usr
  zfs create                                 rpool/usr/local

If this system will have games installed::

  zfs create                                 rpool/var/games

If this system will store local email in /var/mail::

  zfs create                                 rpool/var/mail

If this system will use Snap packages::

  zfs create                                 rpool/var/snap

If you use /var/www on this system::

  zfs create                                 rpool/var/www

If this system will use GNOME::

  zfs create                                 rpool/var/lib/AccountsService

If this system will use Docker (which manages its own datasets &
snapshots)::

  zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/docker

If this system will use NFS (locking)::

  zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/nfs

A tmpfs is recommended later, but if you want a separate dataset for
``/tmp``::

  zfs create -o com.sun:auto-snapshot=false  rpool/tmp
  chmod 1777 /mnt/tmp

The primary goal of this dataset layout is to separate the OS from user data.
This allows the root filesystem to be rolled back without rolling back user
data. The ``com.sun.auto-snapshot`` setting is used by some ZFS
snapshot utilities to exclude transient data.

If you do nothing extra, ``/tmp`` will be stored as part of the root
filesystem. Alternatively, you can create a separate dataset for
``/tmp``, as shown above. This keeps the ``/tmp`` data out of snapshots
of your root filesystem. It also allows you to set a quota on
``rpool/tmp``, if you want to limit the maximum space used. Otherwise,
you can use a tmpfs (RAM filesystem) later.

3.4 Install the minimal system::

  debootstrap bionic /mnt
  zfs set devices=off rpool

The ``debootstrap`` command leaves the new system in an unconfigured
state. An alternative to using ``debootstrap`` is to copy the entirety
of a working system into the new ZFS root.

Step 4: System Configuration
----------------------------

4.1 Configure the hostname:

Replace ``HOSTNAME`` with the desired hostname::

  echo HOSTNAME > /mnt/etc/hostname
  vi /mnt/etc/hosts

.. code-block:: text

  Add a line:
  127.0.1.1       HOSTNAME
  or if the system has a real name in DNS:
  127.0.1.1       FQDN HOSTNAME

**Hint:** Use ``nano`` if you find ``vi`` confusing.

4.2 Configure the network interface:

Find the interface name::

  ip addr show

Adjust NAME below to match your interface name::

  vi /mnt/etc/netplan/01-netcfg.yaml

.. code-block:: yaml

  network:
    version: 2
    ethernets:
      NAME:
        dhcp4: true

Customize this file if the system is not a DHCP client.

4.3 Configure the package sources::

  vi /mnt/etc/apt/sources.list

.. code-block:: sourceslist

  deb http://archive.ubuntu.com/ubuntu bionic main restricted universe multiverse
  deb http://archive.ubuntu.com/ubuntu bionic-updates main restricted universe multiverse
  deb http://archive.ubuntu.com/ubuntu bionic-backports main restricted universe multiverse
  deb http://security.ubuntu.com/ubuntu bionic-security main restricted universe multiverse

4.4 Bind the virtual filesystems from the LiveCD environment to the new
system and ``chroot`` into it::

  mount --rbind /dev  /mnt/dev
  mount --rbind /proc /mnt/proc
  mount --rbind /sys  /mnt/sys
  chroot /mnt /usr/bin/env DISK=$DISK bash --login

**Note:** This is using ``--rbind``, not ``--bind``.

4.5 Configure a basic system environment::

  ln -s /proc/self/mounts /etc/mtab
  apt update

Even if you prefer a non-English system language, always ensure that
``en_US.UTF-8`` is available::

  dpkg-reconfigure locales
  dpkg-reconfigure tzdata

If you prefer ``nano`` over ``vi``, install it::

  apt install --yes nano

4.6 Install ZFS in the chroot environment for the new system::

  apt install --yes --no-install-recommends linux-image-generic
  apt install --yes zfs-initramfs

**Hint:** For the HWE kernel, install ``linux-image-generic-hwe-18.04``
instead of ``linux-image-generic``.

4.7 For LUKS installs only, setup ``/etc/crypttab``::

  apt install --yes cryptsetup

  echo luks1 UUID=$(blkid -s UUID -o value ${DISK}-part4) none \
      luks,discard,initramfs > /etc/crypttab

The use of ``initramfs`` is a work-around for `cryptsetup does not support ZFS
<https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

**Hint:** If you are creating a mirror or raidz topology, repeat the
``/etc/crypttab`` entries for ``luks2``, etc. adjusting for each disk.

4.8 Install GRUB

Choose one of the following options:

4.8a Install GRUB for legacy (BIOS) booting::

  apt install --yes grub-pc

Select (using the space bar) all of the disks (not partitions) in your pool.

4.8b Install GRUB for UEFI booting::

  apt install dosfstools
  mkdosfs -F 32 -s 1 -n EFI ${DISK}-part2
  mkdir /boot/efi
  echo PARTUUID=$(blkid -s PARTUUID -o value ${DISK}-part2) \
      /boot/efi vfat nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
  mount /boot/efi
  apt install --yes grub-efi-amd64-signed shim-signed

**Notes:**

- The ``-s 1`` for ``mkdosfs`` is only necessary for drives which present
  4 KiB logical sectors (“4Kn” drives) to meet the minimum cluster size
  (given the partition size of 512 MiB) for FAT32. It also works fine on
  drives which present 512 B sectors.
- For a mirror or raidz topology, this step only installs GRUB on the
  first disk. The other disk(s) will be handled later.

4.9 (Optional): Remove os-prober::

    apt remove --purge os-prober

This avoids error messages from `update-grub`.  `os-prober` is only necessary
in dual-boot configurations.

4.10 Set a root password::

  passwd

4.11 Enable importing bpool

This ensures that ``bpool`` is always imported, regardless of whether
``/etc/zfs/zpool.cache`` exists, whether it is in the cachefile or not,
or whether ``zfs-import-scan.service`` is enabled.

::

      vi /etc/systemd/system/zfs-import-bpool.service

.. code-block:: ini

      [Unit]
      DefaultDependencies=no
      Before=zfs-import-scan.service
      Before=zfs-import-cache.service

      [Service]
      Type=oneshot
      RemainAfterExit=yes
      ExecStart=/sbin/zpool import -N -o cachefile=none bpool

      [Install]
      WantedBy=zfs-import.target

::

  systemctl enable zfs-import-bpool.service

4.12 Optional (but recommended): Mount a tmpfs to ``/tmp``

If you chose to create a ``/tmp`` dataset above, skip this step, as they
are mutually exclusive choices. Otherwise, you can put ``/tmp`` on a
tmpfs (RAM filesystem) by enabling the ``tmp.mount`` unit.

::

  cp /usr/share/systemd/tmp.mount /etc/systemd/system/
  systemctl enable tmp.mount

4.13 Setup system groups::

  addgroup --system lpadmin
  addgroup --system sambashare

Step 5: GRUB Installation
-------------------------

5.1 Verify that the ZFS boot filesystem is recognized::

  grub-probe /boot

5.2 Refresh the initrd files::

  update-initramfs -c -k all

**Note:** When using LUKS, this will print “WARNING could not determine
root device from /etc/fstab”. This is because `cryptsetup does not
support ZFS
<https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

5.3 Workaround GRUB's missing zpool-features support::

  vi /etc/default/grub
  # Set: GRUB_CMDLINE_LINUX="root=ZFS=rpool/ROOT/ubuntu"

5.4 Optional (but highly recommended): Make debugging GRUB easier::

  vi /etc/default/grub
  # Comment out: GRUB_TIMEOUT_STYLE=hidden
  # Set: GRUB_TIMEOUT=5
  # Below GRUB_TIMEOUT, add: GRUB_RECORDFAIL_TIMEOUT=5
  # Remove quiet and splash from: GRUB_CMDLINE_LINUX_DEFAULT
  # Uncomment: GRUB_TERMINAL=console
  # Save and quit.

Later, once the system has rebooted twice and you are sure everything is
working, you can undo these changes, if desired.

5.5 Update the boot configuration::

  update-grub

**Note:** Ignore errors from ``osprober``, if present.

5.6 Install the boot loader:

5.6a For legacy (BIOS) booting, install GRUB to the MBR::

  grub-install $DISK

Note that you are installing GRUB to the whole disk, not a partition.

If you are creating a mirror or raidz topology, repeat the
``grub-install`` command for each disk in the pool.

5.6b For UEFI booting, install GRUB::

  grub-install --target=x86_64-efi --efi-directory=/boot/efi \
      --bootloader-id=ubuntu --recheck --no-floppy

It is not necessary to specify the disk here. If you are creating a
mirror or raidz topology, the additional disks will be handled later.

5.7 Fix filesystem mount ordering:

`Until ZFS gains a systemd mount
generator <https://github.com/zfsonlinux/zfs/issues/4898>`__, there are
races between mounting filesystems and starting certain daemons. In
practice, the issues (e.g.
`#5754 <https://github.com/zfsonlinux/zfs/issues/5754>`__) seem to be
with certain filesystems in ``/var``, specifically ``/var/log`` and
``/var/tmp``. Setting these to use ``legacy`` mounting, and listing them
in ``/etc/fstab`` makes systemd aware that these are separate
mountpoints. In turn, ``rsyslog.service`` depends on ``var-log.mount``
by way of ``local-fs.target`` and services using the ``PrivateTmp``
feature of systemd automatically use ``After=var-tmp.mount``.

Until there is support for mounting ``/boot`` in the initramfs, we also
need to mount that, because it was marked ``canmount=noauto``. Also,
with UEFI, we need to ensure it is mounted before its child filesystem
``/boot/efi``.

``rpool`` is guaranteed to be imported by the initramfs, so there is no
point in adding ``x-systemd.requires=zfs-import.target`` to those
filesystems.

For UEFI booting, unmount /boot/efi first::

  umount /boot/efi

Everything else applies to both BIOS and UEFI booting::

  zfs set mountpoint=legacy bpool/BOOT/ubuntu
  echo bpool/BOOT/ubuntu /boot zfs \
      nodev,relatime,x-systemd.requires=zfs-import-bpool.service 0 0 >> /etc/fstab

  zfs set mountpoint=legacy rpool/var/log
  echo rpool/var/log /var/log zfs nodev,relatime 0 0 >> /etc/fstab

  zfs set mountpoint=legacy rpool/var/spool
  echo rpool/var/spool /var/spool zfs nodev,relatime 0 0 >> /etc/fstab

If you created a /var/tmp dataset::

  zfs set mountpoint=legacy rpool/var/tmp
  echo rpool/var/tmp /var/tmp zfs nodev,relatime 0 0 >> /etc/fstab

If you created a /tmp dataset::

  zfs set mountpoint=legacy rpool/tmp
  echo rpool/tmp /tmp zfs nodev,relatime 0 0 >> /etc/fstab

Step 6: First Boot
------------------

6.1 Snapshot the initial installation::

  zfs snapshot bpool/BOOT/ubuntu@install
  zfs snapshot rpool/ROOT/ubuntu@install

In the future, you will likely want to take snapshots before each
upgrade, and remove old snapshots (including this one) at some point to
save space.

6.2 Exit from the ``chroot`` environment back to the LiveCD environment::

  exit

6.3 Run these commands in the LiveCD environment to unmount all
filesystems::

  mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
  zpool export -a

6.4 Reboot::

  reboot

Wait for the newly installed system to boot normally. Login as root.

6.5 Create a user account:

Replace ``username`` with your desired username::

  zfs create rpool/home/username
  adduser username

  cp -a /etc/skel/. /home/username
  chown -R username:username /home/username
  usermod -a -G audio,cdrom,dip,floppy,netdev,plugdev,sudo,video username

6.6 Mirror GRUB

If you installed to multiple disks, install GRUB on the additional
disks:

6.6a For legacy (BIOS) booting::

  dpkg-reconfigure grub-pc
  Hit enter until you get to the device selection screen.
  Select (using the space bar) all of the disks (not partitions) in your pool.

6.6b For UEFI booting::

  umount /boot/efi

For the second and subsequent disks (increment ubuntu-2 to -3, etc.)::

  dd if=/dev/disk/by-id/scsi-SATA_disk1-part2 \
     of=/dev/disk/by-id/scsi-SATA_disk2-part2
  efibootmgr -c -g -d /dev/disk/by-id/scsi-SATA_disk2 \
      -p 2 -L "ubuntu-2" -l '\EFI\ubuntu\shimx64.efi'

  mount /boot/efi

Step 7: (Optional) Configure Swap
---------------------------------

**Caution**: On systems with extremely high memory pressure, using a
zvol for swap can result in lockup, regardless of how much swap is still
available. This issue is currently being investigated in:
`https://github.com/zfsonlinux/zfs/issues/7734 <https://github.com/zfsonlinux/zfs/issues/7734>`__

7.1 Create a volume dataset (zvol) for use as a swap device::

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

7.2 Configure the swap device:

**Caution**: Always use long ``/dev/zvol`` aliases in configuration
files. Never use a short ``/dev/zdX`` device name.

::

  mkswap -f /dev/zvol/rpool/swap
  echo /dev/zvol/rpool/swap none swap discard 0 0 >> /etc/fstab
  echo RESUME=none > /etc/initramfs-tools/conf.d/resume

The ``RESUME=none`` is necessary to disable resuming from hibernation.
This does not work, as the zvol is not present (because the pool has not
yet been imported) at the time the resume script runs. If it is not
disabled, the boot process hangs for 30 seconds waiting for the swap
zvol to appear.

7.3 Enable the swap device::

  swapon -av

Step 8: Full Software Installation
----------------------------------

8.1 Upgrade the minimal system::

  apt dist-upgrade --yes

8.2 Install a regular set of software:

Choose one of the following options:

8.2a Install a command-line environment only::

  apt install --yes ubuntu-standard

8.2b Install a full GUI environment::

  apt install --yes ubuntu-desktop
  vi /etc/gdm3/custom.conf
  # In the [daemon] section, add: InitialSetupEnable=false

**Hint**: If you are installing a full GUI environment, you will likely
want to manage your network with NetworkManager::

  rm /mnt/etc/netplan/01-netcfg.yaml
  vi /etc/netplan/01-network-manager-all.yaml

.. code-block:: yaml

  network:
    version: 2
    renderer: NetworkManager

8.3 Optional: Disable log compression:

As ``/var/log`` is already compressed by ZFS, logrotate’s compression is
going to burn CPU and disk I/O for (in most cases) very little gain.
Also, if you are making snapshots of ``/var/log``, logrotate’s
compression will actually waste space, as the uncompressed data will
live on in the snapshot. You can edit the files in ``/etc/logrotate.d``
by hand to comment out ``compress``, or use this loop (copy-and-paste
highly recommended)::

  for file in /etc/logrotate.d/* ; do
      if grep -Eq "(^|[^#y])compress" "$file" ; then
          sed -i -r "s/(^|[^#y])(compress)/\1#\2/" "$file"
      fi
  done

8.4 Reboot::

  reboot

Step 9: Final Cleanup
---------------------

9.1 Wait for the system to boot normally. Login using the account you
created. Ensure the system (including networking) works normally.

9.2 Optional: Delete the snapshots of the initial installation::

  sudo zfs destroy bpool/BOOT/ubuntu@install
  sudo zfs destroy rpool/ROOT/ubuntu@install

9.3 Optional: Disable the root password::

  sudo usermod -p '*' root

9.4 Optional: Re-enable the graphical boot process:

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

9.5 Optional: For LUKS installs only, backup the LUKS header::

  sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
      --header-backup-file luks1-header.dat

Store that backup somewhere safe (e.g. cloud storage). It is protected
by your LUKS passphrase, but you may wish to use additional encryption.

**Hint:** If you created a mirror or raidz topology, repeat this for
each LUKS volume (``luks2``, etc.).

Troubleshooting
---------------

Rescuing using a Live CD
~~~~~~~~~~~~~~~~~~~~~~~~

Go through `Step 1: Prepare The Install
Environment <#step-1-prepare-the-install-environment>`__.

For LUKS, first unlock the disk(s)::

  cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
  # Repeat for additional disks, if this is a mirror or raidz topology.

Mount everything correctly::

  zpool export -a
  zpool import -N -R /mnt rpool
  zpool import -N -R /mnt bpool
  zfs mount rpool/ROOT/ubuntu
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
  mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
  zpool export -a
  reboot

MPT2SAS
~~~~~~~

Most problem reports for this tutorial involve ``mpt2sas`` hardware that
does slow asynchronous drive initialization, like some IBM M1015 or
OEM-branded cards that have been flashed to the reference LSI firmware.

The basic problem is that disks on these controllers are not visible to
the Linux kernel until after the regular system is started, and ZoL does
not hotplug pool members. See
`https://github.com/zfsonlinux/zfs/issues/330 <https://github.com/zfsonlinux/zfs/issues/330>`__.

Most LSI cards are perfectly compatible with ZoL. If your card has this
glitch, try setting ``ZFS_INITRD_PRE_MOUNTROOT_SLEEP=X`` in
``/etc/default/zfs``. The system will wait ``X`` seconds for all drives to
appear before importing the pool.

Areca
~~~~~

Systems that require the ``arcsas`` blob driver should add it to the
``/etc/initramfs-tools/modules`` file and run
``update-initramfs -c -k all``.

Upgrade or downgrade the Areca driver if something like
``RIP: 0010:[<ffffffff8101b316>]  [<ffffffff8101b316>] native_read_tsc+0x6/0x20``
appears anywhere in kernel log. ZoL is unstable on systems that emit
this error message.

VMware
~~~~~~

- Set ``disk.EnableUUID = "TRUE"`` in the vmx file or vsphere
  configuration. Doing this ensures that ``/dev/disk`` aliases are
  created in the guest.

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
     "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd"
  ]

::

  sudo systemctl restart libvirtd.service
