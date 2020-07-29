ZFS I/O (ZIO) Scheduler
=======================

ZFS issues I/O operations to leaf vdevs (usually devices) to satisfy and
complete I/Os. The ZIO scheduler determines when and in what order those
operations are issued. Operations are divided into five I/O classes
prioritized in the following order:

+----------+-------------+-------------------------------------------+
| Priority | I/O Class   | Description                               |
+==========+=============+===========================================+
| highest  | sync read   | most reads                                |
+----------+-------------+-------------------------------------------+
|          | sync write  | as defined by application or via 'zfs'    |
|          |             | 'sync' property                           |
+----------+-------------+-------------------------------------------+
|          | async read  | prefetch reads                            |
+----------+-------------+-------------------------------------------+
|          | async write | most writes                               |
+----------+-------------+-------------------------------------------+
| lowest   | scrub read  | scan read: includes both scrub and        |
|          |             | resilver                                  |
+----------+-------------+-------------------------------------------+

Each queue defines the minimum and maximum number of concurrent
operations issued to the device. In addition, the device has an
aggregate maximum, zfs_vdev_max_active. Note that the sum of the
per-queue minimums must not exceed the aggregate maximum. If the sum of
the per-queue maximums exceeds the aggregate maximum, then the number of
active I/Os may reach zfs_vdev_max_active, in which case no further I/Os
are issued regardless of whether all per-queue minimums have been met.

+-------------+------------------------------------+------------------------------------+
| I/O Class   | Min Active Parameter               | Max Active Parameter               |
+=============+====================================+====================================+
| sync read   | ``zfs_vdev_sync_read_min_active``  | ``zfs_vdev_sync_read_max_active``  |
+-------------+------------------------------------+------------------------------------+
| sync write  | ``zfs_vdev_sync_write_min_active`` | ``zfs_vdev_sync_write_max_active`` |
+-------------+------------------------------------+------------------------------------+
| async read  | ``zfs_vdev_async_read_min_active`` | ``zfs_vdev_async_read_max_active`` |
+-------------+------------------------------------+------------------------------------+
| async write | ``zfs_vdev_async_write_min_active``| ``zfs_vdev_async_write_max_active``|
+-------------+------------------------------------+------------------------------------+
| scrub read  | ``zfs_vdev_scrub_min_active``      | ``zfs_vdev_scrub_max_active``      |
+-------------+------------------------------------+------------------------------------+

For many physical devices, throughput increases with the number of
concurrent operations, but latency typically suffers. Further, physical
devices typically have a limit at which more concurrent operations have
no effect on throughput or can actually cause it to performance to
decrease.

The ZIO scheduler selects the next operation to issue by first looking
for an I/O class whose minimum has not been satisfied. Once all are
satisfied and the aggregate maximum has not been hit, the scheduler
looks for classes whose maximum has not been satisfied. Iteration
through the I/O classes is done in the order specified above. No further
operations are issued if the aggregate maximum number of concurrent
operations has been hit or if there are no operations queued for an I/O
class that has not hit its maximum. Every time an I/O is queued or an
operation completes, the I/O scheduler looks for new operations to
issue.

In general, smaller max_active's will lead to lower latency of
synchronous operations. Larger max_active's may lead to higher overall
throughput, depending on underlying storage and the I/O mix.

The ratio of the queues' max_actives determines the balance of
performance between reads, writes, and scrubs. For example, when there
is contention, increasing zfs_vdev_scrub_max_active will cause the scrub
or resilver to complete more quickly, but reads and writes to have
higher latency and lower throughput.

All I/O classes have a fixed maximum number of outstanding operations
except for the async write class. Asynchronous writes represent the data
that is committed to stable storage during the syncing stage for
transaction groups (txgs). Transaction groups enter the syncing state
periodically so the number of queued async writes quickly bursts up and
then reduce down to zero. The zfs_txg_timeout tunable (default=5
seconds) sets the target interval for txg sync. Thus a burst of async
writes every 5 seconds is a normal ZFS I/O pattern.

Rather than servicing I/Os as quickly as possible, the ZIO scheduler
changes the maximum number of active async write I/Os according to the
amount of dirty data in the pool. Since both throughput and latency
typically increase as the number of concurrent operations issued to
physical devices, reducing the burstiness in the number of concurrent
operations also stabilizes the response time of operations from other
queues. This is particular important for the sync read and write queues,
where the periodic async write bursts of the txg sync can lead to
device-level contention. In broad strokes, the ZIO scheduler issues more
concurrent operations from the async write queue as there's more dirty
data in the pool.
