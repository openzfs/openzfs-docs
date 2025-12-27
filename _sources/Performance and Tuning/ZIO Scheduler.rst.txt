ZFS I/O (ZIO) Scheduler
=======================

ZFS issues I/O operations to leaf `vdevs <https://openzfs.github.io/openzfs-docs/Basic%20Concepts/VDEVs.html>`_
(usually devices) to satisfy and complete I/Os. The ZIO scheduler determines when and in what order those
operations are issued. Operations are divided into nine I/O classes
prioritized in the following order:

+-----------+--------------+-------------------------------------------+-----------------+
| Priority  | I/O Class    | Description                               | I/O Type        |
+===========+==============+===========================================+=================+
| highest   | sync read    | most reads                                | interactive     |
+-----------+--------------+-------------------------------------------+-----------------+
|           | sync write   | as defined by application or via 'zfs'    | interactive     |
|           |              | 'sync' property                           |                 |
+-----------+--------------+-------------------------------------------+-----------------+
|           | async read   | prefetch reads                            | interactive     |
+-----------+--------------+-------------------------------------------+-----------------+
| see below | async write  | most writes                               | interactive     |
+-----------+--------------+-------------------------------------------+-----------------+
|           | scrub read   | scan reads: includes both scrub and       | non-interactive |
|           |              | resilver                                  |                 |
+-----------+--------------+-------------------------------------------+-----------------+
|           | removal      | vdev removal reflow                       | non-interactive |
+-----------+--------------+-------------------------------------------+-----------------+
|           | initializing | vdev space initialization                 | non-interactive |
+-----------+--------------+-------------------------------------------+-----------------+
|           | trim         | TRIM/UNMAP requests                       | interactive     |
+-----------+--------------+-------------------------------------------+-----------------+
| lowest    | rebuild      | sequential reconstruction                 | non-interactive |
+-----------+--------------+-------------------------------------------+-----------------+

For interactive I/Os each queue defines the minimum and maximum number of concurrent
operations issued to the device. Each device also respects an aggregate maximum - `zfs_vdev_max_active <https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Module%20Parameters.html#zfs-vdev-max-active>`_.
Note that the sum of the per-queue minimums must not exceed the aggregate maximum.
If the sum of the per-queue maximums exceeds the aggregate maximum, then the number of
active I/Os may reach `zfs_vdev_max_active <https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Module%20Parameters.html#zfs-vdev-max-active>`_,
in which case no further I/Os are issued regardless of whether all per-queue minimums have been met.

For non-interactive I/O (scrub, resilver, removal, initializing, and rebuild),
the number of concurrently-active I/Os is limited to _min_active, unless
the vdev is "idle". When there are no interactive I/Os active (sync or
async), and `zfs_vdev_nia_delay <https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Module%20Parameters.html#zfs-vdev-nia-delay>`_
I/Os have completed since the last interactive I/O, then the vdev is considered to be "idle", and the number
of concurrently-active non-interactive I/Os is increased to _max_active.

+-------------+-------------------------------------+-------------------------------------+
| I/O Class   | Min Active Parameter                | Max Active Parameter                |
+=============+=====================================+=====================================+
| sync read   | ``zfs_vdev_sync_read_min_active``   | ``zfs_vdev_sync_read_max_active``   |
+-------------+-------------------------------------+-------------------------------------+
| sync write  | ``zfs_vdev_sync_write_min_active``  | ``zfs_vdev_sync_write_max_active``  |
+-------------+-------------------------------------+-------------------------------------+
| async read  | ``zfs_vdev_async_read_min_active``  | ``zfs_vdev_async_read_max_active``  |
+-------------+-------------------------------------+-------------------------------------+
| async write | ``zfs_vdev_async_write_min_active`` | ``zfs_vdev_async_write_max_active`` |
+-------------+-------------------------------------+-------------------------------------+
| scrub read  | ``zfs_vdev_scrub_min_active``       | ``zfs_vdev_scrub_max_active``       |
+-------------+-------------------------------------+-------------------------------------+
| removal     | ``zfs_vdev_removal_min_active``     | ``zfs_vdev_removal_max_active``     |
+-------------+-------------------------------------+-------------------------------------+
| initializing| ``zfs_vdev_initializing_min_active``| ``zfs_vdev_initializing_max_active``|
+-------------+-------------------------------------+-------------------------------------+
| trim        | ``zfs_vdev_trim_min_active``        | ``zfs_vdev_trim_max_active``        |
+-------------+-------------------------------------+-------------------------------------+
| rebuild     | ``zfs_vdev_rebuild_min_active``     | ``zfs_vdev_rebuild_max_active``     |
+-------------+-------------------------------------+-------------------------------------+

I/O queue statistics include most of the I/Os classes and can be viewed via
the `zpool iostat -q <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html#q>`_ command

For many physical devices, throughput increases with the number of
concurrent operations, but latency typically suffers. Further, physical
devices typically have a limit at which more concurrent operations have
no effect on throughput or can cause the disk performance to
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
transaction groups. Transaction groups enter the syncing state
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
queues. This is particularly important for the sync read and write queues,
where the periodic async write bursts of the txg sync can lead to
device-level contention. In broad strokes, the ZIO scheduler issues more
concurrent operations from the async write queue as there's more dirty
data in the pool.

Async Write I/O Scheduling
==========================

The number of concurrent operations issued for the async write I/O class
follows a piece-wise linear function defined by a few adjustable points::

           |                   o---------| <-- zfs_vdev_async_write_max_active
      ^    |                  /^         |
      |    |                 / |         |
    active |                /  |         |
     I/O   |               /   |         |
    count  |              /    |         |
           |             /     |         |
           |------------o      |         | <-- zfs_vdev_async_write_min_active
          0|____________^______|_________|
           0%           |      |        100% of zfs_dirty_data_max
                        |      |
                        |      `-- zfs_vdev_async_write_active_max_dirty_percent
                        `--------- zfs_vdev_async_write_active_min_dirty_percent

Until the amount of dirty data exceeds a minimum percentage of the dirty
data allowed in the pool, the I/O scheduler will limit the number of
concurrent operations to the minimum. As that threshold is crossed, the
number of concurrent operations issued increases linearly to the maximum at
the specified maximum percentage of the dirty data allowed in the pool.

Ideally, the amount of dirty data on a busy pool will stay in the sloped
part of the function between zfs_vdev_async_write_active_min_dirty_percent
and zfs_vdev_async_write_active_max_dirty_percent. If it exceeds the
maximum percentage, this indicates that the rate of incoming data is
greater than the rate that the backend storage can handle. In this case, we
must further throttle incoming writes. See `ZIO Transaction Delay <https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/ZFS%20Transaction%20Delay.html>`_ for details.



Code reference: `vdev_queue.c <https://github.com/openzfs/zfs/blob/master/module/zfs/vdev_queue.c#L42>`_
