.. highlight:: sh

Arch Linux
============

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

.. note::

   Due to the release cycle of OpenZFS and the rapid adoption of new kernels
   it may happen that you won’t be able to
   build DKMS packages for the most recent kernel update.
   If the `latest OpenZFS release <https://github.com/openzfs/zfs/releases/latest>`__
   does not yet support the installed kernel,
   `downgrade kernel <https://wiki.archlinux.org/index.php/downgrading_packages>`__
   before installation.

ZFS packages are provided by the third-party 
`archzfs repository <https://github.com/archzfs/archzfs>`__.
You can use it as follows.

Import archzfs GPG key::

  curl -O https://archzfs.com/archzfs.gpg
  pacman-key -a archzfs.gpg
  pacman-key --lsign-key DDF7DB817396A49B2A2723F7403BD972F75D9D76

Add the archzfs repository::

  tee -a /etc/pacman.conf <<- 'EOF'
  [archzfs]
  Server = https://archzfs.com/$repo/$arch
  Server = https://mirror.sum7.eu/archlinux/archzfs/$repo/$arch
  Server = https://mirror.biocrafting.net/archlinux/archzfs/$repo/$arch
  Server = https://mirror.in.themindsmaze.com/archzfs/$repo/$arch
  EOF

Update pacman database::

  pacman -Sy

Install packages.

* Install prebuilt zfs package.
  Kernel package version must match the zfs package version.

  - archzfs-linux
  - archzfs-linux-lts
  - archzfs-linux-zen
  - archzfs-linux-hardened

  ::

     pacman -S archzfs-linux

* If kernel dependency fails, or if you use a custom kernel,
  install zfs-dkms

  ::

     pacman -S archzfs-dkms

Root on ZFS
-----------
.. toctree::
  :maxdepth: 1
  :glob:

  *Root on ZFS
