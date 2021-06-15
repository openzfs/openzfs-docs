.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

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
    if [ "${INST_PARTSIZE_SWAP}" != "" ]; then
     for i in ${DISK[@]}; do
      echo ${i##*/}-part4-swap ${i}-part4 /dev/urandom swap,cipher=aes-cbc-essiv:sha256,size=256,discard >> /mnt/etc/crypttab
      echo /dev/mapper/${i##*/}-part4-swap none swap defaults 0 0 >> /mnt/etc/fstab
     done
    fi

   By default, systemd will halt boot process if any entry in ``/etc/fstab`` fails
   to mount. This is unnecessary for mirrored EFI boot partitions.
   With the above mount options, systemd will skip mounting them at boot,
   only mount them on demand when accessed.

#. Configure dracut::

    echo 'add_dracutmodules+=" zfs "' > /mnt/etc/dracut.conf.d/zfs.conf

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

#. Install locale package, example for English locale::

    dnf --installroot=/mnt install -y glibc-minimal-langpack glibc-langpack-en

   Program will show errors if not installed.

#. Enable ZFS services::

    systemctl enable zfs-import-scan.service zfs-import.target zfs-mount zfs-zed zfs.target --root=/mnt

#. Chroot::

    echo "INST_PRIMARY_DISK=$INST_PRIMARY_DISK
    INST_LINVAR=$INST_LINVAR
    INST_UUID=$INST_UUID
    INST_ID=$INST_ID
    INST_VDEV=$INST_VDEV
    TERM=xterm" > /mnt/root/chroot
    echo DISK=\($(for i in ${DISK[@]}; do printf "$i "; done)\) >> /mnt/root/chroot
    arch-chroot /mnt bash --login
    unalias -a

#. Source variables::

    source /root/chroot

#. Relabel filesystem on reboot::

    fixfiles -F onboot

#. Set root password::

    passwd

#. Build modules::

    ls -1 /lib/modules \
    | while read kernel_version; do
      dkms autoinstall -k $kernel_version
      done
