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

   This workaround needs to be applied for every GRUB update, as the
   update will overwrite the changes.

#. Install GRUB::

      mkdir -p /boot/efi/arch/grub-bootdir/i386-pc/
      mkdir -p /boot/efi/arch/grub-bootdir/x86_64-efi/
      for i in ${DISK}; do
       grub-install --target=i386-pc --boot-directory \
           /boot/efi/arch/grub-bootdir/i386-pc/  $i
      done
      grub-install --target x86_64-efi --boot-directory \
          /boot/efi/arch/grub-bootdir/x86_64-efi/ --efi-directory \
	  /boot/efi --bootloader-id arch --removable
      grub-mkconfig -o /boot/efi/arch/grub-bootdir/x86_64-efi/grub/grub.cfg
      grub-mkconfig -o /boot/efi/arch/grub-bootdir/i386-pc/grub/grub.cfg

#. For both legacy and EFI booting: mirror ESP content::

    ESP_MIRROR=$(mktemp -d)
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done
    rm -rf $ESP_MIRROR

Finish Installation
~~~~~~~~~~~~~~~~~~~~

#. Exit chroot::

    exit

#. Export pools::

    umount -Rl /mnt
    zpool export -a

#. Reboot::

    reboot

#. You can create a snapshot of the newly installed
   system for later rollback,
   see `this page <https://openzfs.github.io/openzfs-docs/Getting%20Started/Arch%20Linux/Root%20on%20ZFS/6-create-boot-environment.html>`__.
