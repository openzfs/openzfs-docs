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

Live image ships with ZFS support by default.

#. Import separate configration file for ZFS options::

    vim /etc/nixos/configuration.nix
    ##add './zfs.nix' to 'imports'
    # imports = [ ./zfs.nix ];

#. Configure ZFS options::

    tee -a /etc/nixos/zfs.nix <<EOF
    { config, pkgs, ... }:

    { boot.supportedFilesystems = [ "zfs" ];
      networking.hostId = "$(head -c 8 /etc/machine-id)";
    }
    EOF

#. Apply configuation changes::

    nixos-rebuild switch

Root on ZFS
-----------
ZFS can be used as root file system for NixOS.
An installation guide is available.

`Start here <Root%20on%20ZFS/0-overview.html>`__.

.. toctree::
  :maxdepth: 1
  :glob:

  Root on ZFS/*

Contribute
----------
#. Fork and clone `this repo <https://github.com/openzfs/openzfs-docs>`__.

#. Launch an ephemeral nix-shell with the following packages::

    nix-shell -p python39 python39Packages.pip gnumake \
        python39Packages.setuptools

#. Create python virtual environment and install packages::

    cd openzfs-docs
    python -m venv .venv
    source .venv/bin/activate

    pip install -r docs/requirements.txt

#. Make your changes.

#. Test::

    make html
    sensible-browser _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a pull
   request. Mention @ne9z.
