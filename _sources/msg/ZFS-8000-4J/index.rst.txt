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

Message ID: ZFS-8000-4J
=======================

Corrupted device label in a replicated configuration
----------------------------------------------------

+-------------------------+--------------------------------------------------+
| **Type:**               | Error                                            |
+-------------------------+--------------------------------------------------+
| **Severity:**           | Major                                            |
+-------------------------+--------------------------------------------------+
| **Description:**        | A device could not be opened due to a missing or |
|                         | invalid device label.                            |
+-------------------------+--------------------------------------------------+
| **Automated Response:** | A hot spare will be activated if available.      |
+-------------------------+--------------------------------------------------+
| **Impact:**             | The pool is no longer providing the configured   |
|                         | level of replication.                            |
+-------------------------+--------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

.. rubric:: For an active pool:

If this error was encountered while running ``zpool import``, please
see the section below.  Otherwise, run ``zpool status -x`` to determine
which pool has experienced a failure:

::

   # zpool status -x
     pool: test
    state: DEGRADED
   status: One or more devices could not be used because the label is missing or
           invalid.  Sufficient replicas exist for the pool to continue
           functioning in a degraded state.
   action: Replace the device using 'zpool replace'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  DEGRADED     0     0     0
             mirror              DEGRADED     0     0     0
               c0t0d0            ONLINE       0     0     0
               c0t0d1            FAULTED      0     0     0  corrupted data

   errors: No known data errors

If the device has been temporarily detached from the system, attach
the device to the system and run ``zpool status`` again.  The pool
should automatically detect the newly attached device and resume
functioning.

If the device is no longer available, it can be replaced using ``zpool 
replace``:

::

   # zpool replace test c0t0d1 c0t0d2

If the device has been replaced by another disk in the same physical
slot, then the device can be replaced using a single argument to the
``zpool replace`` command:

::

   # zpool replace test c0t0d1

ZFS will begin migrating data to the new device as soon as the
replace is issued.  Once the resilvering completes, the original
device (if different from the replacement) will be removed, and the
pool will be restored to the ONLINE state.

.. rubric:: For an exported pool:

If this error is encountered while running ``zpool import``, the pool
can be still be imported despite the failure:

::

   # zpool import
     pool: test
       id: 5187963178597328409
    state: DEGRADED
   status: One or more devices contains corrupted data.  The fault tolerance of
           the pool may be compromised if imported.
   action: The pool can be imported using its name or numeric identifier.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
   config:

           test              DEGRADED
             mirror          DEGRADED
               c0t0d0        ONLINE
               c0t0d1        FAULTED   corrupted data

To import the pool, run ``zpool import``:

::

   # zpool import test

Once the pool has been imported, the damaged device can be replaced
according to the above procedure.

.. rubric:: Details

The Message ID: ``ZFS-8000-4J`` indicates a device which was unable
to be opened by the ZFS subsystem.
