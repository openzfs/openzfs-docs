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

Install GRUB
~~~~~~~~~~~~~~~~~~~~

#. If using virtio disk, add driver to initrd::

    echo 'filesystems+=" virtio_blk "' >> /etc/dracut.conf.d/fs.conf

#. Generate initrd::

    rm -f /etc/zfs/zpool.cache
    touch /etc/zfs/zpool.cache
    chmod a-w /etc/zfs/zpool.cache
    chattr +i /etc/zfs/zpool.cache
    ls -1 /lib/modules \
    | while read kernel_version; do
      dracut --force --kver $kernel_version
      done

#. When in doubt, install both legacy boot
   and EFI.

#. Load ZFS modules and disable BLS::

    echo 'GRUB_ENABLE_BLSCFG=false' >> /etc/default/grub

#. Create GRUB boot directory, in ESP and boot pool::

    mkdir -p /boot/efi/EFI/rocky        # EFI GRUB dir
    mkdir -p /boot/efi/EFI/rocky/grub2  # legacy GRUB dir
    mkdir -p /boot/grub2

   Boot environment-specific configuration (kernel, etc)
   is stored in ``/boot/grub2/grub.cfg``, enabling rollback.

#. If using legacy booting, install GRUB to every disk::

    for i in ${DISK[@]}; do
     grub2-install --boot-directory /boot/efi/EFI/rocky --target=i386-pc $i
    done

#. If using EFI::

    for i in ${DISK[@]}; do
     efibootmgr -cgp 1 -l "\EFI\rocky\shimx64.efi" \
     -L "rocky-${i##*/}" -d ${i}
    done
    cp -r /usr/lib/grub/x86_64-efi/ /boot/efi/EFI/rocky

#. Generate GRUB Menu::

    grub2-mkconfig -o /boot/efi/EFI/rocky/grub.cfg
    cp /boot/efi/EFI/rocky/grub.cfg /boot/efi/EFI/rocky/grub2/grub.cfg
    cp /boot/efi/EFI/rocky/grub.cfg /boot/grub2/grub.cfg

   If the following error is seen::

    # /usr/sbin/grub2-probe: error: ../grub-core/kern/fs.c:120:unknown filesystem.

   Apply workaround::

    tee /etc/grub.d/09_fix_root_on_zfs <<EOF
    #!/bin/sh
    echo 'insmod zfs'
    echo 'set root=(hd0,gpt2)'
    EOF
    chmod +x /etc/grub.d/09_fix_root_on_zfs

   Regenerate menu with steps above.

#. For both legacy and EFI booting: mirror ESP content::

    ESP_MIRROR=$(mktemp -d)
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done

#. Notes for GRUB on RHEL

   To support Secure Boot, GRUB has been heavily modified by Fedora,
   namely:

    - ``grub2-install`` is `disabled for UEFI <https://bugzilla.redhat.com/show_bug.cgi?id=1917213>`__
    - Only a static, signed version of bootloader is copied to EFI system partition
    - This signed bootloader does not have built-in support for either ZFS or LUKS containers
    - This signed bootloader only loads configuration from ``/boot/efi/EFI/fedora/grub.cfg``

   Unrelated to Secure Boot, GRUB has also been modified to provide optional
   support for `systemd bootloader specification (bls) <https://systemd.io/BOOT_LOADER_SPECIFICATION/>`__.
   Currently ``blscfg.mod`` is incompatible with root on ZFS.

   Also see `Fedora docs for GRUB
   <https://docs.fedoraproject.org/en-US/fedora/rawhide/system-administrators-guide/kernel-module-driver-configuration/Working_with_the_GRUB_2_Boot_Loader/>`__.

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

#. After reboot, consider adding a normal user::

    myUser=UserName
    zfs create $(df --output=source /home | tail -n +2)/${myUser}
    useradd -MUd /home/${myUser} -c 'My Name' ${myUser}
    zfs allow -u ${myUser} mount,snapshot,destroy $(df --output=source /home | tail -n +2)/${myUser}
    chown -R ${myUser}:${myUser} /home/${myUser}
    chmod 700 /home/${myUser}
    restorecon /home/${myUser}
    passwd ${myUser}

   Set up cron job to snapshot user home everyday::

    dnf install cronie
    systemctl enable --now crond
    crontab -eu ${myUser}
    #@daily zfs snap $(df --output=source /home/${myUser} | tail -n +2)@$(dd if=/dev/urandom of=/dev/stdout bs=1 count=100 2>/dev/null |tr -dc 'a-z0-9' | cut -c-6)
    zfs list -t snapshot -S creation $(df --output=source /home/${myUser} | tail -n +2)

   Install package groups::

    dnf group list                         # query package groups
    dnf group install 'Virtualization Host'
