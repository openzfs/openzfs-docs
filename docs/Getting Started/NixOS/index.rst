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

Note that you need to apply these settings even if you don't need
to boot from ZFS.  The kernel module 'zfs.ko' will not be available
to modprobe until you make these changes and reboot.

#. Import separate configration file for ZFS options::

    vim /etc/nixos/configuration.nix
    ##add './zfs.nix' to 'imports'
    # imports = [ ./zfs.nix ];

#. Configure ZFS options::

    tee -a /etc/nixos/zfs.nix <<EOF
    { config, pkgs, ... }:

    {
      boot.supportedFilesystems = [ "zfs" ];
      networking.hostId = (builtins.substring 0 8 (builtins.readFile "/etc/machine-id"));
    }
    EOF

#. Apply configuation changes::

    nixos-rebuild switch

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *
