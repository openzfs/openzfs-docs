.. highlight:: sh

Root on ZFS maintenance
========================

Boot Environment
----------------

This section is compatible with Alpine, Arch, Fedora and RHEL guides.
Not necessary for NixOS.  Incompatible with Ubuntu and Debian guides.

Note: boot environments as described below are intended only for
system recovery purposes, that is, you boot into the alternate boot
environment once to perform system recovery on the default datasets:

.. code-block:: sh

  rpool/distro/root
  bpool/distro/root

then reboot to those datasets once you have successfully recovered the
system.

Switching the default boot environment complicates bootloader recovery
and other maintenance operations and is thus currently not supported.

#. If you want to use the ``@initial-installation`` snapshot created
   during installation, set ``my_boot_env=initial-installation`` and
   skip Step 3 and 4.

#. Identify which dataset is currently mounted as root
   ``/`` and boot ``/boot``
   ::

      set -x
      boot_dataset=$(df -P /boot | tail -n1 | cut -f1 -d' ' || true )
      root_dataset=$(df -P / | tail -n1 | cut -f1 -d' ' || true )

#. Choose a name for the new boot environment
   ::

      my_boot_env=backup

#. Take snapshots of the ``/`` and ``/boot`` datasets

   ::

      zfs snapshot "${boot_dataset}"@"${my_boot_env}"
      zfs snapshot "${root_dataset}"@"${my_boot_env}"

#. Create clones from read-only snapshots

   ::

      new_root_dataset="${root_dataset%/*}"/"${my_boot_env}"
      new_boot_dataset="${boot_dataset%/*}"/"${my_boot_env}"

      zfs clone -o canmount=noauto \
        -o mountpoint=/ \
        "${root_dataset}"@"${my_boot_env}" \
        "${new_root_dataset}"

      zfs clone -o canmount=noauto \
        -o mountpoint=legacy \
        "${boot_dataset}"@"${my_boot_env}" \
        "${new_boot_dataset}"

#. Mount clone and update file system table (fstab)
   ::

        MNT=$(mktemp -d)
        mount -t zfs -o zfsutil "${new_root_dataset}" "${MNT}"
        mount -t zfs  "${new_boot_dataset}" "${MNT}"/boot

        sed -i s,"${root_dataset}","${new_root_dataset}",g "${MNT}"/etc/fstab
        sed -i s,"${boot_dataset}","${new_boot_dataset}",g "${MNT}"/etc/fstab

        if test -f "${MNT}"/boot/grub/grub.cfg; then
          is_grub2=n
          sed -i s,"${boot_dataset#bpool/}","${new_boot_dataset#bpool/}",g "${MNT}"/boot/grub/grub.cfg
        elif test -f "${MNT}"/boot/grub2/grub.cfg; then
          is_grub2=y
          sed -i s,"${boot_dataset#bpool/}","${new_boot_dataset#bpool/}",g "${MNT}"/boot/grub2/grub.cfg
        else
          echo "ERROR: no grub menu found!"
          exit 1
        fi

   Do not proceed if no grub menu was found!

#. Unmount clone
   ::

        umount -Rl "${MNT}"

#. Add new boot environment as GRUB menu entry
   ::

        echo "# ${new_boot_dataset}" > new_boot_env_entry_"${new_boot_dataset##*/}"
        printf '\n%s' "menuentry 'Boot environment ${new_boot_dataset#bpool/} from ${boot_dataset#bpool/}' "  \
          >> new_boot_env_entry_"${new_boot_dataset##*/}"
        if [ "${is_grub2}" = y ]; then
           # shellcheck disable=SC2016
           printf '{ search --set=drive1 --label bpool; configfile ($drive1)/%s@/grub2/grub.cfg; }' \
           "${new_boot_dataset#bpool/}" >> new_boot_env_entry_"${new_boot_dataset##*/}"
        else
           # shellcheck disable=SC2016
           printf '{ search --set=drive1 --label bpool; configfile ($drive1)/%s@/grub/grub.cfg; }' \
           "${new_boot_dataset#bpool/}" >> new_boot_env_entry_"${new_boot_dataset##*/}"
        fi

        find /boot/efis/ -name "grub.cfg" -print0 \
        | xargs -t -0I '{}' sh -vxc "tail -n1 new_boot_env_entry_${new_boot_dataset##*/}  >> '{}'"

   .. ifconfig:: zfs_root_test

      ::

         find /boot/efis/ -name "grub.cfg" -print0 \
         | xargs -t -0I '{}' grub-script-check -v '{}'

#. Do not delete ``new_boot_env_entry_"${new_boot_dataset##*/}"`` file.  It
   is needed when you want to remove the new boot environment from
   GRUB menu later.

#. After reboot, select boot environment entry from GRUB
   menu to boot from the clone.  Press ESC inside
   submenu to return to the previous menu.

#. Steps above can also be used to create a new clone
   from an existing snapshot.

#. To delete the boot environment, first store its name in a
   variable::

      my_boot_env=backup

#. Ensure that the boot environment is not
   currently used
   ::

      set -x
      boot_dataset=$(df -P /boot | tail -n1 | cut -f1 -d' ' || true )
      root_dataset=$(df -P / | tail -n1 | cut -f1 -d' ' || true )
      new_boot_dataset="${boot_dataset%/*}"/"${my_boot_env}"
      rm_boot_dataset=$(head -n1 new_boot_env_entry_"${new_boot_dataset##*/}" | sed 's|^# *||' || true )

      if [ "${boot_dataset}" = "${rm_boot_dataset}" ]; then
        echo "ERROR: the dataset you want to delete is the current root! abort!"
        exit 1
      fi

#. Then check the origin snapshot
   ::

        rm_root_dataset=rpool/"${rm_boot_dataset#bpool/}"

        rm_boot_dataset_origin=$(zfs get -H origin "${rm_boot_dataset}"|cut -f3 || true )
        rm_root_dataset_origin=$(zfs get -H origin "${rm_root_dataset}"|cut -f3 || true )

#. Finally, destroy clone (boot environment) and its
   origin snapshot
   ::

        zfs destroy "${rm_root_dataset}"
        zfs destroy "${rm_root_dataset_origin}"
        zfs destroy "${rm_boot_dataset}"
        zfs destroy "${rm_boot_dataset_origin}"

#. Remove GRUB entry
   ::

        new_entry_escaped=$(tail -n1 new_boot_env_entry_"${new_boot_dataset##*/}" | sed -e 's/[\/&]/\\&/g' || true )
        find /boot/efis/ -name "grub.cfg" -print0 | xargs -t -0I '{}' sed -i "/${new_entry_escaped}/d" '{}'

   .. ifconfig:: zfs_root_test

      ::

         find /boot/efis/ -name "grub.cfg" -print0 \
         | xargs -t -0I '{}' grub-script-check -v '{}'

Disk replacement
----------------

When a disk fails in a mirrored setup, the disk can be replaced with
the following procedure.

#. Shutdown the computer.

#. Replace the failed disk with another disk.  The replacement should
   be at least the same size or larger than the failed disk.

#. Boot the computer.

   When a disk fails, the system will boot, albeit several minutes
   slower than normal.

   For NixOS, this is due to the initrd and systemd designed to only
   import a pool in degraded state after a 90s timeout.

   Swap partition on that disk will also fail.

#. Install GNU ``parted`` with your distribution package manager.

#. Identify the bad disk and a working old disk

   .. code-block:: sh

     ZPOOL_VDEV_NAME_PATH=1 zpool status

     pool:   bpool
     status: DEGRADED
     action: Replace the device using 'zpool replace'.
     ...
     config: bpool
         mirror-0
         2387489723748                    UNAVAIL    0  0  0   was /dev/disk/by-id/ata-BAD-part2
         /dev/disk/by-id/ata-disk_known_good-part2    ONLINE     0  0  0

#. Store the bad disk and a working old disk in a variable, omit the partition number ``-partN``

   .. code-block:: sh

     disk_to_replace=/dev/disk/by-id/ata-disk_to_replace
     disk_known_good=/dev/disk/by-id/ata-disk_known_good

#. Identify the new disk

   .. code-block:: sh

     find /dev/disk/by-id/

     /dev/disk/by-id/ata-disk_known_good-part1
     /dev/disk/by-id/ata-disk_known_good-part2
     ...
     /dev/disk/by-id/ata-disk_known_good-part5
     /dev/disk/by-id/ata-disk_new       <-- new disk w/o partition table

#. Store the new disk in a variable

   .. code-block:: sh

     disk_new=/dev/disk/by-id/ata-disk_new

#. Create partition table on ``"${disk_new}"``, refer to respective
   installation pages for details.

#. Format and mount EFI system partition, refer to respective
   installation pages for details.

#. Replace failed disk in ZFS pool

   .. code-block:: sh

     zpool offline bpool "${disk_to_replace}"-part2
     zpool offline rpool "${disk_to_replace}"-part3
     zpool replace bpool "${disk_to_replace}"-part2 "${disk_new}"-part2
     zpool replace rpool "${disk_to_replace}"-part3 "${disk_new}"-part3
     zpool online  bpool "${disk_new}"-part2
     zpool online  rpool "${disk_new}"-part3

   Let the new disk resilver.  Check status with ``zpool status``.

#. Reinstall and mirror bootloader, refer to respective installation
   pages for details.

   If you are using NixOS, see below.

#. For NixOS, replace bad disk with new disk inside per-host
   configuration file.

   .. code-block:: sh

     sed -i "s|"${disk_to_replace##*/}"|"${disk_new##*/}"|" /etc/nixos/hosts/exampleHost/default.nix

#. Commit and apply the changed configuration, reinstall bootloader, then reboot

   .. code-block:: sh

     git -C /etc/nixos commit -asm "replace "${disk_to_replace##*/}" with "${disk_new##*/}"."

     nixos-rebuild boot --install-bootloader

     reboot

Bootloader Recovery
-------------------

This section is compatible with Alpine, Arch, Fedora, RHEL and NixOS
root on ZFS guides.

Sometimes the GRUB bootloader might be accidentally overwritten,
rendering the system inaccessible.  However, as long as the disk
partitions where boot pool and root pool resides remain untouched, the
system can still be booted easily.

#. Download GRUB rescue image from `this repo
   <https://github.com/ne9z/grub-rescue-flake/releases>`__.

   You can also build the image yourself if you are familiar with Nix
   package manager.

#. Extract either x86_64-efi or i386-pc image from the archive.

#. Write the image to a disk.

#. Boot the computer from the GRUB rescue disk.  Select your distro in
   GRUB menu.

#. Reinstall bootloader.  See respective installation pages for details.
