Fedora
======

Only `DKMS`_ style packages can be provided for Fedora from the official
OpenZFS repository. This is because Fedora is a fast moving distribution
which does not provide a stable kABI. These packages track the official
OpenZFS tags and are updated as new versions are released. Packages are
available for the following configurations:

| **Fedora Releases:** 31, 32, 33
| **Architectures:** x86_64

.. note::
   Due to the release cycle of OpenZFS and Fedora's rapid adoption of new
   kernels it may happen that you won't be able to build DKMS packages for
   the most recent kernel update. If the `latest OpenZFS release`_ does
   not yet support the installed Fedora kernel you will have to pin your
   kernel to an earlier supported version.

To simplify installation a *zfs-release* package is provided which includes
a zfs.repo configuration file and public signing key. All official
OpenZFS packages are signed using this key, and by default dnf will verify a
package's signature before allowing it be to installed. Users are strongly
encouraged to verify the authenticity of the ZFS on Linux public key using
the fingerprint listed here.

| **Location:** /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
| **Fedora 31 Package:** `zfs-release.fc31.noarch.rpm`_
| **Fedora 32 Package:** `zfs-release.fc32.noarch.rpm`_
| **Fedora 33 Package:** `zfs-release.fc33.noarch.rpm`_
| **Download from:**
  `pgp.mit.edu <https://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on>`__
| **Fingerprint:** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

.. code:: sh

   $ sudo dnf install https://zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm
   $ gpg --import --import-options show-only /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   pub   rsa2048 2013-03-21 [SC]
         C93AFFFD9F3F7B03C310CEB6A9D5A1C0F14AB620
   uid                      ZFS on Linux <zfs@zfsonlinux.org>
   sub   rsa2048 2013-03-21 [E]

The OpenZFS packages should be installed with ``dnf`` on Fedora.  Note that
it is important to make sure that the matching *kernel-devel* package is
installed for the running kernel since DKMS requires it to build ZFS.

.. code:: sh

   $ sudo dnf install zfs

If the Fedora provided *zfs-fuse* package is already installed on the
system. Then the ``dnf swap`` command should be used to replace the
existing fuse packages with the ZFS on Linux packages.

.. code:: sh

   $ sudo dnf swap zfs-fuse zfs

By default the OpenZFS kernel modules are automatically loaded when a ZFS
pool is detected. If you would prefer to always load the modules at boot
time you must create an ``/etc/modules-load.d/zfs.conf`` file.

.. code:: sh

   $ sudo sh -c "echo zfs >/etc/modules-load.d/zfs.conf"

Testing Repositories
--------------------

In addition to the primary *zfs* repository a *zfs-testing* repository
is available. This repository, which is disabled by default, contains
the latest version of OpenZFS which is under active development. These
packages are made available in order to get feedback from users regarding
the functionality and stability of upcoming releases. These packages
**should not** be used on production systems. Packages from the testing
repository can be installed as follows.

::

   $ sudo dnf config-manager --enable zfs-testing
   $ sudo dnf install zfs

.. _DKMS: https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support
.. _latest OpenZFS release: https://github.com/openzfs/zfs/releases/latest
.. _zfs-release.fc31.noarch.rpm: https://zfsonlinux.org/fedora/zfs-release.fc31.noarch.rpm
.. _zfs-release.fc32.noarch.rpm: https://zfsonlinux.org/fedora/zfs-release.fc32.noarch.rpm
.. _zfs-release.fc33.noarch.rpm: https://zfsonlinux.org/fedora/zfs-release.fc33.noarch.rpm
