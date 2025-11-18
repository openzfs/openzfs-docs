What is a vdev?
===============

Vdev stands for virtual device. It is a fundamental building block of ZFS storage pools.
It represents a logical grouping of physical storage device(s), such as hard drives or SSDs. 

What is a leaf vdev?
====================

A leaf vdev is the most basic type of vdev that directly corresponds to physical storage device.
It is the endpoint of the storage hierarchy in ZFS.

What is a child vdev?
=====================

Child vdevs are higher-level vdevs that aggregate multiple leaf vdevs into a single logical unit.
By combining multiple leaf vdevs in different ways we can optimize for providing redundancy, performance, or achieve the desired balance of both.

What is a root vdev?
====================

The root vdev is the top of a pool hierarchy. Root vdev is the highest level vdev that aggregate multiple child or leaf vdevs into a single logical unit.

What are the different types of vdevs?
============================================

OpenZFS supports several types of vdevs, including:

* **Single Drive**: A vdev consisting of a single physical device.
* **Striped**: A vdev that stripes data across two or more drives for improved performance, but without redundancy.
* **Mirror**: A vdev that duplicates data across two or more drives for redundancy.
* **RAIDZ**: A vdev that uses parity to provide fault tolerance, similar to traditional RAID. There are three levels of RAID-Z:

   * **RAIDZ1**: Single parity, can tolerate one drive failure.
   * **RAIDZ2**: Double parity, can tolerate two drive failures.
   * **RAIDZ3**: Triple parity, can tolerate three drive failures.

* **dRAID**: A vdev that provides distributed parity across multiple drives allowing for faster rebuild performance after a failure.
* **Spare**: A vdev that acts as a hot spare, automatically replacing a failed drive in another vdev.
* **Cache (L2ARC)**: A Level 2 ARC vdev - used for caching frequently accessed data to improve read performance.
* **Log (ZIL)**: A vdev used for storing the ZFS Intent Log - used to improve synchronous write performance.

How do vdevs relate to storage pools?
=====================================
Vdevs are the building blocks of ZFS storage pools. A storage pool (zpool) is created by combining one or more vdevs.
The overall performance, capacity, and redundancy of the storage pool depend on the configuration and types of vdevs used.

Here is an example layout as seen in `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`_ output
for a RAIDZ1 storage pool with leaf, child, and root vdev labeled in parentheses:

datapoolname (root vdev)
   raidz1-0 (child vdev)
     /dev/dsk/disk0 (leaf vdev)
     /dev/dsk/disk1 (leaf vdev)
     /dev/dsk/disk2 (leaf vdev)
     /dev/dsk/disk3 (leaf vdev)
     /dev/dsk/disk4 (leaf vdev)
   raidz1-1 (child vdev)
     /dev/dsk/disk5 (leaf vdev)
     /dev/dsk/disk6 (leaf vdev)
     /dev/dsk/disk7 (leaf vdev)
     /dev/dsk/disk8 (leaf vdev)
     /dev/dsk/disk9 (leaf vdev)

How does ZFS handle vdev failures?
==================================

ZFS is designed to handle vdev failures gracefully. If a vdev fails, ZFS can continue to operate using the remaining vdevs in the pool,
provided that the redundancy level of the pool allows for it (e.g., in a mirror, RAIDZ, or dRAID configuration).
ZFS will mark the failed vdev as "faulted" and will recover data from the remaining vdevs.
Administrators can `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`_ failed vdevs and ZFS will automatically resilver (rebuild)
the data onto the new vdev to return the pool to a healthy state.

How do I manage vdevs in ZFS?
=============================

Vdevs can be managed using the `zpool(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool.8.html>`_ command-line utility. Common operations include:

* Creating a new storage pool with specified vdev(s). See `zpool-create(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-create.8.html>`_ manpage.
* Adding vdev to an existing pool. See `zpool-add(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-add.8.html>`_ manpage.
* Removing vdev from an existing pool. See `zpool-remove(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-remove.8.html>`_ manpage.
* Replacing failed vdev. See `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`_ manpage.
* Monitoring the health and status of vdev(s) within a pool. See `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`_ manpage.
* Monitoring performance metrics related to vdev(s) using `zpool-iostat(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html>`_ manpage.

----

Last updated: November 17 2025