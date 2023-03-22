.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Enter ephemeral nix-shell with git support::

     mkdir -p /mnt/etc/
     echo DISK=\"$DISK\" > ~/disk

     nix-shell -p git

#. Clone template flake configuration::

     source ~/disk
     git clone https://github.com/ne9z/dotfiles-flake.git /mnt/etc/nixos
     git -C /mnt/etc/nixos checkout openzfs-guide

#. Customize configuration to your hardware::

     for i in $DISK; do
       sed -i \
       "s|/dev/disk/by-id/|${i%/*}/|" \
       /mnt/etc/nixos/hosts/exampleHost/default.nix
       break
     done

     diskNames=""
     for i in $DISK; do
       diskNames="$diskNames \"${i##*/}\""
     done

     sed -i "s|\"bootDevices_placeholder\"|$diskNames|g" \
       /mnt/etc/nixos/hosts/exampleHost/default.nix

     sed -i "s|\"hostId_placeholder\"|\"$(head -c4 /dev/urandom | od -A none -t x4| sed 's| ||g')\"|g" \
       /mnt/etc/nixos/hosts/exampleHost/default.nix

     sed -i "s|\"systemType_placeholder\"|\"$(uname -m)-linux\"|g" \
       /mnt/etc/nixos/flake.nix

#. Set root password::

     rootPwd=$(mkpasswd -m SHA-512 -s)

   Declare password in configuration::

     sed -i \
     "s|rootHash_placeholder|${rootPwd}|" \
     /mnt/etc/nixos/hosts/exampleHost/default.nix

#. Optional: add SSH public key for root and change host name in
   ``/mnt/etc/nixos/hosts/exampleHost/default.nix``.

#. From now on, the complete configuration of the system will be
   tracked by git, set a user name and email address to continue::

     git -C /mnt/etc/nixos config user.email "you@example.com"
     git -C /mnt/etc/nixos config user.name "Alice Q. Nixer"

#. Commit changes to local repo::

     git -C /mnt/etc/nixos commit -asm 'initial installation'

#. Update flake lock file to track latest system version::

     nix \
       --extra-experimental-features 'nix-command flakes' \
       flake update --commit-lock-file \
       "git+file:///mnt/etc/nixos"

#. Install system and apply configuration::

     nixos-install --no-root-passwd --flake "git+file:///mnt/etc/nixos#exampleHost"

   If the host name was changed, use the new host name in this command.

#. Exit ephemeral nix shell with git::

     exit

#. Unmount filesystems::

    umount -Rl /mnt
    zpool export -a

#. Reboot::

     reboot

#. NetworkManager is enabled by default.  To manage network
   connections, execute::

     nmtui

#. Optional: immutable root filesystem can be enabled by setting
   ``my.boot.immutable`` option to ``true``.
   then execute::

     nixos-rebuild boot

   Then reboot.  You may need to make certain
   adjustments to where configuration files are stored,
   see `NixOS wiki <https://nixos.wiki/wiki/ZFS>`__ for
   details.

Replace a failed disk
=====================

When a disk fails in a mirrored setup, the disk can be
replaced with the following procedure.

#. Shutdown the computer.

#. Replace the failed disk with another disk.  The
   replacement should be at least the same size or
   larger than the failed disk.

#. Boot the computer.  When a disk fails, the system will boot, albeit
   several minutes slower than normal.  This is due to
   the initrd and systemd designed to only import a pool
   in degraded state after a 90s timeout.  Swap
   partition on that disk will also fail.

#. Launch a ephemeral nix shell with gptfdisk::

     nix-shell -p gptfdisk

#. Identify the bad disk and a working old disk::

     ZPOOL_VDEV_NAME_PATH=1 zpool status

     pool:   bpool
     status: DEGRADED
     action: Replace the device using 'zpool replace'.
     ...
     config: bpool
               mirror-0
	         2387489723748                    UNAVAIL    0  0  0   was /dev/disk/by-id/ata-BAD-part2
		 /dev/disk/by-id/ata-OLD-part2    ONLINE     0  0  0

#. Store the bad disk and a working old disk in a variable, omit the partition number ``-partN``::

     BAD=/dev/disk/by-id/ata-BAD
     OLD=/dev/disk/by-id/ata-OLD

#. Identify the new disk::

     find /dev/disk/by-id/

     /dev/disk/by-id/ata-OLD-part1
     /dev/disk/by-id/ata-OLD-part2
     ...
     /dev/disk/by-id/ata-OLD-part5
     /dev/disk/by-id/ata-NEW       <-- new disk w/o partition table

#. Store the new disk in a variable::

     NEW=/dev/disk/by-id/ata-NEW

#. Replicate partition table on the new disk::

     sgdisk -Z $NEW
     sgdisk --backup=backup $OLD
     sgdisk --load-backup=backup $NEW
     sgdisk --randomize-guids $NEW

#. If the new disk is larger than the old disk, expand root pool partition size::

     sgdisk --delete=3 $NEW

     # expand to all remaining disk space
     sgdisk -n3:0:0 -t3:BF00 $NEW

   Note that this space will only become available once all disks in the mirrored pool are
   replaced with larger disks.

#. Format and mount EFI system partition::

     mkfs.vfat -n EFI ${NEW}-part1
     mkdir -p  /boot/efis/${NEW##*/}-part1
     mount -t vfat ${NEW}-part1 /boot/efis/${NEW##*/}-part1

#. Replace failed disk in pool::

     zpool offline bpool ${BAD}-part2
     zpool offline rpool ${BAD}-part3
     zpool replace bpool ${BAD}-part2 ${NEW}-part2
     zpool replace rpool ${BAD}-part3 ${NEW}-part3
     zpool online  bpool ${NEW}-part2
     zpool online  rpool ${NEW}-part3

   Let the new disk resilver.  Check status with ``zpool status``.

#. Update NixOS system configuration and commit changes to git repo::

     sed -i "s|${BAD##*/}|${NEW##*/}|" /etc/nixos/hosts/exampleHost/default.nix
     git -C /etc/nixos commit

#. Apply the updated NixOS system configuration, reinstall bootloader, then reboot::

     nixos-rebuild boot --install-bootloader

     reboot
