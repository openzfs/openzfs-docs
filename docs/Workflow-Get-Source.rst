.. raw:: html

   <!--- When this page is updated, please also check the 'Get-the-Source-Code' page -->

Get the Source Code
===================

This document goes over how a developer can get the ZFS source code for
the purpose of making changes to it. For other purposes, please see the
`Get the Source
Code <https://github.com/zfsonlinux/zfs/wiki/Get-the-Source-Code>`__
page.

The Git *master* branch contains the latest version of the software,
including changes that weren't included in the released tarball. This is
the preferred source code location and procedure for ZFS development. If
you would like to do development work for the `ZFS on Linux
Project <https://github.com/zfsonlinux>`__, you can fork the Github
repository and prepare the source by using the following process.

1. Go to the `ZFS on Linux Project <https://github.com/zfsonlinux>`__
   and fork both the ZFS and SPL repositories. This will create two new
   repositories (your *forked* repositories) under your account.
   Detailed instructions can be found at
   `https://help.github.com/articles/fork-a-repo/ <https://help.github.com/articles/fork-a-repo/>`__.
2. Clone both of these repositories onto your development system. This
   will create your *local* repositories. As an example, if your Github
   account is *newzfsdeveloper*, the commands to clone the repositories
   would be:

::

   $ mkdir zfs-on-linux
   $ cd zfs-on-linux
   $ git clone https://github.com/newzfsdeveloper/spl.git
   $ git clone https://github.com/newzfsdeveloper/zfs.git

3. Enter the following commands to make the necessary linkage to the
   *upstream master* repositories and prepare the source to be compiled:

::

   $ cd spl
   $ git remote add upstream https://github.com/zfsonlinux/spl.git
   $ ./autogen.sh
   $ cd ../zfs
   $ git remote add upstream https://github.com/zfsonlinux/zfs.git
   $ ./autogen.sh
   cd ..

The ``./autogen.sh`` script generates the build files. If the build
system is updated by any developer, these scripts need to be run again.
