Troubleshooting
===============

.. todo::
   This page is a draft.

This page contains tips for troubleshooting ZFS on Linux and what info
developers might want for bug triage.

-  `About Log Files <#about-log-files>`__

   -  `Generic Kernel Log <#generic-kernel-log>`__
   -  `ZFS Kernel Module Debug
      Messages <#zfs-kernel-module-debug-messages>`__

-  `Unkillable Process <#unkillable-process>`__
-  `ZFS Events <#zfs-events>`__

--------------

About Log Files
---------------

Log files can be very useful for troubleshooting. In some cases,
interesting information is stored in multiple log files that are
correlated to system events.

Pro tip: logging infrastructure tools like *elasticsearch*, *fluentd*,
*influxdb*, or *splunk* can simplify log analysis and event correlation.

Generic Kernel Log
~~~~~~~~~~~~~~~~~~

Typically, Linux kernel log messages are available from ``dmesg -T``,
``/var/log/syslog``, or where kernel log messages are sent (eg by
``rsyslogd``).

ZFS Kernel Module Debug Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ZFS kernel modules use an internal log buffer for detailed logging
information. This log information is available in the pseudo file
``/proc/spl/kstat/zfs/dbgmsg`` for ZFS builds where ZFS module parameter
`zfs_dbgmsg_enable =
1 <https://github.com/zfsonlinux/zfs/wiki/ZFS-on-Linux-Module-Parameters#zfs_dbgmsg_enable>`__

--------------

Unkillable Process
------------------

Symptom: ``zfs`` or ``zpool`` command appear hung, does not return, and
is not killable

Likely cause: kernel thread hung or panic

Log files of interest: `Generic Kernel Log <#generic-kernel-log>`__,
`ZFS Kernel Module Debug Messages <#zfs-kernel-module-debug-messages>`__

Important information: if a kernel thread is stuck, then a backtrace of
the stuck thread can be in the logs. In some cases, the stuck thread is
not logged until the deadman timer expires. See also `debug
tunables <https://github.com/zfsonlinux/zfs/wiki/ZFS-on-Linux-Module-Parameters#debug>`__

--------------

ZFS Events
----------

ZFS uses an event-based messaging interface for communication of
important events to other consumers running on the system. The ZFS Event
Daemon (zed) is a userland daemon that listens for these events and
processes them. zed is extensible so you can write shell scripts or
other programs that subscribe to events and take action. For example,
the script usually installed at ``/etc/zfs/zed.d/all-syslog.sh`` writes
a formatted event message to ``syslog``. See the man page for ``zed(8)``
for more information.

A history of events is also available via the ``zpool events`` command.
This history begins at ZFS kernel module load and includes events from
any pool. These events are stored in RAM and limited in count to a value
determined by the kernel tunable
`zfs_event_len_max <https://github.com/zfsonlinux/zfs/wiki/ZFS-on-Linux-Module-Parameters#zfs_zevent_len_max>`__.
``zed`` has an internal throttling mechanism to prevent overconsumption
of system resources processing ZFS events.

More detailed information about events is observable using
``zpool events -v`` The contents of the verbose events is subject to
change, based on the event and information available at the time of the
event.

Each event has a class identifier used for filtering event types.
Commonly seen events are those related to pool management with class
``sysevent.fs.zfs.*`` including import, export, configuration updates,
and ``zpool history`` updates.

Events related to errors are reported as class ``ereport.*`` These can
be invaluable for troubleshooting. Some faults can cause multiple
ereports as various layers of the software deal with the fault. For
example, on a simple pool without parity protection, a faulty disk could
cause an ``ereport.io`` during a read from the disk that results in an
``erport.fs.zfs.checksum`` at the pool level. These events are also
reflected by the error counters observed in ``zpool status`` If you see
checksum or read/write errors in ``zpool status`` then there should be
one or more corresponding ereports in the ``zpool events`` output.
