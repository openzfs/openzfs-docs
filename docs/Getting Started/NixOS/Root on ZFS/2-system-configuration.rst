.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Optional: wipe solid-state drives with the generic tool
   `blkdiscard <https://utcc.utoronto.ca/~cks/space/blog/linux/ErasingSSDsWithBlkdiscard>`__,
   to clean previous partition tables and improve performance.

   All content will be irrevocably destroyed::

    for i in ${DISK}; do
    blkdiscard -f $i &
    done
    wait

   This is a quick operation and should be completed under one
   minute.

   For other device specific methods, see
   `Memory cell clearing <https://wiki.archlinux.org/title/Solid_state_drive/Memory_cell_clearing>`__

#. Partition the disks.
   See `Overview <0-overview.html>`__ for details::

     for i in ${DISK}; do
     sgdisk --zap-all $i
     sgdisk -n1:1M:+${INST_PARTSIZE_ESP}G -t1:EF00 $i
     sgdisk -n2:0:+${INST_PARTSIZE_BPOOL}G -t2:BE00 $i
     if [ "${INST_PARTSIZE_SWAP}" != "" ]; then
         sgdisk -n4:0:+${INST_PARTSIZE_SWAP}G -t4:8200 $i
     fi
     if [ "${INST_PARTSIZE_RPOOL}" = "" ]; then
         sgdisk -n3:0:0   -t3:BF00 $i
     else
         sgdisk -n3:0:+${INST_PARTSIZE_RPOOL}G -t3:BF00 $i
     fi
     sgdisk -a1 -n5:24K:+1000K -t5:EF02 $i
     done

#. Create boot pool::


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
        -R /mnt \
        bpool_$INST_UUID \
         $INST_VDEV_BPOOL \
        $(for i in ${DISK}; do
           printf "$i-part2 ";
          done)

   You should not need to customize any of the options for the boot pool.

   GRUB does not support all of the zpool features. See ``spa_feature_names``
   in `grub-core/fs/zfs/zfs.c
   <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
   This step creates a separate boot pool for ``/boot`` with the features
   limited to only those that GRUB supports, allowing the root pool to use
   any/all features.

   Features enabled with ``-o compatibility=grub2`` can be seen
   `here <https://github.com/openzfs/zfs/blob/master/cmd/zpool/compatibility.d/grub2>`__.

#. Create root pool::

       zpool create \
           -o ashift=12 \
           -o autotrim=on \
           -R /mnt \
           -O acltype=posixacl \
           -O canmount=off \
           -O compression=zstd \
           -O dnodesize=auto \
           -O normalization=formD \
           -O relatime=on \
           -O xattr=sa \
           -O mountpoint=/ \
           rpool_$INST_UUID \
           $INST_VDEV \
          $(for i in ${DISK}; do
             printf "$i-part3 ";
            done)

   **Notes:**

   - The use of ``ashift=12`` is recommended here because many drives
     today have 4 KiB (or larger) physical sectors, even though they
     present 512 B logical sectors. Also, a future replacement drive may
     have 4 KiB physical sectors (in which case ``ashift=12`` is desirable)
     or 4 KiB logical sectors (in which case ``ashift=12`` is required).
   - Setting ``-O acltype=posixacl`` enables POSIX ACLs globally. If you
     do not want this, remove that option, but later add
     ``-o acltype=posixacl`` (note: lowercase “o”) to the ``zfs create``
     for ``/var/log``, as `journald requires ACLs
     <https://askubuntu.com/questions/970886/journalctl-says-failed-to-search-journal-acl-operation-not-supported>`__
   - Setting ``normalization=formD`` eliminates some corner cases relating
     to UTF-8 filename normalization. It also implies ``utf8only=on``,
     which means that only UTF-8 filenames are allowed. If you care to
     support non-UTF-8 filenames, do not use this option. For a discussion
     of why requiring UTF-8 filenames may be a bad idea, see `The problems
     with enforced UTF-8 only filenames
     <http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames>`__.
   - ``recordsize`` is unset (leaving it at the default of 128 KiB). If you
     want to tune it (e.g. ``-o recordsize=1M``), see `these
     <https://jrs-s.net/2019/04/03/on-zfs-recordsize/>`__ `various
     <http://blog.programster.org/zfs-record-size>`__ `blog
     <https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSFileRecordsizeGrowth>`__
     `posts
     <https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSRecordsizeAndCompression>`__.
   - Setting ``relatime=on`` is a middle ground between classic POSIX
     ``atime`` behavior (with its significant performance impact) and
     ``atime=off`` (which provides the best performance by completely
     disabling atime updates). Since Linux 2.6.30, ``relatime`` has been
     the default for other filesystems. See `RedHat’s documentation
     <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/power_management_guide/relatime>`__
     for further information.
   - Setting ``xattr=sa`` `vastly improves the performance of extended
     attributes
     <https://github.com/zfsonlinux/zfs/commit/82a37189aac955c81a59a5ecc3400475adb56355>`__.
     Inside ZFS, extended attributes are used to implement POSIX ACLs.
     Extended attributes can also be used by user-space applications.
     `They are used by some desktop GUI applications.
     <https://en.wikipedia.org/wiki/Extended_file_attributes#Linux>`__
     `They can be used by Samba to store Windows ACLs and DOS attributes;
     they are required for a Samba Active Directory domain controller.
     <https://wiki.samba.org/index.php/Setting_up_a_Share_Using_Windows_ACLs>`__
     Note that ``xattr=sa`` is `Linux-specific
     <https://openzfs.org/wiki/Platform_code_differences>`__. If you move your
     ``xattr=sa`` pool to another OpenZFS implementation besides ZFS-on-Linux,
     extended attributes will not be readable (though your data will be). If
     portability of extended attributes is important to you, omit the
     ``-O xattr=sa`` above. Even if you do not want ``xattr=sa`` for the whole
     pool, it is probably fine to use it for ``/var/log``.
   - Make sure to include the ``-part3`` portion of the drive path. If you
     forget that, you are specifying the whole disk, which ZFS will then
     re-partition, and you will lose the bootloader partition(s).

#. This section implements dataset layout as described in `overview <0-overview.html>`__.

   Create root system container:

   - Unencrypted::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       rpool_$INST_UUID/$INST_ID

   - Encrypted:

     Pick a strong password. Once compromised, changing password will not keep your
     data safe. See ``zfs-change-key(8)`` for more info::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
       -o encryption=aes-256-gcm \
       -o keylocation=prompt \
       -o keyformat=passphrase \
       rpool_$INST_UUID/$INST_ID

   Create other system datasets::

    zfs create -o canmount=off -o mountpoint=none bpool_$INST_UUID/$INST_ID
    zfs create -o canmount=off -o mountpoint=none bpool_$INST_UUID/$INST_ID/BOOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/$INST_ID/ROOT
    zfs create -o canmount=off -o mountpoint=none rpool_$INST_UUID/$INST_ID/DATA
    zfs create -o mountpoint=/boot -o canmount=noauto bpool_$INST_UUID/$INST_ID/BOOT/default
    zfs create -o mountpoint=/ -o canmount=off    rpool_$INST_UUID/$INST_ID/DATA/default
    zfs create -o mountpoint=/ -o canmount=off    rpool_$INST_UUID/$INST_ID/DATA/local
    zfs create -o mountpoint=/ -o canmount=noauto rpool_$INST_UUID/$INST_ID/ROOT/default
    zfs mount rpool_$INST_UUID/$INST_ID/ROOT/default
    zfs mount bpool_$INST_UUID/$INST_ID/BOOT/default
    for i in {usr,var,var/lib};
    do
        zfs create -o canmount=off rpool_$INST_UUID/$INST_ID/DATA/default/$i
    done
    for i in {home,root,srv,usr/local,var/log,var/spool};
    do
        zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/$i
    done
    chmod 750 /mnt/root
    for i in {nix,}; do
        zfs create -o canmount=on -o mountpoint=/$i rpool_$INST_UUID/$INST_ID/DATA/local/$i
    done

    zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/state
    for i in {/etc/nixos,/etc/cryptkey.d}; do
      mkdir -p /mnt/state/$i /mnt/$i
      mount -o bind /mnt/state/$i /mnt/$i
    done
    zfs create -o mountpoint=/ -o canmount=noauto rpool_$INST_UUID/$INST_ID/ROOT/empty
    zfs snapshot rpool_$INST_UUID/$INST_ID/ROOT/empty@start

#. Format and mount ESP::

    for i in ${DISK}; do
     mkfs.vfat -n EFI ${i}-part1
     mkdir -p /mnt/boot/efis/${i##*/}-part1
     mount -t vfat ${i}-part1 /mnt/boot/efis/${i##*/}-part1
    done
    mkdir -p /mnt/boot/efi
    mount -t vfat ${INST_PRIMARY_DISK}-part1 /mnt/boot/efi

#. Create optional user data datasets to omit data from rollback::

     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/games
     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/www
     # for GNOME
     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/lib/AccountsService
     # for Docker
     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/lib/docker
     # for NFS
     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/lib/nfs
     # for LXC
     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/lib/lxc
     # for LibVirt
     zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/lib/libvirt
     ##other application
     # zfs create -o canmount=on rpool_$INST_UUID/$INST_ID/DATA/default/var/lib/$name

   Add other datasets when needed, such as PostgreSQL.

#. Generate initial NixOS system configuration::

    nixos-generate-config --root /mnt

   This command will generate two files, ``configuration.nix``
   and ``hardware-configuration-zfs.nix``, which will be the starting point
   of configuring the system.

#. Edit config file to import ZFS options::

    sed -i "s|./hardware-configuration.nix|./hardware-configuration-zfs.nix ./${INST_CONFIG_FILE}|g" /mnt/etc/nixos/configuration.nix
    # backup, prevent being overwritten by nixos-generate-config
    mv /mnt/etc/nixos/hardware-configuration.nix /mnt/etc/nixos/hardware-configuration-zfs.nix

#. ZFS options::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
    { config, pkgs, ... }:

    { boot.supportedFilesystems = [ "zfs" ];
      networking.hostId = "$(head -c 8 /etc/machine-id)";
      boot.zfs.devNodes = "${INST_PRIMARY_DISK%/*}";
    EOF

   ZFS datasets should be mounted with ``-o zfsutil`` option::

    sed -i 's|fsType = "zfs";|fsType = "zfs"; options = [ "zfsutil" "X-mount.mkdir" ];|g' \
    /mnt/etc/nixos/hardware-configuration-zfs.nix

   Allow EFI system partition mounting to fail at boot::

    sed -i 's|fsType = "vfat";|fsType = "vfat"; options = [ "x-systemd.idle-timeout=1min" "x-systemd.automount" "noauto" ];|g' \
    /mnt/etc/nixos/hardware-configuration-zfs.nix

   Restrict kernel to versions supported by ZFS::

     tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
       boot.kernelPackages = config.boot.zfs.package.latestCompatibleLinuxPackages;
     EOF

   Disable cache::

    mkdir -p /mnt/state/etc/zfs/
    rm -f /mnt/state/etc/zfs/zpool.cache
    touch /mnt/state/etc/zfs/zpool.cache
    chmod a-w /mnt/state/etc/zfs/zpool.cache
    chattr +i /mnt/state/etc/zfs/zpool.cache

#. If swap is enabled::

    if [ "${INST_PARTSIZE_SWAP}" != "" ]; then
    sed -i '/swapDevices/d' /mnt/etc/nixos/hardware-configuration-zfs.nix

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      swapDevices = [
    EOF
    for i in $DISK; do
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
        { device = "$i-part4"; randomEncryption.enable = true; }
    EOF
    done
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      ];
    EOF
    fi

#. For immutable root file system, save machine-id and other files::

    mkdir -p /mnt/state/etc/{ssh,zfs}
    systemd-machine-id-setup --print > /mnt/state/etc/machine-id
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      systemd.services.zfs-mount.enable = false;
      environment.etc."machine-id".source = "/state/etc/machine-id";
      environment.etc."zfs/zpool.cache".source
        = "/state/etc/zfs/zpool.cache";
    EOF

#. Configure GRUB boot loader for both legacy boot and UEFI::

    sed -i '/boot.loader/d' /mnt/etc/nixos/configuration.nix
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<-'EOF'
      boot.loader = {
        generationsDir.copyKernels = true;
        ##for problematic UEFI firmware
        grub.efiInstallAsRemovable = true;
        efi.canTouchEfiVariables = false;
        ##if UEFI firmware can detect entries
        #efi.canTouchEfiVariables = true;
        efi.efiSysMountPoint = "/boot/efi";
        grub.enable = true;
        grub.version = 2;
        grub.copyKernels = true;
        grub.efiSupport = true;
        grub.zfsSupport = true;
        # for systemd-autofs
        grub.extraPrepareConfig = ''
          mkdir -p /boot/efis /boot/efi
          for i in  /boot/efis/*; do mount $i ; done
          mount /boot/efi
        '';
        grub.extraInstallCommands = ''
           export ESP_MIRROR=$(mktemp -d -p /tmp)
           cp -r /boot/efi/EFI $ESP_MIRROR
           for i in /boot/efis/*; do
            cp -r $ESP_MIRROR/EFI $i
           done
           rm -rf $ESP_MIRROR
        '';
        grub.devices = [
    EOF
    for i in $DISK; do
      printf "      \"$i\"\n" >>/mnt/etc/nixos/${INST_CONFIG_FILE}
    done
    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
        ];
      };
    EOF
