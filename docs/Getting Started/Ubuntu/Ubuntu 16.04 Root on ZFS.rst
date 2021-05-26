Ubuntu 16.04 Root on ZFS
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

- `64-bit Ubuntu 16.04.5 ("Xenial") Desktop
  CD <http://releases.ubuntu.com/16.04/ubuntu-16.04.5-desktop-amd64.iso>`__
  (*not* the server image)
- `A 64-bit kernel is strongly
  encouraged. <https://github.com/zfsonlinux/zfs/wiki/FAQ#32-bit-vs-64-bit-systems>`__
- A drive which presents 512B logical sectors. Installing on a drive
  which presents 4KiB logical sectors (a “4Kn” drive) should work with
  UEFI partitioning, but this has not been tested.

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
<https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Ubuntu%2016.04%20Root%20on%20ZFS%20HOWTO:>`__.

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

This guide supports the three different Ubuntu encryption options:
unencrypted, LUKS (full-disk encryption), and eCryptfs (home directory
encryption).

Unencrypted does not encrypt anything, of course. All ZFS features are
fully available. With no encryption happening, this option naturally has
the best performance.

LUKS encrypts almost everything: the OS, swap, home directories, and
anything else. The only unencrypted data is the bootloader, kernel, and
initrd. The system cannot boot without the passphrase being entered at
the console. All ZFS features are fully available. Performance is good,
but LUKS sits underneath ZFS, so if multiple disks (mirror or raidz
configurations) are used, the data has to be encrypted once per disk.

eCryptfs protects the contents of the specified home directories. This
guide also recommends encrypted swap when using eCryptfs. Other
operating system directories, which may contain sensitive data, logs,
and/or configuration information, are not encrypted. ZFS compression is
useless on the encrypted home directories. ZFS snapshots are not
automatically and transparently mounted when using eCryptfs, and
manually mounting them requires serious knowledge of eCryptfs
administrative commands. eCryptfs sits above ZFS, so the encryption only
happens once, regardless of the number of disks in the pool. The
performance of eCryptfs may be lower than LUKS in single-disk scenarios.

If you want encryption, LUKS is recommended.

Step 1: Prepare The Install Environment
---------------------------------------

1.1 Boot the Ubuntu Live CD. Select Try Ubuntu. Connect your system to
the Internet as appropriate (e.g. join your WiFi network). Open a
terminal (press Ctrl-Alt-T).

1.2 Setup and update the repositories:

::

  $ sudo apt-add-repository universe
  $ sudo apt update

1.3 Optional: Start the OpenSSH server in the Live CD environment:

If you have a second system, using SSH to access the target system can
be convenient.

::

  $ passwd
    There is no current password; hit enter at that prompt.
  $ sudo apt --yes install openssh-server

**Hint:** You can find your IP address with
``ip addr show scope global | grep inet``. Then, from your main machine,
connect with ``ssh ubuntu@IP``.

1.4 Become root:

::

  $ sudo -i

1.5 Install ZFS in the Live CD environment:

::

  # apt install --yes debootstrap gdisk zfs-initramfs

**Note:** You can ignore the two error lines about "AppStream". They are
harmless.

Step 2: Disk Formatting
-----------------------

2.1 If you are re-using a disk, clear it as necessary:

::

  If the disk was previously used in an MD array, zero the superblock:
  # apt install --yes mdadm
  # mdadm --zero-superblock --force /dev/disk/by-id/scsi-SATA_disk1

  Clear the partition table:
  # sgdisk --zap-all /dev/disk/by-id/scsi-SATA_disk1

2.2 Partition your disk:

::

  Run this if you need legacy (BIOS) booting:
  # sgdisk -a1 -n2:34:2047  -t2:EF02 /dev/disk/by-id/scsi-SATA_disk1

  Run this for UEFI booting (for use now or in the future):
  # sgdisk     -n3:1M:+512M -t3:EF00 /dev/disk/by-id/scsi-SATA_disk1

Choose one of the following options:

2.2a Unencrypted or eCryptfs:

::

  # sgdisk     -n1:0:0      -t1:BF01 /dev/disk/by-id/scsi-SATA_disk1

2.2b LUKS:

::

  # sgdisk     -n4:0:+512M  -t4:8300 /dev/disk/by-id/scsi-SATA_disk1
  # sgdisk     -n1:0:0      -t1:8300 /dev/disk/by-id/scsi-SATA_disk1

Always use the long ``/dev/disk/by-id/*`` aliases with ZFS. Using the
``/dev/sd*`` device nodes directly can cause sporadic import failures,
especially on systems that have more than one storage pool.

**Hints:**

- ``ls -la /dev/disk/by-id`` will list the aliases.
- Are you doing this in a virtual machine? If your virtual disk is
  missing from ``/dev/disk/by-id``, use ``/dev/vda`` if you are using
  KVM with virtio; otherwise, read the
  `troubleshooting <https://github.com/zfsonlinux/zfs/wiki/Ubuntu-16.04-Root-on-ZFS#troubleshooting>`__
  section.

2.3 Create the root pool:

Choose one of the following options:

2.3a Unencrypted or eCryptfs:

::

  # zpool create -o ashift=12 \
        -O atime=off -O canmount=off -O compression=lz4 -O normalization=formD \
        -O mountpoint=/ -R /mnt \
        rpool /dev/disk/by-id/scsi-SATA_disk1-part1

2.3b LUKS:

::

  # cryptsetup luksFormat -c aes-xts-plain64 -s 256 -h sha256 \
        /dev/disk/by-id/scsi-SATA_disk1-part1
  # cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part1 luks1
  # zpool create -o ashift=12 \
        -O atime=off -O canmount=off -O compression=lz4 -O normalization=formD \
        -O mountpoint=/ -R /mnt \
        rpool /dev/mapper/luks1

**Notes:**

- The use of ``ashift=12`` is recommended here because many drives
  today have 4KiB (or larger) physical sectors, even though they
  present 512B logical sectors. Also, a future replacement drive may
  have 4KiB physical sectors (in which case ``ashift=12`` is desirable)
  or 4KiB logical sectors (in which case ``ashift=12`` is required).
- Setting ``normalization=formD`` eliminates some corner cases relating
  to UTF-8 filename normalization. It also implies ``utf8only=on``,
  which means that only UTF-8 filenames are allowed. If you care to
  support non-UTF-8 filenames, do not use this option. For a discussion
  of why requiring UTF-8 filenames may be a bad idea, see `The problems
  with enforced UTF-8 only
  filenames <http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames>`__.
- Make sure to include the ``-part1`` portion of the drive path. If you
  forget that, you are specifying the whole disk, which ZFS will then
  re-partition, and you will lose the bootloader partition(s).
- For LUKS, the key size chosen is 256 bits. However, XTS mode requires
  two keys, so the LUKS key is split in half. Thus, ``-s 256`` means
  AES-128, which is the LUKS and Ubuntu default.
- Your passphrase will likely be the weakest link. Choose wisely. See
  `section 5 of the cryptsetup
  FAQ <https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions#5-security-aspects>`__
  for guidance.

**Hints:**

- The root pool does not have to be a single disk; it can have a mirror
  or raidz topology. In that case, repeat the partitioning commands for
  all the disks which will be part of the pool. Then, create the pool
  using
  ``zpool create ... rpool mirror /dev/disk/by-id/scsi-SATA_disk1-part1 /dev/disk/by-id/scsi-SATA_disk2-part1``
  (or replace ``mirror`` with ``raidz``, ``raidz2``, or ``raidz3`` and
  list the partitions from additional disks).
- The pool name is arbitrary. On systems that can automatically install
  to ZFS, the root pool is named ``rpool`` by default. If you work with
  multiple systems, it might be wise to use ``hostname``,
  ``hostname0``, or ``hostname-1`` instead.

Step 3: System Installation
---------------------------

3.1 Create a filesystem dataset to act as a container:

::

  # zfs create -o canmount=off -o mountpoint=none rpool/ROOT

On Solaris systems, the root filesystem is cloned and the suffix is
incremented for major system changes through ``pkg image-update`` or
``beadm``. Similar functionality for APT is possible but currently
unimplemented. Even without such a tool, it can still be used for
manually created clones.

3.2 Create a filesystem dataset for the root filesystem of the Ubuntu
system:

::

  # zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/ubuntu
  # zfs mount rpool/ROOT/ubuntu

With ZFS, it is not normally necessary to use a mount command (either
``mount`` or ``zfs mount``). This situation is an exception because of
``canmount=noauto``.

3.3 Create datasets:

::

  # zfs create                 -o setuid=off              rpool/home
  # zfs create -o mountpoint=/root                        rpool/home/root
  # zfs create -o canmount=off -o setuid=off  -o exec=off rpool/var
  # zfs create -o com.sun:auto-snapshot=false             rpool/var/cache
  # zfs create                                            rpool/var/log
  # zfs create                                            rpool/var/spool
  # zfs create -o com.sun:auto-snapshot=false -o exec=on  rpool/var/tmp

  If you use /srv on this system:
  # zfs create                                            rpool/srv

  If this system will have games installed:
  # zfs create                                            rpool/var/games

  If this system will store local email in /var/mail:
  # zfs create                                            rpool/var/mail

  If this system will use NFS (locking):
  # zfs create -o com.sun:auto-snapshot=false \
               -o mountpoint=/var/lib/nfs                 rpool/var/nfs

The primary goal of this dataset layout is to separate the OS from user
data. This allows the root filesystem to be rolled back without rolling
back user data such as logs (in ``/var/log``). This will be especially
important if/when a ``beadm`` or similar utility is integrated. Since we
are creating multiple datasets anyway, it is trivial to add some
restrictions (for extra security) at the same time. The
``com.sun.auto-snapshot`` setting is used by some ZFS snapshot utilities
to exclude transient data.

3.4 For LUKS installs only:

::

  # mke2fs -t ext2 /dev/disk/by-id/scsi-SATA_disk1-part4
  # mkdir /mnt/boot
  # mount /dev/disk/by-id/scsi-SATA_disk1-part4 /mnt/boot

3.5 Install the minimal system:

::

  # chmod 1777 /mnt/var/tmp
  # debootstrap xenial /mnt
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
  deb http://archive.ubuntu.com/ubuntu xenial main universe
  deb-src http://archive.ubuntu.com/ubuntu xenial main universe

  deb http://security.ubuntu.com/ubuntu xenial-security main universe
  deb-src http://security.ubuntu.com/ubuntu xenial-security main universe

  deb http://archive.ubuntu.com/ubuntu xenial-updates main universe
  deb-src http://archive.ubuntu.com/ubuntu xenial-updates main universe

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

  # locale-gen en_US.UTF-8

Even if you prefer a non-English system language, always ensure that
``en_US.UTF-8`` is available.

::

  # echo LANG=en_US.UTF-8 > /etc/default/locale

  # dpkg-reconfigure tzdata

  # ln -s /proc/self/mounts /etc/mtab
  # apt update
  # apt install --yes ubuntu-minimal

  If you prefer nano over vi, install it:
  # apt install --yes nano

4.6 Install ZFS in the chroot environment for the new system:

::

  # apt install --yes --no-install-recommends linux-image-generic
  # apt install --yes zfs-initramfs

4.7 For LUKS installs only:

::

  # echo UUID=$(blkid -s UUID -o value \
        /dev/disk/by-id/scsi-SATA_disk1-part4) \
        /boot ext2 defaults 0 2 >> /etc/fstab

  # apt install --yes cryptsetup

  # echo luks1 UUID=$(blkid -s UUID -o value \
        /dev/disk/by-id/scsi-SATA_disk1-part1) none \
        luks,discard,initramfs > /etc/crypttab

  # vi /etc/udev/rules.d/99-local-crypt.rules
  ENV{DM_NAME}!="", SYMLINK+="$env{DM_NAME}"
  ENV{DM_NAME}!="", SYMLINK+="dm-name-$env{DM_NAME}"

  # ln -s /dev/mapper/luks1 /dev/luks1

**Notes:**

- The use of ``initramfs`` is a work-around for `cryptsetup does not
  support
  ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.
- The 99-local-crypt.rules file and symlink in /dev are a work-around
  for `grub-probe assuming all devices are in
  /dev <https://bugs.launchpad.net/ubuntu/+source/grub2/+bug/1527727>`__.

4.8 Install GRUB

Choose one of the following options:

4.8a Install GRUB for legacy (MBR) booting

::

  # apt install --yes grub-pc

Install GRUB to the disk(s), not the partition(s).

4.8b Install GRUB for UEFI booting

::

  # apt install dosfstools
  # mkdosfs -F 32 -n EFI /dev/disk/by-id/scsi-SATA_disk1-part3
  # mkdir /boot/efi
  # echo PARTUUID=$(blkid -s PARTUUID -o value \
        /dev/disk/by-id/scsi-SATA_disk1-part3) \
        /boot/efi vfat nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
  # mount /boot/efi
  # apt install --yes grub-efi-amd64

4.9 Setup system groups:

::

  # addgroup --system lpadmin
  # addgroup --system sambashare

4.10 Set a root password

::

  # passwd

4.11 Fix filesystem mount ordering

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

::

  # zfs set mountpoint=legacy rpool/var/log
  # zfs set mountpoint=legacy rpool/var/tmp
  # cat >> /etc/fstab << EOF
  rpool/var/log /var/log zfs defaults 0 0
  rpool/var/tmp /var/tmp zfs defaults 0 0
  EOF

Step 5: GRUB Installation
-------------------------

5.1 Verify that the ZFS root filesystem is recognized:

::

  # grub-probe /
  zfs

**Note:** GRUB uses ``zpool status`` in order to determine the location
of devices. `grub-probe assumes all devices are in
/dev <https://bugs.launchpad.net/ubuntu/+source/grub2/+bug/1527727>`__.
The ``zfs-initramfs`` package `ships udev rules that create
symlinks <https://packages.ubuntu.com/xenial-updates/all/zfs-initramfs/filelist>`__
to `work around the
problem <https://bugs.launchpad.net/ubuntu/+source/zfs-initramfs/+bug/1530953>`__,
but `there have still been reports of
problems <https://github.com/zfsonlinux/grub/issues/5#issuecomment-249427634>`__.
If this happens, you will get an error saying
``grub-probe: error: failed to get canonical path`` and should run the
following:

::

  # export ZPOOL_VDEV_NAME_PATH=YES

5.2 Refresh the initrd files:

::

  # update-initramfs -c -k all
  update-initramfs: Generating /boot/initrd.img-4.4.0-21-generic

**Note:** When using LUKS, this will print "WARNING could not determine
root device from /etc/fstab". This is because `cryptsetup does not
support
ZFS <https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906>`__.

5.3 Optional (but highly recommended): Make debugging GRUB easier:

::

  # vi /etc/default/grub
  Comment out: GRUB_HIDDEN_TIMEOUT=0
  Remove quiet and splash from: GRUB_CMDLINE_LINUX_DEFAULT
  Uncomment: GRUB_TERMINAL=console
  Save and quit.

Later, once the system has rebooted twice and you are sure everything is
working, you can undo these changes, if desired.

5.4 Update the boot configuration:

::

  # update-grub
  Generating grub configuration file ...
  Found linux image: /boot/vmlinuz-4.4.0-21-generic
  Found initrd image: /boot/initrd.img-4.4.0-21-generic
  done

5.5 Install the boot loader

5.5a For legacy (MBR) booting, install GRUB to the MBR:

::

  # grub-install /dev/disk/by-id/scsi-SATA_disk1
  Installing for i386-pc platform.
  Installation finished. No error reported.

Do not reboot the computer until you get exactly that result message.
Note that you are installing GRUB to the whole disk, not a partition.

If you are creating a mirror, repeat the grub-install command for each
disk in the pool.

5.5b For UEFI booting, install GRUB:

::

  # grub-install --target=x86_64-efi --efi-directory=/boot/efi \
        --bootloader-id=ubuntu --recheck --no-floppy

5.6 Verify that the ZFS module is installed:

::

  # ls /boot/grub/*/zfs.mod

Step 6: First Boot
------------------

6.1 Snapshot the initial installation:

::

  # zfs snapshot rpool/ROOT/ubuntu@install

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
  # zpool export rpool

6.4 Reboot:

::

  # reboot

6.5 Wait for the newly installed system to boot normally. Login as root.

6.6 Create a user account:

Choose one of the following options:

6.6a Unencrypted or LUKS:

::

  # zfs create rpool/home/YOURUSERNAME
  # adduser YOURUSERNAME
  # cp -a /etc/skel/.[!.]* /home/YOURUSERNAME
  # chown -R YOURUSERNAME:YOURUSERNAME /home/YOURUSERNAME

6.6b eCryptfs:

::

  # apt install ecryptfs-utils

  # zfs create -o compression=off -o mountpoint=/home/.ecryptfs/YOURUSERNAME \
        rpool/home/temp-YOURUSERNAME
  # adduser --encrypt-home YOURUSERNAME
  # zfs rename rpool/home/temp-YOURUSERNAME rpool/home/YOURUSERNAME

The temporary name for the dataset is required to work-around `a bug in
ecryptfs-setup-private <https://bugs.launchpad.net/ubuntu/+source/ecryptfs-utils/+bug/1574174>`__.
Otherwise, it will fail with an error saying the home directory is
already mounted; that check is not specific enough in the pattern it
uses.

**Note:** Automatically mounted snapshots (i.e. the ``.zfs/snapshots``
directory) will not work through eCryptfs. You can do another eCryptfs
mount manually if you need to access files in a snapshot. A script to
automate the mounting should be possible, but has not yet been
implemented.

6.7 Add your user account to the default set of groups for an
administrator:

::

  # usermod -a -G adm,cdrom,dip,lpadmin,plugdev,sambashare,sudo YOURUSERNAME

6.8 Mirror GRUB

If you installed to multiple disks, install GRUB on the additional
disks:

6.8a For legacy (MBR) booting:

::

  # dpkg-reconfigure grub-pc
  Hit enter until you get to the device selection screen.
  Select (using the space bar) all of the disks (not partitions) in your pool.

6.8b UEFI

::

  # umount /boot/efi

  For the second and subsequent disks (increment ubuntu-2 to -3, etc.):
  # dd if=/dev/disk/by-id/scsi-SATA_disk1-part3 \
       of=/dev/disk/by-id/scsi-SATA_disk2-part3
  # efibootmgr -c -g -d /dev/disk/by-id/scsi-SATA_disk2 \
        -p 3 -L "ubuntu-2" -l '\EFI\Ubuntu\grubx64.efi'

  # mount /boot/efi

Step 7: Configure Swap
----------------------

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

Choose one of the following options:

7.2a Unencrypted or LUKS:

**Caution**: Always use long ``/dev/zvol`` aliases in configuration
files. Never use a short ``/dev/zdX`` device name.

::

  # mkswap -f /dev/zvol/rpool/swap
  # echo /dev/zvol/rpool/swap none swap defaults 0 0 >> /etc/fstab

7.2b eCryptfs:

::

  # apt install cryptsetup
  # echo cryptswap1 /dev/zvol/rpool/swap /dev/urandom \
        swap,cipher=aes-xts-plain64:sha256,size=256 >> /etc/crypttab
  # systemctl daemon-reload
  # systemctl start systemd-cryptsetup@cryptswap1.service
  # echo /dev/mapper/cryptswap1 none swap defaults 0 0 >> /etc/fstab

7.3 Enable the swap device:

::

  # swapon -av

Step 8: Full Software Installation
----------------------------------

8.1 Upgrade the minimal system:

::

  # apt dist-upgrade --yes

8.2 Install a regular set of software:

Choose one of the following options:

8.2a Install a command-line environment only:

::

  # apt install --yes ubuntu-standard

8.2b Install a full GUI environment:

::

  # apt install --yes ubuntu-desktop

**Hint**: If you are installing a full GUI environment, you will likely
want to manage your network with NetworkManager. In that case,
``rm /etc/network/interfaces.d/eth0``.

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
---------------------

9.1 Wait for the system to boot normally. Login using the account you
created. Ensure the system (including networking) works normally.

9.2 Optional: Delete the snapshot of the initial installation:

::

  $ sudo zfs destroy rpool/ROOT/ubuntu@install

9.3 Optional: Disable the root password

::

  $ sudo usermod -p '*' root

9.4 Optional:

If you prefer the graphical boot process, you can re-enable it now. If
you are using LUKS, it makes the prompt look nicer.

::

  $ sudo vi /etc/default/grub
  Uncomment GRUB_HIDDEN_TIMEOUT=0
  Add quiet and splash to GRUB_CMDLINE_LINUX_DEFAULT
  Comment out GRUB_TERMINAL=console
  Save and quit.

  $ sudo update-grub

Troubleshooting
---------------

Rescuing using a Live CD
~~~~~~~~~~~~~~~~~~~~~~~~

Boot the Live CD and open a terminal.

Become root and install the ZFS utilities:

::

  $ sudo -i
  # apt update
  # apt install --yes zfsutils-linux

This will automatically import your pool. Export it and re-import it to
get the mounts right:

::

  # zpool export -a
  # zpool import -N -R /mnt rpool
  # zfs mount rpool/ROOT/ubuntu
  # zfs mount -a

If needed, you can chroot into your installed environment:

::

  # mount --rbind /dev  /mnt/dev
  # mount --rbind /proc /mnt/proc
  # mount --rbind /sys  /mnt/sys
  # chroot /mnt /bin/bash --login

Do whatever you need to do to fix your system.

When done, cleanup:

::

  # mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
  # zpool export rpool
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
glitch, try setting rootdelay=X in GRUB_CMDLINE_LINUX. The system will
wait up to X seconds for all drives to appear before importing the pool.

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
