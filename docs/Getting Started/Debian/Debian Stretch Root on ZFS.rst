Debian Stretch Root on ZFS
==========================

.. contents:: Table of Contents
  :local:

Overview
--------

Newer release available
~~~~~~~~~~~~~~~~~~~~~~~

- See :doc:`Debian Buster Root on ZFS <./Debian Buster Root on ZFS>` for new
  installs.

Caution
~~~~~~~

- This HOWTO uses a whole physical disk.
- Do not use these instructions for dual-booting.
- Backup your data. Any existing data will be lost.

System Requirements
~~~~~~~~~~~~~~~~~~~

- `64-bit Debian GNU/Linux Stretch Live
  CD <http://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/>`__
- `A 64-bit kernel is strongly
  encouraged. <https://github.com/zfsonlinux/zfs/wiki/FAQ#32-bit-vs-64-bit-systems>`__
- Installing on a drive which presents 4KiB logical sectors (a “4Kn”
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
`#zfsonlinux <irc://irc.freenode.net/#zfsonlinux>`__ on `freenode
<https://freenode.net/>`__. If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @rlaager
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Debian%20Stretch%20Root%20on%20ZFS%20HOWTO:>`__.

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
LUKS (full-disk encryption). ZFS native encryption has not yet been
released. With either option, all ZFS features are fully available.

Unencrypted does not encrypt anything, of course. With no encryption
happening, this option naturally has the best performance.

LUKS encrypts almost everything: the OS, swap, home directories, and
anything else. The only unencrypted data is the bootloader, kernel, and
initrd. The system cannot boot without the passphrase being entered at
the console. Performance is good, but LUKS sits underneath ZFS, so if
multiple disks (mirror or raidz topologies) are used, the data has to be
encrypted once per disk.

Step 1: Prepare The Install Environment
---------------------------------------

1.1 Boot the Debian GNU/Linux Live CD. If prompted, login with the
username ``user`` and password ``live``. Connect your system to the
Internet as appropriate (e.g. join your WiFi network).

1.2 Optional: Install and start the OpenSSH server in the Live CD
environment:

If you have a second system, using SSH to access the target system can
be convenient.

::

  $ sudo apt update
  $ sudo apt install --yes openssh-server
  $ sudo systemctl restart ssh

**Hint:** You can find your IP address with
``ip addr show scope global | grep inet``. Then, from your main machine,
connect with ``ssh user@IP``.

1.3 Become root:

::

  $ sudo -i

1.4 Setup and update the repositories:

::

  # echo deb http://deb.debian.org/debian stretch contrib >> /etc/apt/sources.list
  # echo deb http://deb.debian.org/debian stretch-backports main contrib >> /etc/apt/sources.list
  # apt update

1.5 Install ZFS in the Live CD environment:

::

  # apt install --yes debootstrap gdisk dkms dpkg-dev linux-headers-$(uname -r)
  # apt install --yes -t stretch-backports zfs-dkms
  # modprobe zfs

- The dkms dependency is installed manually just so it comes from
  stretch and not stretch-backports. This is not critical.

Step 2: Disk Formatting
-----------------------

2.1 If you are re-using a disk, clear it as necessary:

::

  If the disk was previously used in an MD array, zero the superblock:
  # apt install --yes mdadm
  # mdadm --zero-superblock --force /dev/disk/by-id/scsi-SATA_disk1

  Clear the partition table:
  # sgdisk --zap-all /dev/disk/by-id/scsi-SATA_disk1

2.2 Partition your disk(s):

::

  Run this if you need legacy (BIOS) booting:
  # sgdisk -a1 -n1:24K:+1000K -t1:EF02 /dev/disk/by-id/scsi-SATA_disk1

  Run this for UEFI booting (for use now or in the future):
  # sgdisk     -n2:1M:+512M   -t2:EF00 /dev/disk/by-id/scsi-SATA_disk1

  Run this for the boot pool:
  # sgdisk     -n3:0:+1G      -t3:BF01 /dev/disk/by-id/scsi-SATA_disk1

Choose one of the following options:

2.2a Unencrypted:

::

  # sgdisk     -n4:0:0        -t4:BF01 /dev/disk/by-id/scsi-SATA_disk1

2.2b LUKS:

::

  # sgdisk     -n4:0:0        -t4:8300 /dev/disk/by-id/scsi-SATA_disk1

Always use the long ``/dev/disk/by-id/*`` aliases with ZFS. Using the
``/dev/sd*`` device nodes directly can cause sporadic import failures,
especially on systems that have more than one storage pool.

**Hints:**

- ``ls -la /dev/disk/by-id`` will list the aliases.
- Are you doing this in a virtual machine? If your virtual disk is
  missing from ``/dev/disk/by-id``, use ``/dev/vda`` if you are using
  KVM with virtio; otherwise, read the
  `troubleshooting <#troubleshooting>`__ section.
- If you are creating a mirror or raidz topology, repeat the
  partitioning commands for all the disks which will be part of the
  pool.

2.3 Create the boot pool:

::

  # zpool create -o ashift=12 -d \
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
        -o feature@userobj_accounting=enabled \
        -O acltype=posixacl -O canmount=off -O compression=lz4 -O devices=off \
        -O normalization=formD -O relatime=on -O xattr=sa \
        -O mountpoint=/ -R /mnt \
        bpool /dev/disk/by-id/scsi-SATA_disk1-part3

You should not need to customize any of the options for the boot pool.

GRUB does not support all of the zpool features. See
``spa_feature_names`` in
`grub-core/fs/zfs/zfs.c <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
This step creates a separate boot pool for ``/boot`` with the features
limited to only those that GRUB supports, allowing the root pool to use
any/all features. Note that GRUB opens the pool read-only, so all
read-only compatible features are "supported" by GRUB.

**Hints:**

- If you are creating a mirror or raidz topology, create the pool using
  ``zpool create ... bpool mirror /dev/disk/by-id/scsi-SATA_disk1-part3 /dev/disk/by-id/scsi-SATA_disk2-part3``
  (or replace ``mirror`` with ``raidz``, ``raidz2``, or ``raidz3`` and
  list the partitions from additional disks).
- The pool name is arbitrary. If changed, the new name must be used
  consistently. The ``bpool`` convention originated in this HOWTO.

2.4 Create the root pool:

Choose one of the following options:

2.4a Unencrypted:

::

  # zpool create -o ashift=12 \
        -O acltype=posixacl -O canmount=off -O compression=lz4 \
        -O dnodesize=auto -O normalization=formD -O relatime=on -O xattr=sa \
        -O mountpoint=/ -R /mnt \
        rpool /dev/disk/by-id/scsi-SATA_disk1-part4

2.4b LUKS:

::

  # apt install --yes cryptsetup
  # cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 \
        /dev/disk/by-id/scsi-SATA_disk1-part4
  # cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
  # zpool create -o ashift=12 \
        -O acltype=posixacl -O canmount=off -O compression=lz4 \
        -O dnodesize=auto -O normalization=formD -O relatime=on -O xattr=sa \
        -O mountpoint=/ -R /mnt \
        rpool /dev/mapper/luks1

- The use of ``ashift=12`` is recommended here because many drives
  today have 4KiB (or larger) physical sectors, even though they
  present 512B logical sectors. Also, a future replacement drive may
  have 4KiB physical sectors (in which case ``ashift=12`` is desirable)
  or 4KiB logical sectors (in which case ``ashift=12`` is required).
- Setting ``-O acltype=posixacl`` enables POSIX ACLs globally. If you
  do not want this, remove that option, but later add
  ``-o acltype=posixacl`` (note: lowercase "o") to the ``zfs create``
  for ``/var/log``, as `journald requires
  ACLs <https://askubuntu.com/questions/970886/journalctl-says-failed-to-search-journal-acl-operation-not-supported>`__
- Setting ``normalization=formD`` eliminates some corner cases relating
  to UTF-8 filename normalization. It also implies ``utf8only=on``,
  which means that only UTF-8 filenames are allowed. If you care to
  support non-UTF-8 filenames, do not use this option. For a discussion
  of why requiring UTF-8 filenames may be a bad idea, see `The problems
  with enforced UTF-8 only
  filenames <http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames>`__.
- Setting ``relatime=on`` is a middle ground between classic POSIX
  ``atime`` behavior (with its significant performance impact) and
  ``atime=off`` (which provides the best performance by completely
  disabling atime updates). Since Linux 2.6.30, ``relatime`` has been
  the default for other filesystems. See `RedHat's
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
  Note that ```xattr=sa`` is
  Linux-specific. <https://openzfs.org/wiki/Platform_code_differences>`__
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

3.1 Create filesystem datasets to act as containers:

::

  # zfs create -o canmount=off -o mountpoint=none rpool/ROOT
  # zfs create -o canmount=off -o mountpoint=none bpool/BOOT

On Solaris systems, the root filesystem is cloned and the suffix is
incremented for major system changes through ``pkg image-update`` or
``beadm``. Similar functionality for APT is possible but currently
unimplemented. Even without such a tool, it can still be used for
manually created clones.

3.2 Create filesystem datasets for the root and boot filesystems:

::

  # zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/debian
  # zfs mount rpool/ROOT/debian

  # zfs create -o canmount=noauto -o mountpoint=/boot bpool/BOOT/debian
  # zfs mount bpool/BOOT/debian

With ZFS, it is not normally necessary to use a mount command (either
``mount`` or ``zfs mount``). This situation is an exception because of
``canmount=noauto``.

3.3 Create datasets:

::

  # zfs create                                 rpool/home
  # zfs create -o mountpoint=/root             rpool/home/root
  # zfs create -o canmount=off                 rpool/var
  # zfs create -o canmount=off                 rpool/var/lib
  # zfs create                                 rpool/var/log
  # zfs create                                 rpool/var/spool

  The datasets below are optional, depending on your preferences and/or
  software choices:

  If you wish to exclude these from snapshots:
  # zfs create -o com.sun:auto-snapshot=false  rpool/var/cache
  # zfs create -o com.sun:auto-snapshot=false  rpool/var/tmp
  # chmod 1777 /mnt/var/tmp

  If you use /opt on this system:
  # zfs create                                 rpool/opt

  If you use /srv on this system:
  # zfs create                                 rpool/srv

  If you use /usr/local on this system:
  # zfs create -o canmount=off                 rpool/usr
  # zfs create                                 rpool/usr/local

  If this system will have games installed:
  # zfs create                                 rpool/var/games

  If this system will store local email in /var/mail:
  # zfs create                                 rpool/var/mail

  If this system will use Snap packages:
  # zfs create                                 rpool/var/snap

  If you use /var/www on this system:
  # zfs create                                 rpool/var/www

  If this system will use GNOME:
  # zfs create                                 rpool/var/lib/AccountsService

  If this system will use Docker (which manages its own datasets & snapshots):
  # zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/docker

  If this system will use NFS (locking):
  # zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/nfs

  A tmpfs is recommended later, but if you want a separate dataset for /tmp:
  # zfs create -o com.sun:auto-snapshot=false  rpool/tmp
  # chmod 1777 /mnt/tmp

The primary goal of this dataset layout is to separate the OS from user
data. This allows the root filesystem to be rolled back without rolling
back user data such as logs (in ``/var/log``). This will be especially
important if/when a ``beadm`` or similar utility is integrated. The
``com.sun.auto-snapshot`` setting is used by some ZFS snapshot utilities
to exclude transient data.

If you do nothing extra, ``/tmp`` will be stored as part of the root
filesystem. Alternatively, you can create a separate dataset for
``/tmp``, as shown above. This keeps the ``/tmp`` data out of snapshots
of your root filesystem. It also allows you to set a quota on
``rpool/tmp``, if you want to limit the maximum space used. Otherwise,
you can use a tmpfs (RAM filesystem) later.

3.4 Install the minimal system:

::

  # debootstrap stretch /mnt
  # zfs set devices=off rpool

The ``debootstrap`` command leaves the new system in an unconfigured
state. An alternative to using ``debootstrap`` is to copy the entirety
of a working system into the new ZFS root.

Step 4: System Configuration
----------------------------

4.1 Configure the hostname (change ``HOSTNAME`` to the desired
hostname).

::

  # echo HOSTNAME > /mnt/etc/hostname

  # vi /mnt/etc/hosts
  Add a line:
  127.0.1.1       HOSTNAME
  or if the system has a real name in DNS:
  127.0.1.1       FQDN HOSTNAME

**Hint:** Use ``nano`` if you find ``vi`` confusing.

4.2 Configure the network interface:

::

  Find the interface name:
  # ip addr show

  # vi /mnt/etc/network/interfaces.d/NAME
  auto NAME
  iface NAME inet dhcp

Customize this file if the system is not a DHCP client.

4.3 Configure the package sources:

::

  # vi /mnt/etc/apt/sources.list
  deb http://deb.debian.org/debian stretch main contrib
  deb-src http://deb.debian.org/debian stretch main contrib
  deb http://security.debian.org/debian-security stretch/updates main contrib
  deb-src http://security.debian.org/debian-security stretch/updates main contrib
  deb http://deb.debian.org/debian stretch-updates main contrib
  deb-src http://deb.debian.org/debian stretch-updates main contrib

  # vi /mnt/etc/apt/sources.list.d/stretch-backports.list
  deb http://deb.debian.org/debian stretch-backports main contrib
  deb-src http://deb.debian.org/debian stretch-backports main contrib

  # vi /mnt/etc/apt/preferences.d/90_zfs
  Package: libnvpair1linux libuutil1linux libzfs2linux libzpool2linux spl-dkms zfs-dkms zfs-test zfsutils-linux zfsutils-linux-dev zfs-zed
  Pin: release n=stretch-backports
  Pin-Priority: 990

4.4 Bind the virtual filesystems from the LiveCD environment to the new
system and ``chroot`` into it:

::

  # mount --rbind /dev  /mnt/dev
  # mount --rbind /proc /mnt/proc
  # mount --rbind /sys  /mnt/sys
  # chroot /mnt /bin/bash --login

**Note:** This is using ``--rbind``, not ``--bind``.

4.5 Configure a basic system environment:

::

  # ln -s /proc/self/mounts /etc/mtab
  # apt update

  # apt install --yes locales
  # dpkg-reconfigure locales

Even if you prefer a non-English system language, always ensure that
``en_US.UTF-8`` is available.

::

  # dpkg-reconfigure tzdata

4.6 Install ZFS in the chroot environment for the new system:

::

  # apt install --yes dpkg-dev linux-headers-amd64 linux-image-amd64
  # apt install --yes zfs-initramfs

4.7 For LUKS installs only, setup crypttab:

::

  # apt install --yes cryptsetup

  # echo luks1 UUID=$(blkid -s UUID -o value \
        /dev/disk/by-id/scsi-SATA_disk1-part4) none \
        luks,discard,initramfs > /etc/crypttab

- The use of ``initramfs`` is a work-around for `cryptsetup does not
  support
  ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

**Hint:** If you are creating a mirror or raidz topology, repeat the
``/etc/crypttab`` entries for ``luks2``, etc. adjusting for each disk.

4.8 Install GRUB

Choose one of the following options:

4.8a Install GRUB for legacy (BIOS) booting

::

  # apt install --yes grub-pc

Install GRUB to the disk(s), not the partition(s).

4.8b Install GRUB for UEFI booting

::

  # apt install dosfstools
  # mkdosfs -F 32 -s 1 -n EFI /dev/disk/by-id/scsi-SATA_disk1-part2
  # mkdir /boot/efi
  # echo PARTUUID=$(blkid -s PARTUUID -o value \
        /dev/disk/by-id/scsi-SATA_disk1-part2) \
        /boot/efi vfat nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
  # mount /boot/efi
  # apt install --yes grub-efi-amd64 shim

- The ``-s 1`` for ``mkdosfs`` is only necessary for drives which
  present 4 KiB logical sectors (“4Kn” drives) to meet the minimum
  cluster size (given the partition size of 512 MiB) for FAT32. It also
  works fine on drives which present 512 B sectors.

**Note:** If you are creating a mirror or raidz topology, this step only
installs GRUB on the first disk. The other disk(s) will be handled
later.

4.9 Set a root password

::

  # passwd

4.10 Enable importing bpool

This ensures that ``bpool`` is always imported, regardless of whether
``/etc/zfs/zpool.cache`` exists, whether it is in the cachefile or not,
or whether ``zfs-import-scan.service`` is enabled.

::

      # vi /etc/systemd/system/zfs-import-bpool.service
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

      # systemctl enable zfs-import-bpool.service

4.11 Optional (but recommended): Mount a tmpfs to /tmp

If you chose to create a ``/tmp`` dataset above, skip this step, as they
are mutually exclusive choices. Otherwise, you can put ``/tmp`` on a
tmpfs (RAM filesystem) by enabling the ``tmp.mount`` unit.

::

  # cp /usr/share/systemd/tmp.mount /etc/systemd/system/
  # systemctl enable tmp.mount

4.12 Optional (but kindly requested): Install popcon

The ``popularity-contest`` package reports the list of packages install
on your system. Showing that ZFS is popular may be helpful in terms of
long-term attention from the distro.

::

  # apt install --yes popularity-contest

Choose Yes at the prompt.

Step 5: GRUB Installation
-------------------------

5.1 Verify that the ZFS boot filesystem is recognized:

::

  # grub-probe /boot
  zfs

5.2 Refresh the initrd files:

::

  # update-initramfs -u -k all
  update-initramfs: Generating /boot/initrd.img-4.9.0-8-amd64

**Note:** When using LUKS, this will print "WARNING could not determine
root device from /etc/fstab". This is because `cryptsetup does not
support
ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

5.3 Workaround GRUB's missing zpool-features support:

::

  # vi /etc/default/grub
  Set: GRUB_CMDLINE_LINUX="root=ZFS=rpool/ROOT/debian"

5.4 Optional (but highly recommended): Make debugging GRUB easier:

::

  # vi /etc/default/grub
  Remove quiet from: GRUB_CMDLINE_LINUX_DEFAULT
  Uncomment: GRUB_TERMINAL=console
  Save and quit.

Later, once the system has rebooted twice and you are sure everything is
working, you can undo these changes, if desired.

5.5 Update the boot configuration:

::

  # update-grub
  Generating grub configuration file ...
  Found linux image: /boot/vmlinuz-4.9.0-8-amd64
  Found initrd image: /boot/initrd.img-4.9.0-8-amd64
  done

**Note:** Ignore errors from ``osprober``, if present.

5.6 Install the boot loader

5.6a For legacy (BIOS) booting, install GRUB to the MBR:

::

  # grub-install /dev/disk/by-id/scsi-SATA_disk1
  Installing for i386-pc platform.
  Installation finished. No error reported.

Do not reboot the computer until you get exactly that result message.
Note that you are installing GRUB to the whole disk, not a partition.

If you are creating a mirror or raidz topology, repeat the
``grub-install`` command for each disk in the pool.

5.6b For UEFI booting, install GRUB:

::

  # grub-install --target=x86_64-efi --efi-directory=/boot/efi \
        --bootloader-id=debian --recheck --no-floppy

5.7 Verify that the ZFS module is installed:

::

  # ls /boot/grub/*/zfs.mod

5.8 Fix filesystem mount ordering

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

::

  For UEFI booting, unmount /boot/efi first:
  # umount /boot/efi

  Everything else applies to both BIOS and UEFI booting:

  # zfs set mountpoint=legacy bpool/BOOT/debian
  # echo bpool/BOOT/debian /boot zfs \
        nodev,relatime,x-systemd.requires=zfs-import-bpool.service 0 0 >> /etc/fstab

  # zfs set mountpoint=legacy rpool/var/log
  # echo rpool/var/log /var/log zfs nodev,relatime 0 0 >> /etc/fstab

  # zfs set mountpoint=legacy rpool/var/spool
  # echo rpool/var/spool /var/spool zfs nodev,relatime 0 0 >> /etc/fstab

  If you created a /var/tmp dataset:
  # zfs set mountpoint=legacy rpool/var/tmp
  # echo rpool/var/tmp /var/tmp zfs nodev,relatime 0 0 >> /etc/fstab

  If you created a /tmp dataset:
  # zfs set mountpoint=legacy rpool/tmp
  # echo rpool/tmp /tmp zfs nodev,relatime 0 0 >> /etc/fstab

Step 6: First Boot
------------------

6.1 Snapshot the initial installation:

::

  # zfs snapshot bpool/BOOT/debian@install
  # zfs snapshot rpool/ROOT/debian@install

In the future, you will likely want to take snapshots before each
upgrade, and remove old snapshots (including this one) at some point to
save space.

6.2 Exit from the ``chroot`` environment back to the LiveCD environment:

::

  # exit

6.3 Run these commands in the LiveCD environment to unmount all
filesystems:

::

  # mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
  # zpool export -a

6.4 Reboot:

::

  # reboot

6.5 Wait for the newly installed system to boot normally. Login as root.

6.6 Create a user account:

::

  # zfs create rpool/home/YOURUSERNAME
  # adduser YOURUSERNAME
  # cp -a /etc/skel/.[!.]* /home/YOURUSERNAME
  # chown -R YOURUSERNAME:YOURUSERNAME /home/YOURUSERNAME

6.7 Add your user account to the default set of groups for an
administrator:

::

  # usermod -a -G audio,cdrom,dip,floppy,netdev,plugdev,sudo,video YOURUSERNAME

6.8 Mirror GRUB

If you installed to multiple disks, install GRUB on the additional
disks:

6.8a For legacy (BIOS) booting:

::

  # dpkg-reconfigure grub-pc
  Hit enter until you get to the device selection screen.
  Select (using the space bar) all of the disks (not partitions) in your pool.

6.8b UEFI

::

  # umount /boot/efi

  For the second and subsequent disks (increment debian-2 to -3, etc.):
  # dd if=/dev/disk/by-id/scsi-SATA_disk1-part2 \
       of=/dev/disk/by-id/scsi-SATA_disk2-part2
  # efibootmgr -c -g -d /dev/disk/by-id/scsi-SATA_disk2 \
        -p 2 -L "debian-2" -l '\EFI\debian\grubx64.efi'

  # mount /boot/efi

Step 7: (Optional) Configure Swap
---------------------------------

**Caution**: On systems with extremely high memory pressure, using a
zvol for swap can result in lockup, regardless of how much swap is still
available. This issue is currently being investigated in:
`https://github.com/zfsonlinux/zfs/issues/7734 <https://github.com/zfsonlinux/zfs/issues/7734>`__

7.1 Create a volume dataset (zvol) for use as a swap device:

::

  # zfs create -V 4G -b $(getconf PAGESIZE) -o compression=zle \
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

  # mkswap -f /dev/zvol/rpool/swap
  # echo /dev/zvol/rpool/swap none swap discard 0 0 >> /etc/fstab
  # echo RESUME=none > /etc/initramfs-tools/conf.d/resume

The ``RESUME=none`` is necessary to disable resuming from hibernation.
This does not work, as the zvol is not present (because the pool has not
yet been imported) at the time the resume script runs. If it is not
disabled, the boot process hangs for 30 seconds waiting for the swap
zvol to appear.

7.3 Enable the swap device:

::

  # swapon -av

Step 8: Full Software Installation
----------------------------------

8.1 Upgrade the minimal system:

::

  # apt dist-upgrade --yes

8.2 Install a regular set of software:

::

  # tasksel

8.3 Optional: Disable log compression:

As ``/var/log`` is already compressed by ZFS, logrotate’s compression is
going to burn CPU and disk I/O for (in most cases) very little gain.
Also, if you are making snapshots of ``/var/log``, logrotate’s
compression will actually waste space, as the uncompressed data will
live on in the snapshot. You can edit the files in ``/etc/logrotate.d``
by hand to comment out ``compress``, or use this loop (copy-and-paste
highly recommended):

::

  # for file in /etc/logrotate.d/* ; do
      if grep -Eq "(^|[^#y])compress" "$file" ; then
          sed -i -r "s/(^|[^#y])(compress)/\1#\2/" "$file"
      fi
  done

8.4 Reboot:

::

  # reboot

Step 9: Final Cleanup
~~~~~~~~~~~~~~~~~~~~~

9.1 Wait for the system to boot normally. Login using the account you
created. Ensure the system (including networking) works normally.

9.2 Optional: Delete the snapshots of the initial installation:

::

  $ sudo zfs destroy bpool/BOOT/debian@install
  $ sudo zfs destroy rpool/ROOT/debian@install

9.3 Optional: Disable the root password

::

  $ sudo usermod -p '*' root

9.4 Optional: Re-enable the graphical boot process:

If you prefer the graphical boot process, you can re-enable it now. If
you are using LUKS, it makes the prompt look nicer.

::

  $ sudo vi /etc/default/grub
  Add quiet to GRUB_CMDLINE_LINUX_DEFAULT
  Comment out GRUB_TERMINAL=console
  Save and quit.

  $ sudo update-grub

**Note:** Ignore errors from ``osprober``, if present.

9.5 Optional: For LUKS installs only, backup the LUKS header:

::

  $ sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
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

This will automatically import your pool. Export it and re-import it to
get the mounts right:

::

  For LUKS, first unlock the disk(s):
  # apt install --yes cryptsetup
  # cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
  Repeat for additional disks, if this is a mirror or raidz topology.

  # zpool export -a
  # zpool import -N -R /mnt rpool
  # zpool import -N -R /mnt bpool
  # zfs mount rpool/ROOT/debian
  # zfs mount -a

If needed, you can chroot into your installed environment:

::

  # mount --rbind /dev  /mnt/dev
  # mount --rbind /proc /mnt/proc
  # mount --rbind /sys  /mnt/sys
  # chroot /mnt /bin/bash --login
  # mount /boot
  # mount -a

Do whatever you need to do to fix your system.

When done, cleanup:

::

  # exit
  # mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
  # zpool export -a
  # reboot

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
glitch, try setting ZFS_INITRD_PRE_MOUNTROOT_SLEEP=X in
/etc/default/zfs. The system will wait X seconds for all drives to
appear before importing the pool.

Areca
~~~~~

Systems that require the ``arcsas`` blob driver should add it to the
``/etc/initramfs-tools/modules`` file and run
``update-initramfs -u -k all``.

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
this on the host:

::

  $ sudo apt install ovmf
  $ sudo vi /etc/libvirt/qemu.conf
  Uncomment these lines:
  nvram = [
     "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd",
     "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd"
  ]
  $ sudo service libvirt-bin restart
