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

#. grub2-probe fails to get canonical path

   When persistent device names ``/dev/disk/by-id/*`` are used
   with ZFS, GRUB will fail to resolve the path of the boot pool
   device. Error::

     # /usr/bin/grub2-probe: error: failed to get canonical path of `/dev/virtio-pci-0000:06:00.0-part3'.

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

#. If using legacy booting, install GRUB to every disk::

    for i in ${DISK}; do
     grub2-install --target=i386-pc $i
    done

#. If using EFI::

    for i in ${DISK}; do
     efibootmgr -cgp 1 -l "\EFI\almalinux\shimx64.efi" \
     -L "almalinux-${i##*/}" -d ${i}
    done
    cp -r /usr/lib/grub/x86_64-efi/ /boot/efi/EFI/almalinux/

#. Generate GRUB Menu:

   Generate menu::

    grub2-mkconfig -o /boot/grub2/grub.cfg
    cp /boot/grub2/grub.cfg /boot/efi/EFI/almalinux/

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
