.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Generate fstab::

    mkdir -p /mnt/etc/
    genfstab -t PARTUUID /mnt | grep -v swap > /mnt/etc/fstab
    sed -i "s|vfat.*rw|vfat rw,x-systemd.idle-timeout=1min,x-systemd.automount,noauto,nofail|" /mnt/etc/fstab

#. Install packages::

     pacstrap /mnt base mg mandoc grub efibootmgr mkinitcpio

     CompatibleVer=$(pacman -Si zfs-linux \
     | grep 'Depends On' \
     | sed "s|.*linux=||" \
     | awk '{ print $1 }')

     pacstrap -U /mnt https://archive.archlinux.org/packages/l/linux/linux-${CompatibleVer}-x86_64.pkg.tar.zst

     pacstrap /mnt zfs-linux zfs-utils

     pacstrap /mnt linux-firmware intel-ucode amd-ucode

#. Configure mkinitcpio::

     mv /mnt/etc/mkinitcpio.conf /mnt/etc/mkinitcpio.conf.original
     tee /mnt/etc/mkinitcpio.conf <<EOF
     HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
     EOF

#. Enable internet time synchronisation::

     hwclock --systohc
     systemctl enable systemd-timesyncd --root=/mnt

#. Generate host id::

    zgenhostid -f -o /mnt/etc/hostid

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

#. Generate initrd::

    mkinitcpio -P

#. Import from by-id::

     echo GRUB_CMDLINE_LINUX=\"zfs_import_dir=/dev/disk/by-id/\" >> /etc/default/grub

#. Set locale, keymap, timezone, hostname and root password::

    rm -f /etc/localtime
    systemd-firstboot --prompt --force
