RHEL and CentOS
===============

`DKMS`_ or `kABI-tracking kmod`_ style packages are provided for RHEL and
CentOS based distributions from the OpenZFS repository. These packages are
updated as new versions are released. Only the current repository for each
major release is updated with new packages. Packages are available for the
following configurations:

| **EL Releases:** 6, 7.9, 8.3
| **Architectures:** x86_64

To simplify installation a *zfs-release* package is provided which includes
a zfs.repo configuration file and public signing key. All official OpenZFS
packages are signed using this key, and by default yum or dnf will verify a
package's signature before allowing it be to installed. Users are strongly
encouraged to verify the authenticity of the ZFS on Linux public key using
the fingerprint listed here.

| **Location:** /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
| **EL6 Package:** `zfs-release.el6.noarch.rpm`_ (zfs-0.8.x)
| **EL7.9 Package:** `zfs-release.el7_9.noarch.rpm`_ (zfs-0.8.x)
| **EL8.3 Package:** `zfs-release.el8_3.noarch.rpm`_ (zfs-0.8.x)
| **Archived Repositories:** `el7_5`_, `el7_6`_, `el7_7`_, `el7_8`_, `el8_0`_, `el8_1`_, `el8_2`_

| **Download from:**
  `pgp.mit.edu <https://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on>`__
| **Fingerprint:** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

For RHEL/CentOS versions 6 and 7 run:

.. code:: sh

   $ sudo yum install https://zfsonlinux.org/epel/zfs-release.<dist>.noarch.rpm
   $ gpg --quiet --with-fingerprint /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   pub  2048R/F14AB620 2013-03-21 ZFS on Linux <zfs@zfsonlinux.org>
       Key fingerprint = C93A FFFD 9F3F 7B03 C310  CEB6 A9D5 A1C0 F14A B620
       sub  2048R/99685629 2013-03-21

And for RHEL/CentOS 8 and newer:

.. code:: sh

   $ sudo dnf install https://zfsonlinux.org/epel/zfs-release.<dist>.noarch.rpm
   $ gpg --import --import-options show-only /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   pub   rsa2048 2013-03-21 [SC]
         C93AFFFD9F3F7B03C310CEB6A9D5A1C0F14AB620
   uid                      ZFS on Linux <zfs@zfsonlinux.org>
   sub   rsa2048 2013-03-21 [E]

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

For RHEL/CentOS versions 6 and 7 run:

.. code:: sh

   $ sudo yum install epel-release
   $ sudo yum install kernel-devel zfs

And for RHEL/CentOS 8 and newer:

.. code:: sh

   $ sudo dnf install epel-release
   $ sudo dnf install kernel-devel zfs

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
only verified to work with the distribution provided kernel.

For RHEL/CentOS versions 6 and 7 run:

.. code:: sh

   $ sudo yum-config-manager --disable zfs
   $ sudo yum-config-manager --enable zfs-kmod
   $ sudo yum install zfs

And for RHEL/CentOS 8 and newer:

.. code:: sh

   $ sudo dnf config-manager --disable zfs
   $ sudo dnf config-manager --enable zfs-kmod
   $ sudo dnf install zfs

By default the OpenZFS kernel modules are automatically loaded when a ZFS
pool is detected. If you would prefer to always load the modules at boot
time you must create an ``/etc/modules-load.d/zfs.conf`` file.

.. code:: sh

   $ sudo sh -c "echo zfs >/etc/modules-load.d/zfs.conf"

.. note::
   When updating to a new RHEL/CentOS minor release the existing kmod
   packages may not work due to upstream kABI changes in the kernel.
   After upgrading users must uninstall OpenZFS and then reinstall it
   from the matching repository as described in this section.

Testing Repositories
--------------------

In addition to the primary *zfs* repository a *zfs-testing* repository
is available. This repository, which is disabled by default, contains
the latest version of OpenZFS which is under active development. These
packages are made available in order to get feedback from users regarding
the functionality and stability of upcoming releases. These packages
**should not** be used on production systems. Packages from the testing
repository can be installed as follows.

For RHEL/CentOS versions 6 and 7 run:

.. code:: sh

   $ sudo yum-config-manager --enable zfs-testing
   $ sudo yum install kernel-devel zfs

And for RHEL/CentOS 8 and newer:

.. code:: sh

   $ sudo dnf config-manager --enable zfs-testing
   $ sudo dnf install kernel-devel zfs

.. note::
   Use *zfs-testing* for DKMS packages and *zfs-testing-kmod*
   kABI-tracking kmod packages.

.. _kABI-tracking kmod: https://elrepoproject.blogspot.com/2016/02/kabi-tracking-kmod-packages.html
.. _DKMS: https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support
.. _zfs-release.el6.noarch.rpm: https://zfsonlinux.org/epel/zfs-release.el6.noarch.rpm
.. _zfs-release.el7_9.noarch.rpm: https://zfsonlinux.org/epel/zfs-release.el7_9.noarch.rpm
.. _zfs-release.el8_3.noarch.rpm: https://zfsonlinux.org/epel/zfs-release.el8_3.noarch.rpm
.. _el7_5: https://zfsonlinux.org/epel/zfs-release.el7_5.noarch.rpm
.. _el7_6: https://zfsonlinux.org/epel/zfs-release.el7_6.noarch.rpm
.. _el7_7: https://zfsonlinux.org/epel/zfs-release.el7_7.noarch.rpm
.. _el7_8: https://zfsonlinux.org/epel/zfs-release.el7_8.noarch.rpm
.. _el8_0: https://zfsonlinux.org/epel/zfs-release.el8_0.noarch.rpm
.. _el8_1: https://zfsonlinux.org/epel/zfs-release.el8_1.noarch.rpm
.. _el8_2: https://zfsonlinux.org/epel/zfs-release.el8_2.noarch.rpm

.. _EPEL repository: https://fedoraproject.org/wiki/EPEL
