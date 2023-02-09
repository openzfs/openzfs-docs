.. highlight:: sh

System Configuration
======================

.. contents:: Table of Contents
   :local:

#. Generate initial system configuration::

    nixos-generate-config --root /mnt

#. Import ZFS-specific configuration::

     sed -i "s|./hardware-configuration.nix|./hardware-configuration.nix ./zfs.nix|g" /mnt/etc/nixos/configuration.nix

#. Configure hostid::

     tee -a /mnt/etc/nixos/zfs.nix <<EOF
     { config, pkgs, ... }:

     { boot.supportedFilesystems = [ "zfs" ];
       networking.hostId = "$(head -c 8 /etc/machine-id)";
       boot.kernelPackages = config.boot.zfs.package.latestCompatibleLinuxPackages;
     EOF

#. Configure bootloader for both legacy boot and UEFI boot and mirror bootloader::

    sed -i '/boot.loader/d' /mnt/etc/nixos/configuration.nix
    sed -i '/services.xserver/d' /mnt/etc/nixos/configuration.nix
    tee -a /mnt/etc/nixos/zfs.nix <<EOF
    boot.loader.efi.efiSysMountPoint = "/boot/efis/$(echo $DISK | cut -f1 -d\ | sed 's|/dev/disk/by-id/||')-part1";
    EOF
    tee -a /mnt/etc/nixos/zfs.nix <<-'EOF'
    boot.loader.efi.canTouchEfiVariables = false;
    boot.loader.generationsDir.copyKernels = true;
    boot.loader.grub.efiInstallAsRemovable = true;
    boot.loader.grub.enable = true;
    boot.loader.grub.version = 2;
    boot.loader.grub.copyKernels = true;
    boot.loader.grub.efiSupport = true;
    boot.loader.grub.zfsSupport = true;
    boot.loader.grub.extraInstallCommands = ''
    ESP_MIRROR=$(mktemp -d)
    cp -r ${config.boot.loader.efi.efiSysMountPoint}/EFI $ESP_MIRROR
    for i in /boot/efis/*; do
     cp -r $ESP_MIRROR/EFI $i
    done
    rm -rf $ESP_MIRROR
    '';
    boot.loader.grub.devices = [
    EOF

    for i in $DISK; do
      printf "      \"$i\"\n" >>/mnt/etc/nixos/zfs.nix
    done

    tee -a /mnt/etc/nixos/zfs.nix <<EOF
        ];
    EOF

#. Mount datasets with zfsutil option::

     sed -i 's|fsType = "zfs";|fsType = "zfs"; options = [ "zfsutil" "X-mount.mkdir" ];|g' \
     /mnt/etc/nixos/hardware-configuration.nix

#. Mount EFI partitions on demand::

     sed -i 's|fsType = "vfat";|fsType = "vfat"; options = [ "x-systemd.idle-timeout=1min" "x-systemd.automount" "noauto" "nofail" ];|g' \
     /mnt/etc/nixos/hardware-configuration.nix

#. Set root password::

     rootPwd=$(mkpasswd -m SHA-512 -s)

   Declare password in configuration::

     tee -a /mnt/etc/nixos/zfs.nix <<EOF
     users.users.root.initialHashedPassword = "${rootPwd}";
     }
     EOF

#. Install system and apply configuration::

     nixos-install -v --show-trace --no-root-passwd --root /mnt

#. Unmount filesystems::

    umount -Rl /mnt
    zpool export -a

#. Reboot::

     reboot
