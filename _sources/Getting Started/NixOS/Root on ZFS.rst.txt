.. highlight:: sh

.. ifconfig:: zfs_root_test

  # For the CI/CD test run of this guide,
  # Enable verbose logging of bash shell and fail immediately when
  # a commmand fails.
  set -vxeuf

.. In this document, there are three types of code-block markups:
   ``::`` are commands intended for both the vm test and the users
   ``.. ifconfig:: zfs_root_test`` are commands intended only for vm test
   ``.. code-block:: sh`` are commands intended only for users

NixOS Root on ZFS
=======================================

**Customization**

Unless stated otherwise, it is not recommended to customize system
configuration before reboot.

**UEFI support only**

Only UEFI is supported by this guide.  Make sure your computer is
booted in UEFI mode.

Preparation
---------------------------

#. Download `NixOS Live Image
   <https://nixos.org/download.html#nixos-iso>`__ and boot from it.

   .. code-block:: sh

       sha256sum -c ./nixos-*.sha256

       dd if=input-file of=output-file bs=1M

#. Connect to the Internet.
#. Set root password or ``/root/.ssh/authorized_keys``.
#. Start SSH server

   .. code-block:: sh

    systemctl restart sshd

#. Connect from another computer

   .. code-block:: sh

    ssh root@192.168.1.91

#. Target disk

   List available disks with

   .. code-block:: sh

    find /dev/disk/by-id/

   If virtio is used as disk bus, power off the VM and set serial numbers for disk.
   For QEMU, use ``-drive format=raw,file=disk2.img,serial=AaBb``.
   For libvirt, edit domain XML.  See `this page
   <https://bugzilla.redhat.com/show_bug.cgi?id=1245013>`__ for examples.

   Declare disk array

   .. code-block:: sh

    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'

   For single disk installation, use

   .. code-block:: sh

    DISK='/dev/disk/by-id/disk1'

   .. ifconfig:: zfs_root_test

    ::

         # install installation tools
         nix-env -f '<nixpkgs>' -iA nixos-install-tools

         # for github test run, use chroot and loop devices
         DISK="$(losetup --all| grep nixos | cut -f1 -d: | xargs -t -I '{}' printf '{} ')"

         # if there is no loopdev, then we are using qemu virtualized test
         # run, use sata disks instead
         if test -z "${DISK}"; then
           DISK=$(find /dev/disk/by-id -type l | grep -v DVD-ROM | grep -v -- -part | xargs -t -I '{}' printf '{} ')
         fi

#. Set a mount point
   ::

      MNT=$(mktemp -d)

#. Set partition size:

   Set swap size in GB, set to 1 if you don't want swap to
   take up too much space

   .. code-block:: sh

    SWAPSIZE=4

   .. ifconfig:: zfs_root_test

    # For the test run, use 1GB swap space to avoid hitting CI/CD
    # quota
    SWAPSIZE=1

   Set how much space should be left at the end of the disk, minimum 1GB

   ::

    RESERVE=1

System Installation
---------------------------

#. Partition the disks.

   Note: you must clear all existing partition tables and data structures from target disks.

   For flash-based storage, this can be done by the blkdiscard command below:
   ::

     partition_disk () {
      local disk="${1}"
      blkdiscard -f "${disk}" || true

      parted --script --align=optimal  "${disk}" -- \
      mklabel gpt \
      mkpart EFI 1MiB 4GiB \
      mkpart rpool 4GiB -$((SWAPSIZE + RESERVE))GiB \
      mkpart swap  -$((SWAPSIZE + RESERVE))GiB -"${RESERVE}"GiB \
      set 1 esp on \

      partprobe "${disk}"
     }

     for i in ${DISK}; do
        partition_disk "${i}"
     done

   .. ifconfig:: zfs_root_test

     ::

       # When working with GitHub chroot runners, we are using loop
       # devices as installation target.  However, the alias support for
       # loop device was just introduced in March 2023. See
       # https://github.com/systemd/systemd/pull/26693
       # For now, we will create the aliases maunally as a workaround
       looppart="1 2 3 4 5"
       for i in ${DISK}; do
         for j in ${looppart}; do
           if test -e "${i}p${j}"; then
                    ln -s "${i}p${j}" "${i}-part${j}"
                  fi
         done
       done

#. Setup temporary encrypted swap for this installation only.  This is
   useful if the available memory is small::

     for i in ${DISK}; do
        cryptsetup open --type plain --key-file /dev/random "${i}"-part3 "${i##*/}"-part3
        mkswap /dev/mapper/"${i##*/}"-part3
        swapon /dev/mapper/"${i##*/}"-part3
     done


#. **LUKS only**: Setup encrypted LUKS container for root pool::

     for i in ${DISK}; do
        # see PASSPHRASE PROCESSING section in cryptsetup(8)
        printf "YOUR_PASSWD" | cryptsetup luksFormat --type luks2 "${i}"-part2 -
        printf "YOUR_PASSWD" | cryptsetup luksOpen "${i}"-part2 luks-rpool-"${i##*/}"-part2 -
     done

#. Create root pool

   - Unencrypted

     .. code-block:: sh

       # shellcheck disable=SC2046
       zpool create \
           -o ashift=12 \
           -o autotrim=on \
           -R "${MNT}" \
           -O acltype=posixacl \
           -O canmount=off \
           -O dnodesize=auto \
           -O normalization=formD \
           -O relatime=on \
           -O xattr=sa \
           -O mountpoint=none \
           rpool \
           mirror \
          $(for i in ${DISK}; do
             printf '%s ' "${i}-part2";
            done)

   - LUKS encrypted

     ::

       # shellcheck disable=SC2046
       zpool create \
           -o ashift=12 \
           -o autotrim=on \
           -R "${MNT}" \
           -O acltype=posixacl \
           -O canmount=off \
           -O dnodesize=auto \
           -O normalization=formD \
           -O relatime=on \
           -O xattr=sa \
           -O mountpoint=none \
           rpool \
           mirror \
          $(for i in ${DISK}; do
             printf '/dev/mapper/luks-rpool-%s ' "${i##*/}-part2";
            done)

   If not using a multi-disk setup, remove ``mirror``.

#. Create root system container:

     ::

      zfs create -o canmount=noauto -o mountpoint=legacy rpool/root

   Create system datasets,
   manage mountpoints with ``mountpoint=legacy``
   ::

      zfs create -o mountpoint=legacy rpool/home
      mount -o X-mount.mkdir -t zfs rpool/root "${MNT}"
      mount -o X-mount.mkdir -t zfs rpool/home "${MNT}"/home

#. Format and mount ESP.  Only one of them is used as /boot, you need to set up mirroring afterwards
   ::

     for i in ${DISK}; do
      mkfs.vfat -n EFI "${i}"-part1
     done

     for i in ${DISK}; do
      mount -t vfat -o fmask=0077,dmask=0077,iocharset=iso8859-1,X-mount.mkdir "${i}"-part1 "${MNT}"/boot
      break
     done


System Configuration
---------------------------

#. Generate system configuration::

     nixos-generate-config --root "${MNT}"

#. Edit system configuration:

   .. code-block:: sh

      nano "${MNT}"/etc/nixos/hardware-configuration.nix

#. Set networking.hostId:

   .. code-block:: sh

      networking.hostId = "abcd1234";

#. If using LUKS, add the output from following command to system
   configuration

   .. code-block:: sh

     tee <<EOF
       boot.initrd.luks.devices = {
     EOF

     for i in ${DISK}; do echo \"luks-rpool-"${i##*/}-part2"\".device = \"${i}-part2\"\; ; done

     tee <<EOF
     };
     EOF

#. Install system and apply configuration

   .. code-block:: sh

     nixos-install  --root "${MNT}"

   Wait for the root password reset prompt to appear.

#. Unmount filesystems
   ::

    cd /
    umount -Rl "${MNT}"
    zpool export -a

#. Reboot

   .. code-block:: sh

     reboot

   .. ifconfig:: zfs_root_test

    ::

     # For qemu test run, power off instead.
     # Test run is successful if the vm powers off
     if ! (echo "${DISK}" | grep "/dev/loop"); then
       poweroff
     fi

#. Set up networking, desktop and swap.

#. Mount other EFI system partitions then set up a service for syncing
   their contents.
