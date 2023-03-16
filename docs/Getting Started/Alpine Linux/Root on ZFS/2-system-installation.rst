.. highlight:: sh

System Installation
======================

.. contents:: Table of Contents
   :local:

#. Partition the disks::

     for i in ${DISK}; do

     # wipe flash-based storage device to improve
     # performance.
     # ALL DATA WILL BE LOST
     # blkdiscard -f $i

     sgdisk --zap-all $i

     sgdisk -n1:1M:+1G -t1:EF00 $i

     sgdisk -n2:0:+4G -t2:BE00 $i

     sgdisk -n4:0:+${INST_PARTSIZE_SWAP}G -t4:8200 $i

     if test -z $INST_PARTSIZE_RPOOL; then
         sgdisk -n3:0:0   -t3:BF00 $i
     else
         sgdisk -n3:0:+${INST_PARTSIZE_RPOOL}G -t3:BF00 $i
     fi

     sgdisk -a1 -n5:24K:+1000K -t5:EF02 $i

     sync && udevadm settle && sleep 3 

     cryptsetup open --type plain --key-file /dev/random $i-part4 ${i##*/}-part4
     mkswap /dev/mapper/${i##*/}-part4
     swapon /dev/mapper/${i##*/}-part4 
     done

#. Create boot pool::

      zpool create -d \
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

   You should not need to customize any of the options for the boot pool.

   GRUB does not support all of the zpool features. See ``spa_feature_names``
   in `grub-core/fs/zfs/zfs.c
   <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
   This step creates a separate boot pool for ``/boot`` with the features
   limited to only those that GRUB supports, allowing the root pool to use
   any/all features.

   Features enabled with ``-o compatibility=grub2`` can be seen
   `here <https://github.com/openzfs/zfs/blob/master/cmd/zpool/compatibility.d/grub2>`__.

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

#. Create root system container:

   - Unencrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       rpool/alpinelinux

   - Encrypted:

     Pick a strong password. Once compromised, changing password will not keep your
     data safe. See ``zfs-change-key(8)`` for more info::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       -o encryption=on \
       -o keylocation=prompt \
       -o keyformat=passphrase \
       rpool/alpinelinux

   You can automate this step (insecure) with: ``echo POOLPASS | zfs create ...``.

   Create system datasets, let Alpinelinux declaratively
   manage mountpoints with ``mountpoint=legacy``::

      zfs create -o mountpoint=/ -o canmount=noauto rpool/alpinelinux/root
      zfs mount rpool/alpinelinux/root
      zfs create -o mountpoint=legacy rpool/alpinelinux/home
      mkdir /mnt/home
      mount -t zfs rpool/alpinelinux/home /mnt/home
      zfs create -o mountpoint=legacy  rpool/alpinelinux/var
      zfs create -o mountpoint=legacy rpool/alpinelinux/var/lib
      zfs create -o mountpoint=legacy rpool/alpinelinux/var/log
      zfs create -o mountpoint=none bpool/alpinelinux
      zfs create -o mountpoint=legacy bpool/alpinelinux/root
      mkdir /mnt/boot
      mount -t zfs bpool/alpinelinux/root /mnt/boot
      mkdir -p /mnt/var/log
      mkdir -p /mnt/var/lib
      mount -t zfs rpool/alpinelinux/var/lib /mnt/var/lib
      mount -t zfs rpool/alpinelinux/var/log /mnt/var/log

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

#. Allow EFI system partition to fail at boot::

    sed -i "s|vfat.*rw|vfat rw,nofail|" /mnt/etc/fstab

#. Chroot::

    m='/dev /proc /sys'
    for i in $m; do mount --rbind $i /mnt/$i; done

    chroot /mnt /usr/bin/env DISK="$DISK" sh

#. Rebuild initrd::

    sed -i 's|zfs|nvme zfs|' /etc/mkinitfs/mkinitfs.conf
    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      mkinitfs $kernel_version
    done

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

#. Exit chroot::

     exit

#. Unmount filesystems::

     cut -f2 -d\  /proc/mounts | grep ^/mnt | tac | while read i; do umount -l $i; done
     zpool export -a

#. Reboot::

     reboot

Post installaion
~~~~~~~~~~~~~~~~

#. Setup graphical desktop::

     setup-desktop

#. Configure swap.

#. You can create a snapshot of the newly installed
   system for later rollback,
   see `this page <https://openzfs.github.io/openzfs-docs/Getting%20Started/Arch%20Linux/Root%20on%20ZFS/6-create-boot-environment.html>`__.
