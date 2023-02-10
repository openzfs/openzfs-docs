.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Download system configuration from this repo::

     mkdir -p /mnt/etc/nixos/
     curl -o /mnt/etc/nixos/configuration.nix -L \
     https://github.com/openzfs/openzfs-docs/raw/master/docs/Getting%20Started/NixOS/Root%20on%20ZFS/configuration.nix

#. Customize configuration to your hardware::

     for i in $DISK; do
       sed -i \
       "s|PLACEHOLDER_FOR_DEV_NODE_PATH|\"${i%/*}/\"|" \
       /mnt/etc/nixos/configuration.nix
       break
     done

     diskNames=""
     for i in $DISK; do
       diskNames="$diskNames \"${i##*/}\""
     done
     tee -a /mnt/etc/nixos/machine.nix <<EOF
     {
       bootDevices = [ $diskNames ];
     }
     EOF

#. Set root password::

     rootPwd=$(mkpasswd -m SHA-512 -s)

   Declare password in configuration::

     sed -i \
     "s|PLACEHOLDER_FOR_ROOT_PWD_HASH|\""${rootPwd}"\"|" \
     /mnt/etc/nixos/configuration.nix

#. Optional: enable NetworkManager for easier wireless configuration and enable desktop
   environments.  See ``man configuration.nix`` for details.  By default, the system is
   installed without any other software.

#. Install system and apply configuration::

     nixos-install --no-root-passwd --root /mnt

#. Unmount filesystems::

    umount -Rl /mnt
    zpool export -a

#. Reboot::

     reboot

#. Optional: manage system configuration with git.

#. Optional: immutable root filesystem can be enabled by
   using this `configuration file
   <https://github.com/openzfs/openzfs-docs/raw/master/docs/Getting%20Started/NixOS/Root%20on%20ZFS/configuration-immutable.nix>`__.
   Apply your own hardware configuration in this file,
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

#. Update NixOS system configuration::

     sed -i "s|${BAD##*/}|${NEW##*/}|" /etc/nixos/machine.nix

#. Apply the updated NixOS system configuration, reinstall bootloader, then reboot::

     nixos-rebuild boot --install-bootloader

     reboot
