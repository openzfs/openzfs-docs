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

NixOS live image ships with ZFS support by default.

Note that you need to apply these settings even if you don't need
to boot from ZFS.  The kernel module 'zfs.ko' will not be available
to modprobe until you make these changes and reboot.

#. Edit ``/etc/nixos/configuration.nix`` and add the following
   options::

    boot.supportedFilesystems = [ "zfs" ];
    boot.zfs.forceImportRoot = false;
    networking.hostId = "yourHostId";

   Where hostID can be generated with::

     head -c4 /dev/urandom | od -A none -t x4

#. Apply configuration changes::

    nixos-rebuild boot

#. Reboot::

     reboot

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *

Contribute
----------

You can contribute to this documentation.  Fork this repo, edit the
documentation, then opening a pull request.

#. To test your changes locally, use the devShell in this repo::

    git clone https://github.com/ne9z/nixos-live openzfs-docs-dev
    cd openzfs-docs-dev
    nix develop ./openzfs-docs-dev/#docs

#. Inside the openzfs-docs repo, build pages::

     make html

#. Look for errors and warnings in the make output. If there is no
   errors::

     xdg-open _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a
   pull request. Mention @ne9z.
