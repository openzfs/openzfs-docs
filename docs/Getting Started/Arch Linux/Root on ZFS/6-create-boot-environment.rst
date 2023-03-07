.. highlight:: sh

Create a Boot Environment
==========================

This page is tested for Alpine, Arch Linux, Fedora and
RHEL guides.  Not useful for NixOS since system rollback
is already managed by Nix.

With Root on ZFS, it is possible to take snapshots of
existing root file systems, which is a read-only copy of
that file system.  A new, full-fledged file system --
clones -- can be then created from this snapshot.  This
bootable clone of the current system is then called a
"Boot Environment".

This could be useful if you are performing a major
system upgrade and wish to have the option to go back to
a previous state if the upgrade fails.

#. Identify which dataset is currently mounted as root
   ``/`` and boot ``/boot``::

     findmnt /
     # output
     TARGET SOURCE               FSTYPE OPTIONS
     /      rpool/archlinux/root zfs    rw,relatime,xattr,posixacl

     findmnt /boot
     # output
     TARGET SOURCE               FSTYPE OPTIONS
     /boot  bpool/archlinux/root zfs    rw,relatime,xattr,posixacl

#. Identify your distribution in the dataset (file system) path::

     DISTRO=archlinux # or `fedora', `alma', `alpinelinux'

#. Choose a name for the new boot environment::

     BE_NAME=backup

#. Take snapshots of the ``/`` and ``/boot`` datasets::

     zfs snapshot rpool/$DISTRO/root@$BE_NAME
     zfs snapshot bpool/$DISTRO/root@$BE_NAME

#. Create clones from read-only snapshots::

     zfs clone -o canmount=noauto \
       -o mountpoint=/ \
       rpool/$DISTRO/root@$BE_NAME \
       rpool/$DISTRO/$BE_NAME

     zfs clone -o canmount=noauto \
       -o mountpoint=legacy \
       bpool/$DISTRO/root@$BE_NAME \
       bpool/$DISTRO/$BE_NAME

#. Mount clone and update file system table (fstab) ::

     mount -t zfs -o zfsutil rpool/$DISTRO/$BE_NAME /mnt
     mount -t zfs  bpool/$DISTRO/$BE_NAME /mnt/boot

     sed -i "s|rpool/$DISTRO/root|rpool/$DISTRO/$BE_NAME|g" /mnt/etc/fstab
     sed -i "s|bpool/$DISTRO/root|bpool/$DISTRO/$BE_NAME|g" /mnt/etc/fstab

   If legacy mountpoint is used, omit ``-o zfsutil``
   from mount command.

#. Create GRUB menu for new clone::

     m='/dev /proc /sys'
     for i in $m; do mount --rbind $i /mnt/$i; done
     chroot /mnt /usr/bin/env sh <<EOF
       if which grub-mkconfig; then
         grub-mkconfig -o /boot/grub.cfg
       else
         grub2-mkconfig -o /boot/grub.cfg
       fi
     EOF

   GRUB menu contains information on kernel version and initramfs.

#. Unmount clone::

     umount -Rl /mnt

#. Add new boot environment as GRUB menu entry::

     tee -a new_entry <<EOF
     menuentry 'ZFS Clone of ${DISTRO}: ${BE_NAME}' { configfile (hd0,gpt2)/${DISTRO}/${BE_NAME}@/grub.cfg }
     EOF

     find /boot/efis/ -name "grub.cfg" \
     | while read i; do
         if grep -q "${DISTRO}" $i; then
           cat $i new_entry > grub.cfg
	   cp grub.cfg $i
	 fi
       done

     rm new_entry

#. After reboot, select boot environment entry from GRUB
   menu to boot from the clone.  Press ESC inside
   submenu to return to the previous menu.

#. Steps above can also be used to create a new clone
   from an existing snapshot.

#. To set a boot environment as default, replace
   existing ``grub.cfg`` inside EFI system partition
   with the one from the boot environment::

     mount -t zfs  bpool/$DISTRO/$BE_NAME /mnt

     # backup existing grub.cfg inside EFI
     # then replace it with menu from clone

     mkdir -p /mnt/grub_menu_backup
     menu_counter=1
     find /boot/efis/ -name "grub.cfg" \
     | while read i; do
         if grep -q "${DISTRO}" $i; then
	   cp $i /mnt/grub_menu_backup/grub_${menu_counter}.cfg
           echo $i > /mnt/grub_menu_backup/grub_${menu_counter}_path.txt
	   cp /mnt/grub.cfg $i
	   menu_counter=$(($menu_counter + 1))
	 fi
       done

     umount -Rl /mnt

#. To delete the boot environment, check with
   ``findmnt`` that the boot environment is not
   currently used::

     findmnt /
     findmnt /boot

   Set variables::

     DISTRO=archlinux

   Then check the origin snapshot::

     zfs get origin rpool/archlinux/backup
     # rpool/archlinux/root@backup
     zfs get origin bpool/archlinux/backup
     # bpool/archlinux/root@backup

     RM_BE=backup
     RM_SNAPSHOT=root@backup

   Finally, destroy clone (boot environment) and its
   origin snapshot::

     zfs destroy rpool/${DISTRO}/${RM_BE}
     zfs destroy rpool/${DISTRO}/${RM_SNAPSHOT}

     zfs destroy bpool/${DISTRO}/${RM_BE}
     zfs destroy bpool/${DISTRO}/${RM_SNAPSHOT}

   Remove GRUB entry::

     find /boot/efis/ -name "grub.cfg" \
     | while read i; do
         if grep -q "${DISTRO}/${RM_BE}@/grub.cfg" $i; then
             head -n -1 $i > grub.cfg
	     cp grub.cfg $i
	 fi
       done
