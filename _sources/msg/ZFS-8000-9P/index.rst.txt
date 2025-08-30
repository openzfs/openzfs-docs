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

Message ID: ZFS-8000-9P
=======================

Failing device in replicated configuration
------------------------------------------

+-------------------------+----------------------------------------------------+
| **Type:**               | Error                                              |
+-------------------------+----------------------------------------------------+
| **Severity:**           | Minor                                              |
+-------------------------+----------------------------------------------------+
| **Description:**        | A device has experienced uncorrectable errors in a |
|                         | replicated configuration.                          |
+-------------------------+----------------------------------------------------+
| **Automated Response:** | ZFS has attempted to repair the affected data.     |
+-------------------------+----------------------------------------------------+
| **Impact:**             | The system is unaffected, though errors may        |
|                         | indicate future failure.  Future errors may cause  |
|                         | ZFS to automatically fault the device.             |
+-------------------------+----------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

Run ``zpool status -x`` to determine which pool has experienced errors:

::

   # zpool status
     pool: test
    state: ONLINE
   status: One or more devices has experienced an unrecoverable error.  An
           attempt was made to correct the error.  Applications are unaffected.
   action: Determine if the device needs to be replaced, and clear the errors
           using 'zpool online' or replace the device with 'zpool replace'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  ONLINE       0     0     0
             mirror              ONLINE       0     0     0
               c0t0d0            ONLINE       0     0     2
               c0t0d1            ONLINE       0     0     0

   errors: No known data errors

Find the device with a non-zero error count for READ, WRITE, or
CKSUM.  This indicates that the device has experienced a read I/O
error, write I/O error, or checksum validation error.  Because the
device is part of a mirror or RAID-Z device, ZFS was able to recover
from the error and subsequently repair the damaged data.

If these errors persist over a period of time, ZFS may determine the
device is faulty and mark it as such.  However, these error counts may
or may not indicate that the device is unusable.  It depends on how
the errors were caused, which the administrator can determine in
advance of any ZFS diagnosis.  For example, the following cases will
all produce errors that do not indicate potential device failure:

-  A network attached device lost connectivity but has now
   recovered
-  A device suffered from a bit flip, an expected event over long
   periods of time
-  An administrator accidentally wrote over a portion of the disk
   using another program

In these cases, the presence of errors does not indicate that the
device is likely to fail in the future, and therefore does not need
to be replaced.  If this is the case, then the device errors should be
cleared using ``zpool clear``:

::

   # zpool clear test c0t0d0

On the other hand, errors may very well indicate that the device has
failed or is about to fail.  If there are continual I/O errors to a
device that is otherwise attached and functioning on the system, it
most likely needs to be replaced.  The administrator should check the
system log for any driver messages that may indicate hardware
failure.  If it is determined that the device needs to be replaced,
then the ``zpool replace`` command should be used:

::

   # zpool replace test c0t0d0 c0t0d2

This will attach the new device to the pool and begin resilvering
data to it.  Once the resilvering process is complete, the old device
will automatically be removed from the pool, at which point it can
safely be removed from the system.  If the device needs to be replaced
in-place (because there are no available spare devices), the original
device can be removed and replaced with a new device, at which point
a different form of ``zpool replace`` can be used:

::

   # zpool replace test c0t0d0

This assumes that the original device at 'c0t0d0' has been replaced
with a new device under the same path, and will be replaced
appropriately.

You can monitor the progress of the resilvering operation by using
the ``zpool status -x`` command:

::

   # zpool status -x
     pool: test
    state: DEGRADED
   status: One or more devices is currently being replaced.  The pool may not be
           providing the necessary level of replication.
   action: Wait for the resilvering operation to complete
    scrub: resilver in progress, 0.14% done, 0h0m to go
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  ONLINE       0     0     0
             mirror              ONLINE       0     0     0
               replacing         ONLINE       0     0     0
                 c0t0d0          ONLINE       0     0     3           
                 c0t0d2          ONLINE       0     0     0  58.5K resilvered
               c0t0d1            ONLINE       0     0     0

   errors: No known data errors

.. rubric:: Details

The Message ID: ``ZFS-8000-9P`` indicates a device has exceeded the
acceptable limit of errors allowed by the system.  See document
`203768 <http://web.archive.org/web/20090409151209/http://sunsolve.sun.com/search/document.do?assetkey=1-61-203768-1&searchclause=203768/>`__
for additional information.
