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

Message ID: ZFS-8000-ER
=======================

ZFS Errata #1
-------------

+-------------------------+--------------------------------------------------+
| **Type:**               | Compatibility                                    |
+-------------------------+--------------------------------------------------+
| **Severity:**           | Moderate                                         |
+-------------------------+--------------------------------------------------+
| **Description:**        | The ZFS pool contains an on-disk format          |
|                         | incompatibility.                                 |
+-------------------------+--------------------------------------------------+
| **Automated Response:** | No automated response will be taken.             |
+-------------------------+--------------------------------------------------+
| **Impact:**             | Until the pool is scrubbed using OpenZFS version |
|                         | 0.6.3 or newer the pool may not be imported by   |
|                         | older versions of OpenZFS or other ZFS           |
|                         | implementations.                                 |
+-------------------------+--------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

The pool contains an on-disk format incompatibility.  Affected pools
must be imported and scrubbed using the current version of ZFS.  This
will return the pool to a state in which it may be imported by other
implementations.  This errata only impacts compatibility between ZFS
versions, no user data is at risk as result of this erratum.

::

   # zpool status -x
     pool: test
    state: ONLINE
   status: Errata #1 detected.
   action: To correct the issue run 'zpool scrub'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
     scan: none requested
   config:

       NAME            STATE     READ WRITE CKSUM
       test            ONLINE    0    0     0
         raidz1-0      ONLINE    0    0     0
           vdev0       ONLINE    0    0     0
           vdev1       ONLINE    0    0     0
           vdev2       ONLINE    0    0     0
           vdev3       ONLINE    0    0     0

   errors: No known data errors

   # zpool scrub test

   # zpool status -x
   all pools are healthy


ZFS Errata #2
-------------

+-------------------------+---------------------------------------------------+
| **Type:**               | Compatibility                                     |
+-------------------------+---------------------------------------------------+
| **Severity:**           | Moderate                                          |
+-------------------------+---------------------------------------------------+
| **Description:**        | The ZFS packages were updated while an            |
|                         | asynchronous destroy was in progress and the pool |
|                         | contains an on-disk format incompatibility.       |
+-------------------------+---------------------------------------------------+
| **Automated Response:** | No automated response will be taken.              |
+-------------------------+---------------------------------------------------+
| **Impact:**             | The pool cannot be imported until the issue is    |
|                         | corrected.                                        |
+-------------------------+---------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

Affected pools must be reverted to the previous ZFS version where
they can be correctly imported.  Once imported, all asynchronous
destroy operations must be allowed to complete.  The ZFS packages may
then be updated and the pool can be imported cleanly by the newer
software.

::

   # zpool import
     pool: test
       id: 1165955789558693437
    state: ONLINE
   status: Errata #2 detected.
   action: The pool cannot be imported with this version of ZFS due to
           an active asynchronous destroy.  Revert to an earlier version
           and allow the destroy to complete before updating.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
   config:

       test           ONLINE
         raidz1-0     ONLINE
           vdev0      ONLINE
           vdev1      ONLINE
           vdev2      ONLINE
           vdev3      ONLINE

Revert to previous ZFS version, import the pool, then wait for the
``freeing`` property to drop to zero. This indicates that all
outstanding asynchronous destroys have completed.

::

   # zpool get freeing
   NAME  PROPERTY  VALUE    SOURCE
   test  freeing   0        default

The ZFS packages may be now be updated and the pool imported.  The
on-disk format incompatibility can now be corrected online as
described in `Errata #1 <#1>`__.


ZFS Errata #3
-------------

+-------------------------+----------------------------------------------------+
| **Type:**               | Compatibility                                      |
+-------------------------+----------------------------------------------------+
| **Severity:**           | Moderate                                           |
+-------------------------+----------------------------------------------------+
| **Description:**        | An encrypted dataset contains an on-disk format    |
|                         | incompatibility.                                   |
+-------------------------+----------------------------------------------------+
| **Automated Response:** | No automated response will be taken.               |
+-------------------------+----------------------------------------------------+
| **Impact:**             | Encrypted datasets created before the ZFS packages |
|                         | were updated cannot be mounted or opened for       |
|                         | write.  The errata impacts the ability of ZFS to   |
|                         | correctly perform raw sends, so this functionality |
|                         | has been disabled for these datasets.              |
+-------------------------+----------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

System administrators with affected pools will need to recreate any
encrypted datasets created before the new version of ZFS was used.
This can be accomplished by using ``zfs send`` and ``zfs receive``.
Note, however, that backups can NOT be done with a raw ``zfs send -w``,
since this would preserve the on-disk incompatibility.
Alternatively, system administrators can use conventional tools to
back up data to new encrypted datasets.  The new version of ZFS will
prevent new data from being written to the impacted datasets, but
they can still be mounted read-only.

::

   # zpool status
     pool: test
       id: 1165955789558693437
    state: ONLINE
   status: Errata #3 detected.
   action: To correct the issue backup existing encrypted datasets to new
           encrypted datasets and destroy the old ones.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
   config:

       test           ONLINE
         raidz1-0     ONLINE
           vdev0      ONLINE
           vdev1      ONLINE
           vdev2      ONLINE
           vdev3      ONLINE

Import the pool and backup any existing encrypted datasets to new
datasets.  To ensure the new datasets are re-encrypted, be sure to
receive them below an encryption root or use ``zfs receive -o
encryption=on``, then destroy the source dataset.

::

   # zfs send test/crypt1@snap1 | zfs receive -o encryption=on -o keyformat=passphrase -o keylocation=file:///path/to/keyfile test/newcrypt1
   # zfs send -I test/crypt1@snap1 test/crypt1@snap5 | zfs receive test/newcrypt1
   # zfs destroy -R test/crypt1

New datasets can be mounted read-write and used normally.  The errata
will be cleared upon reimporting the pool and the alert will only be
shown again if another dataset is found with the errata.  To ensure
that all datasets are on the new version reimport the pool, load all
keys, mount all encrypted datasets, and check ``zpool status``.

::

   # zpool export test
   # zpool import test
   # zfs load-key -a
   Enter passphrase for 'test/crypt1':
   1 / 1 key(s) successfully loaded
   # zfs mount -a
   # zpool status -x
   all pools are healthy


ZFS Errata #4
-------------

+-------------------------+----------------------------------------------------+
| **Type:**               | Compatibility                                      |
+-------------------------+----------------------------------------------------+
| **Severity:**           | Moderate                                           |
+-------------------------+----------------------------------------------------+
| **Description:**        | An encrypted dataset contains an on-disk format    |
|                         | incompatibility.                                   |
+-------------------------+----------------------------------------------------+
| **Automated Response:** | No automated response will be taken.               |
+-------------------------+----------------------------------------------------+
| **Impact:**             | Encrypted datasets created before the ZFS packages |
|                         | were updated cannot be backed up via a raw send to |
|                         | an updated system.  These datasets also cannot     |
|                         | receive additional snapshots.  New encrypted       |
|                         | datasets cannot be created until the               |
|                         | ``bookmark_v2`` feature has been enabled.          |
+-------------------------+----------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

First, system administrators with affected pools will need to enable
the ``bookmark_v2`` feature on their pools.  Enabling this feature
will prevent this pool from being imported by previous versions of
the ZFS software after any new bookmarks are created (including
read-only imports).  If the pool contains no encrypted datasets, this
is the only step required.  If there are existing encrypted datasets,
administrators will then need to back these datasets up.  This can be
done in several ways.  Non-raw ``zfs send`` and ``zfs receive`` can be
used as per usual, as can traditional backup tools.  Raw receives of
existing encrypted datasets and raw receives into existing encrypted
datasets are currently disabled because ZFS is not able to guarantee
that the stream and the existing dataset came from a consistent
source.  This check can be disabled which will allow ZFS to receive
these streams anyway.  Note that this can result in datasets with data
that cannot be accessed due to authentication errors if raw and
non-raw receives are mixed over the course of several incremental
backups.  To disable this restriction, set the
``zfs_disable_ivset_guid_check`` module parameter to 1.  Streams
received this way (as well as any received before the upgrade) will
need to be manually checked by reading the data to ensure they are
not corrupted.  Note that ``zpool scrub`` cannot be used for this
purpose because the scrub does not check the cryptographic
authentication codes.  For more information on this issue, please
refer to the zfs man page section on ``zfs receive`` which describes
the restrictions on raw sends.

::

   # zpool status
     pool: test
    state: ONLINE
   status: Errata #4 detected.
           Existing encrypted datasets contain an on-disk incompatibility
           which needs to be corrected.
   action: To correct the issue enable the bookmark_v2 feature and backup
           any existing encrypted datasets to new encrypted datasets and
           destroy the old ones. If this pool does not contain any
           encrypted datasets, simply enable the bookmark_v2 feature.
      see: http://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
     scan: none requested
   config:

           NAME           STATE     READ WRITE CKSUM
           test           ONLINE       0     0     0
             /root/vdev0  ONLINE       0     0     0

   errors: No known data errors

Import the pool and enable the ``bookmark_v2`` feature.  Then backup
any existing encrypted datasets to new datasets.  This can be done
with traditional tools or via ``zfs send``.  Raw sends will require
that the ``zfs_disable_ivset_guid_check`` is set to 1 on the receive
side.  Once this is done, the original datasets should be destroyed.

::

   # zpool set feature@bookmark_v2=enabled test
   # echo 1 > /sys/module/zfs/parameters/zfs_disable_ivset_guid_check
   # zfs send -Rw test/crypt1@snap1 | zfs receive test/newcrypt1
   # zfs send -I test/crypt1@snap1 test/crypt1@snap5 | zfs receive test/newcrypt1
   # zfs destroy -R test/crypt1
   # echo 0 > /sys/module/zfs/parameters/zfs_disable_ivset_guid_check

The errata will be cleared upon reimporting the pool and the alert
will only be shown again if another dataset is found with the errata.
To check that all datasets are fixed, perform a ``zfs list -t all``,
and check ``zpool status`` once it is completed.

::

   # zpool export test
   # zpool import test
   # zpool scrub # wait for completion
   # zpool status -x
   all pools are healthy
