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
instance of an operating system.

`bieaz <https://gitlab.com/m_zhou/bieaz/-/releases/>`__ can
be installed to manage boot environments. Download and install
prebuilt rpm file.

Encrypt boot pool
~~~~~~~~~~~~~~~~~~~

**WARNING**: Encrypting boot pool may cause significant boot time increases.
In test installation, GRUB took nearly 2 minutes to decrypt LUKS container.

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

#. Backup boot pool::

    zfs snapshot -r bpool_$INST_UUID/$INST_ID@pre-luks
    zfs send -Rv bpool_$INST_UUID/$INST_ID@pre-luks > /root/bpool_$INST_UUID-${INST_ID}-pre-luks

#. Unmount EFI partition::

    umount /boot/efi

    for i in ${DISK[@]}; do
     umount /boot/efis/${i##*/}-part1
    done

#. Destroy boot pool::

    zpool destroy bpool_$INST_UUID

#. Create LUKS containers::

    for i in ${DISK[@]}; do
     cryptsetup luksFormat -q --type luks1 --key-file /etc/cryptkey.d/bpool_$INST_UUID-key-luks $i-part2
     echo $LUKS_PWD | cryptsetup luksAddKey --key-file /etc/cryptkey.d/bpool_$INST_UUID-key-luks $i-part2
     cryptsetup open ${i}-part2 ${i##*/}-part2-luks-bpool_$INST_UUID --key-file /etc/cryptkey.d/bpool_$INST_UUID-key-luks
     echo ${i##*/}-part2-luks-bpool_$INST_UUID ${i}-part2 /etc/cryptkey.d/bpool_$INST_UUID-key-luks discard >> /etc/crypttab
    done

   GRUB 2.06 still does not have complete support for LUKS2, LUKS1
   is used instead.

#. Embed key file in initrd::

    echo "install_items+=\" \
     /etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs \
     /etc/cryptkey.d/bpool_$INST_UUID-key-luks \"" \
     > /etc/dracut.conf.d/rpool_$INST_UUID-${INST_ID}-key-zfs.conf

#. Recreate boot pool with mappers as vdev::

    zpool create \
    -d -o feature@async_destroy=enabled \
    -o feature@bookmarks=enabled \
    -o feature@embedded_data=enabled \
    -o feature@empty_bpobj=enabled \
    -o feature@enabled_txg=enabled \
    -o feature@extensible_dataset=enabled \
    -o feature@filesystem_limits=enabled \
    -o feature@hole_birth=enabled \
    -o feature@large_blocks=enabled \
    -o feature@lz4_compress=enabled \
    -o feature@spacemap_histogram=enabled \
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
        $INST_VDEV \
        $(for i in ${DISK[@]}; do
           printf "/dev/mapper/${i##*/}-part2-luks-bpool_$INST_UUID ";
          done)

#. Restore boot pool backup::

    zfs recv bpool_${INST_UUID}/${INST_ID} < /root/bpool_$INST_UUID-${INST_ID}-pre-luks
    rm /root/bpool_$INST_UUID-${INST_ID}-pre-luks

#. Mount boot dataset and EFI partitions::

    mount /boot
    mount /boot/efi

    for i in ${DISK[@]}; do
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

#. Enable GRUB cryptodisk::

        echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub

#. Import bpool service::

    tee /etc/systemd/system/zfs-import-bpool-mapper.service <<EOF
    [Unit]
    Description=Import encrypted boot pool
    Documentation=man:zpool(8)
    DefaultDependencies=no
    Requires=systemd-udev-settle.service
    After=cryptsetup.target
    Before=boot.mount
    ConditionPathIsDirectory=/sys/module/zfs
    
    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/sbin/zpool import -aNd /dev/mapper
    
    [Install]
    WantedBy=zfs-import.target
    EOF
    systemctl enable zfs-import-bpool-mapper.service

#. **Important**: Back up root dataset key ``/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs``
   to a secure location.

   In the possible event of LUKS container corruption,
   data on root set will only be available
   with this key.
