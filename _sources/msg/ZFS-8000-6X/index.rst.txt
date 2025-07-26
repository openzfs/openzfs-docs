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

Message ID: ZFS-8000-6X
=======================

Missing top level device
------------------------

+-------------------------+--------------------------------------------+
| **Type:**               | Error                                      |
+-------------------------+--------------------------------------------+
| **Severity:**           | Critical                                   |
+-------------------------+--------------------------------------------+
| **Description:**        | One or more top level devices are missing. |
+-------------------------+--------------------------------------------+
| **Automated Response:** | No automated response will be taken.       |
+-------------------------+--------------------------------------------+
| **Impact:**             | The pool cannot be imported.               |
+-------------------------+--------------------------------------------+

.. rubric:: Suggested Action for System Administrator

Run ``zpool import`` to list which pool cannot be imported:

::

   # zpool import
     pool: test
       id: 13783646421373024673
    state: FAULTED
   status: One or more devices are missing from the system.
   action: The pool cannot be imported.  Attach the missing devices and try again.
      see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-6X
   config:

           test              FAULTED   missing device
             c0t0d0          ONLINE

   Additional devices are known to be part of this pool, though their
   exact configuration cannot be determined.

ZFS attempts to store enough configuration data on the devices such
that the configuration is recoverable from any subset of devices.  In
some cases, particularly when an entire toplevel virtual device is
not attached to the system, ZFS will be unable to determine the
complete configuration.  It will always detect that these devices are
missing, even if it cannot identify all of the devices.

The pool cannot be imported until the unknown missing device is
attached to the system. If the device has been made available in an
alternate location, use the ``-d`` option to ``zpool import`` to search
for devices in a different directory.  If the missing device is
unavailable, then the pool cannot be imported.

.. rubric:: Details

The Message ID: ``ZFS-8000-6X`` indicates one or more top level
devices are missing from the configuration.
