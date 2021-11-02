.. highlight:: sh

archzfs repo
============

.. contents:: Table of Contents
  :local:

ZFS packages are provided by the third-party
`archzfs repository <https://github.com/archzfs/archzfs>`__.
You can use it as follows.

#. Import keys of archzfs repository::

    curl -L https://archzfs.com/archzfs.gpg |  pacman-key -a -
    pacman-key --lsign-key $(curl -L https://git.io/JsfVS)
    curl -L https://git.io/Jsfw2 > /etc/pacman.d/mirrorlist-archzfs

#. Add archzfs repository::

    tee -a /etc/pacman.conf <<- 'EOF'

    #[archzfs-testing]
    #Include = /etc/pacman.d/mirrorlist-archzfs

    [archzfs]
    Include = /etc/pacman.d/mirrorlist-archzfs
    EOF

#. Update pacman database::

     pacman -Sy
