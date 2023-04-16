.. highlight:: sh

NixOS
=====

Contents
--------
.. toctree::
  :maxdepth: 1
  :glob:

  *

Support
-------
Reach out to the community using the :ref:`mailing_lists` or IRC at
`#zfsonlinux <ircs://irc.libera.chat/#zfsonlinux>`__ on `Libera Chat
<https://libera.chat/>`__.

If you have a bug report or feature request
related to this HOWTO, please `file a new issue and mention @ne9z
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Nix%20ZFS%20HOWTO:>`__.

Installation
------------

Note: this is for installing ZFS on an existing
NixOS installation. To use ZFS as root file system,
see below.

NixOS live images ship with ZFS support by default.

Note that you need to apply these settings even if you don't need
to boot from ZFS. The kernel module 'zfs.ko' will not be available
to modprobe until you make these changes and reboot.

#. Import separate configration file for ZFS options
  add './zfs.nix' to 'imports' in /etc/nixos/configuration.nix::

    imports = [ ./zfs.nix ];

#. Configure ZFS options
  To get the hostId string run: `head -c 8 /etc/machine-id`::

    tee -a /etc/nixos/zfs.nix <<EOF
    { ... }:

    { boot.supportedFilesystems = [ "zfs" ];
      networking.hostId = "7b5489cd";
    }
    EOF

#. Apply configuation changes::

    nixos-rebuild switch

Root on ZFS
-----------
ZFS can be used as root file system for NixOS.
An installation guide is available.

Start from "Preparation".

.. toctree::
  :maxdepth: 1
  :glob:

  Root on ZFS/*

Contribute
----------
#. Fork and clone `this repo <https://github.com/openzfs/openzfs-docs>`__.

#. Launch an ephemeral nix-shell with the following packages::

    nix-shell -p python3 python3Packages.pip gnumake python3Packages.setuptools

#. Create python virtual environment and install packages::

    cd openzfs-docs
    python -m venv .venv
    source .venv/bin/activate

    pip install -r docs/requirements.txt

#. Make your changes.

#. Test::

    make html
    xdg-open _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a pull
   request. Mention @ne9z.
