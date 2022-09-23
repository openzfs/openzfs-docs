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

#. Configure dracut::

    echo 'add_dracutmodules+=" zfs "' > /mnt/etc/dracut.conf.d/zfs.conf

#. Force load mpt3sas module if used::

     if grep mpt3sas /proc/modules; then
       echo 'forced_drivers+=" mpt3sas "'  >> /mnt/etc/dracut.conf.d/zfs.conf
     fi

#. Set locale, keymap, timezone, hostname and root password::

    rm -f /mnt/etc/localtime
    systemd-firstboot --root=/mnt --prompt --root-password=PASSWORD --force

#. Generate host id::

    zgenhostid -f -o /mnt/etc/hostid

#. Install locale package, example for English locale::

    dnf --installroot=/mnt install -y glibc-minimal-langpack glibc-langpack-en

#. Enable ZFS services::

    systemctl enable zfs-import-scan.service zfs-mount zfs-import.target zfs-zed zfs.target --root=/mnt

#. By default SSH server is enabled, allowing root login by password,
   disable SSH server::

    systemctl disable sshd --root=/mnt
    systemctl enable firewalld --root=/mnt

#. Chroot::

    m='/dev /proc /sys'
    for i in $m; do mount --rbind $i /mnt/$i; done

    history -w /mnt/home/sys-install-pre-chroot.txt
    chroot /mnt /usr/bin/env DISK="$DISK" bash --login

#. For SELinux, relabel filesystem on reboot::

    fixfiles -F onboot

#. Set root password, the password set earlier does not work due to SELinux::

    passwd

#. Build ZFS modules::

    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      dkms autoinstall -k $kernel_version
    done
