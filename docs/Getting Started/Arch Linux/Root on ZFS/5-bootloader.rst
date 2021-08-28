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

    rm -f /etc/zfs/zpool.cache
    touch /etc/zfs/zpool.cache
    chmod a-w /etc/zfs/zpool.cache
    chattr +i /etc/zfs/zpool.cache
    mkinitcpio -P

#. Create GRUB boot directory, in ESP and boot pool::

    mkdir -p /boot/efi/EFI/arch
    mkdir -p /boot/grub

   Boot environment-specific configuration (kernel, etc)
   is stored in ``/boot/grub/grub.cfg``, enabling rollback.

#. When in doubt, install both legacy boot
   and EFI.

#. If using legacy booting, install GRUB to every disk::

    for i in ${DISK}; do
     grub-install --boot-directory /boot/efi/EFI/arch --target=i386-pc $i
    done

#. If using EFI::

    grub-install --boot-directory /boot/efi/EFI/arch --efi-directory /boot/efi/
    grub-install --boot-directory /boot/efi/EFI/arch --efi-directory /boot/efi/ --removable
    for i in ${DISK}; do
     efibootmgr -cgp 1 -l "\EFI\arch\grubx64.efi" \
     -L "arch-${i##*/}" -d ${i}
    done

#. Generate GRUB Menu::

    grub-mkconfig -o /boot/efi/EFI/arch/grub/grub.cfg
    cp /boot/efi/EFI/arch/grub/grub.cfg /boot/grub/grub.cfg

#. For both legacy and EFI booting: mirror ESP content::
   
    ESP_MIRROR=$(mktemp -d)
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done

Enable Secure Boot
----------------------------

This is optional. `See Arch Wiki article <https://wiki.archlinux.org/title/Secure_Boot>`__.

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

Post installaion
~~~~~~~~~~~~~~~~

#. If you have other data pools, generate list of datasets for `zfs-mount-generator
   <https://manpages.ubuntu.com/manpages/focal/man8/zfs-mount-generator.8.html>`__ to mount them at boot::

    DATA_POOL='tank0 tank1'

    # tab-separated zfs properties
    # see /etc/zfs/zed.d/history_event-zfs-list-cacher.sh
    export \
    PROPS="name,mountpoint,canmount,atime,relatime,devices,exec\
    ,readonly,setuid,nbmand,encroot,keylocation"

    for i in $DATA_POOL; do
    zfs list -H -t filesystem -o $PROPS -r $i > /etc/zfs/zfs-list.cache/$i
    done

#. After reboot, consider adding a normal user::

    myUser=UserName
    zfs create $(df --output=source /home | tail -n +2)/${myUser}
    useradd -MUd /home/${myUser} -c 'My Name' ${myUser}
    zfs allow -u ${myUser} mount,snapshot,destroy $(df --output=source /home | tail -n +2)/${myUser}
    chown -R ${myUser}:${myUser} /home/${myUser}
    chmod 700 /home/${myUser}
    passwd ${myUser}

   Set up cron job to snapshot user home everyday::

    pacman -S cronie
    systemctl enable --now cronie
    crontab -eu ${myUser}
    #@daily zfs snap $(df --output=source /home/${myUser} | tail -n +2)@$(dd if=/dev/urandom of=/dev/stdout bs=1 count=100 2>/dev/null |tr -dc 'a-z0-9' | cut -c-6)
    zfs list -t snapshot -S creation $(df --output=source /home/${myUser} | tail -n +2)

   Install package groups::

    pacman -Sg        # query package groups
    pacman -S 'gnome'
    pacman -S 'plasma'

