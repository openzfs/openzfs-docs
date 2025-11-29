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

Message ID: ZFS-8000-3C
=======================

Missing device in non-replicated configuration
----------------------------------------------

+-------------------------+--------------------------------------------------+
| **Type:**               | Error                                            |
+-------------------------+--------------------------------------------------+
| **Severity:**           | Critical                                         |
+-------------------------+--------------------------------------------------+
| **Description:**        | A device could not be opened and no replicas are |
|                         | available.                                       |
+-------------------------+--------------------------------------------------+
| **Automated Response:** | No automated response will be taken.             |
+-------------------------+--------------------------------------------------+
| **Impact:**             | The pool is no longer available.                 |
+-------------------------+--------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

.. rubric:: For an active pool:

If this error was encountered while running ``zpool import``, please
see the section below.  Otherwise, run ``zpool status -x`` to determine
which pool has experienced a failure:

::

   # zpool status -x
     pool: test
    state: FAULTED
   status: One or more devices could not be opened.  There are insufficient
           replicas for the pool to continue functioning.
   action: Attach the missing device and online it using 'zpool online'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-3C
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  FAULTED      0     0     0  insufficient replicas
             c0t0d0              ONLINE       0     0     0
             c0t0d1              FAULTED      0     0     0  cannot open

   errors: No known data errors

If the device has been temporarily detached from the system, attach
the device to the system and run ``zpool status`` again.  The pool
should automatically detect the newly attached device and resume
functioning.  You may have to mount the filesystems in the pool
explicitly using ``zfs mount -a``.

If the device is no longer available and cannot be reattached to the
system, then the pool must be destroyed and re-created from a backup
source.

.. rubric:: For an exported pool:

If this error is encountered during a ``zpool import``, it means that
one of the devices is not attached to the system:

::

   # zpool import
     pool: test
       id: 10121266328238932306
    state: FAULTED
   status: One or more devices are missing from the system.
   action: The pool cannot be imported.  Attach the missing devices and try again.
           see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-3C
   config:

           test              FAULTED   insufficient replicas
             c0t0d0          ONLINE
             c0t0d1          FAULTED   cannot open

The pool cannot be imported until the missing device is attached to
the system.  If the device has been made available in an alternate
location, use the ``-d`` option to ``zpool import`` to search for devices
in a different directory.  If the missing device is unavailable, then
the pool cannot be imported.

.. rubric:: Details

The Message ID: ``ZFS-8000-3C`` indicates a device which was unable
to be opened by the ZFS subsystem.
