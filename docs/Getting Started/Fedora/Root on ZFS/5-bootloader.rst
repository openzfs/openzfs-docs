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
    for directory in /lib/modules/*; do
      kernel_version=$(basename $directory)
      dracut --force --kver $kernel_version
    done

#. Disable BLS::

    echo "GRUB_ENABLE_BLSCFG=false" >> /etc/default/grub

#. Create GRUB boot directory, in ESP and boot pool::

    mkdir -p /boot/efi/EFI/fedora        # EFI GRUB dir
    mkdir -p /boot/efi/EFI/fedora/grub2  # legacy GRUB dir
    mkdir -p /boot/grub2

   Boot environment-specific configuration (kernel, etc)
   is stored in ``/boot/grub2/grub.cfg``, enabling rollback.

#. When in doubt, install both legacy boot
   and EFI.

#. If using legacy booting, install GRUB to every disk::

    for i in ${DISK}; do
     grub2-install --boot-directory /boot/efi/EFI/fedora --target=i386-pc $i
    done

#. If using EFI::

    for i in ${DISK}; do
     efibootmgr -cgp 1 -l "\EFI\fedora\shimx64.efi" \
     -L "fedora-${i##*/}" -d ${i}
    done
    cp -r /usr/lib/grub/x86_64-efi/ /boot/efi/EFI/fedora

#. Generate GRUB Menu::

    grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
    cp /boot/efi/EFI/fedora/grub.cfg /boot/efi/EFI/fedora/grub2/grub.cfg
    cp /boot/efi/EFI/fedora/grub.cfg /boot/grub2/grub.cfg

#. For both legacy and EFI booting: mirror ESP content::

    ESP_MIRROR=$(mktemp -d)
    unalias -a
    cp -r /boot/efi/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done

#. Automatically regenerate GRUB menu on kernel update::

     tee /etc/dnf/plugins/post-transaction-actions.d/00-update-grub-menu-for-kernel.action <<EOF >/dev/null
     # kernel-core package contains vmlinuz and initramfs
     # change package name if non-standard kernel is used
     kernel-core:in:/usr/local/sbin/update-grub-menu.sh
     kernel-core:out:/usr/local/sbin/update-grub-menu.sh
     EOF

     tee /usr/local/sbin/update-grub-menu.sh <<-'EOF' >/dev/null
     #!/bin/sh
     export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
     export ZPOOL_VDEV_NAME_PATH=YES
     source /etc/os-release
     grub2-mkconfig -o /boot/efi/EFI/${ID}/grub.cfg
     cp /boot/efi/EFI/${ID}/grub.cfg /boot/efi/EFI/${ID}/grub2/grub.cfg
     cp /boot/efi/EFI/${ID}/grub.cfg /boot/grub2/grub.cfg
     ESP_MIRROR=$(mktemp -d)
     cp -r /boot/efi/EFI $ESP_MIRROR
     for i in /boot/efis/*; do
      cp -r $ESP_MIRROR/EFI $i
     done
     rm -rf $ESP_MIRROR
     EOF

     chmod +x /usr/local/sbin/update-grub-menu.sh

#. Notes for GRUB on Fedora

   To support Secure Boot, GRUB has been heavily modified by Fedora,
   namely:

   - ``grub2-install`` is `disabled for UEFI <https://bugzilla.redhat.com/show_bug.cgi?id=1917213>`__
   - Only a static, signed version of bootloader is copied to EFI system partition
   - This signed bootloader does not have built-in support for either ZFS or LUKS containers
   - This signed bootloader only loads configuration from ``/boot/efi/EFI/fedora/grub.cfg``

   Unrelated to Secure Boot, GRUB has also been modified to provide optional
   support for `systemd bootloader specification (bls) <https://systemd.io/BOOT_LOADER_SPECIFICATION/>`__.
   Currently ``blscfg.mod`` is incompatible with root on ZFS.

   As bls is disabled, you will need to regenerate GRUB menu after each kernel upgrade.
   Or else the new kernel will not be recognized and system will boot the old kernel
   on reboot.

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
    restorecon /home/${myUser}
    passwd ${myUser}

   Set up cron job to snapshot user home everyday::

    dnf install cronie
    systemctl enable --now crond
    crontab -eu ${myUser}
    #@daily /usr/sbin/zfs snap $(df --output=source /home/${myUser} | tail -n +2)@$(dd if=/dev/urandom of=/dev/stdout bs=1 count=100 2>/dev/null |tr -dc 'a-z0-9' | cut -c-6)
    zfs list -t snapshot -S creation $(df --output=source /home/${myUser} | tail -n +2)

   Install package groups::

    dnf group list --hidden -v       # query package groups
    dnf group install 'i3 Desktop'
    dnf group install 'Fedora Workstation' # GNOME
    dnf group install 'Web Server'
