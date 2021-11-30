.. highlight:: sh

Optional Configuration
======================

.. contents:: Table of Contents
   :local:

Skip to `bootloader <5-bootloader.html>`__ section if
no optional configuration is needed.

Boot environment manager
~~~~~~~~~~~~~~~~~~~~~~~~

A boot environment is a dataset which contains a bootable
instance of an operating system. Within the context of this installation,
boot environments can be created on-the-fly to preserve root file system
states before pacman transactions.

Install an AUR helper of choice then install ``rozb3-pac`` from AUR
for pacman integration::

  pacman -S --needed git base-devel sudo
  echo 'nobody ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/00_nobody
  su - nobody -s /bin/bash
  mkdir /tmp/build
  export HOME=/tmp/build
  git clone https://aur.archlinux.org/paru-bin.git
  cd paru-bin
  makepkg -si
  paru -S rozb3-pac
  logout
  rm /etc/sudoers.d/00_nobody

Supply password with SSH
~~~~~~~~~~~~~~~~~~~~~~~~

#. Install mkinitcpio tools::

    pacman -S mkinitcpio-netconf mkinitcpio-dropbear openssh

#. Store public keys in ``/etc/dropbear/root_key``::

    vi /etc/dropbear/root_key

#. Edit mkinitcpio::

    tee /etc/mkinitcpio.conf <<- 'EOF'
    HOOKS=(base udev autodetect modconf block keyboard netconf dropbear zfsencryptssh zfs filesystems)
    EOF

#. Add ``ip=`` to kernel command line::

    # example DHCP
    echo 'GRUB_CMDLINE_LINUX="ip=::::::dhcp"' >> /etc/default/grub

   Details for ``ip=`` can be found at
   `here <https://www.kernel.org/doc/html/latest/admin-guide/nfs/nfsroot.html#kernel-command-line>`__.

#. Generate host keys::

    ssh-keygen -Am pem
    dropbearconvert openssh dropbear /etc/ssh/ssh_host_ed25519_key /etc/dropbear/dropbear_ed25519_host_key

   `mkinitcpio-dropbear
   <https://archlinux.org/packages/community/any/mkinitcpio-dropbear/>`__
   lacks support for converting ed25519 host key,
   `see this pull request
   <https://github.com/grazzolini/mkinitcpio-dropbear/pull/13>`__.

Encrypt boot pool
~~~~~~~~~~~~~~~~~~~
Note: This will disable password with SSH. The password previously set for
root pool will be replaced by keyfile, embedded in initrd.

#. LUKS password::

    LUKS_PWD=secure-passwd

   You will need to enter the same password for
   each disk at boot. As root pool key is
   protected by this password, the previous warning
   about password strength still apply.

   Double-check password here. Complete reinstallation is
   needed if entered wrong.

#. Create encryption keys::

    mkdir /etc/cryptkey.d/
    chmod 700 /etc/cryptkey.d/
    dd bs=32 count=1 if=/dev/urandom of=/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs
    dd bs=32 count=1 if=/dev/urandom of=/etc/cryptkey.d/bpool_$INST_UUID-key-luks
    chmod u=r,go= /etc/cryptkey.d/*

#. Backup boot pool::

    zfs snapshot -r bpool_$INST_UUID/$INST_ID@pre-luks
    zfs send -Rv bpool_$INST_UUID/$INST_ID@pre-luks > /root/bpool_$INST_UUID-${INST_ID}-pre-luks

#. Unmount EFI partition::

    umount /boot/efi

    for i in ${DISK}; do
     umount /boot/efis/${i##*/}-part1
    done

#. Destroy boot pool::

    zpool destroy bpool_$INST_UUID

#. Create LUKS containers::

    for i in ${DISK}; do
     cryptsetup luksFormat -q --type luks2 --key-file /etc/cryptkey.d/bpool_$INST_UUID-key-luks $i-part2
     echo $LUKS_PWD | cryptsetup luksAddKey --pbkdf pbkdf2 --key-file /etc/cryptkey.d/bpool_$INST_UUID-key-luks $i-part2
     cryptsetup open ${i}-part2 ${i##*/}-part2-luks-bpool_$INST_UUID --key-file /etc/cryptkey.d/bpool_$INST_UUID-key-luks
     echo ${i##*/}-part2-luks-bpool_$INST_UUID ${i}-part2 /etc/cryptkey.d/bpool_$INST_UUID-key-luks discard >> /etc/crypttab
    done

   In GRUB 2.06, only the PBKDF2 key derivation function
   is supported, thus PBKDF2 is used
   for passphrase key slot. Other slots are not affected.

#. Embed key file in initrd::

    echo 'FILES=(/etc/cryptkey.d/* )' >> /etc/mkinitcpio.conf

#. Recreate boot pool with mappers as vdev::

    disk_num=0; for i in $DISK; do disk_num=$(( $disk_num + 1 )); done
    if [ $disk_num -gt 1 ]; then INST_VDEV_BPOOL=mirror; fi


    zpool create \
        -o compatibility=grub2 \
        -o ashift=12 \
        -o autotrim=on \
        -O acltype=posixacl \
        -O canmount=off \
        -O compression=lz4 \
        -O devices=off \
        -O normalization=formD \
        -O relatime=on \
        -O xattr=sa \
        -O mountpoint=/boot \
        bpool_$INST_UUID \
         $INST_VDEV_BPOOL \
        $(for i in ${DISK}; do
           printf "/dev/mapper/${i##*/}-part2-luks-bpool_$INST_UUID ";
          done)

#. Restore boot pool backup::

    zfs recv bpool_${INST_UUID}/${INST_ID} < /root/bpool_$INST_UUID-${INST_ID}-pre-luks
    rm /root/bpool_$INST_UUID-${INST_ID}-pre-luks

#. Mount boot dataset and EFI partitions::

    mount /boot
    mount /boot/efi

    for i in ${DISK}; do
     mount /boot/efis/${i##*/}-part1
    done

#. As keys are stored in initrd,
   set secure permissions for ``/boot``::

    chmod 700 /boot

#. Change root pool password to key file::

    zfs change-key -l \
    -o keylocation=file:///etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs \
    -o keyformat=raw \
    rpool_$INST_UUID/$INST_ID

#. Import encrypted boot pool from ``/dev/mapper``::

     curl -L https://git.io/Jsfwj > /etc/systemd/system/zfs-import-bpool-mapper.service
     systemctl enable zfs-import-bpool-mapper.service

#. Remove ``zfsencryptssh`` hook.
   Encrypted boot pool is incompatible with
   password by SSH::

    sed -i 's|zfsencryptssh||g' /etc/mkinitcpio.conf

   If ``zfsencryptssh`` is not removed, initrd will
   stuck at ``fail to load key material`` and fail to boot.

#. Enable GRUB cryptodisk::

     echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub
#. Let GRUB decrypt all LUKS containers on boot::

     tee -a /etc/grub.d/09_bpool_luks2-decryption <<FOE
     #!/bin/sh
     cat <<EOF
       insmod luks2
       insmod pbkdf2
       insmod part_gpt
       insmod gcry_rijndael
       insmod gcry_sha256
       insmod cryptodisk
       cryptomount hd0,gpt2
     EOF
     FOE

     chmod +x /etc/grub.d/09_bpool_luks2-decryption

#. **Important**: Back up root dataset key ``/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs``
   to a secure location.

   In the possible event of LUKS container corruption,
   data on root set will only be available
   with this key.

Persistent swap and hibernation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Optional: enable persistent swap partition. By default
   encryption key of swap partition is discarded on reboot::

    INST_SWAPKEY=/etc/cryptkey.d/${INST_PRIMARY_DISK##*/}-part4-key-luks-swap
    INST_SWAPMAPPER=${INST_PRIMARY_DISK##*/}-part4-luks-swap

    # fstab
    # remove all existing swap entries
    sed -i '/ none swap defaults 0 0/d' /etc/fstab
    # add single swap entry for LUKS encrypted swap partition
    echo "/dev/mapper/${INST_SWAPMAPPER} none swap defaults 0 0" >> /etc/fstab

    # comment out entry in crypttab
    sed -i "s|^${INST_PRIMARY_DISK##*/}-part4-swap|#${INST_PRIMARY_DISK##*/}-part4-swap|" /etc/crypttab

    # create key and format partition as LUKS container
    dd bs=32 count=1 if=/dev/urandom of=${INST_SWAPKEY};
    chmod u=r,go= /etc/cryptkey.d/*
    cryptsetup luksFormat -q --type luks2 --key-file ${INST_SWAPKEY} ${INST_PRIMARY_DISK}-part4
    cryptsetup luksOpen ${INST_PRIMARY_DISK}-part4 ${INST_SWAPMAPPER} --key-file ${INST_SWAPKEY}

    # initialize swap space
    mkswap /dev/mapper/${INST_SWAPMAPPER}

#. Optional: after enabling persistent swap partition,
   enable hibernation::

    # add hook in initrd
    sed -i 's| zfs | encrypt resume zfs |' /etc/mkinitcpio.conf
    # add kernel cmdline to decrypt swap in initrd
    echo "GRUB_CMDLINE_LINUX=\" \
    zfs_import_dir=${INST_PRIMARY_DISK%/*} \
    cryptdevice=PARTUUID=$(blkid -s PARTUUID -o value ${INST_PRIMARY_DISK}-part4):${INST_SWAPMAPPER}:allow-discards \
    cryptkey=rootfs:${INST_SWAPKEY} \
    resume=/dev/mapper/${INST_SWAPMAPPER}\"" \
    >> /etc/default/grub

   Note that hibernation might not work with discrete graphics, virtio graphics or
   AMD APU integrated graphics. This is not specific to this guide.

   Computer must resume from a continuous swap space, resume
   from multiple swap partitions is not supported.

   ``encrypt`` hook can only decrypt one container at boot.
   ``sd-encrypt`` can decrypt multiple devices but is
   not compatible with ``zfs`` hook.

   Do not touch anything on disk while the computer is
   in hibernation, see `kernel documentation
   <https://www.kernel.org/doc/html/latest/power/swsusp.html>`__.

Boot Live ISO with GRUB
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GRUB `can be configured <https://wiki.archlinux.org/title/Multiboot_USB_drive>`__ to boot ISO file directly.

In this section, we will download Live ISO to ESP and configure GRUB to
boot from it. This enables system recovery and re-installation.

#. Download Live iso to EFI system partition::

    mkdir /boot/efi/iso
    cd /boot/efi/iso
    # select a mirror # curl -O https://mirrors.ocf.berkeley.edu/archlinux/iso/2021.11.01/archlinux-2021.11.01-x86_64.iso
    curl -O https://archlinux.org/iso/2021.11.01/archlinux-2021.11.01-x86_64.iso.sig
    gpg --auto-key-retrieve --verify archlinux-2021.11.01-x86_64.iso.sig

   Additionally you can build your own live image
   with `archiso package <https://gitlab.archlinux.org/archlinux/archiso>`__.

   GRUB supports verifying checksum.
   See `manual page
   <https://www.gnu.org/software/grub/manual/grub/html_node/Command_002dline-and-menu-entry-commands.html#Command_002dline-and-menu-entry-commands>`__
   for details.

#. Add custom GRUB entry for ``/boot/efi/iso/archlinux-*.iso``::

    curl -L https://git.io/Jsfr3 > /etc/grub.d/43_archiso
    chmod +x /etc/grub.d/43_archiso

   You can also boot Live ISO for other distros, see `glim
   <https://github.com/thias/glim/tree/master/grub2>`__
   configurations.

   ISO is not mirrored to other devices due to its size.
   Change ``$ESP_MNT`` to adapt to other ESP.

#. Generate ``grub.cfg`` in the next step. If a new file
   has been added later, regenerate ``grub.cfg``.
