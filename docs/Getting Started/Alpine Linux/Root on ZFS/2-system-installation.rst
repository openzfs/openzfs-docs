.. highlight:: sh

System Installation
======================

.. contents:: Table of Contents
   :local:

#. Partition the disks::

     for i in ${DISK}; do

     sgdisk --zap-all $i

     sgdisk -n1:1M:+1G -t1:EF00 $i

     sgdisk -n2:0:+4G -t2:BE00 $i

     test -z $INST_PARTSIZE_SWAP || sgdisk -n4:0:+${INST_PARTSIZE_SWAP}G -t4:8200 $i

     if test -z $INST_PARTSIZE_RPOOL; then
         sgdisk -n3:0:0   -t3:BF00 $i
     else
         sgdisk -n3:0:+${INST_PARTSIZE_RPOOL}G -t3:BF00 $i
     fi

     sgdisk -a1 -n5:24K:+1000K -t5:EF02 $i
     done

#. Probe new partitions::

    for i in ${DISK}; do
      partprobe $i
    done
    udevadm settle
    sync

#. Create boot partition::

    for i in ${DISK}; do
      mkfs.ext4 -F $i-part2
    done

#. Create root pool::

       zpool create \
           -o ashift=12 \
           -o autotrim=on \
           -R /mnt \
           -O acltype=posixacl \
           -O canmount=off \
           -O compression=zstd \
           -O dnodesize=auto \
           -O normalization=formD \
           -O relatime=on \
           -O xattr=sa \
           -O mountpoint=/ \
           rpool \
           mirror \
          $(for i in ${DISK}; do
             printf "$i-part3 ";
            done)

   If not using a multi-disk setup, remove ``mirror``.

#. This section implements dataset layout as described in `overview <1-preparation.html>`__.

   Create root system container:

   - Unencrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       rpool/alpine

   - Encrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       -o encryption=on \
       -o keylocation=prompt \
       -o keyformat=passphrase \
       rpool/alpine

#. Create datasets::

     zfs create -o canmount=on -o mountpoint=/     rpool/alpine/root
     zfs create -o canmount=on -o mountpoint=/home rpool/alpine/home
     zfs create -o canmount=off -o mountpoint=/var  rpool/alpine/var
     zfs create -o canmount=on  rpool/alpine/var/lib
     zfs create -o canmount=on  rpool/alpine/var/log

#. Mount /boot::

    mkdir -p /mnt/boot
    mount -t ext4 $(echo $DISK | cut -f1 -d\ )-part2 /mnt/boot/

#. Format and mount ESP::

    mkdir -p /mnt/boot/efi
    mount -t vfat $(echo $DISK | cut -f1 -d\ )-part1 /mnt/boot/efi

#. By default ``setup-disk`` command does not support zfs and will refuse to run,
   add zfs support::

     sed -i 's|supported="ext|supported="zfs ext|g' /sbin/setup-disk

#. Workaround for GRUB to recognize predictable disk names::

     export ZPOOL_VDEV_NAME_PATH=YES

#. Install system to disk::

     BOOTLOADER=grub setup-disk -v /mnt

   GRUB installation will fail and will be reinstalled later.

#. Chroot::

    m='/dev /proc /sys'
    for i in $m; do mount --rbind $i /mnt/$i; done

    chroot /mnt /usr/bin/env DISK=$DISK sh

#. Apply GRUB workaround::

     echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile.d/zpool_vdev_name_path.sh
     source /etc/profile.d/zpool_vdev_name_path.sh

     sed -i "s|rpool=.*|rpool=rpool|"  /etc/grub.d/10_linux

     sed -i 's|stat -f -c %T /|echo zfs|' /usr/sbin/grub-mkconfig

   This workaround needs to be applied for every GRUB update, as the
   update will overwrite the changes.

#. Generate GRUB menu::

     grub-mkconfig -o /boot/grub/grub.cfg

#. Rebuild initrd::

    mkdir -p /etc/zfs
    rm -f /etc/zfs/zpool.cache
    touch /etc/zfs/zpool.cache
    chmod a-w /etc/zfs/zpool.cache
    chattr +i /etc/zfs/zpool.cache

    sed -i 's|zfs|nvme zfs|' /etc/mkinitfs/mkinitfs.conf
    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      mkinitfs $kernel_version
    done

#. Enable dataset mounting at boot::

     rc-update add zfs-mount sysinit

#. Replace predictable disk path with traditional disk path:

   For SATA drives::

     sed -i 's|/dev/disk/by-id/ata-.*-part|/dev/sda|' /etc/fstab

   For NVMe drives::

     sed -i 's|/dev/disk/by-id/nvme-.*-part|/dev/nvme0n1p|' /etc/fstab

#. Mount datasets with zfsutil option::

     sed -i 's|,posixacl|,zfsutil,posixacl|' /etc/fstab
     
#. Install GRUB::

      export ZPOOL_VDEV_NAME_PATH=YES
      for i in ${DISK}; do
       grub-install --target=i386-pc $i
      done
      grub-install --target x86_64-efi --bootloader-id alpine --removable
      
#. Unmount filesystems::

     exit
     cut -f2 -d\  /proc/mounts | grep ^/mnt | tac | while read i; do umount -l $i; done
     zpool export -a

#. Reboot::

     poweroff

   Disconnect the live media and other non-boot storage devices.
   Due to missing support of predictable device names in initrd,
   Alpine Linux will mount whichever disk appears to be /dev/sda or /dev/nvme0
   at /boot and /boot/efi at boot.

   Root filesystem at / is ZFS and imported via pool name thus not affected by the above restriction.

#. Post-install:

   #. Setup mirroring of /boot partition and /boot/efi via dd.
   #. Setup swap.
