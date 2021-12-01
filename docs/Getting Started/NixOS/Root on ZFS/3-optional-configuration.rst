.. highlight:: sh

Optional Configuration
======================

.. contents:: Table of Contents
   :local:

Skip to `System Installation <./4-system-installation.html>`__ section if
no optional configuration is needed.

Supply password with SSH
~~~~~~~~~~~~~~~~~~~~~~~~

Note: if you choose to encrypt boot pool, where decryption is handled
by GRUB, as described in the next section, configuration performed
in this section will have no effect.

This example uses DHCP::

 mkdir -p /mnt/etc/state/ssh/
 ssh-keygen -t ed25519 -N "" -f /mnt/state/etc/ssh/ssh_host_initrd_ed25519_key
 tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
   #networking.interfaces.enp1s0.useDHCP = true;
   boot = {
     initrd.network = {
       enable = true;
       ssh = {
         enable = true;
         hostKeys = [ /state/etc/ssh/ssh_host_initrd_ed25519_key ];
         authorizedKeys = [ "$YOUR_PUBLIC_KEY" ];
       };
       postCommands = ''
         echo "zfs load-key -a; killall zfs" >> /root/.profile
       '';
     };
   };
 EOF

Encrypt boot pool
~~~~~~~~~~~~~~~~~~~
Note: This will disable password with SSH. The password previously set for
root pool will be replaced by keyfile, embedded in initrd.

#. Add package::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      environment.systemPackages = [ pkgs.cryptsetup ];
    EOF

#. LUKS password::

    LUKS_PWD=secure-passwd

   You will need to enter the same password for
   each disk at boot. As root pool key is
   protected by this password, the previous warning
   about password strength still apply.

   Double-check password here. Complete reinstallation is
   needed if entered wrong.

#. Create encryption keys::

    mkdir -p /mnt/etc/cryptkey.d/
    chmod 700 /mnt/etc/cryptkey.d/
    dd bs=32 count=1 if=/dev/urandom of=/mnt/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs
    dd bs=32 count=1 if=/dev/urandom of=/mnt/etc/cryptkey.d/bpool_$INST_UUID-key-luks
    chmod u=r,go= /mnt/etc/cryptkey.d/*

#. Backup boot pool::

    zfs snapshot -r bpool_$INST_UUID/$INST_ID@pre-luks
    zfs send -Rv bpool_$INST_UUID/$INST_ID@pre-luks > /mnt/root/bpool_$INST_UUID-${INST_ID}-pre-luks

#. Unmount EFI partition::

    for i in ${DISK}; do
     umount /mnt/boot/efis/${i##*/}-part1
    done
    umount /mnt/boot/efi

#. Destroy boot pool::

    zpool destroy bpool_$INST_UUID

#. Create LUKS containers::

    for i in ${DISK}; do
     cryptsetup luksFormat -q --type luks1 --key-file /mnt/etc/cryptkey.d/bpool_$INST_UUID-key-luks $i-part2
     echo $LUKS_PWD | cryptsetup luksAddKey --key-file /mnt/etc/cryptkey.d/bpool_$INST_UUID-key-luks $i-part2
     cryptsetup open ${i}-part2 ${i##*/}-part2-luks-bpool_$INST_UUID --key-file /mnt/etc/cryptkey.d/bpool_$INST_UUID-key-luks
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      boot.initrd.luks.devices = {
        "${i##*/}-part2-luks-bpool_$INST_UUID" = {
          device = "${i}-part2";
          allowDiscards = true;
          keyFile = "/etc/cryptkey.d/bpool_$INST_UUID-key-luks";
        };
      };
    EOF
    done

   GRUB 2.06 still does not have complete support for LUKS2, LUKS1
   is used instead.

#. Embed key file in initrd::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      boot.initrd.secrets = {
        "/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs" = "/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs";
        "/etc/cryptkey.d/bpool_$INST_UUID-key-luks" = "/etc/cryptkey.d/bpool_$INST_UUID-key-luks";
      };
    EOF

#. Recreate boot pool with mappers as vdev::

    disk_num=0; for i in $DISK; do disk_num=$(( $disk_num + 1 )); done
    if [ $disk_num -gt 1 ]; then INST_VDEV_BPOOL=mirror; fi


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
        -R /mnt \
        bpool_$INST_UUID \
         $INST_VDEV_BPOOL \
        $(for i in ${DISK}; do
           printf "/dev/mapper/${i##*/}-part2-luks-bpool_$INST_UUID ";
          done)

#. Restore boot pool backup::

    zfs recv bpool_${INST_UUID}/${INST_ID} < /mnt/root/bpool_$INST_UUID-${INST_ID}-pre-luks
    rm /mnt/root/bpool_$INST_UUID-${INST_ID}-pre-luks

#. Mount boot dataset and EFI partitions::

    zfs mount bpool_$INST_UUID/$INST_ID/BOOT/default

    for i in ${DISK}; do
     mount ${i}-part1 /mnt/boot/efis/${i##*/}-part1
    done

    mount -t vfat ${INST_PRIMARY_DISK}-part1 /mnt/boot/efi

#. As keys are stored in initrd,
   set secure permissions for ``/boot``::

    chmod 700 /mnt/boot

#. Change root pool password to key file::

    mkdir -p /etc/cryptkey.d/
    cp /mnt/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs /etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs
    zfs change-key -l \
    -o keylocation=file:///etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs \
    -o keyformat=raw \
    rpool_$INST_UUID/$INST_ID

#. Import encrypted boot pool from ``/dev/mapper``::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<-'EOF'
      systemd.services.zfs-import-bpool-mapper = {
        wantedBy = [ "zfs-import.target" ];
        description = "Import encrypted boot pool";
        after = [ "cryptsetup.target" ];
        before = [ "boot.mount" ];
        serviceConfig = {
          Type = "oneshot";
          ExecStart = ''${pkgs.zfs}/bin/zpool import -aNd /dev/mapper'';
        };
      };
    EOF

#. Enable GRUB cryptodisk::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      boot.loader.grub.enableCryptodisk = true;
    EOF

#. **Important**: Back up root dataset key ``/etc/cryptkey.d/rpool_$INST_UUID-${INST_ID}-key-zfs``
   to a secure location.

   In the possible event of LUKS container corruption,
   data on root set will only be available
   with this key.

Persistent swap and hibernation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Optional: enable persistent swap partition. By default
   encryption key of swap partition is discarded on reboot::

    INST_SWAPKEY=/mnt/etc/cryptkey.d/${INST_PRIMARY_DISK##*/}-part4-key-luks-swap
    INST_SWAPMAPPER=${INST_PRIMARY_DISK##*/}-part4-luks-swap

    # fstab
    # remove existing swap entries
    for i in $DISK; do echo $i; done | grep -v ${INST_PRIMARY_DISK##*/} \
    | while read j; do sed -i "\,$j-part4\"; randomEncryption.enable,d" /mnt/etc/nixos/${INST_CONFIG_FILE} ; done
    sed -i "s|${INST_PRIMARY_DISK}-part4\"; randomEncryption.enable = true|/dev/mapper/${INST_SWAPMAPPER}\"|g" /mnt/etc/nixos/${INST_CONFIG_FILE}

    # create key and format partition as LUKS container
    dd bs=32 count=1 if=/dev/urandom of=${INST_SWAPKEY};
    chmod u=r,go= /mnt/etc/cryptkey.d/*
    cryptsetup luksFormat -q --type luks2 --key-file ${INST_SWAPKEY} ${INST_PRIMARY_DISK}-part4
    cryptsetup luksOpen ${INST_PRIMARY_DISK}-part4 ${INST_SWAPMAPPER} --key-file ${INST_SWAPKEY}

    # initialize swap space
    mkswap /dev/mapper/${INST_SWAPMAPPER}

    # add initrd key
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      boot.initrd.secrets = {
        "/etc/cryptkey.d/${INST_PRIMARY_DISK##*/}-part4-key-luks-swap" = "/etc/cryptkey.d/${INST_PRIMARY_DISK##*/}-part4-key-luks-swap";
      };
      boot.initrd.luks.devices = {
        "${INST_SWAPMAPPER}" = {
          device = "${INST_PRIMARY_DISK}-part4";
          allowDiscards = true;
          keyFile = "/etc/cryptkey.d/${INST_PRIMARY_DISK##*/}-part4-key-luks-swap";
        };
      };
    EOF

#. Optional: after enabling persistent swap partition,
   enable hibernation::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      boot.resumeDevice = "/dev/mapper/${INST_SWAPMAPPER}";
    EOF


   Note that hibernation might not work with discrete graphics, virtio graphics or
   AMD APU integrated graphics. This is not specific to this guide.

   Computer must resume from a continuous swap space, resume
   from multiple swap partitions is not supported.

   Do not touch anything on disk while the computer is
   in hibernation, see `kernel documentation
   <https://www.kernel.org/doc/html/latest/power/swsusp.html>`__.
