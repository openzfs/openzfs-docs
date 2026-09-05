Snapshots, Clones and Bookmarks
===============================

Because ZFS never modifies a block in place, keeping an old version of a
dataset costs nothing more than a reference to the blocks that were live at
that moment. Snapshots, clones and bookmarks are all built on that.

Snapshots
~~~~~~~~~

A snapshot is a read-only copy of a file system or volume at a point in time.
Creating one is nearly instantaneous and initially consumes no additional
space; it starts to account for space as the live dataset diverges and blocks
only the snapshot references can no longer be freed.

Snapshots are atomic — they include every system call that completed before
that point in time. Snapshots created recursively with ``-r`` are all taken at
the same instant, which makes a recursive snapshot usable as one consistent
image across several datasets.

.. code:: bash

   # snapshot a single dataset
   zfs snapshot pool/home/user@monday

   # snapshot a dataset and all of its descendants, atomically
   zfs snapshot -r pool/home@monday

   # list snapshots (they are hidden from plain "zfs list" by default)
   zfs list -t snapshot -r pool/home

``zfs list`` omits snapshots unless ``-t snapshot`` is given; the pool property
``listsnapshots`` (default ``off``) changes that default for a whole pool.

Accessing snapshot contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^

File system snapshots are reachable through the ``.zfs/snapshot`` directory in
the root of the file system, without being mounted explicitly — they are
mounted on demand and unmounted again after a while. This makes restoring a
single file a plain ``cp``:

.. code:: bash

   cp /home/user/.zfs/snapshot/monday/notes.txt /home/user/notes.txt

The ``snapdir`` property controls whether the ``.zfs`` directory is
``disabled``, ``hidden`` (the default — it exists but does not show up in
``ls``) or ``visible``.

For volumes there is no directory to browse. Snapshot device nodes appear
under ``/dev/zvol/<pool>`` when the volume's ``snapdev`` property is set to
``visible``; the default is ``hidden``.

Rolling back
^^^^^^^^^^^^

``zfs rollback`` discards everything written since the snapshot and returns
the dataset to that state. By default it refuses to roll back to anything but
the most recent snapshot:

.. code:: bash

   zfs rollback pool/home/user@monday          # only if it is the newest snapshot
   zfs rollback -r pool/home/user@monday       # also destroy newer snapshots and bookmarks
   zfs rollback -R pool/home/user@monday       # additionally destroy clones of those snapshots

``-r`` and ``-R`` do not recurse into child datasets: only direct snapshots of
the named file system are destroyed. Rolling a recursive snapshot back
completely means rolling back each child dataset individually.

The file system must be unmounted (or unmountable) for a rollback; ``-f`` used
together with ``-R`` forces the unmount of clones that are about to be
destroyed.

Space accounting
^^^^^^^^^^^^^^^^

Two properties answer most "why is my pool full" questions:

* ``used`` on a snapshot is the space that would be freed if *that snapshot
  alone* were destroyed — blocks referenced by no other snapshot and not by
  the live dataset.
* ``usedbysnapshots`` on a dataset is the space that would be freed if *all*
  of its snapshots were destroyed. It is not the sum of the snapshots' ``used``
  values, because space can be shared between several snapshots.

.. code:: bash

   zfs list -o name,used,referenced,usedbysnapshots pool/home/user
   zfs list -t snapshot -o name,used,referenced,written -r pool/home/user

``referenced`` is how much data the snapshot (or dataset) can see, and
``written`` is how much data changed since the previous snapshot — useful for
sizing incremental replication.

A single old snapshot can pin an arbitrary amount of space: if a large file
was deleted after the snapshot was taken, the space stays allocated until the
snapshot goes away.

Holds and deferred destruction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A hold is a named reference that prevents a snapshot from being destroyed.
Replication tools use holds so that the snapshot a stream is based on cannot
disappear mid-transfer.

.. code:: bash

   zfs hold keep pool/home/user@monday
   zfs holds pool/home/user@monday
   zfs release keep pool/home/user@monday

While a hold exists, ``zfs destroy`` on that snapshot fails with ``EBUSY``.
``zfs destroy -d`` marks such a snapshot for deferred destruction instead of
failing: it disappears automatically once the last hold is released and it has
no clones.

Comparing snapshots
^^^^^^^^^^^^^^^^^^^

``zfs diff`` reports what changed between a snapshot and a later snapshot (or
the live file system):

.. code:: bash

   zfs diff pool/home/user@monday pool/home/user@tuesday
   zfs diff pool/home/user@monday

Limiting snapshot counts
^^^^^^^^^^^^^^^^^^^^^^^^

``snapshot_limit`` caps the number of snapshots that may exist on a dataset and
its descendants, and ``snapshot_count`` reports the current number. A limit set
on a descendant does not override an ancestor's limit — it adds to it. The
limit is not enforced against a user who is allowed to change it.

The ``snapshots_changed`` property records when a snapshot of the dataset was
last created or destroyed, which lets monitoring and backup tooling skip
datasets that cannot have changed without walking the whole snapshot list.

.. _snapshot-scheduling:

Taking them on a schedule
^^^^^^^^^^^^^^^^^^^^^^^^^

ZFS creates snapshots but does not schedule or expire them. Something has to
decide when to take one and when to destroy it, or a pool quietly fills with
years of hourlies.

A timer calling ``zfs snapshot -r`` and a second one destroying anything older
than *N* is enough for simple cases. Beyond that, third-party tools handle
retention policies, and the same ones usually handle replication —
``sanoid``/``syncoid``, ``zrepl`` and ``zfstools`` are among the established
ones. None are part of OpenZFS, so treat them as you would any other
dependency holding your backups.

Some tools key off the ``com.sun:auto-snapshot`` user property to decide which
datasets to include, which is why it appears in examples such as the swap zvol
in :doc:`ZVOLs </Basic Concepts/Datasets/ZVOLs>`.

See :doc:`Send and Receive </Basic Concepts/Operations/Send and Receive>` for
the replication side.

Clones
~~~~~~

A clone is a *writable* dataset whose initial contents are those of a
snapshot. Like a snapshot it is created almost instantly and initially
consumes no extra space; it then diverges from its origin as it is written to.

.. code:: bash

   zfs snapshot pool/vm/base@golden
   zfs clone pool/vm/base@golden pool/vm/guest1
   zfs clone pool/vm/base@golden pool/vm/guest2

Clones can only be created from a snapshot, and they create a dependency: the
origin snapshot cannot be destroyed while a clone of it exists. The clone's
``origin`` property names the snapshot it came from, and ``zfs destroy`` lists
such dependencies when it refuses to remove a snapshot.

Promoting a clone
^^^^^^^^^^^^^^^^^

``zfs promote`` reverses the parent/child relationship: the clone becomes the
dataset that owns the shared snapshots, and the former origin becomes a clone
of it. That is what makes it possible to retire the original dataset:

.. code:: bash

   zfs promote pool/vm/guest1
   zfs destroy -r pool/vm/base       # now possible

Typical uses of clones are virtual machine images from a common golden image,
throwaway copies of a production dataset for testing, and recovering from a
mistake without discarding the newer data a rollback would delete.

Bookmarks
~~~~~~~~~

A bookmark is a read-only marker for the point in time a snapshot was taken.
It is even cheaper than a snapshot — it consumes no additional space at all —
but it also holds on to no data: it cannot be browsed, mounted, cloned or
rolled back to.

.. code:: bash

   zfs bookmark pool/home/user@monday pool/home/user#monday
   zfs list -t bookmark -r pool/home/user

The point of a bookmark is incremental replication. To send an incremental
stream, the sending side normally has to keep the previous snapshot around. If
it keeps a bookmark instead, the snapshot itself — and the space it pins — can
be destroyed, and ``zfs send -i`` can still produce the incremental stream:

.. code:: bash

   zfs send -i pool/home/user#monday pool/home/user@tuesday | ...

A bookmark is initially tied to a snapshot, but it survives the destruction of
that snapshot. See :doc:`Send and Receive </Basic Concepts/Operations/Send and Receive>` for how they fit
into a replication workflow.

Further reading
~~~~~~~~~~~~~~~

* `zfsconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsconcepts.7.html>`__
* `zfs-snapshot(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-snapshot.8.html>`__,
  `zfs-rollback(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-rollback.8.html>`__,
  `zfs-destroy(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-destroy.8.html>`__
* `zfs-clone(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-clone.8.html>`__,
  `zfs-promote(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-promote.8.html>`__
* `zfs-bookmark(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-bookmark.8.html>`__
* `zfs-hold(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-hold.8.html>`__,
  `zfs-diff(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-diff.8.html>`__
