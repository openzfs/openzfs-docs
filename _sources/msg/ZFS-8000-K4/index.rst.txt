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

Message ID: ZFS-8000-K4
=======================

ZFS intent log read failure
---------------------------

+-------------------------+--------------------------------------------+
| **Type:**               | Error                                      |
+-------------------------+--------------------------------------------+
| **Severity:**           | Major                                      |
+-------------------------+--------------------------------------------+
| **Description:**        | A ZFS intent log device could not be read. |
+-------------------------+--------------------------------------------+
| **Automated Response:** | No automated response will be taken.       |
+-------------------------+--------------------------------------------+
| **Impact:**             | The intent log(s) cannot be replayed.      |
+-------------------------+--------------------------------------------+

.. rubric:: Suggested Action for System Administrator

A ZFS intent log record could not be read due to an error.  This may
be due to a missing or broken log device, or a device within the pool
may be experiencing I/O errors.  The pool itself is not corrupt but is
missing some pool changes that happened shortly before a power loss
or system failure.  These are pool changes that applications had
requested to be written synchronously but had not been committed in
the pool.  This transaction group commit currently occurs every five
seconds, and so typically at most five seconds worth of synchronous
writes have been lost.  ZFS itself cannot determine if the pool
changes lost are critical to those applications running at the time
of the system failure.  This is a decision the administrator must
make.  You may want to consider mirroring log devices.  First determine
which pool is in error:

::

   # zpool status -x
     pool: test
    state: FAULTED
   status: One or more of the intent logs could not be read.
           Waiting for adminstrator intervention to fix the faulted pool.
   action: Either restore the affected device(s) and run 'zpool online',
           or ignore the intent log records by running 'zpool clear'.
    scrub: none requested
   config:

           NAME              STATE     READ WRITE CKSUM
           test              FAULTED      0     0     0  bad intent log
             c3t2d0          ONLINE       0     0     0
           logs              FAULTED      0     0     0  bad intent log
             c5t3d0          UNAVAIL      0     0     0  cannot open

There are two courses of action to resolve this problem.
If the validity of the pool from an application perspective requires
the pool changes then the log devices must be recovered.  Make sure
power and cables are connected and that the affected device is
online.  Then run ``zpool online`` and then ``zpool clear``:

::

   # zpool online test c5t3d0
   # zpool clear test
   # zpool status test
     pool: test
    state: ONLINE
    scrub: none requested
   config:

           NAME              STATE     READ WRITE CKSUM
           test              ONLINE       0     0     0
             c3t2d0          ONLINE       0     0     0
           logs              ONLINE       0     0     0
             c5t3d0          ONLINE       0     0     0

   errors: No known data errors

The second alternative action is to ignore the most recent pool
changes that could not be read.  To do this run ``zpool clear``:

::

   # zpool clear test
   # zpool status test
     pool: test
    state: DEGRADED
   status: One or more devices could not be opened.  Sufficient replicas exist for
           the pool to continue functioning in a degraded state.
   action: Attach the missing device and online it using 'zpool online'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-2Q
    scrub: none requested
   config:

           NAME              STATE     READ WRITE CKSUM
           test              DEGRADED     0     0     0
             c3t2d0          ONLINE       0     0     0
           logs              DEGRADED     0     0     0
             c5t3d0          UNAVAIL      0     0     0  cannot open

   errors: No known data errors

Future log records will not use a failed log device but will be
written to the main pool.  You should fix or replace any failed log
devices.

.. rubric:: Details

The Message ID: ``ZFS-8000-K4`` indicates that a log device is
missing or cannot be read.
