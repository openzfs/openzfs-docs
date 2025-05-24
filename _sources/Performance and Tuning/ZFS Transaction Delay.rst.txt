ZFS Transaction Delay
=====================

ZFS write operations are delayed when the backend storage isn't able to
accommodate the rate of incoming writes. This delay process is known as
the ZFS write throttle.

If there is already a write transaction waiting, the delay is relative
to when that transaction will finish waiting. Thus the calculated delay
time is independent of the number of threads concurrently executing
transactions.

If there is only one waiter, the delay is relative to when the
transaction started, rather than the current time. This credits the
transaction for "time already served." For example, if a write
transaction requires reading indirect blocks first, then the delay is
counted at the start of the transaction, just prior to the indirect
block reads.

The minimum time for a transaction to take is calculated as:

::

   min_time = zfs_delay_scale * (dirty - min) / (max - dirty)
   min_time is then capped at 100 milliseconds

The delay has two degrees of freedom that can be adjusted via tunables:

1. The percentage of dirty data at which we start to delay is defined by
   zfs_delay_min_dirty_percent. This is typically be at or above
   zfs_vdev_async_write_active_max_dirty_percent so delays occur after
   writing at full speed has failed to keep up with the incoming write
   rate.
2. The scale of the curve is defined by zfs_delay_scale. Roughly
   speaking, this variable determines the amount of delay at the
   midpoint of the curve.

::

   delay
    10ms +-------------------------------------------------------------*+
         |                                                             *|
     9ms +                                                             *+
         |                                                             *|
     8ms +                                                             *+
         |                                                            * |
     7ms +                                                            * +
         |                                                            * |
     6ms +                                                            * +
         |                                                            * |
     5ms +                                                           *  +
         |                                                           *  |
     4ms +                                                           *  +
         |                                                           *  |
     3ms +                                                          *   +
         |                                                          *   |
     2ms +                                              (midpoint) *    +
         |                                                  |    **     |
     1ms +                                                  v ***       +
         |             zfs_delay_scale ---------->     ********         |
       0 +-------------------------------------*********----------------+
         0%                    <- zfs_dirty_data_max ->               100%

Note that since the delay is added to the outstanding time remaining on
the most recent transaction, the delay is effectively the inverse of
IOPS. Here the midpoint of 500 microseconds translates to 2000 IOPS. The
shape of the curve was chosen such that small changes in the amount of
accumulated dirty data in the first 3/4 of the curve yield relatively
small differences in the amount of delay.

The effects can be easier to understand when the amount of delay is
represented on a log scale:

::

   delay
   100ms +-------------------------------------------------------------++
         +                                                              +
         |                                                              |
         +                                                             *+
    10ms +                                                             *+
         +                                                           ** +
         |                                              (midpoint)  **  |
         +                                                  |     **    +
     1ms +                                                  v ****      +
         +             zfs_delay_scale ---------->        *****         +
         |                                             ****             |
         +                                          ****                +
   100us +                                        **                    +
         +                                       *                      +
         |                                      *                       |
         +                                     *                        +
    10us +                                     *                        +
         +                                                              +
         |                                                              |
         +                                                              +
         +--------------------------------------------------------------+
         0%                    <- zfs_dirty_data_max ->               100%

Note here that only as the amount of dirty data approaches its limit
does the delay start to increase rapidly. The goal of a properly tuned
system should be to keep the amount of dirty data out of that range by
first ensuring that the appropriate limits are set for the I/O scheduler
to reach optimal throughput on the backend storage, and then by changing
the value of zfs_delay_scale to increase the steepness of the curve.
