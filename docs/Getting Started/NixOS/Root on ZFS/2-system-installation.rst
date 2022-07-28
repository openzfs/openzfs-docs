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

#. Create boot pool::

    zpool create \
        -o compatibility=grub2 \
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

#. This section implements dataset layout as described in `overview <1-preparation.html>`__.

   Create root system container:

   - Unencrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       rpool/nixos

   - Encrypted:

     Pick a strong password. Once compromised, changing password will not keep your
     data safe. See ``zfs-change-key(8)`` for more info::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       -o encryption=on \
       -o keylocation=prompt \
       -o keyformat=passphrase \
       rpool/nixos

   Create system datasets::

      zfs create -o canmount=on -o mountpoint=/     rpool/nixos/root
      zfs create -o canmount=on -o mountpoint=/home rpool/nixos/home
      zfs create -o canmount=off -o mountpoint=/var  rpool/nixos/var
      zfs create -o canmount=on  rpool/nixos/var/lib
      zfs create -o canmount=on  rpool/nixos/var/log

   Create boot dataset::

     zfs create -o canmount=off -o mountpoint=none bpool/nixos
     zfs create -o canmount=on -o mountpoint=/boot bpool/nixos/root

#. Format and mount ESP::

    for i in ${DISK}; do
     mkfs.vfat -n EFI ${i}-part1
     mkdir -p /mnt/boot/efis/${i##*/}-part1
     mount -t vfat ${i}-part1 /mnt/boot/efis/${i##*/}-part1
    done

    mkdir -p /mnt/boot/efi
    mount -t vfat $(echo $DISK | cut -f1 -d\ )-part1 /mnt/boot/efi
