.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Generate fstab::

    mkdir -p /mnt/etc/
    for i in ${DISK}; do
       echo UUID=$(blkid -s UUID -o value ${i}-part1) /boot/efis/${i##*/}-part1 vfat \
       umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab
    done
    echo $(echo $DISK | cut -f1 -d\ )-part1 /boot/efi vfat \
       noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab

#. Configure mkinitcpio::

     mv /mnt/etc/mkinitcpio.conf /mnt/etc/mkinitcpio.conf.original
     tee /mnt/etc/mkinitcpio.conf <<EOF
     HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
     EOF

#. Enable internet time synchronisation::

     hwclock --systohc
     systemctl enable systemd-timesyncd --root=/mnt

#. Set locale, keymap, timezone, hostname and root password::

    rm -f /mnt/etc/localtime
    systemd-firstboot --root=/mnt --prompt --force

#. Generate host id::

    zgenhostid -f -o /mnt/etc/hostid

#. Enable ZFS services::

    systemctl enable zfs-import-scan.service zfs-mount zfs-import.target zfs-zed zfs.target --root=/mnt

#. Add archzfs repo::

     curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a - --gpgdir /mnt/etc/pacman.d/gnupg
     pacman-key --lsign-key --gpgdir /mnt/etc/pacman.d/gnupg $(curl -L https://git.io/JsfVS)
     curl -L https://git.io/Jsfw2 > /mnt/etc/pacman.d/mirrorlist-archzfs

     tee -a /mnt/etc/pacman.conf <<- 'EOF'

     #[archzfs-testing]
     #Include = /etc/pacman.d/mirrorlist-archzfs

     [archzfs]
     Include = /etc/pacman.d/mirrorlist-archzfs
     EOF


#. Chroot::

    history -w /mnt/home/sys-install-pre-chroot.txt
    arch-chroot /mnt /usr/bin/env DISK="$DISK" bash

#. Generate locales::

    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen
