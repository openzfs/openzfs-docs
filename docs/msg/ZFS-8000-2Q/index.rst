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

Message ID: ZFS-8000-2Q
=======================

Missing device in replicated configuration
------------------------------------------

+-------------------------+--------------------------------------------------+
| **Type:**               | Error                                            |
+-------------------------+--------------------------------------------------+
| **Severity:**           | Major                                            |
+-------------------------+--------------------------------------------------+
| **Description:**        | A device in a replicated configuration could not |
|                         | be opened.                                       |
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
   status: One or more devices could not be opened.  Sufficient replicas exist for
           the pool to continue functioning in a degraded state.
   action: Attach the missing device and online it using 'zpool online'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-2Q
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  DEGRADED     0     0     0
             mirror              DEGRADED     0     0     0
               c0t0d0            ONLINE       0     0     0
               c0t0d1            FAULTED      0     0     0  cannot open

   errors: No known data errors

Determine which device failed to open by looking for a FAULTED device
with an additional 'cannot open' message.  If this device has been
inadvertently removed from the system, attach the device and bring it
online with ``zpool online``:

::

   # zpool online test c0t0d1

If the device is no longer available, the device can be replaced
using the ``zpool replace`` command:

::

   # zpool replace test c0t0d1 c0t0d2

If the device has been replaced by another disk in the same physical
slot, then the device can be replaced using a single argument to the
``zpool replace`` command:

::

   # zpool replace test c0t0d1

Existing data will be resilvered to the new device.  Once the
resilvering completes, the device will be removed from the pool.

.. rubric:: For an exported pool:

If this error is encountered during a ``zpool import``, it means that
one of the devices is not attached to the system:

::

   # zpool import
     pool: test
       id: 10121266328238932306
    state: DEGRADED
   status: One or more devices are missing from the system.
   action: The pool can be imported despite missing or damaged devices.  The
           fault tolerance of the pool may be compromised if imported.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-2Q
   config:

           test              DEGRADED
             mirror          DEGRADED
               c0t0d0        ONLINE
               c0t0d1        FAULTED   cannot open

Unlike when the pool is active on the system, the device cannot be
replaced while the pool is exported.  If the device can be attached to
the system, attach the device and run ``zpool import`` again.

Alternatively, the pool can be imported as-is, though it will be
placed in the DEGRADED state due to a missing device.  The device will
be marked as UNAVAIL. Once the pool has been imported, the missing
device can be replaced as described above.

.. rubric:: Details

The Message ID: ``ZFS-8000-2Q`` indicates a device which was unable
to be opened by the ZFS subsystem.
