.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Generate fstab::

    mkdir -p /mnt/etc/
    genfstab -t PARTUUID /mnt | grep -v swap > /mnt/etc/fstab
    sed -i "s|vfat.*rw|vfat rw,x-systemd.idle-timeout=1min,x-systemd.automount,noauto,nofail|" /mnt/etc/fstab

#. Install basic system packages::

     dnf --installroot=/mnt \
     --releasever=$VERSION_ID -y install \
     @core  grub2-efi-x64 \
     grub2-pc-modules grub2-efi-x64-modules \
     shim-x64  efibootmgr \
     kernel-$(uname -r)

     dnf --installroot=/mnt \
     --releasever=$VERSION_ID -y install \
     https://zfsonlinux.org/epel/zfs-release-2-2$(rpm --eval "%{dist}").noarch.rpm
     dnf config-manager --installroot=/mnt --disable zfs
     dnf config-manager --installroot=/mnt --enable zfs-kmod
     dnf --installroot=/mnt --releasever=$VERSION_ID \
     -y install zfs zfs-dracut

#. Configure dracut::

    echo 'add_dracutmodules+=" zfs "' >> /mnt/etc/dracut.conf.d/zfs.conf
    echo 'forced_drivers+=" zfs "' >> /mnt/etc/dracut.conf.d/zfs.conf
    if grep mpt3sas /proc/modules; then
      echo 'forced_drivers+=" mpt3sas "'  >> /mnt/etc/dracut.conf.d/zfs.conf
    fi
    if grep virtio_blk /proc/modules; then
      echo 'filesystems+=" virtio_blk "' >> /mnt/etc/dracut.conf.d/fs.conf
    fi

#. Generate host id::

    zgenhostid -f -o /mnt/etc/hostid

#. Install locale package, example for English locale::

    dnf --installroot=/mnt install -y glibc-minimal-langpack glibc-langpack-en

#. By default SSH server is enabled, allowing root login by password,
   disable SSH server::

    systemctl disable sshd --root=/mnt
    systemctl enable firewalld --root=/mnt

#. Chroot::

     history -w /mnt/home/sys-install-pre-chroot.txt
     arch-chroot /mnt /usr/bin/env DISK="$DISK" bash --login

#. For SELinux, relabel filesystem on reboot::

    fixfiles -F onboot

#. Generate initrd::

    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      dracut --force --kver $kernel_version
    done

#. Set locale, keymap, timezone, hostname and root password::

    rm -f /etc/localtime
    systemd-firstboot --prompt --root-password=PASSWORD --force

#. Set root password, the password set earlier does not work due to SELinux::

    passwd
