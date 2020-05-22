.. image:: docs/_static/img/logo/480px-Open-ZFS-Secondary-Logo-Colour-halfsize.png
.. highlight:: sh

OpenZFS Documentation
=====================

Public link: https://openzfs.github.io/openzfs-docs/

Building Locally
----------------

Install Prerequisites
~~~~~~~~~~~~~~~~~~~~~

Debian 11 (“testing”) / Ubuntu 20.04 or later::

   sudo apt install python3-sphinx python3-sphinx-issues python3-sphinx-rtd-theme

Debian 10 (”Buster”) and earlier::

   sudo apt install pip3
   pip3 install -r requirements.txt
   # Add ~/.local/bin to your $PATH, e.g. by adding this to ~/.bashrc:
   PATH=$HOME/.local/bin:$PATH

Other distros::

   pip install -r requirements.txt
   # Add ~/.local/bin to your $PATH, e.g. by adding this to ~/.bashrc:
   PATH=$HOME/.local/bin:$PATH

Build
~~~~~

::

   cd docs
   make html
   # HTML files will be generated in: _build/html
