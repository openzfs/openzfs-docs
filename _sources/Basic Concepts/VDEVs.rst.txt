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

* **Striped Disk(s)**: A vdev consisting of one or more physical devices striped together (like RAID 0). It provides no redundancy and will lead to data loss if a drive fails.
* **Mirror**: A vdev that stores the same data on two or more drives for redundancy.
* `RAIDZ <./RAIDZ.html>`__: A vdev that uses parity to provide fault tolerance, similar to traditional RAID 5/6. There are three levels of RAIDZ:

   * **RAIDZ1**: Single parity, similar to RAID 5. Requires at least 2 disks (3+ recommended), can tolerate one drive failure.
   * **RAIDZ2**: Double parity, similar to RAID 6. Requires at least 3 disks (5+ recommended), can tolerate two drive failures.
   * **RAIDZ3**: Triple parity. Requires at least 4 disks (7+ recommended), can tolerate three drive failures.

* `dRAID <./dRAID%20Howto.html>`__: Distributed RAID. A vdev that provides distributed parity and hot spares across multiple drives, allowing for much faster rebuild performance after a failure.

Auxiliary vdevs provide specific functionality:

* **Spare**: A drive that acts as a hot spare, automatically replacing a failed drive in another vdev.
* **Cache (L2ARC)**: A Level 2 ARC vdev used for caching frequently accessed data to improve random read performance.
* **Log (SLOG)**: A separate log vdev (SLOG) used to store the ZFS Intent Log (ZIL) for improved synchronous write performance.
* **Special**: A vdev dedicated to storing metadata, and optionally small file blocks and the Dedup Table (DDT).
* **Dedup**: A vdev dedicated strictly to storing the Deduplication Table (DDT).

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

ZFS is designed to handle vdev failures gracefully. If a vdev fails, ZFS can continue to operate using the remaining vdevs in the pool,
provided that the redundancy level of the pool allows for it (e.g., in a mirror, RAIDZ, or dRAID configuration).
When there is still enough redundancy in the pool, ZFS will mark the failed vdev as "faulted" and will recover data from the remaining vdevs.
Administrators can `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`_ failed vdev with a new one and ZFS will automatically resilver (rebuild)
the data onto the new vdev to return the pool to a healthy state.

How do I manage vdevs in ZFS?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vdevs are managed using the `zpool(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool.8.html>`_ command-line utility. Common operations include:

* **Creating a pool**: `zpool create` allows you to specify the vdev layout. See `zpool-create(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-create.8.html>`_.
* **Adding vdevs**: `zpool add` attaches new top-level vdevs to an existing pool, expanding its capacity and performance (by increasing stripe width). See `zpool-add(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-add.8.html>`_.
* **Removing vdevs**: `zpool remove` can remove certain types of top-level vdevs evacuating their data to other vdevs. See `zpool-remove(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-remove.8.html>`_.
* **Replacing drives**: `zpool replace` swaps a failed or small drive with a new one. See `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`_.
* **Monitoring status**: `zpool status` shows the health and layout of all vdevs. See `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`_.
* **Monitoring performance**: `zpool iostat` displays I/O statistics for the pool and individual vdevs. See `zpool-iostat(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html>`_.
