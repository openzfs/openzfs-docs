Building ZFS
============

GitHub Repositories
~~~~~~~~~~~~~~~~~~~

The official source for OpenZFS is maintained at GitHub by the
`openzfs <https://github.com/openzfs/>`__ organization. The primary
git repository for the project is the `zfs
<https://github.com/openzfs/zfs>`__ repository.

There are two main components in this repository:

- **ZFS**: The ZFS repository contains a copy of the upstream OpenZFS
   code which has been adapted and extended for Linux and FreeBSD. The
   vast majority of the core OpenZFS code is self-contained and can be
   used without modification.

- **SPL**: The SPL is thin shim layer which is responsible for
   implementing the fundamental interfaces required by OpenZFS. It's
   this layer which allows OpenZFS to be used across multiple
   platforms. SPL used to be maintained in a separate repository, but
   was merged into the `zfs <https://github.com/openzfs/zfs>`__
   repository in the ``0.8`` major release.

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

The first thing you'll need to do is prepare your environment by
installing a full development tool chain. In addition, development
headers for both the kernel and the following libraries must be
available. It is important to note that if the development kernel
headers for the currently running kernel aren't installed, the modules
won't compile properly.

The following dependencies should be installed to build the latest ZFS
0.8 release.

-  **RHEL/CentOS 7**:

.. code:: sh

   sudo yum install epel-release gcc make autoconf automake libtool rpm-build dkms libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) python python2-devel python-setuptools python-cffi libffi-devel

-  **RHEL/CentOS 8, Fedora**:

.. code:: sh

   sudo dnf install gcc make autoconf automake libtool rpm-build dkms libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) python3 python3-devel python3-setuptools python3-cffi libffi-devel

-  **Debian, Ubuntu**:

.. code:: sh

   sudo apt install build-essential autoconf automake libtool gawk alien fakeroot dkms libblkid-dev uuid-dev libudev-dev libssl-dev zlib1g-dev libaio-dev libattr1-dev libelf-dev linux-headers-$(uname -r) python3 python3-dev python3-setuptools python3-cffi libffi-dev

Build Options
~~~~~~~~~~~~~

There are two options for building OpenZFS; the correct one largely
depends on your requirements.

-  **Packages**: Often it can be useful to build custom packages from
   git which can be installed on a system. This is the best way to
   perform integration testing with systemd, dracut, and udev. The
   downside to using packages it is greatly increases the time required
   to build, install, and test a change.

- **In-tree**: Development can be done entirely in the SPL/ZFS source
   tree. This speeds up development by allowing developers to rapidly
   iterate on a patch. When working in-tree developers can leverage
   incremental builds, load/unload kernel modules, execute utilities,
   and verify all their changes with the ZFS Test Suite.

The remainder of this page focuses on the **in-tree** option which is
the recommended method of development for the majority of changes. See
the :doc:`custom packages <./Custom Packages>` page for additional information on building
custom packages.

Developing In-Tree
~~~~~~~~~~~~~~~~~~

Clone from GitHub
^^^^^^^^^^^^^^^^^

Start by cloning the ZFS repository from GitHub. The repository has a
**master** branch for development and a series of **\*-release**
branches for tagged releases. After checking out the repository your
clone will default to the master branch. Tagged releases may be built
by checking out zfs-x.y.z tags with matching version numbers or
matching release branches.

::

   git clone https://github.com/openzfs/zfs

Configure and Build
^^^^^^^^^^^^^^^^^^^

For developers working on a change always create a new topic branch
based off of master. This will make it easy to open a pull request with
your change latter. The master branch is kept stable with extensive
`regression testing <http://build.zfsonlinux.org/>`__ of every pull
request before and after it's merged. Every effort is made to catch
defects as early as possible and to keep them out of the tree.
Developers should be comfortable frequently rebasing their work against
the latest master branch.

In this example we'll use the master branch and walk through a stock
**in-tree** build. Start by checking out the desired branch then build
the ZFS and SPL source in the tradition autotools fashion.

::

   cd ./zfs
   git checkout master
   sh autogen.sh
   ./configure
   make -s -j$(nproc)

| **tip:** ``--with-linux=PATH`` and ``--with-linux-obj=PATH`` can be
  passed to configure to specify a kernel installed in a non-default
  location. This option is also supported when building ZFS.
| **tip:** ``--enable-debug`` can be set to enable all ASSERTs and
  additional correctness tests. This option is also supported when
  building ZFS.

**Optional** Build packages

::

   make deb #example for Debian/Ubuntu

Install
^^^^^^^

You can run ``zfs-tests.sh`` without installing ZFS, see below. If you
have reason to install ZFS after building it, pay attention to how your
distribution handles kernel modules. On Ubuntu, for example, the modules
from this repository install in the ``extra`` kernel module path, which
is not in the standard ``depmod`` search path. Therefore, for the
duration of your testing, edit ``/etc/depmod.d/ubuntu.conf`` and add
``extra`` to the beginning of the search path.

You may then install using
``sudo make install; sudo ldconfig; sudo depmod``. You'd uninstall with
``sudo make uninstall; sudo ldconfig; sudo depmod``.

.. _running-zloopsh-and-zfs-testssh:

Running zloop.sh and zfs-tests.sh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you wish to run the ZFS Test Suite (ZTS), then ``ksh`` and a few
additional utilities must be installed.

-  **RHEL/CentOS 7:**

.. code:: sh

   sudo yum install ksh bc fio acl sysstat mdadm lsscsi parted attr dbench nfs-utils samba rng-tools pax perf

-  **RHEL/CentOS 8, Fedora:**

.. code:: sh

   sudo dnf install ksh bc fio acl sysstat mdadm lsscsi parted attr dbench nfs-utils samba rng-tools pax perf

-  **Debian, Ubuntu:**

.. code:: sh

   sudo apt install ksh bc fio acl sysstat mdadm lsscsi parted attr dbench nfs-kernel-server samba rng-tools pax linux-tools-common selinux-utils quota

There are a few helper scripts provided in the top-level scripts
directory designed to aid developers working with in-tree builds.

-  **zfs-helper.sh:** Certain functionality (i.e. /dev/zvol/) depends on
   the ZFS provided udev helper scripts being installed on the system.
   This script can be used to create symlinks on the system from the
   installation location to the in-tree helper. These links must be in
   place to successfully run the ZFS Test Suite. The **-i** and **-r**
   options can be used to install and remove the symlinks.

::

   sudo ./scripts/zfs-helpers.sh -i

-  **zfs.sh:** The freshly built kernel modules can be loaded using
   ``zfs.sh``. This script can latter be used to unload the kernel
   modules with the **-u** option.

::

   sudo ./scripts/zfs.sh

-  **zloop.sh:** A wrapper to run ztest repeatedly with randomized
   arguments. The ztest command is a user space stress test designed to
   detect correctness issues by concurrently running a random set of
   test cases. If a crash is encountered, the ztest logs, any associated
   vdev files, and core file (if one exists) are collected and moved to
   the output directory for analysis.

::

   sudo ./scripts/zloop.sh

-  **zfs-tests.sh:** A wrapper which can be used to launch the ZFS Test
   Suite. Three loopback devices are created on top of sparse files
   located in ``/var/tmp/`` and used for the regression test. Detailed
   directions for the ZFS Test Suite can be found in the
   `README <https://github.com/openzfs/zfs/tree/master/tests>`__
   located in the top-level tests directory.

::

    ./scripts/zfs-tests.sh -vx

**tip:** The **delegate** tests will be skipped unless group read
permission is set on the zfs directory and its parents.
