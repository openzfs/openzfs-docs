.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Set `mkinitcpio zfs hook scan path
   <https://github.com/archzfs/archzfs/blob/master/src/zfs-utils/zfs-utils.initcpio.install>`__::

    echo GRUB_CMDLINE_LINUX=\"zfs_import_dir=${INST_PRIMARY_DISK%/*}\" >> /mnt/etc/default/grub

#. Generate fstab::

    genfstab -U /mnt | sed 's;zfs[[:space:]]*;zfs zfsutil,;g' | grep "zfs zfsutil" >> /mnt/etc/fstab
    for i in ${DISK}; do
       echo UUID=$(blkid -s UUID -o value ${i}-part1) /boot/efis/${i##*/}-part1 vfat \
       x-systemd.idle-timeout=1min,x-systemd.automount,noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab
    done
    echo UUID=$(blkid -s UUID -o value ${INST_PRIMARY_DISK}-part1) /boot/efi vfat \
    x-systemd.idle-timeout=1min,x-systemd.automount,noauto,umask=0022,fmask=0022,dmask=0022 0 1 >> /mnt/etc/fstab
    if [ "${INST_PARTSIZE_SWAP}" != "" ]; then
     for i in ${DISK}; do
      echo ${i##*/}-part4-swap ${i}-part4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256,discard >> /mnt/etc/crypttab
      echo /dev/mapper/${i##*/}-part4-swap none swap defaults 0 0 >> /mnt/etc/fstab
     done
    fi

   By default, systemd will halt boot process if any entry in ``/etc/fstab`` fails
   to mount. This is unnecessary for mirrored EFI boot partitions.
   With the above mount options, systemd will skip mounting them at boot,
   only mount them on demand when accessed.

#. Configure mkinitcpio::

    mv /mnt/etc/mkinitcpio.conf /mnt/etc/mkinitcpio.conf.original
    tee /mnt/etc/mkinitcpio.conf <<EOF
    HOOKS=(base udev autodetect modconf block keyboard zfs filesystems)
    EOF

   For more information on mkinitcpio configuration,
   such as support for other keyboard layouts, see
   `wiki article <https://wiki.archlinux.org/title/mkinitcpio>`__.

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

#. Enable internet time sync::

    hwclock --systohc
    systemctl enable systemd-timesyncd --root=/mnt

#. Interactively set locale, keymap, timezone, hostname and root password::

    rm -f /mnt/etc/localtime
    systemd-firstboot --root=/mnt --force --prompt --root-password=PASSWORD

   This can be non-interactive, see man page for details::

    rm -f /mnt/etc/localtime
    systemd-firstboot --root=/mnt --force \
     --locale="en_US.UTF-8" --locale-messages="en_US.UTF-8" \
     --keymap=us --timezone="Europe/Berlin" --hostname=myHost \
     --root-password=PASSWORD --root-shell=/bin/bash

   ``systemd-firstboot`` has bugs for setting root password, reset it here::

    arch-chroot /mnt passwd

#. Generate host id::

    zgenhostid -f -o /mnt/etc/hostid

#. Ignore kernel updates::

    sed -i 's/#IgnorePkg/IgnorePkg/' /mnt/etc/pacman.conf
    sed -i "/^IgnorePkg/ s/$/ ${INST_LINVAR} ${INST_LINVAR}-headers zfs-${INST_LINVAR} zfs-utils/" /mnt/etc/pacman.conf

   Kernel will be updated manually. See `here <../1-zfs-linux.html#update-kernel>`__.

#. Enable ZFS services::

    systemctl enable zfs-import-scan.service zfs-import.target zfs-zed zfs.target --root=/mnt
    systemctl disable zfs-mount --root=/mnt

   At boot, datasets on rpool are mounted with ``/etc/fstab``,
   which can control the mounting process more precisely than ``zfs-mount.service``.

#. Chroot::

    echo "INST_PRIMARY_DISK=$INST_PRIMARY_DISK
    INST_LINVAR=$INST_LINVAR
    INST_UUID=$INST_UUID
    INST_ID=$INST_ID
    INST_VDEV=$INST_VDEV
    DISK=$DISK" > /mnt/root/chroot
    arch-chroot /mnt bash --login

#. Source variables::

    source /root/chroot

#. Apply locales, change if needed::

    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen

#. `Add archzfs repo <../0-archzfs-repo.html>`__.
