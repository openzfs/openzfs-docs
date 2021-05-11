.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Set `mkinitcpio zfs hook scan path
   <https://github.com/archzfs/archzfs/blob/master/src/zfs-utils/zfs-utils.initcpio.install>`__::

    echo GRUB_CMDLINE_LINUX=\"zfs_import_dir=${INST_PRIMARY_DISK%/*}\" >> /mnt/etc/default/grub

#. Generate list of datasets for `zfs-mount-generator
   <https://manpages.ubuntu.com/manpages/focal/man8/zfs-mount-generator.8.html>`__ to mount them at boot::

    # tab-separated zfs properties
    # see /etc/zfs/zed.d/history_event-zfs-list-cacher.sh
    export \
    PROPS="name,mountpoint,canmount,atime,relatime,devices,exec\
    ,readonly,setuid,nbmand,encroot,keylocation"
    mkdir -p /mnt/etc/zfs/zfs-list.cache
    zfs list -H -t filesystem -o $PROPS -r rpool_$INST_UUID > /mnt/etc/zfs/zfs-list.cache/rpool_$INST_UUID
    sed -Ei "s|/mnt/?|/|" /mnt/etc/zfs/zfs-list.cache/*

#. Generate fstab::

    echo bpool_$INST_UUID/$INST_ID/BOOT/default /boot zfs rw,xattr,posixacl 0 0 >> /mnt/etc/fstab
    for i in ${DISK[@]}; do
       echo UUID=$(blkid -s UUID -o value ${i}-part1) /boot/efis/${i##*/}-part1 vfat \
       x-systemd.idle-timeout=1min,x-systemd.automount,noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab
    done
    echo UUID=$(blkid -s UUID -o value ${INST_PRIMARY_DISK}-part1) /boot/efi vfat \
    x-systemd.idle-timeout=1min,x-systemd.automount,noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab

   By default systemd will halt boot process if EFI system partition
   fails to mount at boot. The above mount options
   tells systemd to only mount partitions on demand.
   Thus if a disk fails, system will still boot normally.

   Add encrypted swap. Skip if swap was not created::

    if [ "${INST_PARTSIZE_SWAP}" != "" ]; then
     for i in ${DISK[@]}; do
      echo ${i##*/}-part4-swap ${i}-part4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256,discard >> /mnt/etc/crypttab
      echo /dev/mapper/${i##*/}-part4-swap none swap defaults 0 0 >> /mnt/etc/fstab
     done
    fi

#. Configure mkinitcpio::

    mv /mnt/etc/mkinitcpio.conf /mnt/etc/mkinitcpio.conf.original

    tee /mnt/etc/mkinitcpio.conf <<EOF
    HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
    EOF

#. Host name::

    echo $INST_HOST > /mnt/etc/hostname

#. Enable DHCP on all ethernet ports::

     tee /mnt/etc/systemd/network/20-default.network <<EOF

     [Match]
     Name=en*
     Name=eth*

     [Network]
     DHCP=yes
     EOF
     systemctl enable systemd-networkd systemd-resolved --root=/mnt

   Customize this file if the system is not using wired DHCP network.
   See `Network Configuration <https://wiki.archlinux.org/index.php/Network_configuration>`__.

   Alternatively, install a network manager such as
   ``NetworkManager``.

#. Timezone::

    ln -sf $INST_TZ /mnt/etc/localtime
    hwclock --systohc
    systemctl enable systemd-timesyncd --root=/mnt

#. Locale::

    echo "en_US.UTF-8 UTF-8" >> /mnt/etc/locale.gen
    echo "LANG=en_US.UTF-8" >> /mnt/etc/locale.conf

   Other locales should be added after reboot.

#. Ignore kernel updates::

    sed -i 's/#IgnorePkg/IgnorePkg/' /mnt/etc/pacman.conf
    sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR} zfs-utils/" /mnt/etc/pacman.conf

   Kernel will be updated manually. See `here <../2-zfs-linux.html>`__.

#. Enable ZFS services::

    systemctl enable zfs-import-scan.service zfs-import.target zfs-mount zfs-zed zfs.target --root=/mnt


#. Chroot::

    echo "INST_PRIMARY_DISK=$INST_PRIMARY_DISK
    INST_LINVAR=$INST_LINVAR
    INST_UUID=$INST_UUID
    INST_ID=$INST_ID
    INST_VDEV=$INST_VDEV" > /mnt/root/chroot
    echo DISK=\($(for i in ${DISK[@]}; do printf "$i "; done)\) >> /mnt/root/chroot
    arch-chroot /mnt bash --login

#. Source variables::

    source /root/chroot

#. Apply locales::

    locale-gen

#. `Add archzfs repo <../0-archzfs-repo.html>`__.

#. Set root password::

     passwd
