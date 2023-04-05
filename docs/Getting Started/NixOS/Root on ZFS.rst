.. ifconfig:: zfs_root_test

  #!/usr/bin/env bash
  # For the CI/CD test run of this guide,
  # Enable verbose logging of bash shell and fail immediately when
  # a commmand fails.
  set -xe

.. In this documentation, there are three types of code markups:
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

Preparation
======================

#. Disable Secure Boot. ZFS modules can not be loaded if Secure Boot is enabled.
#. Download `NixOS Live Image
   <https://nixos.org/download.html#download-nixos>`__ and boot from it.
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

   If using virtio as disk bus, use ``/dev/disk/by-path/``.

   Declare disk array

   .. code-block:: sh

    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'

   For single disk installation, use

   .. code-block:: sh

    DISK='/dev/disk/by-id/disk1'

   .. ifconfig:: zfs_root_test

    # For the test run, two predefined disks are
    # specified in the qemu command
    DISK=$(find /dev/disk/by-id -type l | grep -v DVD-ROM | grep -v -- -part | xargs -I '{}' printf '{} ')

#. Set partition size:

   Set swap size, set to 1 if you don't want swap to
   take up too much space

   .. code-block:: sh

    INST_PARTSIZE_SWAP=4

   .. ifconfig:: zfs_root_test

    # For the test run, use !GB swap space to avoid hitting CI/CD
    # quota
    INST_PARTSIZE_SWAP=1

   Root pool size, use all remaining disk space if not set

   .. code-block:: sh

    INST_PARTSIZE_RPOOL=

#. Enable Nix Flakes functionality
   ::

      mkdir -p ~/.config/nix
      echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

#. Install programs needed for system installation
   ::

     nix-env -f '<nixpkgs>' -iA git jq parted gptfdisk

System Installation
======================

#. Partition the disks
   ::

     for i in ${DISK}; do

     # wipe flash-based storage device to improve
     # performance.
     # ALL DATA WILL BE LOST
     # blkdiscard -f $i

     sgdisk --zap-all $i

     sgdisk -n1:1M:+1G -t1:EF00 $i

     sgdisk -n2:0:+4G -t2:BE00 $i

     sgdisk -n4:0:+${INST_PARTSIZE_SWAP}G -t4:8200 $i

     if test -z $INST_PARTSIZE_RPOOL; then
         sgdisk -n3:0:0   -t3:BF00 $i
     else
         sgdisk -n3:0:+${INST_PARTSIZE_RPOOL}G -t3:BF00 $i
     fi

     sgdisk -a1 -n5:24K:+1000K -t5:EF02 $i

     sync && udevadm settle

     partprobe ${i}

     cryptsetup open --type plain --key-file /dev/random $i-part4 ${i##*/}-part4
     mkswap /dev/mapper/${i##*/}-part4
     swapon /dev/mapper/${i##*/}-part4
     done

#. Create boot pool
   ::

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
          bpool \
        mirror \
          $(for i in ${DISK}; do
             printf "$i-part2 ";
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
   ::

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
           rpool \
           mirror \
          $(for i in ${DISK}; do
             printf "$i-part3 ";
            done)

   If not using a multi-disk setup, remove ``mirror``.

#. Create root system container:

   - Unencrypted

     .. code-block:: sh

      zfs create \
       -o canmount=off \
       -o mountpoint=none \
      rpool/nixos

   - Encrypted:

     Pick a strong password. Once compromised, changing password will not keep your
     data safe. See ``zfs-change-key(8)`` for more info

     .. code-block:: sh

      zfs create \
        -o canmount=off \
	-o mountpoint=none \
	-o encryption=on \
	-o keylocation=prompt \
	-o keyformat=passphrase \
      rpool/nixos

     .. ifconfig:: zfs_root_test

      # Use encryption for the test run
      echo poolpass | zfs create \
      -o canmount=off \
      -o mountpoint=none \
      -o encryption=on \
      -o keylocation=prompt \
      -o keyformat=passphrase \
      rpool/nixos

   You can automate this step (insecure) with: ``echo POOLPASS | zfs create ...``.

   Create system datasets, let NixOS declaratively
   manage mountpoints with ``mountpoint=legacy``
   ::

      zfs create -o mountpoint=legacy     rpool/nixos/root
      mount -t zfs rpool/nixos/root /mnt/
      zfs create -o mountpoint=legacy rpool/nixos/home
      mkdir /mnt/home
      mount -t zfs rpool/nixos/home /mnt/home
      zfs create -o mountpoint=legacy  rpool/nixos/var
      zfs create -o mountpoint=legacy rpool/nixos/var/lib
      zfs create -o mountpoint=legacy rpool/nixos/var/log
      zfs create -o mountpoint=none bpool/nixos
      zfs create -o mountpoint=legacy bpool/nixos/root
      mkdir /mnt/boot
      mount -t zfs bpool/nixos/root /mnt/boot
      mkdir -p /mnt/var/log
      mkdir -p /mnt/var/lib
      mount -t zfs rpool/nixos/var/lib /mnt/var/lib
      mount -t zfs rpool/nixos/var/log /mnt/var/log
      zfs create -o mountpoint=legacy rpool/nixos/empty
      zfs snapshot rpool/nixos/empty@start

#. Format and mount ESP
   ::

     for i in ${DISK}; do
      mkfs.vfat -n EFI ${i}-part1
      mkdir -p /mnt/boot/efis/${i##*/}-part1
      mount -t vfat ${i}-part1 /mnt/boot/efis/${i##*/}-part1
     done


System Configuration
======================

#. Clone template flake configuration

   .. code-block:: sh

     mkdir -p /mnt/etc
     git clone --depth 1 --branch openzfs-guide \
       https://github.com/ne9z/dotfiles-flake.git /mnt/etc/nixos

   .. ifconfig:: zfs_root_test

     # Use vm branch of the template config for test run
     mkdir -p /mnt/etc
     git clone --depth 1 --branch openzfs-guide-testvm \
       https://github.com/ne9z/dotfiles-flake.git /mnt/etc/nixos

#. Customize configuration to your hardware

   ::

     for i in $DISK; do
       sed -i \
       "s|/dev/disk/by-id/|${i%/*}/|" \
       /mnt/etc/nixos/hosts/exampleHost/default.nix
       break
     done

     diskNames=""
     for i in $DISK; do
       diskNames="$diskNames \"${i##*/}\""
     done

     sed -i "s|\"bootDevices_placeholder\"|$diskNames|g" \
       /mnt/etc/nixos/hosts/exampleHost/default.nix

     sed -i "s|\"abcd1234\"|\"$(head -c4 /dev/urandom | od -A none -t x4| sed 's| ||g')\"|g" \
       /mnt/etc/nixos/hosts/exampleHost/default.nix

     sed -i "s|\"x86_64-linux\"|\"$(uname -m)-linux\"|g" \
       /mnt/etc/nixos/flake.nix

#. Set root password

   .. code-block:: sh

     rootPwd=$(mkpasswd -m SHA-512 -s)

   .. ifconfig:: zfs_root_test

     # Use "test" for root password in test run
     rootPwd=$(echo test | mkpasswd -m SHA-512 -s)

   Declare password in configuration
   ::

     sed -i \
     "s|rootHash_placeholder|${rootPwd}|" \
     /mnt/etc/nixos/configuration.nix

#. You can enable NetworkManager for wireless networks and GNOME
   desktop environment in ``configuration.nix``.

#. From now on, the complete configuration of the system will be
   tracked by git, set a user name and email address to continue
   ::

     git -C /mnt/etc/nixos config user.email "you@example.com"
     git -C /mnt/etc/nixos config user.name "Alice Q. Nixer"

#. Commit changes to local repo
   ::

     git -C /mnt/etc/nixos commit -asm 'initial installation'

#. Reuse nixpkgs repo on the live media
   ::

     LIVE_ISO_NIXPKGS_REVISION=$(nixos-version --json | jq -r ."nixpkgsRevision")
     sed -i "s|github:nixos/nixpkgs/nixos-.*\"|github:NixOS/nixpkgs/$LIVE_ISO_NIXPKGS_REVISION\"|" \
      /mnt/etc/nixos/flake.nix
     git -C /mnt/etc/nixos commit -asm 'use the same nixpkgs repo as live iso'

#. Update flake lock file to track latest system version
   ::

     nix flake update --commit-lock-file \
       "git+file:///mnt/etc/nixos"

#. Install system and apply configuration
   ::

     nixos-install --no-root-passwd --flake "git+file:///mnt/etc/nixos#exampleHost"

#. Track latest stable nixpkgs
   ::

      git -C /mnt/etc/nixos reset --hard HEAD~1

#. Unmount filesystems
   ::

    umount -Rl /mnt
    zpool export -a

#. Reboot

   .. code-block:: sh

     reboot

   .. ifconfig:: zfs_root_test

     # For test run, power off instead.
     # Test run is successful if the vm powers off
     poweroff
