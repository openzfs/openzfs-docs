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

Message ID: ZFS-8000-JQ
=======================

ZFS pool I/O failures
---------------------

+-------------------------+----------------------------------------+
| **Type:**               | Error                                  |
+-------------------------+----------------------------------------+
| **Severity:**           | Major                                  |
+-------------------------+----------------------------------------+
| **Description:**        | The ZFS pool has experienced currently |
|                         | unrecoverable I/O failures.            |
+-------------------------+----------------------------------------+
| **Automated Response:** | No automated response will be taken.   |
+-------------------------+----------------------------------------+
| **Impact:**             | Write I/Os cannot be serviced.         |
+-------------------------+----------------------------------------+

.. rubric:: Suggested Action for System Administrator

The pool has experienced I/O failures.  Since the ZFS pool property
``failmode`` is set to 'continue', read I/Os will continue to be
serviced, but write I/Os are blocked.  See the zpoolprops(8) manpage for
more information on the ``failmode`` property.  Manual intervention is
required for write I/Os to be serviced.  You can see which devices are
affected by running ``zpool status -x``:

::

   # zpool status -x
     pool: test
    state: FAULTED
   status: There are I/O failures.
   action: Make sure the affected devices are connected, then run 'zpool clear'.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-HC
    scrub: none requested
   config:

           NAME        STATE     READ WRITE CKSUM
           test        FAULTED      0    13     0  insufficient replicas
             sda9      FAULTED      0     7     0  experienced I/O failures
             sdb9      ONLINE       0     0     0

   errors: 1 data errors, use '-v' for a list

After you have made sure the affected devices are connected, run
``zpool clear`` to allow write I/O to the pool again:

::

   # zpool clear test

If I/O failures continue to happen, then applications and commands
for the pool may hang.  At this point, a reboot may be necessary to
allow I/O to the pool again.

.. rubric:: Details

The Message ID: ``ZFS-8000-JQ`` indicates that the pool has
experienced I/O failures.  Take the documented action to resolve the
problem.
