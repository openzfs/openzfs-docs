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

Message ID: ZFS-8000-5E
=======================

Corrupted device label in non-replicated configuration
------------------------------------------------------

+-------------------------+--------------------------------------------------+
| **Type:**               | Error                                            |
+-------------------------+--------------------------------------------------+
| **Severity:**           | Critical                                         |
+-------------------------+--------------------------------------------------+
| **Description:**        | A device could not be opened due to a missing or |
|                         | invalid device label and no replicas are         |
|                         | available.                                       |
+-------------------------+--------------------------------------------------+
| **Automated Response:** | No automated response will be taken.             |
+-------------------------+--------------------------------------------------+
| **Impact:**             | The pool is no longer available.                 |
+-------------------------+--------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

.. rubric:: For an active pool:

If this error was encountered while running ``zpool import``, please see the
section below.  Otherwise, run ``zpool status -x`` to determine which pool has
experienced a failure:

::

   # zpool status -x
     pool: test
    state: FAULTED
   status: One or more devices could not be used because the the label is missing
           or invalid.  There are insufficient replicas for the pool to continue
           functioning.
   action: Destroy and re-create the pool from a backup source.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-5E
    scrub: none requested
   config:

           NAME        STATE     READ WRITE CKSUM
           test        FAULTED      0     0     0  insufficient replicas
             c0t0d0    FAULTED      0     0     0  corrupted data
             c0t0d1    ONLINE       0     0     0

   errors: No known data errors

The device listed as FAULTED with 'corrupted data' cannot be opened due to a
corrupt label.  ZFS will be unable to use the pool, and all data within the
pool is irrevocably lost.  The pool must be destroyed and recreated from an
appropriate backup source.  Using replicated configurations will prevent this
from happening in the future.

.. rubric:: For an exported pool:

If this error is encountered during ``zpool import``, the action is the same.
The pool cannot be imported - all data is lost and must be restored from an
appropriate backup source.

.. rubric:: Details

The Message ID: ``ZFS-8000-5E`` indicates a device which was unable to be
opened by the ZFS subsystem.
