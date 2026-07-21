.. image:: docs/_static/img/logo/480px-Open-ZFS-Secondary-Logo-Colour-halfsize.png
.. highlight:: sh

OpenZFS Documentation
=====================

Public link: https://openzfs.github.io/openzfs-docs/

Building Locally
----------------

Install Prerequisites
~~~~~~~~~~~~~~~~~~~~~

The dependencies are available via pip::

   # For Debian based distros
   sudo apt install python3-pip
   # For RPM-based distros
   sudo yum install python3-pip
   # For openSUSE
   sudo zypper in python3-pip

   pip3 install -r docs/requirements.txt
   # Add ~/.local/bin to your $PATH, e.g. by adding this to ~/.bashrc:
   PATH=$HOME/.local/bin:$PATH

Or, you can use tox::

   tox -e develop
   . .tox/develop/bin/activate

Build
~~~~~

::

   cd docs
   make html
   # HTML files will be generated in: _build/html

Generated pages
~~~~~~~~~~~~~~~

Some pages are not stored in this repository, they are built from the
OpenZFS sources by the targets below. Run them before ``make html`` if you
need those pages locally; CI always does. Each one clones
``https://github.com/openzfs/zfs`` into ``docs/_build/zfs`` on first use::

   make man             # man pages, for every release and master
   make feature_matrix  # feature flags support matrix
   make module_params   # Module Parameters page

The Module Parameters page is generated from the parameter declarations in
the OpenZFS sources; the tuning advice on it is maintained by hand in
``docs/module_parameters.yaml``. ``make module_params_check`` validates that
file without rebuilding the page - it fails if an entry describes a
parameter that no version of OpenZFS has.
