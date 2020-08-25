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

Message ID: ZFS-8000-72
=======================

Corrupted pool metadata
-----------------------

+-------------------------+-------------------------------------------+
| **Type:**               | Error                                     |
+-------------------------+-------------------------------------------+
| **Severity:**           | Critical                                  |
+-------------------------+-------------------------------------------+
| **Description:**        | The metadata required to open the pool is |
|                         | corrupt.                                  |
+-------------------------+-------------------------------------------+
| **Automated Response:** | No automated response will be taken.      |
+-------------------------+-------------------------------------------+
| **Impact:**             | The pool is no longer available.          |
+-------------------------+-------------------------------------------+

.. rubric:: Suggested Action for System Administrator

Even though all the devices are available, the on-disk data has been
corrupted such that the pool cannot be opened.  If a recovery action
is presented, the pool can be returned to a usable state.  Otherwise,
all data within the pool is lost, and the pool must be destroyed and
restored from an appropriate backup source.  ZFS includes built-in
metadata replication to prevent this from happening even for
unreplicated pools, but running in a replicated configuration will
decrease the chances of this happening in the future.

If this error is encountered during ``zpool import``, see the section
below.  Otherwise, run ``zpool status -x`` to determine which pool is
faulted and if a recovery option is available:

::

   # zpool status -x
     pool: test
       id: 13783646421373024673
    state: FAULTED
   status: The pool metadata is corrupted and cannot be opened.
   action: Recovery is possible, but will result in some data loss.
           Returning the pool to its state as of Mon Sep 28 10:24:39 2009
           should correct the problem.  Approximately 59 seconds of data
           will have to be discarded, irreversibly.  Recovery can be
           attempted by executing 'zpool clear -F test'.  A scrub of the pool
           is strongly recommended following a successful recovery.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-72
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  FAULTED      0     0     2  corrupted data
               c0t0d0            ONLINE       0     0     2
               c0t0d1            ONLINE       0     0     2

If recovery is unavailable, the recommended action will be:

::

   action: Destroy the pool and restore from backup.

If this error is encountered during ``zpool import``, and if no recovery option
is mentioned, the pool is unrecoverable and cannot be imported.  The pool must
be restored from an appropriate backup source.  If a recovery option is
available, the output from ``zpool import`` will look something like the
following:

::

   # zpool import share
   cannot import 'share': I/O error
           Recovery is possible, but will result in some data loss.
           Returning the pool to its state as of Sun Sep 27 12:31:07 2009
           should correct the problem.  Approximately 53 seconds of data
           will have to be discarded, irreversibly.  Recovery can be
           attempted by executing 'zpool import -F share'.  A scrub of the pool
           is strongly recommended following a successful recovery.

Recovery actions are requested with the -F option to either ``zpool
clear`` or ``zpool import``.  Recovery will result in some data loss,
because it reverts the pool to an earlier state.  A dry-run recovery
check can be performed by adding the ``-n`` option, affirming if recovery
is possible without actually reverting the pool to its earlier state.

.. rubric:: Details

The Message ID: ``ZFS-8000-72`` indicates a pool was unable to be
opened due to a detected corruption in the pool metadata.
