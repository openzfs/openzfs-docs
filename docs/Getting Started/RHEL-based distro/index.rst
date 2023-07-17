RHEL-based distro
=======================

Contents
--------
.. toctree::
  :maxdepth: 1
  :glob:

  *

`DKMS`_ and `kABI-tracking kmod`_ style packages are provided for x86_64 RHEL-
and CentOS-based distributions from the OpenZFS repository.  These packages
are updated as new versions are released.  Only the repository for the current
minor version of each current major release is updated with new packages.

To simplify installation, a *zfs-release* package is provided which includes
a zfs.repo configuration file and public signing key. All official OpenZFS
packages are signed using this key, and by default yum or dnf will verify a
package's signature before allowing it be to installed. Users are strongly
encouraged to verify the authenticity of the OpenZFS public key using
the fingerprint listed here.

| **Key location:** /etc/pki/rpm-gpg/RPM-GPG-KEY-openzfs (previously -zfsonlinux)
| **Current release packages:** `EL7`_, `EL8`_, `EL9`_
| **Archived release packages:** `see repo page <https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/epel>`__

| **Signing key1 (EL8 and older, Fedora 36 and older)**
  `pgp.mit.edu <https://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on>`__ /
  `direct link <https://raw.githubusercontent.com/zfsonlinux/zfsonlinux.github.com/master/zfs-release/RPM-GPG-KEY-openzfs-key1>`__
| **Fingerprint:** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

| **Signing key2 (EL9+, Fedora 37+)**
  `pgp.mit.edu <https://pgp.mit.edu/pks/lookup?search=0xA599FD5E9DB84141&op=index&fingerprint=on>`__ /
  `direct link <https://raw.githubusercontent.com/zfsonlinux/zfsonlinux.github.com/master/zfs-release/RPM-GPG-KEY-openzfs-key2>`__
| **Fingerprint:** 7DC7 299D CF7C 7FD9 CD87 701B A599 FD5E 9DB8 4141

For EL7 run::

 yum install https://zfsonlinux.org/epel/zfs-release-2-3$(rpm --eval "%{dist}").noarch.rpm

and for EL8 and 9::

 dnf install https://zfsonlinux.org/epel/zfs-release-2-3$(rpm --eval "%{dist}").noarch.rpm

After installing the *zfs-release* package and verifying the public key
users can opt to install either the DKMS or kABI-tracking kmod style packages.
DKMS packages are recommended for users running a non-distribution kernel or
for users who wish to apply local customizations to OpenZFS.  For most users
the kABI-tracking kmod packages are recommended in order to avoid needing to
rebuild OpenZFS for every kernel update.

DKMS
----

To install DKMS style packages issue the following commands. First add the
`EPEL repository`_ which provides DKMS by installing the *epel-release*
package, then the *kernel-devel* and *zfs* packages. Note that it is
important to make sure that the matching *kernel-devel* package is installed
for the running kernel since DKMS requires it to build OpenZFS.

For EL6 and 7, separately run::

 yum install -y epel-release
 yum install -y kernel-devel
 yum install -y zfs

And for EL8 and newer, separately run::

 dnf install -y epel-release
 dnf install -y kernel-devel
 dnf install -y zfs

.. note::
   When switching from DKMS to kABI-tracking kmods first uninstall the
   existing DKMS packages. This should remove the kernel modules for all
   installed kernels, then the kABI-tracking kmods can be installed as
   described in the section below.

kABI-tracking kmod
------------------

By default the *zfs-release* package is configured to install DKMS style
packages so they will work with a wide range of kernels. In order to
install the kABI-tracking kmods the default repository must be switched
from *zfs* to *zfs-kmod*. Keep in mind that the kABI-tracking kmods are
only verified to work with the distribution-provided, non-Stream kernel.

For EL6 and 7 run::

 yum-config-manager --disable zfs
 yum-config-manager --enable zfs-kmod
 yum install zfs

And for EL8 and newer::

 dnf config-manager --disable zfs
 dnf config-manager --enable zfs-kmod
 dnf install zfs

By default the OpenZFS kernel modules are automatically loaded when a ZFS
pool is detected. If you would prefer to always load the modules at boot
time you can create such configuration in ``/etc/modules-load.d``::

 echo zfs >/etc/modules-load.d/zfs.conf

.. note::
   When updating to a new EL minor release the existing kmod
   packages may not work due to upstream kABI changes in the kernel.
   The configuration of the current release package may have already made an
   updated package available, but the package manager may not know to install
   that package if the version number isn't newer.  When upgrading, users
   should verify that the *kmod-zfs* package is providing suitable kernel
   modules, reinstalling the *kmod-zfs* package if necessary.

Previous minor EL releases
--------------------------

The current release package uses `"${releasever}"` rather than specify a particular
minor release as previous release packages did.  Typically `"${releasever}"` will
resolve to just the major version (e.g. `8`), and the resulting repository URL
will be aliased to the current minor version (e.g. `8.7`), but you can specify
`--releasever` to use previous repositories. ::

  [vagrant@localhost ~]$ dnf list available --showduplicates kmod-zfs
  Last metadata expiration check: 0:00:08 ago on tor 31 jan 2023 17:50:05 UTC.
  Available Packages
  kmod-zfs.x86_64                          2.1.6-1.el8                          zfs-kmod
  kmod-zfs.x86_64                          2.1.7-1.el8                          zfs-kmod
  kmod-zfs.x86_64                          2.1.8-1.el8                          zfs-kmod
  kmod-zfs.x86_64                          2.1.9-1.el8                          zfs-kmod
  [vagrant@localhost ~]$ dnf list available --showduplicates --releasever=8.6 kmod-zfs
  Last metadata expiration check: 0:16:13 ago on tor 31 jan 2023 17:34:10 UTC.
  Available Packages
  kmod-zfs.x86_64                          2.1.4-1.el8                          zfs-kmod
  kmod-zfs.x86_64                          2.1.5-1.el8                          zfs-kmod
  kmod-zfs.x86_64                          2.1.5-2.el8                          zfs-kmod
  kmod-zfs.x86_64                          2.1.6-1.el8                          zfs-kmod
  [vagrant@localhost ~]$

In the above example, the former packages were built for EL8.7, and the latter for EL8.6.

Testing Repositories
--------------------

In addition to the primary *zfs* repository a *zfs-testing* repository
is available. This repository, which is disabled by default, contains
the latest version of OpenZFS which is under active development. These
packages are made available in order to get feedback from users regarding
the functionality and stability of upcoming releases. These packages
**should not** be used on production systems. Packages from the testing
repository can be installed as follows.

For EL6 and 7 run::

 yum-config-manager --enable zfs-testing
 yum install kernel-devel zfs

And for EL8 and newer::

 dnf config-manager --enable zfs-testing
 dnf install kernel-devel zfs

.. note::
   Use *zfs-testing* for DKMS packages and *zfs-testing-kmod*
   for kABI-tracking kmod packages.

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *

.. _kABI-tracking kmod: https://elrepoproject.blogspot.com/2016/02/kabi-tracking-kmod-packages.html
.. _DKMS: https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support
.. _EL7: https://zfsonlinux.org/epel/zfs-release-2-3.el7.noarch.rpm
.. _EL8: https://zfsonlinux.org/epel/zfs-release-2-3.el8.noarch.rpm
.. _EL9: https://zfsonlinux.org/epel/zfs-release-2-3.el9.noarch.rpm
.. _EPEL repository: https://fedoraproject.org/wiki/EPEL
