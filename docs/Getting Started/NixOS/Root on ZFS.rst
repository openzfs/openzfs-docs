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
**Note for arm64**:

Currently there is a bug with the grub installation script.  See `here
<https://github.com/NixOS/nixpkgs/issues/222491>`__ for details.

**Note for Immutable Root**:

Immutable root can be enabled or disabled by setting
``zfs-root.boot.immutable`` option inside per-host configuration.

**Customization**

Unless stated otherwise, it is not recommended to customize system
configuration before reboot.

**Only use well-tested pool features**

You should only use well-tested pool features.  Avoid using new features if data integrity is paramount.  See, for example, `this comment <https://github.com/openzfs/openzfs-docs/pull/464#issuecomment-1776918481>`__.

Preparation
---------------------------

#. Disable Secure Boot. ZFS modules can not be loaded if Secure Boot is enabled.
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

#. Enable Nix Flakes functionality
   ::

      mkdir -p ~/.config/nix
      echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

#. Install programs needed for system installation
   ::

      if ! command -v git; then nix-env -f '<nixpkgs>' -iA git; fi
      if ! command -v partprobe;  then nix-env -f '<nixpkgs>' -iA parted; fi

   .. ifconfig:: zfs_root_test

      ::

       # install missing packages in chroot
       if (echo "${DISK}" | grep "/dev/loop"); then
         nix-env -f '<nixpkgs>' -iA nixos-install-tools
       fi

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
      mkpart EFI 2MiB 1GiB \
      mkpart bpool 1GiB 5GiB \
      mkpart rpool 5GiB -$((SWAPSIZE + RESERVE))GiB \
      mkpart swap  -$((SWAPSIZE + RESERVE))GiB -"${RESERVE}"GiB \
      mkpart BIOS 1MiB 2MiB \
      set 1 esp on \
      set 5 bios_grub on \
      set 5 legacy_boot on

      partprobe "${disk}"
      udevadm settle
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

#. Setup encrypted swap.  This is useful if the available memory is
   small::

     for i in ${DISK}; do
        cryptsetup open --type plain --key-file /dev/random "${i}"-part4 "${i##*/}"-part4
        mkswap /dev/mapper/"${i##*/}"-part4
        swapon /dev/mapper/"${i##*/}"-part4
     done

#. **LUKS only**: Setup encrypted LUKS container for root pool::

     for i in ${DISK}; do
        # see PASSPHRASE PROCESSING section in cryptsetup(8)
        printf "YOUR_PASSWD" | cryptsetup luksFormat --type luks2 "${i}"-part3 -
        printf "YOUR_PASSWD" | cryptsetup luksOpen "${i}"-part3 luks-rpool-"${i##*/}"-part3 -
     done

#. Create boot pool
   ::

      # shellcheck disable=SC2046
      zpool create -o compatibility=legacy  \
          -o ashift=12 \
          -o autotrim=on \
          -O acltype=posixacl \
          -O canmount=off \
          -O devices=off \
          -O normalization=formD \
          -O relatime=on \
          -O xattr=sa \
          -O mountpoint=/boot \
          -R "${MNT}" \
          bpool \
        mirror \
          $(for i in ${DISK}; do
             printf '%s ' "${i}-part2";
            done)

   If not using a multi-disk setup, remove ``mirror``.

   You should not need to customize any of the options for the boot pool.

   GRUB does not support all of the zpool features. See ``spa_feature_names``
   in `grub-core/fs/zfs/zfs.c
   <http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276>`__.
   This step creates a separate boot pool for ``/boot`` with the features
   limited to only those that GRUB supports, allowing the root pool to use
   any/all features.

   Features enabled with ``-o compatibility=grub2`` can be seen
   `here <https://github.com/openzfs/zfs/blob/master/cmd/zpool/compatibility.d/grub2>`__.

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
           -O compression=zstd \
           -O dnodesize=auto \
           -O normalization=formD \
           -O relatime=on \
           -O xattr=sa \
           -O mountpoint=/ \
           rpool \
           mirror \
          $(for i in ${DISK}; do
             printf '%s ' "${i}-part3";
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
           -O compression=zstd \
           -O dnodesize=auto \
           -O normalization=formD \
           -O relatime=on \
           -O xattr=sa \
           -O mountpoint=/ \
           rpool \
           mirror \
          $(for i in ${DISK}; do
             printf '/dev/mapper/luks-rpool-%s ' "${i##*/}-part3";
            done)

   If not using a multi-disk setup, remove ``mirror``.

#. Create root system container:

   - Unencrypted

     ::

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
      rpool/nixos

   - Encrypted:

     Avoid ZFS send/recv when using native encryption, see `a ZFS developer's comment on
     this issue`__ and `this spreadsheet of bugs`__.  In short, if you
     care about your data, don't use native encryption.  This section
     has been removed, use LUKS encryption instead.

   Create system datasets,
   manage mountpoints with ``mountpoint=legacy``
   ::

      zfs create -o mountpoint=legacy     rpool/nixos/root
      mount -t zfs rpool/nixos/root "${MNT}"/
      zfs create -o mountpoint=legacy rpool/nixos/home
      mkdir "${MNT}"/home
      mount -t zfs rpool/nixos/home "${MNT}"/home
      zfs create -o mountpoint=none   rpool/nixos/var
      zfs create -o mountpoint=legacy rpool/nixos/var/lib
      zfs create -o mountpoint=legacy rpool/nixos/var/log
      zfs create -o mountpoint=none bpool/nixos
      zfs create -o mountpoint=legacy bpool/nixos/root
      mkdir "${MNT}"/boot
      mount -t zfs bpool/nixos/root "${MNT}"/boot
      mkdir -p "${MNT}"/var/log
      mkdir -p "${MNT}"/var/lib
      mount -t zfs rpool/nixos/var/lib "${MNT}"/var/lib
      mount -t zfs rpool/nixos/var/log "${MNT}"/var/log
      zfs create -o mountpoint=legacy rpool/nixos/empty
      zfs snapshot rpool/nixos/empty@start

#. Format and mount ESP
   ::

     for i in ${DISK}; do
      mkfs.vfat -n EFI "${i}"-part1
      mkdir -p "${MNT}"/boot/efis/"${i##*/}"-part1
      mount -t vfat -o iocharset=iso8859-1 "${i}"-part1 "${MNT}"/boot/efis/"${i##*/}"-part1
     done


System Configuration
---------------------------

#. Clone template flake configuration

   .. code-block:: sh

     mkdir -p "${MNT}"/etc
     git clone --depth 1 --branch openzfs-guide \
       https://github.com/ne9z/dotfiles-flake.git "${MNT}"/etc/nixos

   .. ifconfig:: zfs_root_test

    ::

     # Use vm branch of the template config for test run
     mkdir -p "${MNT}"/etc
     git clone --depth 1 --branch openzfs-guide-testvm \
       https://github.com/ne9z/dotfiles-flake.git "${MNT}"/etc/nixos
     # for debugging: show template revision
     git -C "${MNT}"/etc/nixos log -n1

#. From now on, the complete configuration of the system will be
   tracked by git, set a user name and email address to continue
   ::

     rm -rf "${MNT}"/etc/nixos/.git
     git -C "${MNT}"/etc/nixos/ init -b main
     git -C "${MNT}"/etc/nixos/ add "${MNT}"/etc/nixos/
     git -C "${MNT}"/etc/nixos config user.email "you@example.com"
     git -C "${MNT}"/etc/nixos config user.name "Alice Q. Nixer"
     git -C "${MNT}"/etc/nixos commit -asm 'initial commit'

#. Customize configuration to your hardware

   ::

     for i in ${DISK}; do
       sed -i \
       "s|/dev/disk/by-id/|${i%/*}/|" \
       "${MNT}"/etc/nixos/hosts/exampleHost/default.nix
       break
     done

     diskNames=""
     for i in ${DISK}; do
       diskNames="${diskNames} \"${i##*/}\""
     done

     sed -i "s|\"bootDevices_placeholder\"|${diskNames}|g" \
       "${MNT}"/etc/nixos/hosts/exampleHost/default.nix

     sed -i "s|\"abcd1234\"|\"$(head -c4 /dev/urandom | od -A none -t x4| sed 's| ||g' || true)\"|g" \
       "${MNT}"/etc/nixos/hosts/exampleHost/default.nix

     sed -i "s|\"x86_64-linux\"|\"$(uname -m || true)-linux\"|g" \
       "${MNT}"/etc/nixos/flake.nix

#. **LUKS only**: Enable LUKS support::

     sed -i 's|luks.enable = false|luks.enable = true|' "${MNT}"/etc/nixos/hosts/exampleHost/default.nix

#. Detect kernel modules needed for boot

   .. code-block:: sh

     cp "$(command -v nixos-generate-config || true)" ./nixos-generate-config

     chmod a+rw ./nixos-generate-config

     # shellcheck disable=SC2016
     echo 'print STDOUT $initrdAvailableKernelModules' >> ./nixos-generate-config

     kernelModules="$(./nixos-generate-config --show-hardware-config --no-filesystems | tail -n1 || true)"

     sed -i "s|\"kernelModules_placeholder\"|${kernelModules}|g" \
       "${MNT}"/etc/nixos/hosts/exampleHost/default.nix

   .. ifconfig:: zfs_root_test

     ::

       sed -i "s|\"kernelModules_placeholder\"|\"nvme\"|g" \
         "${MNT}"/etc/nixos/hosts/exampleHost/default.nix

       # show generated config
       cat  "${MNT}"/etc/nixos/hosts/exampleHost/default.nix

#. Set root password

   .. code-block:: sh

     rootPwd=$(mkpasswd -m SHA-512)

   .. ifconfig:: zfs_root_test

    ::

     # Use "test" for root password in test run
     rootPwd=$(echo yourpassword | mkpasswd -m SHA-512 -)

   Declare password in configuration
   ::

     sed -i \
     "s|rootHash_placeholder|${rootPwd}|" \
     "${MNT}"/etc/nixos/configuration.nix

#. You can enable NetworkManager for wireless networks and GNOME
   desktop environment in ``configuration.nix``.

#. Commit changes to local repo
   ::

     git -C "${MNT}"/etc/nixos commit -asm 'initial installation'

#. Update flake lock file to track latest system version
   ::

     nix flake update --commit-lock-file \
       "git+file://${MNT}/etc/nixos"

#. Install system and apply configuration

   .. code-block:: sh

     nixos-install \
     --root "${MNT}" \
     --no-root-passwd \
     --flake "git+file://${MNT}/etc/nixos#exampleHost"

   .. ifconfig:: zfs_root_test

     ::

         if (echo "${DISK}" | grep "/dev/loop"); then
          # nixos-install command might fail in a chroot environment
          # due to
          # https://github.com/NixOS/nixpkgs/issues/220211
          # it should be sufficient to test if the configuration builds
          nix build "git+file://${MNT}/etc/nixos/#nixosConfigurations.exampleHost.config.system.build.toplevel"

          nixos-install \
          --root "${MNT}" \
          --no-root-passwd \
          --flake "git+file://${MNT}/etc/nixos#exampleHost" || true
         else
          # but with qemu test installation must be fully working
          nixos-install \
          --root "${MNT}" \
          --no-root-passwd \
          --flake "git+file://${MNT}/etc/nixos#exampleHost"
         fi

   .. ifconfig:: zfs_root_test

     ::

          # list contents of boot dir to confirm
          # that the mirroring succeeded
          find "${MNT}"/boot/efis/ -type d

#. Unmount filesystems
   ::

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

#. For instructions on maintenance tasks, see `Root on ZFS maintenance
   page <../zfs_root_maintenance.html>`__.
