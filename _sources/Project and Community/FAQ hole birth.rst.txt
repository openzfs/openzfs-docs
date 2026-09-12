:orphan:

FAQ Hole birth
==============

Short explanation
~~~~~~~~~~~~~~~~~

The hole_birth feature has/had bugs, the result of which is that, if you
do a ``zfs send -i`` (or ``-R``, since it uses ``-i``) from an affected
dataset, the receiver will not see any checksum or other errors, but the
resulting destination snapshot will not match the source.

ZoL versions 0.6.5.8 and 0.7.0-rc1 (and above) default to ignoring the
faulty metadata which causes this issue *on the sender side*.

FAQ
~~~

I have a pool with hole_birth enabled, how do I know if I am affected?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is technically possible to calculate whether you have any affected
files, but it requires scraping zdb output for each file in each
snapshot in each dataset, which is a combinatoric nightmare. (If you
really want it, there is a proof of concept
`here <https://github.com/rincebrain/hole_birth_test>`__.

Is there any less painful way to fix this if we have already received an affected snapshot?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No, the data you need was simply not present in the send stream,
unfortunately, and cannot feasibly be rewritten in place.

Long explanation
~~~~~~~~~~~~~~~~

hole_birth is a feature to speed up ZFS send -i - in particular, ZFS
used to not store metadata on when "holes" (sparse regions) in files
were created, so every zfs send -i needed to include every hole.

hole_birth, as the name implies, added tracking for the txg (transaction
group) when a hole was created, so that zfs send -i could only send
holes that had a birth_time between (starting snapshot txg) and (ending
snapshot txg), and life was wonderful.

Unfortunately, hole_birth had a number of edge cases where it could
"forget" to set the birth_time of holes in some cases, causing it to
record the birth_time as 0 (the value used prior to hole_birth, and
essentially equivalent to "since file creation").

This meant that, when you did a zfs send -i, since zfs send does not
have any knowledge of the surrounding snapshots when sending a given
snapshot, it would see the creation txg as 0, conclude "oh, it is 0, I
must have already sent this before", and not include it.

This means that, on the receiving side, it does not know those holes
should exist, and does not create them. This leads to differences
between the source and the destination.

ZoL versions 0.6.5.8 and 0.7.0-rc1 (and above) default to ignoring this
metadata and always sending holes with birth_time 0, configurable using
the tunable known as ``ignore_hole_birth`` or
``send_holes_without_birth_time``. The latter is what OpenZFS
standardized on. ZoL version 0.6.5.8 only has the former, but for any
ZoL version with ``send_holes_without_birth_time``, they point to the
same value, so changing either will work.
