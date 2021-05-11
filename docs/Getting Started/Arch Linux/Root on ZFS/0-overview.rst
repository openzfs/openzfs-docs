.. highlight:: sh

Overview
======================
Before following this guide, you might want to read `index page <../index.html>`__.

This document describes how to install Arch Linux with ZFS as root
file system.

Caution
~~~~~~~

- This guide wipes entire physical disks. Back up existing data.
- `GRUB does not and
  will not work on 4Kn drive with legacy (BIOS) booting.
  <http://savannah.gnu.org/bugs/?46700>`__

Partition layout
~~~~~~~~~~~~~~~~

GUID partition table (GPT) is used.
EFI system partition will be referred to as **ESP** in this document.

+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+
| Name                 | legacy boot          | ESP                   | Boot pool            | swap                | root pool             | remaining space |
+======================+======================+=======================+======================+=====================+=======================+=================+
| File system          |                      |  vfat                 | ZFS                  | swap                | ZFS                   |                 |
+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+
| Size                 |  1M                  |  4G, or 1G w/o ISO    | 4G                   | depends on RAM size |                       |                 |
+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+
| Optional encryption  |                      |  *Secure Boot*        | luks 1               | plain dm-crypt or   | ZFS native encryption |                 |
|                      |                      |                       |                      | luks2               |                       |                 |
+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+
| Partition no.        | 5                    | 1                     | 2                    | 4                   | 3                     |                 |
+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+
| Mount point          |                      | /boot/efi             | /boot                |                     | /                     |                 |
|                      |                      | /boot/efis/disk-part1 |                      |                     |                       |                 |
+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+

Dataset layout
~~~~~~~~~~~~~~

+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
| Dataset                   | canmount             | mountpoint           | container                           | notes                                     |
+===========================+======================+======================+=====================================+===========================================+
| bpool                     | off                  | /boot                | contains sys                        |                                           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
| rpool                     | off                  | /                    | contains sys                        |                                           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
| bpool/sys                 | off                  | none                 | contains BOOT                       |                                           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|      rpool/sys            | off                  | none                 | contains ROOT                       | sys is encryptionroot                     |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|      bpool/sys/BOOT       | off                  | none                 | contains boot environments          |                                           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|      rpool/sys/ROOT       | off                  | none                 | contains boot environments          |                                           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|      rpool/sys/DATA       | off                  | none                 | contains placeholder "default"      |                                           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|  rpool/sys/DATA/default   | off                  | /                    | contains user datasets              | child datsets inherits mountpoint         |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
| rpool/sys/DATA/default/   | on                   |  /home (inherited)   | no                                  |                                           |
| home                      |                      |                      |                                     | user datasets, also called "shared        |
|                           |                      |                      |                                     | datasets", "persistent datasets"; also    |
|                           |                      |                      |                                     | include /var/lib, /srv, ...               |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   bpool/sys/BOOT/default  | noauto               | legacy /boot         | no                                  | noauto is used to switch BE. because of   |
|                           |                      |                      |                                     | noauto, must use fstab to mount           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   rpool/sys/ROOT/default  | noauto               | /                    | no                                  | mounted by initrd zfs hook                |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   bpool/sys/BOOT/be1      | noauto               | legacy /boot         | no                                  | see bpool/sys/BOOT/default                |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   rpool/sys/ROOT/be1      | noauto               | /                    | no                                  | see rpool/sys/ROOT/default                |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+

Encryption
~~~~~~~~~~
User should be aware that, ZFS native encryption, used on root pool,
does not encrypt some metadata of the datasets.

ZFS native encryption also does not change master key when ``zfs change-key`` is invoked,
it means that you must wipe the disk when password is compromised to protect confidentiality.

See `zfs-load-key.8 <https://openzfs.github.io/openzfs-docs/man/8/zfs-load-key.8.html>`__
and `zfs-change-key.8 <https://openzfs.github.io/openzfs-docs/man/8/zfs-change-key.8.html>`__ for more information.

Root dataset encryption is enabled at creation and can not be disabled later. If root dataset is protected
with a passphrase and boot pool is not encrypted, then password can be supplied via SSH.

Boot pool can be encrypted with LUKS 1, this requires the password to be interactively entered at boot
in GRUB.
