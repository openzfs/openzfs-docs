VDEVs
=====

What is a VDEV?
~~~~~~~~~~~~~~~

A vdev (virtual device) is a fundamental building block of ZFS storage pools. It represents a logical grouping of physical storage devices, such as hard drives, SSDs, or partitions.

What is a leaf vdev?
~~~~~~~~~~~~~~~~~~~~

A leaf vdev is the most basic type of vdev, which directly corresponds to a physical storage device. It is the endpoint of the storage hierarchy in ZFS.

What is a top-level vdev?
~~~~~~~~~~~~~~~~~~~~~~~~~

Top-level vdevs are the direct children of the root vdev. They can be single devices or logical groups that aggregate multiple leaf vdevs (like mirrors or RAIDZ groups). ZFS dynamically stripes data across all top-level vdevs in a pool.

What is a root vdev?
~~~~~~~~~~~~~~~~~~~~

The root vdev is the top of the pool hierarchy. It aggregates all top-level vdevs into a single logical storage unit (the pool).

What are the different types of vdevs?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenZFS supports several types of vdevs. Top-level vdevs carry data and provide redundancy:

* **Single device**: A lone disk, file or partition used as a top-level vdev. It provides no redundancy, and its loss loses the whole pool. Note that there is no "stripe" vdev type in ZFS — striping is what the pool does *across* its top-level vdevs, not a vdev in its own right.
* **Mirror**: A vdev that stores the same data on two or more drives for redundancy.
* :doc:`RAIDZ </Basic Concepts/Pool Structure/RAIDZ>`: A vdev that uses parity to provide fault tolerance, similar to traditional RAID 5/6. There are three levels of RAIDZ:

   * **RAIDZ1**: Single parity, similar to RAID 5. Requires at least 2 disks (3+ recommended), can tolerate one drive failure.
   * **RAIDZ2**: Double parity, similar to RAID 6. Requires at least 3 disks (5+ recommended), can tolerate two drive failures.
   * **RAIDZ3**: Triple parity. Requires at least 4 disks (7+ recommended), can tolerate three drive failures.

* :doc:`dRAID </Basic Concepts/Pool Structure/dRAID Howto>`: Distributed RAID. A vdev that provides distributed parity and hot spares across multiple drives, allowing for much faster rebuild performance after a failure.

Auxiliary vdevs provide specific functionality:

* **Spare**: A drive that acts as a hot spare, automatically replacing a failed drive in another vdev.
* **Cache (L2ARC)**: A Level 2 ARC vdev used for caching frequently accessed data to improve random read performance. It holds only a second copy of data that is already in the pool, so losing it is harmless.
* **Log (SLOG)**: A separate log vdev (SLOG) used to store the ZFS Intent Log (ZIL) for improved synchronous write performance. It is not a write cache — only synchronous writes use it.
* **Special**: A vdev dedicated to storing metadata, and optionally small file blocks and the Dedup Table (DDT).
* **Dedup**: A vdev dedicated strictly to storing the Deduplication Table (DDT).

``special`` and ``dedup`` vdevs are the only data the pool has for those
blocks, so they must be as redundant as the pool's normal vdevs — losing one
loses the pool. See :doc:`Caching and Auxiliary Devices </Basic Concepts/Pool Structure/Caching>` for when
each of these is worth adding.

How do vdevs relate to storage pools?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vdevs are the building blocks of ZFS storage pools. A storage pool (zpool) is created by combining one or more top-level vdevs. The overall performance, capacity, and redundancy of the storage pool depend on the configuration and types of vdevs used.

Here is an example layout as seen in `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`_ output
for a pool with two RAIDZ1 top-level vdevs and 10 leaf vdevs:

::

   datapoolname (root vdev)
     raidz1-0 (top-level vdev)
       /dev/dsk/disk0 (leaf vdev)
       /dev/dsk/disk1 (leaf vdev)
       /dev/dsk/disk2 (leaf vdev)
       /dev/dsk/disk3 (leaf vdev)
       /dev/dsk/disk4 (leaf vdev)
     raidz1-1 (top-level vdev)
       /dev/dsk/disk5 (leaf vdev)
       /dev/dsk/disk6 (leaf vdev)
       /dev/dsk/disk7 (leaf vdev)
       /dev/dsk/disk8 (leaf vdev)
       /dev/dsk/disk9 (leaf vdev)

How does ZFS handle vdev failures?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Redundancy in ZFS lives **inside** a top-level vdev, not across them. A mirror
survives the loss of all but one of its leaf vdevs, and a raidz\ *N* survives
the loss of *N*. When a leaf vdev fails, ZFS marks it "faulted", keeps serving
reads and writes from the surviving members of that same top-level vdev, and
reconstructs the missing data from them.

The corollary matters more than the rule: **if a top-level vdev is lost, the
pool is lost.** Because data is striped across all top-level vdevs, there is
no copy of its contents anywhere else. A single non-redundant disk added to an
otherwise mirrored pool therefore puts the entire pool at the mercy of that
one disk.

Administrators can `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`_ a failed leaf vdev with a new one and ZFS will automatically resilver (rebuild)
the data onto it to return the pool to a healthy state. See
:doc:`Scrub and Resilver </Basic Concepts/Operations/Scrub and Resilver>`.

How do I manage vdevs in ZFS?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vdevs are managed using the `zpool(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool.8.html>`_ command-line utility. Common operations include:

* **Creating a pool**: `zpool create` allows you to specify the vdev layout. See `zpool-create(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-create.8.html>`_.
* **Adding vdevs**: `zpool add` attaches new top-level vdevs to an existing pool, expanding its capacity and performance (by increasing stripe width). See `zpool-add(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-add.8.html>`_.
* **Widening a vdev**: `zpool attach` adds a device to a mirror, or to an existing raidz group (RAIDZ expansion). See `zpool-attach(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-attach.8.html>`_.
* **Removing vdevs**: `zpool remove` can remove certain types of top-level vdevs evacuating their data to other vdevs. It is not possible at all if the pool contains a raidz or draid top-level vdev. See `zpool-remove(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-remove.8.html>`_.
* **Replacing drives**: `zpool replace` swaps a failed or small drive with a new one. See `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`_.
* **Monitoring status**: `zpool status` shows the health and layout of all vdevs. See `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`_.
* **Monitoring performance**: `zpool iostat` displays I/O statistics for the pool and individual vdevs. See `zpool-iostat(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html>`_.

:doc:`Changing Pool Layout </Basic Concepts/Pool Structure/Changing Pool Layout>` covers these operations and
their constraints in detail.
