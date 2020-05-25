Async Writes
============

The number of concurrent operations issued for the async write I/O class
follows a piece-wise linear function defined by a few adjustable points.

::

          |              o---------| <-- zfs_vdev_async_write_max_active
     ^    |             /^         |
     |    |            / |         |
   active |           /  |         |
    I/O   |          /   |         |
   count  |         /    |         |
          |        /     |         |
          |-------o      |         | <-- zfs_vdev_async_write_min_active
         0|_______^______|_________|
          0%      |      |       100% of zfs_dirty_data_max
                  |      |
                  |      `-- zfs_vdev_async_write_active_max_dirty_percent
                  `--------- zfs_vdev_async_write_active_min_dirty_percent

Until the amount of dirty data exceeds a minimum percentage of the dirty
data allowed in the pool, the I/O scheduler will limit the number of
concurrent operations to the minimum. As that threshold is crossed, the
number of concurrent operations issued increases linearly to the maximum
at the specified maximum percentage of the dirty data allowed in the
pool.

Ideally, the amount of dirty data on a busy pool will stay in the sloped
part of the function between
zfs_vdev_async_write_active_min_dirty_percent and
zfs_vdev_async_write_active_max_dirty_percent. If it exceeds the maximum
percentage, this indicates that the rate of incoming data is greater
than the rate that the backend storage can handle. In this case, we must
further throttle incoming writes, as described in the next section.
