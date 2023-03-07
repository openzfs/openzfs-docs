.. highlight:: sh

Bootloader
======================

.. contents:: Table of Contents
   :local:

#. Apply GRUB workaround::

     echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile.d/zpool_vdev_name_path.sh
     source /etc/profile.d/zpool_vdev_name_path.sh

     # GRUB fails to detect rpool name, hard code as "rpool"
     sed -i "s|rpool=.*|rpool=rpool|"  /etc/grub.d/10_linux

   This ``sed`` workaround needs to be applied for every
   GRUB update, as the update will overwrite the
   changes.

#. Install GRUB::

      echo 'GRUB_ENABLE_BLSCFG=false' >> /etc/default/grub
      mkdir -p /boot/efi/almalinux/grub-bootdir/i386-pc/
      mkdir -p /boot/efi/almalinux/grub-bootdir/x86_64-efi/
      for i in ${DISK}; do
       grub2-install --target=i386-pc --boot-directory \
           /boot/efi/almalinux/grub-bootdir/i386-pc/  $i
      done
      cp -r /usr/lib/grub/x86_64-efi/ /boot/efi/EFI/almalinux/
      grub2-mkconfig -o /boot/efi/EFI/almalinux/grub.cfg
      grub2-mkconfig -o /boot/efi/almalinux/grub-bootdir/i386-pc/grub2/grub.cfg

#. For both legacy and EFI booting: mirror ESP content::

    unalias -a
    ESP_MIRROR=$(mktemp -d)
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done
    rm -rf $ESP_MIRROR

#. Note: you need to regenerate GRUB menu after kernel
   updates, otherwise computer will still boot old
   kernel on reboot::

      grub2-mkconfig -o /boot/efi/EFI/almalinux/grub.cfg
      grub2-mkconfig -o /boot/efi/almalinux/grub-bootdir/i386-pc/grub2/grub.cfg

Finish Installation
~~~~~~~~~~~~~~~~~~~~

#. Exit chroot::

    exit

#. Export pools::

    umount -Rl /mnt
    zpool export -a

#. Reboot::

    reboot

Post installaion
~~~~~~~~~~~~~~~~
#. Install package groups::

    dnf group list --hidden -v       # query package groups
    dnf group install gnome-desktop

#. Add new user, configure swap.

#. You can create a snapshot of the newly installed
   system for later rollback,
   see `this page <https://openzfs.github.io/openzfs-docs/Getting%20Started/Arch%20Linux/Root%20on%20ZFS/6-create-boot-environment.html>`__.
