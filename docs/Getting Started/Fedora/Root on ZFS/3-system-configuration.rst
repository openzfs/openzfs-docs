.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

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
      echo /dev/mapper/${i##*/}-part4-swap none swap x-systemd.requires=cryptsetup.target,defaults 0 0 >> /mnt/etc/fstab
     done
    fi

   By default, systemd will halt boot process if any entry in ``/etc/fstab`` fails
   to mount. This is unnecessary for mirrored EFI boot partitions.
   With the above mount options, systemd will skip mounting them at boot,
   only mount them on demand when accessed.

#. Configure dracut::

    echo 'add_dracutmodules+=" zfs "' > /mnt/etc/dracut.conf.d/zfs.conf

#. Enable timezone sync::

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

   ``systemd-firstboot`` have bugs, root password is set below.

#. Generate host id::

    zgenhostid -f -o /mnt/etc/hostid

#. Install locale package, example for English locale::

    dnf --installroot=/mnt install -y glibc-minimal-langpack glibc-langpack-en

   Program will show errors if not installed.

#. Enable ZFS services::

    systemctl enable zfs-import-scan.service zfs-import.target zfs-zed zfs.target --root=/mnt
    systemctl disable zfs-mount --root=/mnt

   At boot, datasets on rpool are mounted with ``/etc/fstab``,
   which can control the mounting process more precisely than ``zfs-mount.service``.


#. By default SSH server is enabled, allowing root login by password,
   disable SSH server::

    systemctl disable sshd --root=/mnt
    systemctl enable firewalld --root=/mnt

#. Chroot::

    echo "INST_PRIMARY_DISK=$INST_PRIMARY_DISK
    INST_LINVAR=$INST_LINVAR
    INST_UUID=$INST_UUID
    INST_ID=$INST_ID
    unalias -a
    INST_VDEV=$INST_VDEV
    DISK=$DISK" > /mnt/root/chroot
    arch-chroot /mnt bash --login

#. Source variables::

    source /root/chroot

#. For SELinux, relabel filesystem on next boot::

    fixfiles -F onboot

#. Set root password::

    passwd

#. Build ZFS modules::

    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      dkms autoinstall -k $kernel_version
    done
