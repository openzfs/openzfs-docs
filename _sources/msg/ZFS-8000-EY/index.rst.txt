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

Message ID: ZFS-8000-EY
=======================

ZFS label hostid mismatch
-------------------------

+-------------------------+---------------------------------------------------+
| **Type:**               | Error                                             |
+-------------------------+---------------------------------------------------+
| **Severity:**           | Major                                             |
+-------------------------+---------------------------------------------------+
| **Description:**        | The ZFS pool was last accessed by another system. |
+-------------------------+---------------------------------------------------+
| **Automated Response:** | No automated response will be taken.              |
+-------------------------+---------------------------------------------------+
| **Impact:**             | ZFS filesystems are not available.                |
+-------------------------+---------------------------------------------------+

.. rubric:: Suggested Action for System Administrator

The pool has been written to from another host, and was not cleanly
exported from the other system.  Actively importing a pool on multiple
systems will corrupt the pool and leave it in an unrecoverable state.
To determine which system last accessed the pool, run the ``zpool
import`` command:

::

   # zpool import
     pool: test
       id: 14702934086626715962
    state: ONLINE
   status: The pool was last accessed by another system.
   action: The pool can be imported using its name or numeric identifier and
           the '-f' flag.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-EY
   config:

           test              ONLINE
             c0t0d0          ONLINE

   # zpool import test
   cannot import 'test': pool may be in use from other system, it was last
   accessed by 'tank' (hostid: 0x1435718c) on Fri Mar  9 15:42:47 2007
   use '-f' to import anyway

If you are certain that the pool is not being actively accessed by
another system, then you can use the ``-f`` option to ``zpool import`` to
forcibly import the pool.

.. rubric:: Details

The Message ID: ``ZFS-8000-EY`` indicates that the pool cannot be
imported as it was last accessed by another system.  Take the
documented action to resolve the problem.
