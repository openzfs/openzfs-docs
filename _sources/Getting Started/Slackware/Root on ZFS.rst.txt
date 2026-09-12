Slackware Root on ZFS
=====================

This page shows some possible ways to configure Slackware to use zfs for the root filesystem.

There are countless different ways to achieve such setup, particularly with the flexibility that zfs allows. We'll show only a simple recipe and give pointers for further customization.

Kernel considerations
---------------------

For this mini-HOWTO we'll be using the generic kernel and customize the stock initrd.

If you use the huge kernel, you may want to switch to the generic kernel first, and install both the kernel-generic and mkinitrd packages. This makes things easier since we'll need an initrd.

If you absolutely do not want to use an initrd, see "Other options" further down.


The problem space
-----------------

In order to have the root filesystem on zfs, two problems need to be addressed:

#. The boot loader needs to be able to load the kernel and its initrd.

#. The kernel (or, rather, the initrd) needs to be able to mount the zfs root filesystem and run /sbin/init.

The second problem is relatively easy to deal with, and only requires slight modifications to the default Slackware initrd scripts.

For the first problem, however, a variety of scenarios are possible; on a PC, for example, you might be booting:

#. In UEFI mode, via an additional bootloader like elilo: here, the kernel and its initrd are on (read: have been copied to) the ESP, and the additional bootloader doesn't need to understand zfs.

#. In UEFI mode, by booting the kernel straight from the firmware. All Slackware kernels are built with EFI_STUB=Y, so if you copy your kernel and initrd to the ESP and configure a boot entry with efibootmgr, you are all set (note that the kernel image must have a .efi extension).

#. In legacy BIOS mode, using lilo or grub or similar: lilo doesn't understand zfs and even the latest grub understands it with some limitations (for example, no zstd compression). If you're stuck with legacy BIOS mode, the best option is to put /boot on a separate partition that your loader understands (for example, ext4).

If you are not using a PC, things will likely be quite different, so refer to relevant hardware documentation for your platform; on a Raspberry PI, for example, the firmware loads kernel and initrd from a FAT32 partition, so the situation is similar to a PC booting in UEFI mode.

The simplest setup, discussed in this recipe, is the one using UEFI. As said above, if you boot in legacy BIOS mode, you will have to ensure that the boot loader of your choice can load the kernel image.


Partition layout
----------------

Repartitioning an existing system disk in order to make room for a zfs root partition is left as an exercise to the reader (there's nothing specific to zfs).

As a pointer: if you're starting from a whole-disk ext4 filesystem, you could use resize2fs to shrink it to half of disk size and then relocate it to the second half of the disk with sfdisk. After that, you could create a ZFS partition before it, and copy stuff across using cp or rsync. This approach has the benefit of providing some kind of recovery mechanism in case stuff goes wrong. When you are happy about the final setup, you can then delete the ext4 partition and enlarge the ZFS one.

In any case you will want to have a rescue cdrom at hand, and one that supports zfs out of the box. A Ubuntu live CD will do.

For this recipe, we'll be assuming that we're booting in UEFI mode and there's a single disk configured like this:

.. code-block:: sh

  /dev/sda1 # EFI system partition
  /dev/sda2 # zfs pool (contains the "root" filesystem)

..

Since we are creating a zpool inside a disk partition (as opposed to using up a whole disk), make sure that the partition type is set correctly (for GPT, 54 or 67 are good choices).

When creating the zfs filesystem, you will want to set "mountpoint=legacy" so that the filesystem can be mounted with "mount" in a traditional way; Slackware startup and shutdown scripts expect that.

Back to our recipe, this is a working example:

.. code-block:: sh

  zpool create -o ashift=12 -O mountpoint=none tank /dev/sda2
  zfs create -o mountpoint=legacy -o compression=zstd tank/root
  # add more as needed:
  # zfs create -o mountpoint=legacy [..] tank/home
  # zfs create -o mountpoint=legacy [..] tank/usr
  # zfs create -o mountpoint=legacy [..] tank/opt

..

Tweak options to taste; while "mountpoint=legacy" is required for the root filesystem, it is not required for any additional filesystems. In the example above we applied it to all of them, but that's a matter of personal preference, as is setting "mountpoint=none" on the pool itself so it's not mounted anywhere by default (do note that zpool's "mountpoint=none" wants an uppercase "-O").

You can check your setup with:

.. code-block:: sh

  zpool list
  zfs list

..

Then, adjust /etc/fstab to something like this:

.. code-block:: sh

  tank/root    /       zfs   defaults   0   0
  # add more as needed:
  # tank/home    /home   zfs   defaults   0   0
  # tank/usr     /usr    zfs   defaults   0   0
  # tank/opt     /opt    zfs   defaults   0   0

..

This allow us to mount and umount them as usual, once we have imported the pool with "zpool import tank". Which leads us to...


Patch and rebuild the initrd
----------------------------

Since we're using the generic kernel, we already have a usable /boot/initrd-tree/ (if you don't, prepare one by running mkinitrd once).

Copy the zfs userspace tools to it (/sbin/zfs isn't strictly necessary, but may be handy for rescuing a system that refuses to boot):

.. code-block:: sh

  install -m755 /sbin/zpool /sbin/zfs /boot/initrd-tree/sbin/

..

Modify /boot/initrd-tree/init; locate the first "case" statement that sets ROOTDEV; it reads:

.. code-block:: sh

    root=/dev/*)
      ROOTDEV=$(echo $ARG | cut -f2 -d=)
    ;;
    root=LABEL=*)
      ROOTDEV=$(echo $ARG | cut -f2- -d=)
    ;;
    root=UUID=*)
      ROOTDEV=$(echo $ARG | cut -f2- -d=)
    ;;
..

Replace the three cases with:

.. code-block:: sh

    root=*)
      ROOTDEV=$(echo $ARG | cut -f2 -d=)
    ;;

..

This allows us to specify something like "root=tank/root" (if you look carefully at the script, you will notice that you can collapse the /dev/*, LABEL=*, UUID=* and the newly-added case into a single one).

Further down in the script, locate the section that handles RESUMEDEV ("# Resume state from swap"), and insert the following just before it:

.. code-block:: sh

  # Support for zfs root filesystem:
  if [ x"$ROOTFS" = xzfs ]; then
    POOL=${ROOTDEV%%/*}
    echo "Importing zfs pool: $POOL"
    zpool import -o cachefile=none -N $POOL
  fi

..
    
Finally, rebuild the initrd with something like:

.. code-block:: sh

  mkinitrd -m zfs

..

It may make sense to use the "-o" option and create an initrd.gz in a different file, just in case. Look at /boot/README.initrd for more details.

Rebuilding the initrd should also copy in the necessary libraries (libzfs.so, etc.) under /lib/; verify it by running:

.. code-block:: sh

  chroot /boot/initrd-tree /sbin/zpool --help

..

When you're happy, remember to copy the new initrd.gz to the ESP partition.

There are other ways to ensure that the zfs binaries and filesystem module are always built into the initrd - see man initrd.


Configure the boot loader
-------------------------

Any of these three options will do:

#. Append "rootfstype=zfs root=tank/root" to the boot loader configuration (e.g. elilo.conf or equivalent).
#. Modify /boot/initrd-tree/rootdev and /boot/initrd-tree/rootfs in the previous step, then rebuild the initrd.
#. When rebuilding the initrd, add "-f zfs -r tank/root".

If you're using elilo, it should look something like this:

.. code-block:: sh

  image=vmlinuz
    label=linux
    initrd=initrd.gz
    append="root=tank/root rootfstype=zfs"

..

Should go without saying, but doublecheck that the file referenced by initrd is the one you just generated (e.g. if you're using the ESP, make sure you copy the newly-built initrd to it).


Before rebooting
----------------

Make sure you have an emergency kernel around in case something goes wrong.
If you upgrade kernel or packages, make use of snapshosts.


Other options
-------------

You can build zfs support right into the kernel. If you do so and do not want to use an initrd, you can embed a small initramfs in the kernel image that performs the "zpool import" step).


Snapshots and boot environments
-------------------------------

The modifications above also allow you to create a clone of the root filesystem and boot into it; something like this should work:

.. code-block:: sh

  zfs snapshot tank/root@mysnapshot
  zfs clone tank/root@mysnapshot tank/root-clone
  zfs set mountpoint=legacy tank/root-clone
  zfs promote tank/root-clone

..

Adjust boot parameters to mount "tank/root-clone" instead of "tank/root" (making a copy of the known-good kernel and initrd on the ESP is not a bad idea).


Support
-------

If you need help, reach out to the community using the :ref:`mailing_lists` or IRC at `#zfsonlinux <ircs://irc.libera.chat/#zfsonlinux>`__ on `Libera Chat <https://libera.chat/>`__. If you have a bug report or feature request related to this HOWTO, please `file a new issue and mention @a-biardi <https://github.com/openzfs/openzfs-docs/issues/new?body=@a-biardi,%20re.%20Slackware%20Root%20on%20ZFS%20HOWTO>`__.
