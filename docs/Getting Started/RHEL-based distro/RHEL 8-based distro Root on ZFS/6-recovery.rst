.. highlight:: sh

Recovery
======================

.. contents:: Table of Contents
   :local:

GRUB Tips
-------------

Boot from GRUB rescue
~~~~~~~~~~~~~~~~~~~~~~~

If bootloader file is damaged, it's still possible
to boot computer with GRUB rescue image.

This section is also applicable if you are in
``grub rescue>``.

#. On another computer, generate rescue image with::

     pacman -S --needed mtools libisoburn grub
     grub-mkrescue -o grub-rescue.img
     dd if=grub-rescue.img of=/dev/your-usb-stick

   Boot computer from the rescue media.
   Both legacy and EFI mode are supported.

   Skip this step if you are in GRUB rescue.

#. List available disks with ``ls`` command::

    grub> ls (hd # press tab
    Possible devices are:

     hd0 hd1 hd2 hd3

   If you are dropped to GRUB rescue instead of
   booting from GRUB rescue image, boot disk can be found
   out with::

    echo $root
    # cryto0
    # hd0,gpt2

   GRUB configuration is loaded from::

    echo $prefix
    # (crypto0)/sys/BOOT/default@/grub
    # (hd0,gpt2)/sys/BOOT/default@/grub

#. List partitions by pressing tab key:

   .. code-block:: text

     grub> ls (hd0 # press tab
     Possible partitions are:

     Device hd0: No known filesystem detected - Sector size 512B - Total size  20971520KiB
     Partition hd0,gpt1: Filesystem type fat - Label `EFI', UUID 0DF5-3A76 - Partition start at 1024KiB - Total size 1048576KiB
     Partition hd0,gpt2: No known filesystem detected - Partition start at 1049600KiB - Total size 4194304KiB

   - If boot pool is encrypted:

     Unlock it with ``cryptomount``::

         grub> insmod luks
         grub> cryptomount hd0,gpt2
         Attempting to decrypt master key...
         Enter passphrase for hd0,gpt2 (af5a240e13e24483acf02600d61e0f36):
         Slot 1 opened

     Unlocked LUKS container is ``(crypto0)``:

     .. code-block:: text

         grub> ls (crypto0)
         Device crypto0: Filesystem type zfs - Label `bpool_ip3tdb' - Last modification
         time 2021-05-03 12:14:08 Monday, UUID f14d7bdf89fe21fb - Sector size 512B -
         Total size 4192256KiB

   - If boot pool is not encrypted:

     .. code-block:: text

       grub> ls (hd0,gpt2)
       Device hd0,gpt2: Filesystem type zfs - Label `bpool_ip3tdb' - Last modification
       time 2021-05-03 12:14:08 Monday, UUID f14d7bdf89fe21fb - Sector size 512B -
       Total size 4192256KiB

#. List boot environments nested inside ``bpool/$INST_ID/BOOT``::

     grub> ls (crypto0)/sys/BOOT
     @/ default/ be0/

#. Instruct GRUB to load configuration from ``be0`` boot environment
   then enter normal mode::

     grub> prefix=(crypto0)/sys/BOOT/be0/@/grub
     grub> insmod normal
     grub> normal

#. GRUB menu should now appear.

#. After entering system, `reinstall GRUB <#grub-installation>`__.

Switch GRUB prefix when disk fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using LUKS encrypted boot pool with multiple disks,
the primary disk failed, GRUB will fail to load configuration.

If there's still enough redundancy for the boot pool, try fix
GRUB with the following method:

#. Ensure ``Slot 1 opened`` message
   is shown

   .. code-block:: text

      Welcome to GRUB!

      error: no such cryptodisk found.
      Attempting to decrypt master key...
      Enter passphrase for hd0,gpt2 (c0987ea1a51049e9b3056622804de62a):
      Slot 1 opened
      error: disk `cryptouuid/47ed1b7eb0014bc9a70aede3d8714faf' not found.
      Entering rescue mode...
      grub rescue>

   If ``error: access denied.`` is shown,
   try re-enter password with::

     grub rescue> cryptomount hd0,gpt2

#. Check prefix::

      grub rescue > set
      # prefix=(cryptouuid/47ed1b7eb0014bc9a70aede3d8714faf)/sys/BOOT/be0@/grub
      # root=cryptouuid/47ed1b7eb0014bc9a70aede3d8714faf

#. Set correct ``prefix`` and ``root`` by replacing
   ``cryptouuid/UUID`` with ``crypto0``::

      grub rescue> prefix=(crypto0)/sys/BOOT/default@/grub
      grub rescue> root=crypto0

#. Boot GRUB::

      grub rescue> insmod normal
      grub rescue> normal

   GRUB should then boot normally.

#. After entering system, edit ``/etc/fstab`` to promote
   one backup to ``/boot/efi``.

#. Make the change to ``prefix`` and ``root``
   permanent by `reinstalling GRUB <#grub-installation>`__.

Access system in chroot
-----------------------

#. Go through `preparation <1-preparation.html>`__.

#. Import and unlock root and boot pool::

     zpool import -NR /mnt rpool_$INST_UUID
     zpool import -NR /mnt bpool_$INST_UUID

   If using password::

     zfs load-key rpool_$INST_UUID/$INST_ID

   If using keyfile::

     zfs load-key -L file:///path/to/keyfile rpool_$INST_UUID/$INST_ID

#. Find the current boot environment::

     zfs list
     BE=default

#. Mount root filesystem::

     zfs mount rpool_$INST_UUID/$INST_ID/ROOT/$BE

#. chroot into the system::

     rhel-chroot /mnt /bin/bash --login
     zfs mount -a
     mount -a

#. Finish rescue. See `finish installation <#finish-installation>`__.

Backup and migrate existing installation
----------------------------------------
With the help of `zfs send
<https://openzfs.github.io/openzfs-docs/man/8/zfs-send.8.html>`__
it is relatively easy to perform a system backup and migration.

#. Create a snapshot of root file system::

    zfs snapshot -r rpool/rhel@backup
    zfs snapshot -r bpool/rhel@backup

#. Save snapshot to a file or pipe to SSH::

    zfs send --options rpool/rhel@backup > /backup/rhel-rpool
    zfs send --options bpool/rhel@backup > /backup/rhel-bpool

#. Re-create partitions and root/boot
   pool on target system.

#. Restore backup::

    zfs recv rpool_new/rhel < /backup/rhel-rpool
    zfs recv bpool_new/rhel < /backup/rhel-bpool

#. Chroot and reinstall bootloader.

#. Update pool name in ``/etc/fstab``, ``/boot/grub/grub.cfg``
   and ``/etc/zfs/zfs-list.cache/*``.

#. Update device name, etc, in ``/etc/fstab`` and ``/etc/crypttab``.
