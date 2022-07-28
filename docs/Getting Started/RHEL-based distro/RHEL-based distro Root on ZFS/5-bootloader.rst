.. highlight:: sh

Bootloader
======================

.. contents:: Table of Contents
   :local:


#. If using virtio disk, add driver to initrd::

    echo 'filesystems+=" virtio_blk "' >> /etc/dracut.conf.d/fs.conf

#. Create empty cache file and generate initrd::

    rm -f /etc/zfs/zpool.cache
    touch /etc/zfs/zpool.cache
    chmod a-w /etc/zfs/zpool.cache
    chattr +i /etc/zfs/zpool.cache

    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      dracut --force --kver $kernel_version
    done

#. Load ZFS modules and disable BLS::

    echo 'GRUB_ENABLE_BLSCFG=false' >> /etc/default/grub

#. Apply GRUB workaround::

     echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile.d/zpool_vdev_name_path.sh
     source /etc/profile.d/zpool_vdev_name_path.sh

     # GRUB fails to detect rpool name, hard code as "rpool"
     sed -i "s|rpool=.*|rpool=rpool|"  /etc/grub.d/10_linux

   This workaround needs to be applied for every GRUB update, as the
   update will overwrite the changes.

#. Install GRUB::

      export ZPOOL_VDEV_NAME_PATH=YES
      mkdir -p /boot/efi/almalinux/grub-bootdir/i386-pc/
      mkdir -p /boot/efi/almalinux/grub-bootdir/x86_64-efi/
      for i in ${DISK}; do
       grub2-install --target=i386-pc --boot-directory \
           /boot/efi/almalinux/grub-bootdir/i386-pc/  $i
      done

      cp -r /usr/lib/grub/x86_64-efi/ /boot/efi/EFI/almalinux/

#. Generate GRUB menu::

     grub2-mkconfig -o /boot/efi/EFI/almalinux/grub.cfg
     grub2-mkconfig -o /boot/efi/almalinux/grub-bootdir/i386-pc/grub2/grub.cfg

#. For both legacy and EFI booting: mirror ESP content::

    ESP_MIRROR=$(mktemp -d)
    unalias -a
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done
    rm -rf $ESP_MIRROR

#. Notes for GRUB on RHEL

   As bls is disabled, you will need to regenerate GRUB menu after each kernel upgrade.
   Or else the new kernel will not be recognized and system will boot the old kernel
   on reboot.

Finish Installation
~~~~~~~~~~~~~~~~~~~~

#. Exit chroot::

    exit

#. Export pools::

    umount -Rl /mnt
    zpool export -a

#. Reboot::

    reboot

#. On first reboot, the boot process will fail, with failure messages such
   as "You are in Emergency Mode...Press Ctrl-D to continue".

   Wait for the computer to automatically reboot and the problem will be resolved.

Post installaion
~~~~~~~~~~~~~~~~
#. Install package groups::

    dnf group list --hidden -v       # query package groups
    dnf group install @gnome-desktop

#. Add new user, configure swap.
