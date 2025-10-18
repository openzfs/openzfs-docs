..
   CDDL HEADER START

   The contents of this file are subject to the terms of the
   Common Development and Distribution License (the "License").
   You may not use this file except in compliance with the License.

   You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
   or http://www.opensolaris.org/os/licensing.
   See the License for the specific language governing permissions
   and limitations under the License.

   When distributing Covered Code, include this CDDL HEADER in each
   file and include the License file at usr/src/OPENSOLARIS.LICENSE.
   If applicable, add the following below this CDDL HEADER, with the
   fields enclosed by brackets "[]" replaced with your own identifying
   information: Portions Copyright [yyyy] [name of copyright owner]

   CDDL HEADER END

   Portions Copyright 2007 Sun Microsystems, Inc.

.. highlight:: none

Message ID: ZFS-8000-8A
=======================

Corrupted data
--------------

+-------------------------+----------------------------------------------+
| **Type:**               | Error                                        |
+-------------------------+----------------------------------------------+
| **Severity:**           | Critical                                     |
+-------------------------+----------------------------------------------+
| **Description:**        | A file or directory could not be read due to |
|                         | corrupt data.                                |
+-------------------------+----------------------------------------------+
| **Automated Response:** | No automated response will be taken.         |
+-------------------------+----------------------------------------------+
| **Impact:**             | The file or directory is unavailable.        |
+-------------------------+----------------------------------------------+

.. rubric:: Suggested Action for System Administrator

Run ``zpool status -x`` to determine which pool is damaged:

::

   # zpool status -x
     pool: test
    state: ONLINE
   status: One or more devices has experienced an error and no valid replicas
           are available.  Some filesystem data is corrupt, and applications
           may have been affected.
   action: Destroy the pool and restore from backup.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-8A
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  ONLINE       0     0     2
             c0t0d0              ONLINE       0     0     2
             c0t0d1              ONLINE       0     0     0

   errors: 1 data errors, use '-v' for a list

Unfortunately, the data cannot be repaired, and the only choice to
repair the data is to restore the pool from backup.  Applications
attempting to access the corrupted data will get an error (EIO), and
data may be permanently lost.

The list of affected files can be retrieved by using the ``-v`` option to
``zpool status``:

::

   # zpool status -xv
     pool: test
    state: ONLINE
   status: One or more devices has experienced an error and no valid replicas
           are available.  Some filesystem data is corrupt, and applications
           may have been affected.
   action: Destroy the pool and restore from backup.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-8A
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  ONLINE       0     0     2
             c0t0d0              ONLINE       0     0     2
             c0t0d1              ONLINE       0     0     0

   errors: Permanent errors have been detected in the following files:

           /export/example/foo

Damaged files may or may not be able to be removed depending on the
type of corruption.  If the corruption is within the plain data, the
file should be removable.  If the corruption is in the file metadata,
then the file cannot be removed, though it can be moved to an
alternate location.  In either case, the data should be restored from
a backup source.  It is also possible for the corruption to be within
pool-wide metadata, resulting in entire datasets being unavailable.
If this is the case, the only option is to destroy the pool and
re-create the datasets from backup.

.. rubric:: Details

The Message ID: ``ZFS-8000-8A`` indicates corrupted data exists in
the current pool.
