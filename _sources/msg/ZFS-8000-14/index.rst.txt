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

Message ID: ZFS-8000-14
=======================

Corrupt ZFS cache
-----------------

+-------------------------+--------------------------------------+
| **Type:**               | Error                                |
+-------------------------+--------------------------------------+
| **Severity:**           | Critical                             |
+-------------------------+--------------------------------------+
| **Description:**        | The ZFS cache file is corrupted.     |
+-------------------------+--------------------------------------+
| **Automated Response:** | No automated response will be taken. |
+-------------------------+--------------------------------------+
| **Impact:**             | ZFS filesystems are not available.   |
+-------------------------+--------------------------------------+

.. rubric:: Suggested Action for System Administrator

ZFS keeps a list of active pools on the filesystem to avoid having to
scan all devices when the system is booted.  If this file is corrupted,
then normally active pools will not be automatically opened.  The pools
can be recovered using the ``zpool import`` command:

::

   # zpool import
     pool: test
       id: 12743384782310107047
    state: ONLINE
   action: The pool can be imported using its name or numeric identifier.
   config:

           test              ONLINE
             sda9            ONLINE

This will automatically scan ``/dev`` for any devices part of a pool.
If devices have been made available in an alternate location, use the
``-d`` option to ``zpool import`` to search for devices in a different
directory.

Once you have determined which pools are available for import, you
can import the pool explicitly by specifying the name or numeric
identifier:

::

   # zpool import test

Alternately, you can import all available pools by specifying the ``-a``
option.  Once a pool has been imported, the ZFS cache will be repaired
so that the pool will appear normally in the future.

.. rubric:: Details

The Message ID: ``ZFS-8000-14`` indicates a corrupted ZFS cache file.
Take the documented action to resolve the problem.
