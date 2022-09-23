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

     tee -a /root/grub2 <<EOF
     # Features which are supported by GRUB2
     async_destroy
     bookmarks
     embedded_data
     empty_bpobj
     enabled_txg
     extensible_dataset
     filesystem_limits
     hole_birth
     large_blocks
     lz4_compress
     spacemap_histogram
     EOF

     zpool create \
      -o compatibility=/root/grub2 \
      -o ashift=12 \
      -o autotrim=on \
      -O acltype=posixacl \
      -O canmount=off \
      -O compression=lz4 \
      -O devices=off \
      -O normalization=formD \
      -O relatime=on \
      -O xattr=sa \
      -O mountpoint=/boot \
      -R /mnt \
      bpool \
      mirror \
      $(for i in ${DISK}; do
         printf "$i-part2 ";
        done)

   If not using a multi-disk setup, remove ``mirror``.

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
     zfs create -o canmount=off  -o mountpoint=none bpool/alpine
     zfs create -o canmount=on  -o mountpoint=/boot bpool/alpine/root

#. Format and mount ESP::

    for i in ${DISK}; do
     mkfs.vfat -n EFI ${i}-part1
     mkdir -p /mnt/boot/efis/${i##*/}-part1
     mount -t vfat ${i}-part1 /mnt/boot/efis/${i##*/}-part1
    done

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

    chroot /mnt /usr/bin/env DISK="$DISK" sh

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

#. Apply GRUB workaround::

     echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile.d/zpool_vdev_name_path.sh
     source /etc/profile.d/zpool_vdev_name_path.sh

     # GRUB fails to detect rpool name, hard code as "rpool"
     sed -i "s|rpool=.*|rpool=rpool|"  /etc/grub.d/10_linux

     # BusyBox stat does not recognize zfs, replace fs detection with ZFS
     sed -i 's|stat -f -c %T /|echo zfs|' /usr/sbin/grub-mkconfig

     # grub-probe fails to identify fs mounted at /boot
     sed -i "s|GRUB_DEVICE_BOOT=.*|GRUB_DEVICE_BOOT=$(echo $DISK | cut -f1 -d\ )-part2|"  /usr/sbin/grub-mkconfig

   This workaround needs to be applied for every GRUB update, as the
   update will overwrite the changes.

#. Install GRUB::

      export ZPOOL_VDEV_NAME_PATH=YES
      mkdir -p /boot/efi/alpine/grub-bootdir/i386-pc/
      mkdir -p /boot/efi/alpine/grub-bootdir/x86_64-efi/
      for i in ${DISK}; do
       grub-install --target=i386-pc --boot-directory \
           /boot/efi/alpine/grub-bootdir/i386-pc/  $i
      done
      grub-install --target x86_64-efi --boot-directory \
          /boot/efi/alpine/grub-bootdir/x86_64-efi/ --efi-directory \
	  /boot/efi --bootloader-id alpine --removable

#. Generate GRUB menu::

     grub-mkconfig -o /boot/efi/alpine/grub-bootdir/x86_64-efi/grub/grub.cfg
     grub-mkconfig -o /boot/efi/alpine/grub-bootdir/i386-pc/grub/grub.cfg

#. For both legacy and EFI booting: mirror ESP content::

    ESP_MIRROR=$(mktemp -d)
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done
    rm -rf $ESP_MIRROR

#. Unmount filesystems::

     exit
     cut -f2 -d\  /proc/mounts | grep ^/mnt | tac | while read i; do umount -l $i; done
     zpool export -a

#. Reboot::

     poweroff

   Disconnect the live media and other non-boot storage devices.
   Due to missing support of predictable device names in initrd,
   Alpine Linux will mount whichever disk appears to be /dev/sda or /dev/nvme0
   at /boot/efi at boot.

   Root filesystem at / and /boot are ZFS and imported via pool name thus not affected by the above restriction.

#. Post-install:

   #. Setup swap.
