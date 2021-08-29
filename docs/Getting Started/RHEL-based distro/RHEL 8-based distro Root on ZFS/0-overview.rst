.. highlight:: sh

Overview
======================
This document describes how to install RHEL 8-based distro with ZFS as root
file system.

Caution
~~~~~~~
- With less than 4GB RAM, DKMS might fail to build
  in live environment.
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
| Size                 |  1M                  |  2G                   | 4G                   | depends on RAM size |                       |                 |
+----------------------+----------------------+-----------------------+----------------------+---------------------+-----------------------+-----------------+
| Optional encryption  |                      |  *Secure Boot*        |                      | plain dm-crypt      | ZFS native encryption |                 |
|                      |                      |                       |                      |                     |                       |                 |
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
|   bpool/sys/BOOT/default  | noauto               |        /boot         | no                                  | noauto is used to switch BE. because of   |
|                           |                      |                      |                                     | noauto, must use fstab to mount           |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   rpool/sys/ROOT/default  | noauto               | /                    | no                                  | mounted by initrd zfs hook                |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   bpool/sys/BOOT/be1      | noauto               |        /boot         | no                                  | see bpool/sys/BOOT/default                |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+
|   rpool/sys/ROOT/be1      | noauto               | /                    | no                                  | see rpool/sys/ROOT/default                |
+---------------------------+----------------------+----------------------+-------------------------------------+-------------------------------------------+

Encryption
~~~~~~~~~~

- Swap

  Swap is always encrypted. By default, swap is encrypted
  with plain dm-crypt with key generated from ``/dev/urandom``
  at every boot. Swap content does not persist between reboots.

- Root pool

  ZFS native encryption can be optionally enabled for ``rpool/sys``
  and child datasets.

  User should be aware that, ZFS native encryption does not
  encrypt some metadata of the datasets.
  ZFS native encryption also does not change master key when ``zfs change-key`` is invoked.
  Therefore, you should wipe the disk when password is compromised to protect confidentiality.
  See `zfs-load-key.8 <https://openzfs.github.io/openzfs-docs/man/8/zfs-load-key.8.html>`__
  and `zfs-change-key.8 <https://openzfs.github.io/openzfs-docs/man/8/zfs-change-key.8.html>`__
  for more information regarding ZFS native encryption.

  Encryption is enabled at dataset creation and can not be disabled later.

- Boot pool

  Boot pool can not be encrypted.

- Bootloader

  Bootloader can not be encrypted.

  However, with Secure Boot, bootloader
  can be verified by motherboard firmware to be untempered,
  which should be sufficient for most purposes.

  Secure Boot is not supported out-of-the-box due to ZFS module.

Booting with disk failure
~~~~~~~~~~~~~~~~~~~~~~~~~

This guide is written with disk failure in mind.

If disks used in Root on ZFS pool failed, but
sufficient redundancy for both root pool and boot pool
still exists, the system will still boot normally.

Swap partition on the failed disk will fail to mount,
after an 1m30s timeout.

This feature is useful for use cases such
as an unattended remote server.

Example:

 - System has disks ``n>1``

 - Installed with mirrored setup

 - Mirrored setup can tolerate up to ``n-1`` disk failures

 - Disconnect one or more disks, keep at least
   one disk connected

 - System still boots, but fails to mount swap and
   EFI partition
