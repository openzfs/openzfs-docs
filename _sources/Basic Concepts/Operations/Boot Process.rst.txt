Pools at Boot
=============

Nothing about a ZFS pool is described in ``/etc/fstab`` by default. Pools are
discovered, imported, mounted and shared by ZFS itself, which is convenient
until something does not come up and there is no fstab line to look at. This
page covers what happens between power-on and a mounted dataset.

The order of events
~~~~~~~~~~~~~~~~~~~

#. **Pools are imported.** Either from the cache file, or by scanning
   devices.
#. **Datasets are mounted**, in mountpoint order, by ``zfs mount -a`` or by
   generated systemd mount units.
#. **Shares are published** by ``zfs share -a`` — see
   :doc:`Sharing Datasets </Basic Concepts/Operations/Sharing>`.
#. **zvols appear** under ``/dev/zvol``; anything waiting on them has to wait
   for that.
#. **zed starts**, so events from this point on are acted upon.

A root-on-ZFS system does step 1 earlier and differently: the root pool is
imported from the initramfs (Linux) or by the loader (FreeBSD) before the
real root can be mounted at all. The
:doc:`Root on ZFS guides </Getting Started/index>` cover that case.

The cache file
~~~~~~~~~~~~~~

``/etc/zfs/zpool.cache`` records which pools were imported, so the system can
bring them back without scanning every block device. **Every pool listed there
is imported automatically at boot.**

The pool property ``cachefile`` controls this:

* the default (empty string) uses the standard location;
* ``none`` means the pool is never cached — it will *not* come back
  automatically, which is what you want for removable media, clustering and
  failover;
* an explicit path caches it elsewhere, to be imported later with
  ``zpool import -c <path>``.

.. code:: bash

   zpool get cachefile pool
   zpool set cachefile=none pool          # stop importing it at boot
   zpool set cachefile= pool              # back to the default

The file is a binary nvlist; ``zdb`` with no arguments prints its contents. If
it is stale or missing, a pool can still be found by scanning
(``zpool import -d``), which is what the ``zfs-import-scan`` path does.

Two common surprises: a pool you imported once keeps coming back after reboot
because it is in the cache, and a pool imported with ``-R`` (which sets
``cachefile=none``) does *not* come back, by design. See
:doc:`Troubleshooting </Basic Concepts/Operations/Troubleshooting>`.

hostid and importing on the wrong machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A pool records the ``hostid`` of the system that imported it. If another
system sees a pool that a different host still has imported, it refuses to
import it — this is the "pool was last accessed by another system" message,
and ``-f`` overrides it.

That guard is advisory. It compares a recorded id; it does not check whether
the other host is still writing. Forcing an import of a pool that is genuinely
active elsewhere will corrupt it.

On Linux the id comes from ``/etc/hostid``; generate one with
``zgenhostid`` if it is missing. A missing or duplicated hostid is a classic
cause of pools that either refuse to import after a hostname change or fail to
protect themselves in a cluster.

For shared storage where two hosts really can reach the same devices, the
``multihost`` pool property turns the advisory check into an active one: hosts
write periodic heartbeats, and an import is refused — *even with* ``-f`` —
while the pool looks alive. Each host must have a unique hostid for it to
work.

.. code:: bash

   zgenhostid                       # if /etc/hostid is missing
   zpool set multihost=on pool

Note what ``multihost`` does not do: it protects the pool at import time, not
individual devices from being claimed by two different pools.

systemd
~~~~~~~

On Linux the sequence is a set of units, and knowing their names is most of
the battle:

``zfs-import-cache.service``
    Imports the pools listed in ``zpool.cache``.
``zfs-import-scan.service``
    Imports by scanning devices instead. Normally the alternative to the
    cache service, not a companion to it.
``zfs-import.target``
    Reached once importing is done; things needing pools order after it.
``zfs-mount.service``
    Runs ``zfs mount -a``.
``zfs-share.service``
    Runs ``zfs share -a``.
``zfs-volume-wait.service`` / ``zfs-volumes.target``
    Waits until zvol device nodes exist.
``zfs-zed.service``
    The event daemon.
``zfs.target``
    The aggregate; enable or disable ZFS at boot here.

.. code:: bash

   systemctl list-units 'zfs*'
   systemctl status zfs-import-cache.service
   journalctl -u zfs-import-cache.service -b

There are also the periodic maintenance timers —
``zfs-scrub-weekly@<pool>.timer``, ``zfs-scrub-monthly@<pool>.timer`` and the
matching ``zfs-trim-*`` ones. See
:doc:`Scrub and Resilver </Basic Concepts/Operations/Scrub and Resilver>` and
:doc:`TRIM </Basic Concepts/Operations/TRIM>`.

``zfs-mount-generator``
^^^^^^^^^^^^^^^^^^^^^^^

Mounting everything with one ``zfs mount -a`` late in boot means systemd knows
nothing about the individual mounts, so units that need a particular dataset
cannot order themselves against it.

``zfs-mount-generator`` solves that by generating a native ``.mount`` unit per
dataset at generator time, from a cached list of dataset properties. Datasets
with ``mountpoint=legacy`` or ``none`` are skipped, as are those with
``canmount=off``.

This is what to reach for when a service starts before its data is mounted.
It also lets an encrypted dataset's key be requested through the normal
systemd credential machinery rather than blocking a shell —
see :doc:`Native Encryption </Basic Concepts/Data Storage/Encryption>`.

FreeBSD
~~~~~~~

The cache file lives at ``/boot/zfs/zpool.cache``. Pools are imported by the
``zfs`` rc script, enabled with ``zfs_enable="YES"`` in ``/etc/rc.conf``, and
the loader imports the root pool before the kernel starts. The concepts —
cache file, hostid, mount then share — are the same.

Further reading
~~~~~~~~~~~~~~~

* `zpoolprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolprops.7.html>`__ —
  ``cachefile``, ``multihost``
* `zfs-mount-generator(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-mount-generator.8.html>`__,
  `zgenhostid(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zgenhostid.8.html>`__
* `zpool-import(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-import.8.html>`__
* :doc:`Troubleshooting </Basic Concepts/Operations/Troubleshooting>`,
  :doc:`Root on ZFS guides </Getting Started/index>`
