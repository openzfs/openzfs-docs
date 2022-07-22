.. highlight:: sh

Bootloader
======================

.. contents:: Table of Contents
   :local:

Apply workarounds
~~~~~~~~~~~~~~~~~~~~
Currently GRUB has multiple compatibility problems with ZFS,
especially with regards to newer ZFS features.
Workarounds have to be applied.

#. grub-probe fails to get canonical path

   When persistent device names ``/dev/disk/by-id/*`` are used
   with ZFS, GRUB will fail to resolve the path of the boot pool
   device. Error::

     # /usr/bin/grub-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.0-part3'.

   Solution::

    echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile.d/zpool_vdev_name_path.sh
    source /etc/profile.d/zpool_vdev_name_path.sh

#. Pool name missing

   See `this bug report <https://savannah.gnu.org/bugs/?59614>`__.
   Root pool name is missing from ``root=ZFS=rpool_$INST_UUID/ROOT/default``
   kernel cmdline in generated ``grub.cfg`` file.

   A workaround is to replace the pool name detection with ``zdb``
   command::

     sed -i "s|rpool=.*|rpool=\`zdb -l \${GRUB_DEVICE} \| grep -E '[[:blank:]]name' \| cut -d\\\' -f 2\`|"  /etc/grub.d/10_linux

   Caution:  this fix must be applied after every GRUB update and before generating the menu.

Install GRUB
~~~~~~~~~~~~~~~~~~~~
#. Create empty cache file and generate initrd::

    rm -f /etc/zfs/zpool.cache
    touch /etc/zfs/zpool.cache
    chmod a-w /etc/zfs/zpool.cache
    chattr +i /etc/zfs/zpool.cache

    mkinitcpio -P

#. If using legacy booting, install GRUB to every disk::

    for i in ${DISK}; do
     grub-install --target=i386-pc $i
    done

#. If using EFI::

     grub-install --target x86_64-efi
     grub-install --target x86_64-efi --removable
     for i in ${DISK}; do
      efibootmgr -cgp 1 -l "\EFI\arch\grubx64.efi" \
      -L "arch-${i##*/}" -d ${i}
     done

#. Generate GRUB Menu:

   Generate menu::

    echo GRUB_CMDLINE_LINUX=\"zfs_import_dir=/dev/disk/by-id/\" >> /etc/default/grub
    grub-mkconfig -o /boot/grub/grub.cfg
    cp /boot/grub/grub.cfg /boot/efi/EFI/arch/

#. For both legacy and EFI booting: mirror ESP content::

    ESP_MIRROR=$(mktemp -d)
    unalias -a
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
