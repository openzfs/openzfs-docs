Signing Keys
============

All tagged ZFS on Linux
`releases <https://github.com/zfsonlinux/zfs/releases>`__ are signed by
the official maintainer for that branch. These signatures are
automatically verified by GitHub and can be checked locally by
downloading the maintainers public key.

Maintainers
-----------

Release branch (spl/zfs-\*-release)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Maintainer:** `Ned Bass <https://github.com/nedbass>`__
| **Download:**
  `pgp.mit.edu <http://pgp.mit.edu/pks/lookup?op=vindex&search=0xB97467AAC77B9667&fingerprint=on>`__
| **Key ID:** C77B9667
| **Fingerprint:** 29D5 610E AE29 41E3 55A2 FE8A B974 67AA C77B 9667

| **Maintainer:** `Tony Hutter <https://github.com/tonyhutter>`__
| **Download:**
  `pgp.mit.edu <http://pgp.mit.edu/pks/lookup?op=vindex&search=0x6ad860eed4598027&fingerprint=on>`__
| **Key ID:** D4598027
| **Fingerprint:** 4F3B A9AB 6D1F 8D68 3DC2 DFB5 6AD8 60EE D459 8027

Master branch (master)
~~~~~~~~~~~~~~~~~~~~~~

| **Maintainer:** `Brian Behlendorf <https://github.com/behlendorf>`__
| **Download:**
  `pgp.mit.edu <http://pgp.mit.edu/pks/lookup?op=vindex&search=0x0AB9E991C6AF658B&fingerprint=on>`__
| **Key ID:** C6AF658B
| **Fingerprint:** C33D F142 657E D1F7 C328 A296 0AB9 E991 C6AF 658B

Checking the Signature of a Git Tag
-----------------------------------

First import the public key listed above in to your key ring.

::

   $ gpg --keyserver pgp.mit.edu --recv C6AF658B
   gpg: requesting key C6AF658B from hkp server pgp.mit.edu
   gpg: key C6AF658B: "Brian Behlendorf <behlendorf1@llnl.gov>" not changed
   gpg: Total number processed: 1
   gpg:              unchanged: 1

After the public key is imported the signature of a git tag can be
verified as shown.

::

   $ git tag --verify zfs-0.6.5
   object 7a27ad00ae142b38d4aef8cc0af7a72b4c0e44fe
   type commit
   tag zfs-0.6.5
   tagger Brian Behlendorf <behlendorf1@llnl.gov> 1441996302 -0700

   ZFS Version 0.6.5
   gpg: Signature made Fri 11 Sep 2015 11:31:42 AM PDT using DSA key ID C6AF658B
   gpg: Good signature from "Brian Behlendorf <behlendorf1@llnl.gov>"
   gpg:                 aka "Brian Behlendorf (LLNL) <behlendorf1@llnl.gov>"
