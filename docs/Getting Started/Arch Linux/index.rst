.. highlight:: sh

Arch Linux
============

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
<https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Arch%20Linux%20ZFS%20HOWTO:>`__.

Overview
--------
Due to license incompatibility,
ZFS is not available in Arch Linux official repo.

ZFS support is provided by third-party `archzfs repo <https://github.com/archzfs/archzfs>`__.

Installation
------------

Note: this is for installing ZFS on an existing Arch
Linux installation. To use ZFS as root file system,
see below.

#. `Add archzfs repo to pacman <0-archzfs-repo.html>`__.

#. Install `zfs-linux* <1-zfs-linux.html>`__
   or `zfs-dkms <2-zfs-dkms.html>`__ depending on your needs.
   See the respective pages for details.

Live image
----------
Kernel package shipped with latest live image might
not be compatible with ZFS, user should check kernel version
following instructions `here <3-live.html>`__.

Root on ZFS
-----------
ZFS can be used as root file system for Arch Linux.
An installation guide is available.

`Start here <Root%20on%20ZFS/0-overview.html>`__.

.. toctree::
  :maxdepth: 1
  :glob:

  Root on ZFS/*

Contribute
----------
#. Fork and clone `this repo <https://github.com/openzfs/openzfs-docs>`__.

#. Install the tools::

    sudo pacman -S --needed python-pip make

    pip3 install -r docs/requirements.txt

    # Add ~/.local/bin to your $PATH, e.g. by adding this to ~/.bashrc:
    [ -d $HOME/.local/bin ] && export PATH=$HOME/.local/bin:$PATH

#. Make your changes.

#. Test::

    cd docs
    make html
    sensible-browser _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a pull
   request. Mention @ne9z.
