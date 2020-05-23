Fedora
======

Only
`DKMS <https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support>`__
style packages can be provided for Fedora from the official
zfsonlinux.org repository. This is because Fedora is a fast moving
distribution which does not provide a stable kABI. These packages track
the official ZFS on Linux tags and are updated as new versions are
released. Packages are available for the following configurations:

| **Fedora Releases:** 30, 31, 32
| **Architectures:** x86_64

.. note::
   Due to the release cycle of OpenZFS and Fedora adoption
   of new kernels in current distribution release, it may happen that you
   won't be able to build DKMS package on the most recent kernel update.
   For example, Fedora 32 was released with kernel 5.6 but it is expected
   that it will update to 5.7. OpenZFS was released with support for kernel
   5.6 but not for 5.7 and there will be no update right after 5.7 will hit
   Fedora repository so you have to take into account that you will have to
   pin your kernel version at some point.

To simplify installation a zfs-release package is provided which
includes a zfs.repo configuration file and the ZFS on Linux public
signing key. All official ZFS on Linux packages are signed using this
key, and by default both yum and dnf will verify a package's signature
before allowing it be to installed. Users are strongly encouraged to
verify the authenticity of the ZFS on Linux public key using the
fingerprint listed here.

| **Location:** /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
| **Fedora 30 Package:**
  `http://download.zfsonlinux.org/fedora/zfs-release.fc30.noarch.rpm <http://download.zfsonlinux.org/fedora/zfs-release.fc30.noarch.rpm>`__
| **Fedora 31 Package:**
  `http://download.zfsonlinux.org/fedora/zfs-release.fc31.noarch.rpm <http://download.zfsonlinux.org/fedora/zfs-release.fc31.noarch.rpm>`__
| **Fedora 32 Package:**
  `http://download.zfsonlinux.org/fedora/zfs-release.fc32.noarch.rpm <http://download.zfsonlinux.org/fedora/zfs-release.fc32.noarch.rpm>`__
| **Download from:**
  `pgp.mit.edu <http://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on>`__
| **Fingerprint:** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

.. code:: sh

   $ sudo dnf install http://download.zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm
   $ gpg --quiet --with-fingerprint /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   pub  2048R/F14AB620 2013-03-21 ZFS on Linux <zfs@zfsonlinux.org>
       Key fingerprint = C93A FFFD 9F3F 7B03 C310  CEB6 A9D5 A1C0 F14A B620
       sub  2048R/99685629 2013-03-21

The ZFS on Linux packages should be installed with ``dnf`` on Fedora.
Note that it is important to make sure that the matching *kernel-devel*
package is installed for the running kernel since DKMS requires it to
build ZFS.

.. code:: sh

   $ sudo dnf install kernel-devel zfs

If the Fedora provided *zfs-fuse* package is already installed on the
system. Then the ``dnf swap`` command should be used to replace the
existing fuse packages with the ZFS on Linux packages.

.. code:: sh

   $ sudo dnf swap zfs-fuse zfs

Testing Repositories
--------------------

In addition to the primary *zfs* repository a *zfs-testing* repository
is available. This repository, which is disabled by default, contains
the latest version of ZFS on Linux which is under active development.
These packages are made available in order to get feedback from users
regarding the functionality and stability of upcoming releases. These
packages **should not** be used on production systems. Packages from the
testing repository can be installed as follows.

::

   $ sudo dnf --enablerepo=zfs-testing install kernel-devel zfs
