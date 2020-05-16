RHEL and CentOS
===============

`kABI-tracking
kmod <http://elrepoproject.blogspot.com/2016/02/kabi-tracking-kmod-packages.html>`__
or
`DKMS <https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support>`__
style packages are provided for RHEL / CentOS based distributions from
the official zfsonlinux.org repository. These packages track the
official ZFS on Linux tags and are updated as new versions are released.
Packages are available for the following configurations:

| **EL Releases:** 6.x, 7.x, 8.x
| **Architectures:** x86_64

To simplify installation a zfs-release package is provided which
includes a zfs.repo configuration file and the ZFS on Linux public
signing key. All official ZFS on Linux packages are signed using this
key, and by default yum will verify a package's signature before
allowing it be to installed. Users are strongly encouraged to verify the
authenticity of the ZFS on Linux public key using the fingerprint listed
here.

| **Location:** /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
| **EL6 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el6.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el6.noarch.rpm>`__
| **EL7.5 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el7_5.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el7_5.noarch.rpm>`__
| **EL7.6 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el7_6.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el7_6.noarch.rpm>`__
| **EL7.7 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el7_7.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el7_7.noarch.rpm>`__
| **EL7.8 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el7_8.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el7_8.noarch.rpm>`__
| **EL8.0 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el8_0.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el8_0.noarch.rpm>`__
| **EL8.1 Package:**
  `http://download.zfsonlinux.org/epel/zfs-release.el8_1.noarch.rpm <http://download.zfsonlinux.org/epel/zfs-release.el8_1.noarch.rpm>`__
| **Note:** Starting with EL7.7 **zfs-0.8** will become the default,
  EL7.6 and older will continue to track the **zfs-0.7** point releases.

| **Download from:**
  `pgp.mit.edu <http://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on>`__
| **Fingerprint:** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

::

   $ sudo yum install http://download.zfsonlinux.org/epel/zfs-release.<dist>.noarch.rpm
   $ gpg --quiet --with-fingerprint /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   pub  2048R/F14AB620 2013-03-21 ZFS on Linux <zfs@zfsonlinux.org>
       Key fingerprint = C93A FFFD 9F3F 7B03 C310  CEB6 A9D5 A1C0 F14A B620
       sub  2048R/99685629 2013-03-21

After installing the zfs-release package and verifying the public key
users can opt to install ether the kABI-tracking kmod or DKMS style
packages. For most users the kABI-tracking kmod packages are recommended
in order to avoid needing to rebuild ZFS for every kernel update. DKMS
packages are recommended for users running a non-distribution kernel or
for users who wish to apply local customizations to ZFS on Linux.

kABI-tracking kmod
------------------

By default the zfs-release package is configured to install DKMS style
packages so they will work with a wide range of kernels. In order to
install the kABI-tracking kmods the default repository in the
*/etc/yum.repos.d/zfs.repo* file must be switch from *zfs* to
*zfs-kmod*. Keep in mind that the kABI-tracking kmods are only verified
to work with the distribution provided kernel.

.. code:: diff

   # /etc/yum.repos.d/zfs.repo
    [zfs]
    name=ZFS on Linux for EL 7 - dkms
    baseurl=http://download.zfsonlinux.org/epel/7/$basearch/
   -enabled=1
   +enabled=0
    metadata_expire=7d
    gpgcheck=1
    gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   @@ -9,7 +9,7 @@
    [zfs-kmod]
    name=ZFS on Linux for EL 7 - kmod
    baseurl=http://download.zfsonlinux.org/epel/7/kmod/$basearch/
   -enabled=0
   +enabled=1
    metadata_expire=7d
    gpgcheck=1
    gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux

The ZFS on Linux packages can now be installed using yum.

::

   $ sudo yum install zfs

DKMS
----

To install DKMS style packages issue the following yum commands. First
add the `EPEL repository <https://fedoraproject.org/wiki/EPEL>`__ which
provides DKMS by installing the *epel-release* package, then the
*kernel-devel* and *zfs* packages. Note that it is important to make
sure that the matching *kernel-devel* package is installed for the
running kernel since DKMS requires it to build ZFS.

::

   $ sudo yum install epel-release
   $ sudo yum install "kernel-devel-uname-r == $(uname -r)" zfs

Important Notices
-----------------

.. _rhelcentos-7x-kmod-package-upgrade:

RHEL/CentOS 7.x kmod package upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When updating to a new RHEL/CentOS 7.x release the existing kmod
packages will not work due to upstream kABI changes in the kernel. After
upgrading to 7.x users must uninstall ZFS and then reinstall it as
described in the `kABI-tracking
kmod <https://github.com/zfsonlinux/zfs/wiki/RHEL-%26-CentOS/#kabi-tracking-kmod>`__
section. Compatible kmod packages will be installed from the matching
CentOS 7.x repository.

::

   $ sudo yum remove zfs zfs-kmod spl spl-kmod libzfs2 libnvpair1 libuutil1 libzpool2 zfs-release
   $ sudo yum install http://download.zfsonlinux.org/epel/zfs-release.el7_6.noarch.rpm
   $ sudo yum autoremove
   $ sudo yum clean metadata
   $ sudo yum install zfs 

Switching from DKMS to kABI-tracking kmod
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When switching from DKMS to kABI-tracking kmods first uninstall the
existing DKMS packages. This should remove the kernel modules for all
installed kernels but in practice it's not always perfectly reliable.
Therefore, it's recommended that you manually remove any remaining ZFS
kernel modules as shown. At this point the kABI-tracking kmods can be
installed as described in the section above.

::

   $ sudo yum remove zfs zfs-kmod spl spl-kmod libzfs2 libnvpair1 libuutil1 libzpool2 zfs-release

   $ sudo find /lib/modules/ \( -name "splat.ko" -or -name "zcommon.ko" \
   -or -name "zpios.ko" -or -name "spl.ko" -or -name "zavl.ko" -or \
   -name "zfs.ko" -or -name "znvpair.ko" -or -name "zunicode.ko" \) \
   -exec /bin/rm {} \;

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

   $ sudo yum --enablerepo=zfs-testing install kernel-devel zfs 
