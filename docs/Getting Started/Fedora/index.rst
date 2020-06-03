.. highlight:: sh

Fedora
======

.. contents:: Table of Contents
  :local:

Installation
------------

If you want to use ZFS as your root filesystem, see the `Root on ZFS`_
links below instead.

Currently, due to Fedora's unstable fast-paced kernel ABI (kABI), only DKMS style packages can be provided at this time.
As of right now, the following configurations are supported:
  
**Fedora Releases**: 30, 31, 32
**Architectures**: x86_64 (amd64)

.. note::
   Due to the release cycle of OpenZFS and Fedora adoption of new kernels in current distribution release, it may happen that you won’t be able to build DKMS package on the most recent kernel update. For example, Fedora 32 was released with kernel 5.6 but it is expected that it will update to 5.7. OpenZFS was released with support for kernel 5.6 but not for 5.7 and there will be no update right after 5.7 will hit Fedora repository so you have to take into account that you will have to either versionlock/pin your kernel and/or build ZFS On Linux from source code (not recommended for beginners). 
   To simplify installation a zfs-release package is provided which includes a zfs.repo configuration file and the ZFS on Linux public signing key. All official ZFS on Linux packages are signed using this key, and by default both yum and dnf will verify a package’s signature before allowing it to be installed. Users are strongly encouraged to verify the authenticity of the ZFS on Linux public key using the fingerprint listed here.
.. warning::
   Firstly, note that Fedora Rawhide is not officially supported and things will break if you use it.
   Also that the OpenZFS team is not responsible for any damages caused by using ZFS On Linux and that the latest code on GitHub is not tested and may break your system.

| **Location**: /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
| **Fedora 30 Package**: http://download.zfsonlinux.org/fedora/zfs-release.fc30.noarch.rpm
| **Fedora 31 Package**: http://download.zfsonlinux.org/fedora/zfs-release.fc31.noarch.rpm
| **Fedora 32 Package**: http://download.zfsonlinux.org/fedora/zfs-release.fc32.noarch.rpm
| **Download from**: pgp.mit.edu
| **Fingerprint**: C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

.. code:: sh

   $ sudo dnf install http://download.zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm
   $ gpg --quiet --with-fingerprint /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux
   pub  2048R/F14AB620 2013-03-21 ZFS on Linux <zfs@zfsonlinux.org>
       Key fingerprint = C93A FFFD 9F3F 7B03 C310  CEB6 A9D5 A1C0 F14A B620
       sub  2048R/99685629 2013-03-21

Root on ZFS
-----------
.. toctree::
   :maxdepth: 1
   :glob:

   *


