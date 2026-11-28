Troubleshooting
===============

Where to look when a pool misbehaves, how to read what ZFS tells you, and what
to collect before filing a bug.

First look
~~~~~~~~~~

.. code:: bash

   zpool status -v                 # health, and the list of damaged files
   zpool status -x                 # only pools with problems
   zpool status -es                # unhealthy vdevs only, with slow-I/O counts
   zpool events -v                 # the event history, most detail
   dmesg -T | grep -i zfs          # kernel-level errors
   zfs version

``zpool status -x`` printing ``all pools are healthy`` rules out most of what
follows.

Reading ``zpool status``
~~~~~~~~~~~~~~~~~~~~~~~~

Pool health is one of three states: **ONLINE** (everything normal),
**DEGRADED** (a device failed but redundancy is covering it), or **FAULTED**
(corrupted metadata, or too few replicas left to function).

Individual vdevs report more detail:

``ONLINE``
    Working.
``DEGRADED``
    Checksum errors, slow I/Os, or I/O errors exceed acceptable levels. ZFS
    keeps using the device, flagging that something may be wrong.
``FAULTED``
    The device opened but its contents did not match expectations, or its
    error count is high enough that ZFS stopped using it.
``OFFLINE``
    Taken offline deliberately with ``zpool offline``.
``REMOVED``
    Physically pulled while running. Detection is hardware-dependent.
``UNAVAIL``
    Could not be opened at all. If the pool was imported while the device was
    missing, it shows a GUID rather than a path — the path was never valid.

The three counter columns mean different things, and the distinction matters:

``READ`` / ``WRITE``
    I/O errors reported by the device itself.
``CKSUM``
    The device returned data that failed its checksum — silent corruption.

A damaged block that ZFS could reconstruct is charged to the disk that held the
bad copy. A block it could **not** reconstruct — three damaged disks in a
raidz2, say — cannot be attributed, so the checksum error is reported against
*every* disk holding that block. A row of disks all showing CKSUM errors is
therefore usually one unrecoverable block, not simultaneous failure of the
whole row.

Non-zero CKSUM on a disk that reports no I/O errors more often indicates
cabling, an HBA, or memory than the disk.

``zpool clear pool`` resets the counters. It does not repair anything — fix
the cause first, then clear, then watch whether the counters come back.

Permanent errors
~~~~~~~~~~~~~~~~

``zpool status -v`` lists files with unrepairable errors. That data is gone:
restore those files from a backup or a snapshot. If the listing shows a hex
object number instead of a path, the file has already been deleted, or the
dataset is not mounted.

Entries persist until a scrub confirms they are gone, so run a scrub after
restoring. See
:doc:`Scrub and Resilver </Basic Concepts/Operations/Scrub and Resilver>`.

Errors in metadata rather than a file, or the ``<metadata>`` marker, are more
serious — that is the case redundancy exists for, and without it the pool may
not be fully recoverable.

A pool that will not import
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Work up this ladder, least destructive first. **The options marked below
destroy data** — read the next section before using any of them.

.. code:: bash

   zpool import                              # what is visible at all
   zpool import -d /dev/disk/by-id           # scan a specific path
   zpool import -o readonly=on -N pool       # look without changing anything
   zpool import -f pool                      # last used by another system
   zpool import -m pool                      # LOSES DATA: discards a missing log
   zpool import -F -n pool                   # dry run: is rewind possible?
   zpool import -F pool                      # LOSES DATA: discards transactions
   zpool import -FX pool                     # LOSES MORE DATA: extended rewind

``zpool import`` with no arguments and ``-d`` are safe — they only scan.
``-f`` overrides the "pool was last used by another system" guard; it does
not itself discard anything, but importing a pool that is genuinely still
active on another host will corrupt it.

``-o readonly=on -N`` is the right first move on a pool you care about: it
imports without mounting and without writing, so you can look before deciding.

What each destructive option actually costs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``-m`` — **discards the intent log.**
    This is data loss, and it is easy to miss because the flag reads like a
    convenience. A missing or dead SLOG holds synchronous writes that were
    acknowledged to applications but not yet written to the pool. Importing
    with ``-m`` throws them away: the pool comes up consistent, but recent
    transactions the application was told were durable are gone. For a
    database or an NFS server that is silent corruption at the application
    level, not at the ZFS level — ZFS will report the pool as healthy.

    Before reaching for ``-m``, try to make the log device readable again.
    This is also the argument for mirroring a SLOG.

``-F`` — **discards the last few transaction groups.**
    Rewinds the pool to an earlier consistent state. Everything written after
    that point is irretrievably lost, and not every damaged pool can be
    recovered this way. Always run ``-F -n`` first: it reports whether the
    rewind would succeed without performing it.

``-X`` — **extended rewind.**
    Searches further back in time, so it can lose correspondingly more. Use
    only after ``-F`` has failed.

If the pool has a checkpoint, ``zpool import --rewind-to-checkpoint`` is a
cleaner and better-defined undo than ``-F``, because you chose the point it
returns to. Note that it too is irreversible once imported without
``readonly``.

See
:doc:`Changing Pool Layout </Basic Concepts/Pool Structure/Changing Pool Layout>`
for checkpoints.

A pool that was **destroyed** is not immediately gone. ``zpool import -D``
lists destroyed pools, and importing with ``-D`` brings one back, as long as
its devices have not been reused:

.. code:: bash

   zpool import -D                 # what can still be recovered
   zpool import -D pool

Importing somewhere unusual — a rescue environment, or a pool whose mount
points would collide with the running system — is what ``-R`` is for. It sets
``altroot``, so every mount point is prefixed, and ``cachefile=none`` so the
import is not remembered:

.. code:: bash

   zpool import -R /mnt -N pool

Device names that changed between boots are a common cause of a pool that
"disappeared" — import with ``-d /dev/disk/by-id`` and see the
:doc:`FAQ </Project and Community/FAQ>` on selecting ``/dev/`` names.

A suspended pool
~~~~~~~~~~~~~~~~

When connectivity to the underlying devices is lost, the pool is suspended and
the ``failmode`` property decides what happens:

``wait``
    The default. Blocks all I/O until connectivity returns and the errors are
    cleared with ``zpool clear``.
``continue``
    Returns ``EIO`` to new writes but still serves reads from healthy devices.
    Uncommitted writes stay blocked.
``panic``
    Prints a message and crashes the system, generating a dump.

A suspended pool with ``failmode=wait`` looks exactly like a hang: commands
touching it block forever and are unkillable. Check ``zpool status`` for
another pool, and ``dmesg``, before concluding ZFS has deadlocked.

Hung processes and slow I/O
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Symptom:* a ``zfs`` or ``zpool`` command never returns and cannot be killed.

*Usual cause:* a stuck kernel thread, a suspended pool, or genuinely slow
hardware.

ZFS has a *deadman* timer for this. A pool sync taking longer than
``zfs_deadman_synctime_ms``, or a single I/O longer than
``zfs_deadman_ziotime_ms``, is declared hung. With the default
``zfs_deadman_failmode=wait`` this is only *logged* — so the evidence is in
the logs, not on your terminal. The deadman is disabled automatically once a
pool is suspended.

Slow but not hung storage is easier to see directly:

.. code:: bash

   zpool status -s                 # slow I/O count per leaf vdev
   zpool iostat -l 1               # latency breakdown
   zpool iostat -w                 # latency histograms

``-s`` counts I/Os that took longer than ``zio_slow_io_ms`` (30 s by default).
They did not necessarily fail — but a single disk accumulating them is the
classic signature of a drive about to go, and on RAIDZ it drags the whole
group down (see :doc:`RAIDZ </Basic Concepts/Pool Structure/RAIDZ>`).

Log files
~~~~~~~~~

**Kernel log.** ``dmesg -T``, ``/var/log/syslog``, or wherever ``rsyslogd``
sends kernel messages. Stack traces from stuck threads land here — sometimes
only once the deadman timer expires.

**ZFS debug messages.** The modules keep an internal log buffer, readable at
``/proc/spl/kstat/zfs/dbgmsg``, when the module parameter
`zfs_dbgmsg_enable <../../Performance and Tuning/Module Parameters.html#zfs-dbgmsg-enable>`__
is 1. This is frequently what developers ask for.

**Per-pool I/O statistics.** ``/proc/spl/kstat/zfs/<pool>/`` on Linux.

**What was done to this pool.** ``zpool history`` replays the administrative
commands the pool has seen — stored in the pool itself, so it survives
reboots and moves with the pool to another host. Frequently the fastest way
to answer "what changed?".

.. code:: bash

   zpool history pool
   zpool history -l pool           # who, from which host
   zpool history -i pool           # include internally logged events

Logging infrastructure — elasticsearch, fluentd, influxdb, splunk — makes
correlating these with system events considerably easier.

ZFS events
~~~~~~~~~~

ZFS reports notable events through an event channel. The ZFS Event Daemon
(``zed``) listens and acts on them; it is extensible, so scripts can subscribe
and take action. The script usually installed at
``/etc/zfs/zed.d/all-syslog.sh`` writes a formatted message to syslog. See
``zed(8)``.

.. code:: bash

   zpool events                    # history since module load, all pools
   zpool events -v                 # full detail per event
   zpool events -f                 # follow

The history lives in RAM and is capped by
`zfs_zevent_len_max <../../Performance and Tuning/Module Parameters.html#zfs-zevent-len-max>`__.
``zed`` throttles internally so a failing device cannot exhaust the system.

Each event carries a class used for filtering:

``sysevent.fs.zfs.*``
    Pool management — import, export, configuration updates, ``zpool
    history`` entries.
``ereport.*``
    Errors. One fault often produces several, as each layer reports it: a
    failing disk can raise an ``ereport.io`` on the read and an
    ``ereport.fs.zfs.checksum`` at the pool level. These correspond to the
    counters in ``zpool status`` — if you see errors there, matching ereports
    exist here.
``ereport.fs.zfs.delay``
    A slow I/O, including a RAIDZ child being put in sit-out.

The exact contents of verbose events change between versions; treat them as
diagnostic detail, not a stable interface.

Reporting a problem
~~~~~~~~~~~~~~~~~~~

Before opening an issue, confirm it is a bug rather than a support question —
the :doc:`mailing lists </Project and Community/Mailing Lists>` are the place
for the latter. Then collect:

* ``zfs version`` and the distribution and kernel version
* ``zpool status -v`` and ``zpool get all <pool>``
* the relevant part of ``dmesg`` and of ``/proc/spl/kstat/zfs/dbgmsg``
* ``zpool events -v`` around the failure
* non-default module parameters
* whether the system uses ECC memory, and whether it is virtualised
* a reproducer, if you have one — this matters more than anything else above

The :doc:`FAQ </Project and Community/FAQ>` has the full list and the issue
tracker link.

Further reading
~~~~~~~~~~~~~~~

* `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`__,
  `zpool-events(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-events.8.html>`__,
  `zpool-import(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-import.8.html>`__
* `zpoolconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolconcepts.7.html>`__ —
  ``Device Failure and Recovery``
* `zed(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zed.8.html>`__
* :doc:`ZFS Messages </msg/index>` — the ``ZFS-8000-*`` codes from
  ``zpool status``
