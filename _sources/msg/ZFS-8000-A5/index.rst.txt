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

Message ID: ZFS-8000-A5
=======================

Incompatible version
--------------------

+-------------------------+------------------------------------------------+
| **Type:**               | Error                                          |
+-------------------------+------------------------------------------------+
| **Severity:**           | Major                                          |
+-------------------------+------------------------------------------------+
| **Description:**        | The on-disk version is not compatible with the |
|                         | running system.                                |
+-------------------------+------------------------------------------------+
| **Automated Response:** | No automated response will occur.              |
+-------------------------+------------------------------------------------+
| **Impact:**             | The pool is unavailable.                       |
+-------------------------+------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

If this error is seen during ``zpool import``, see the section below.
Otherwise, run ``zpool status -x`` to determine which pool is faulted:

::

   # zpool status -x
     pool: test
    state: FAULTED
   status: The ZFS version for the pool is incompatible with the software running
           on this system.
   action: Destroy and re-create the pool.
    scrub: none requested
   config:

           NAME                  STATE     READ WRITE CKSUM
           test                  FAULTED      0     0     0  incompatible version
             mirror              ONLINE       0     0     0
               sda9              ONLINE       0     0     0
               sdb9              ONLINE       0     0     0

   errors: No known errors

The pool cannot be used on this system.  Either move the storage to
the system where the pool was originally created, upgrade the current
system software to a more recent version, or destroy the pool and
re-create it from backup.

If this error is seen during import, the pool cannot be imported on
the current system.  The disks must be attached to the system which
originally created the pool, and imported there.

The list of currently supported versions can be displayed using
``zpool upgrade -v``.

.. rubric:: Details

The Message ID: ``ZFS-8000-A5`` indicates a version mismatch exists
between the running system and the on-disk data.
