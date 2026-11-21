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
related to this HOWTO, please `file a new issue
<https://github.com/openzfs/openzfs-docs/issues/new>`__.

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

#. To test your changes locally, clone the repo and build the docs::

    git clone https://github.com/openzfs/openzfs-docs
    cd openzfs-docs
    make html

#. Look for errors and warnings in the make output. If there are no
   errors::

     xdg-open _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a
   pull request.
