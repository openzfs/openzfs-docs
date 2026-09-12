Caching and Auxiliary Devices
=============================

ZFS has one read cache in RAM (the ARC), an optional second read cache on
disk (L2ARC), and two kinds of write-path device that are often mistaken for
caches but are not: the separate intent log (SLOG) and the special allocation
class.

Adding devices is easy and undoing it is not, so it is worth knowing which
problem each one actually solves.

ARC
~~~

The Adaptive Replacement Cache is ZFS' in-memory cache. It keeps both recently
used and frequently used blocks, and adapts the balance between them, which is
why it usually outperforms a simple LRU page cache.

Per dataset, ``primarycache`` controls what may enter it: ``all`` (the
default), ``metadata``, or ``none``.

.. code:: bash

   zfs set primarycache=metadata pool/bigsequentialdata
   zarcsummary                    # arc_summary before OpenZFS 2.4.0
   zarcstat 1                     # arcstat before OpenZFS 2.4.0
   cat /proc/spl/kstat/zfs/arcstats

RAM is by far the most effective ZFS "tuning knob". Before adding any cache
device, check whether the ARC is simply too small — see
:doc:`Module Parameters </Performance and Tuning/Module Parameters>` for
``zfs_arc_max`` and friends.

L2ARC (``cache`` vdev)
~~~~~~~~~~~~~~~~~~~~~~

A cache device is a second-level read cache between RAM and the pool. It helps
when the working set is much larger than RAM and the workload is
**random reads of mostly static content**. It does nothing for writes.

.. code:: bash

   zpool add pool cache nvme0n1
   zfs set secondarycache=metadata pool/data      # all | metadata | none

Properties of cache devices:

* They cannot be mirrored or part of a raidz group. A read error is simply
  reissued against the pool, so losing one is harmless.
* Their contents survive reboots (persistent L2ARC) and are restored
  asynchronously on import. This can be disabled with
  ``l2arc_rebuild_enabled=0``. Devices smaller than 1 GiB do not get the
  metadata needed for a rebuild.
* **L2ARC costs RAM.** Every cached block needs a header in the ARC, so an
  oversized L2ARC shrinks the cache that actually matters. On a
  RAM-constrained system an L2ARC can make things slower.

SLOG (``log`` vdev)
~~~~~~~~~~~~~~~~~~~

The ZFS Intent Log satisfies POSIX durability requirements: ``fsync()`` and
``O_SYNC`` writes must be on stable storage before the call returns. The ZIL
exists on every pool — by default it is allocated from blocks in the main
pool. A ``log`` vdev just moves it to a dedicated device.

.. code:: bash

   zpool add pool log mirror nvme0n1 nvme1n1

Consequences worth being precise about:

* A SLOG is **not a write cache**. Asynchronous writes never touch the ZIL;
  they are aggregated in memory and written out at the next transaction group.
  If your workload has no synchronous writes, a SLOG changes nothing.
* It is only ever *read* after a crash, to replay what had not yet been
  committed.
* It should be a low-latency device with power-loss protection. Consumer SSDs
  without it will happily report data as stable that a power cut then loses.
* Multiple log devices load-balance and can be mirrored; raidz is not
  supported for the intent log.

Typical beneficiaries: NFS servers, databases, and VM hosts with sync-heavy
guests. The ``sync`` and ``logbias`` dataset properties control the behavior —
``logbias=throughput`` bypasses the log devices for a dataset, and
``sync=disabled`` skips the ZIL entirely, trading recent-write durability for
speed.

Special vdev (``special`` allocation class)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A special vdev is not a cache either — it is storage that permanently holds a
specific class of blocks: metadata, the indirect blocks of user data,
deduplication tables, and optionally small file blocks.

.. code:: bash

   zpool add pool special mirror nvme0n1 nvme1n1

Putting metadata on flash is usually the single biggest win available to a
pool of spinning disks: directory traversal, ``zfs list``, scrubs and
resilvers all become dramatically faster. But because the blocks live *only*
there, the vdev must be as redundant as the rest of the pool, and on a raidz
pool it can never be removed again.

It has enough sharp edges to deserve its own page —
see :doc:`Special vdev </Basic Concepts/Pool Structure/Special vdev>`.

Choosing between them
~~~~~~~~~~~~~~~~~~~~~

+-------------------------+-------------------------------+------------------+
| Symptom                 | What helps                    | Removable later? |
+=========================+===============================+==================+
| Slow reads, ARC too     | More RAM, then L2ARC          | yes              |
| small for working set   |                               |                  |
+-------------------------+-------------------------------+------------------+
| Slow synchronous writes | SLOG with power-loss          | yes              |
| (NFS, databases, VMs)   | protection                    |                  |
+-------------------------+-------------------------------+------------------+
| Slow metadata operations| special vdev (mirrored)       | only if the pool |
| on spinning disks       |                               | has no raidz     |
+-------------------------+-------------------------------+------------------+
| Dedup table thrashing   | dedup vdev (mirrored)         | same as special  |
+-------------------------+-------------------------------+------------------+

Further reading
~~~~~~~~~~~~~~~

* `zpoolconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolconcepts.7.html>`__ —
  ``Intent Log``, ``Cache Devices``, ``Special Allocation Class``
* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``primarycache``, ``secondarycache``, ``special_small_blocks``, ``logbias``,
  ``sync``
* :doc:`VDEVs </Basic Concepts/Pool Structure/VDEVs>`,
  :doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`,
  :doc:`Module Parameters </Performance and Tuning/Module Parameters>`
