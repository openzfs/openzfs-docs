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

    echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile
    source /etc/profile

   Note that ``sudo`` will not read ``/etc/profile`` and will
   not pass variables in parent shell. Consider setting the following
   in ``/etc/sudoers``::

    pacman -S --noconfirm --needed sudo
    echo 'Defaults env_keep += "ZPOOL_VDEV_NAME_PATH"' >> /etc/sudoers

#. Pool name missing

   See `this bug report <https://savannah.gnu.org/bugs/?59614>`__.
   Root pool name is missing from ``root=ZFS=rpool_$INST_UUID/ROOT/default``
   kernel cmdline in generated ``grub.cfg`` file.

   A workaround is to replace the pool name detection with ``zdb``
   command::

     sed -i "s|rpool=.*|rpool=\`zdb -l \${GRUB_DEVICE} \| grep -E '[[:blank:]]name' \| cut -d\\\' -f 2\`|"  /etc/grub.d/10_linux

Install GRUB
~~~~~~~~~~~~~~~~~~~~

#. Generate initrd::

     mkinitcpio -P

#. When not sure, install both legacy boot
   and EFI.

#. If using legacy booting, install GRUB to every disk::

    for i in ${DISK[@]}; do
     grub-install --target=i386-pc $i
    done

#. If using EFI::

    grub-install && grub-install --removable
    # mirror ESP content
    ESP_MIRROR=$(mktemp -d)
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done
    for i in ${DISK[@]}; do
     efibootmgr -cgp 1 -l "\EFI\arch\grubx64.efi" \
     -L "arch-${i##*/}" -d ${i}
    done

#. Generate GRUB Menu::

    grub-mkconfig -o /boot/grub/grub.cfg

Enable Secure Boot
----------------------------

This is optional.

- Method 1: Generate and enroll your own certificates, then sign bootloader
  with these keys.

  This is the most secure method, see
  `here <https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html>`__
  and `ArchWiki article
  <https://wiki.archlinux.org/title/Secure_Boot#Using_your_own_keys>`__
  for more information. However, enrolling your own key
  `might brick your motherboard
  <https://h30434.www3.hp.com/t5/Notebook-Operating-System-and-Recovery/Black-screen-after-enabling-secure-boot-and-installing/td-p/6754130>`__.

  Tip: The author of this installation guide has
  bricked EliteBook 820 G3 with ``KeyTool.efi`` during enrollment.

- Method 2: Use a preloader
  signed with `Microsoft Corporation UEFI CA
  <https://www.microsoft.com/pkiops/certs/MicCorUEFCA2011_2011-06-27.crt>`__ certificate.
  See `ArchWiki article <https://wiki.archlinux.org/title/Secure_Boot#Using_a_signed_boot_loader>`__
  and `here <https://www.rodsbooks.com/efi-bootloaders/secureboot.html>`__.

  Example configuration with `signed PreLoader.efi
  <https://blog.hansenpartnership.com/linux-foundation-secure-boot-system-released/>`__::

   # download signed PreLoader and HashTool
   curl -LO https://blog.hansenpartnership.com/wp-uploads/2013/HashTool.efi
   curl -LO https://blog.hansenpartnership.com/wp-uploads/2013/PreLoader.efi
   # rename GRUB to loader.efi
   mv /boot/efi/EFI/BOOT/BOOTX64.EFI /boot/efi/EFI/BOOT/loader.efi

   mv PreLoader.efi /boot/efi/EFI/BOOT/BOOTX64.EFI
   mv HashTool.efi /boot/efi/EFI/BOOT/

   for i in ${DISK[@]}; do
    efibootmgr -cgp 1 -l "\EFI\BOOT\BOOTX64.EFI" \
    -L "arch-PreLoader-${i##*/}" -d ${i}
   done

  After reboot, re-enable Secure Boot in firmware settings, save and reboot.
  After enabling Secure Boot,
  enroll the hash of ``loader.efi`` with ``HashTool.efi``::

   # OK -> Enroll Hash -> loader.efi -> Yes -> Reboot System -> Yes

  Re-enrolling the hash is needed if GRUB has been reinstalled.

Finish Installation
~~~~~~~~~~~~~~~~~~~~

#. Exit chroot::

    exit

#. Take a snapshot of the clean installation for future use::

    zfs snapshot -r rpool_$INST_UUID/$INST_ID@install
    zfs snapshot -r bpool_$INST_UUID/$INST_ID@install

#. Unmount EFI system partition::

    umount /mnt/boot/efi
    umount /mnt/boot/efis/*

#. Export pools::

    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID

#. Reboot::

    reboot
