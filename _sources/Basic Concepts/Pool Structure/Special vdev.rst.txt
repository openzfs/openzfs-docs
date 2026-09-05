Special vdev
============

A ``special`` vdev is a top-level vdev that holds a specific *allocation
class* rather than general pool data: metadata, the indirect blocks of user
data, deduplication tables, and — optionally, per dataset — small file blocks.

It is not a cache. The blocks routed there exist **only** there. That single
fact drives everything else on this page.

.. warning::

   A ``special`` vdev must be at least as redundant as the pool's normal
   vdevs. Losing it loses the pool, exactly as losing any other top-level
   vdev would. Never add one as a single device to a redundant pool.

Why it helps
~~~~~~~~~~~~

On a pool of spinning disks, metadata access is the dominant source of random
I/O: directory traversal, ``zfs list``, ``find``, backup scans, and — most
visibly — scrub and resilver, which must walk the whole block tree. Moving
that class onto flash converts those random reads into something the pool can
actually serve, without paying for an all-flash pool.

This is usually a larger and more reliable win than adding an L2ARC, because
it is a permanent placement rather than a cache that must warm up and that
costs ARC headers. See
:doc:`Caching and Auxiliary Devices </Basic Concepts/Pool Structure/Caching>`.

Adding one
~~~~~~~~~~

.. code:: bash

   zpool add pool special mirror nvme0n1 nvme1n1
   zpool list -v pool                  # per-vdev usage, special class included

A pool must already have at least one normal vdev before ``special`` or
``dedup`` devices can be assigned. Multiple special vdevs load-balance
allocations between them.

What actually lands there
~~~~~~~~~~~~~~~~~~~~~~~~~

The selection happens per block, in this order:

#. **Deduplication tables** go to a ``dedup`` vdev if the pool has one;
   otherwise to the special vdev. Setting the ``zfs_ddt_data_is_special``
   module parameter to 0 keeps them out of the special class.
#. **Metadata** — every object type ZFS marks as metadata — goes to the
   special class.
#. **Indirect blocks of user data** (any block above level 0) go there too,
   controlled by ``zfs_user_indirect_is_special`` (default on). These are the
   block pointers, so this is much of what makes tree walks fast.
#. **Small user data blocks** go there only if the dataset opts in via
   ``special_small_blocks`` — and only while the class is below its
   metadata reserve, see below.
#. Everything else goes to the normal class.

The **ZIL** is a separate case. An intent log block is allocated from, in
order: a dedicated ``log`` vdev, then log space reserved on the special vdev,
then the special class proper, then log space reserved on normal vdevs, then
the normal class. So a special vdev absorbs the ZIL when there is no SLOG,
but a SLOG always wins.

Small blocks: ``special_small_blocks``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   zfs set special_small_blocks=32K pool/data

Blocks whose size is less than or equal to this value — measured **after
compression and encryption** — are placed in the special class. The default
is 0, meaning the feature is off; the maximum is the maximum block size
(16 MiB). It is a per-dataset property, so you can enable it only where it
pays.

Two things surprise people here:

**It is compared against the physical size.** A 128 KiB record that compresses
to 20 KiB counts as a 20 KiB block. Setting the threshold near your
``recordsize`` will therefore pull far more onto the special vdev than
expected — for a well-compressing dataset, potentially all of it.

**There is a metadata reserve.** Small blocks are only accepted while the
special class is below ``100 - zfs_special_class_metadata_reserve_pct``
percent full — 75% by default. The last quarter is kept for metadata alone.
This is a floor for metadata, not a ceiling for the vdev: metadata itself may
fill it completely.

When it fills up
~~~~~~~~~~~~~~~~

Allocations that no longer fit spill back into the normal class. Nothing
fails, and no data is lost — but the metadata written from that point on
lands on the slow disks, and the benefit quietly degrades. Existing blocks are
never migrated, in either direction.

This makes monitoring the fill level worthwhile:

.. code:: bash

   zpool list -v pool

Sizing is workload-dependent and hard to predict from first principles. The
honest approach is to measure the pool you actually have — ``zdb -bbb pool``
reports space usage broken down by block type, from which the metadata total
can be read off — and then leave generous headroom, because the cost of
guessing low is a vdev you cannot shrink.

Removing one
~~~~~~~~~~~~

.. code:: bash

   zpool remove pool special-1

This works only under the same constraints as any top-level vdev removal: the
pool must contain **no** raidz or draid top-level vdev, all top-level vdevs
must share the same ``ashift``, keys for encrypted datasets must be loaded,
and the ``device_removal`` feature must be enabled.

The practical consequence is blunt: **on a raidz pool, a special vdev can
never be removed.** Adding one is a permanent decision. See
:doc:`Changing Pool Layout </Basic Concepts/Pool Structure/Changing Pool Layout>`.

Related vdev types
~~~~~~~~~~~~~~~~~~

``dedup``
    The same idea restricted to deduplication tables. Use it when dedup is
    enabled and you want its table isolated from metadata. Same redundancy
    requirement, same removal constraints. See
    :doc:`Deduplication </Basic Concepts/Data Storage/Deduplication>`.

``log`` (SLOG)
    Not an allocation class in the same sense — it holds the intent log and
    is read only after a crash. Losing a modern SLOG costs at most the last
    few seconds of synchronous writes, not the pool.

``cache`` (L2ARC)
    A genuine cache: a second copy of data that also lives in the pool.
    Losing it is harmless.

Further reading
~~~~~~~~~~~~~~~

* `zpoolconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolconcepts.7.html>`__ —
  ``Special Allocation Class``
* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``special_small_blocks``
* `zpool-add(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-add.8.html>`__,
  `zpool-remove(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-remove.8.html>`__
* :doc:`VDEVs </Basic Concepts/Pool Structure/VDEVs>`,
  :doc:`Caching and Auxiliary Devices </Basic Concepts/Pool Structure/Caching>`
