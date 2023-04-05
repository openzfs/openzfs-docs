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

See `Archlinux Wiki <https://wiki.archlinux.org/title/ZFS>`__.

Root on ZFS
-----------
ZFS can be used as root file system for Arch Linux.
An installation guide is available.

.. toctree::
  :maxdepth: 1
  :glob:

  *

Contribute
----------
#. Fork and clone `this repo <https://github.com/openzfs/openzfs-docs>`__.

#. Install the tools::

    sudo pacman -S --needed python-pip make

    pip3 install -r docs/requirements.txt

    # Add ~/.local/bin to your "${PATH}", e.g. by adding this to ~/.bashrc:
    [ -d "${HOME}"/.local/bin ] && export PATH="${HOME}"/.local/bin:"${PATH}"

#. Make your changes.

#. Test::

    cd docs
    make html
    sensible-browser _build/html/index.html

#. ``git commit --signoff`` to a branch, ``git push``, and create a pull
   request. Mention @ne9z.
