Changing Pool Layout
====================

Pools are not immutable, but the operations available differ sharply by vdev
type — and some of them are one-way. This page collects what can be added,
grown, replaced, and taken back out.

See :doc:`VDEVs </Basic Concepts/Pool Structure/VDEVs>` for the vocabulary and :doc:`RAIDZ </Basic Concepts/Pool Structure/RAIDZ>` for
raidz geometry.

Adding capacity
~~~~~~~~~~~~~~~

``zpool add`` appends a new top-level vdev. The pool stripes across all
top-level vdevs, so the new one starts taking writes immediately, but existing
data is not rebalanced.

.. code:: bash

   zpool add pool mirror sdc sdd
   zpool add -n pool mirror sdc sdd     # dry run — print the resulting layout

Match the new vdev's redundancy to the existing ones. ``zpool add`` will warn
about a mismatch (adding a bare disk to a mirrored pool, say); overriding that
warning with ``-f`` gives the pool a single point of failure that cannot be
undone if raidz is involved.

Growing existing vdevs
~~~~~~~~~~~~~~~~~~~~~~

**Bigger disks.** Replace each device in a vdev with a larger one, one at a
time, waiting for each resilver. Space becomes available only once *every*
device in that mirror or raidz group has been replaced.

.. code:: bash

   zpool set autoexpand=on pool          # default is off
   zpool replace pool sda sdX
   # ...or, after growing a LUN underneath:
   zpool online -e pool sda

``autoexpand=on`` resizes the pool automatically when a device grows;
otherwise ``zpool online -e`` does it explicitly.

**RAIDZ expansion.** A device can be attached to an existing raidz vdev to
widen it:

.. code:: bash

   zpool attach pool raidz2-0 sdX

This reads all allocated data and rewrites it across the wider group;
``zpool status`` shows the progress. Redundancy is maintained throughout, and
the expansion pauses if a disk fails until the vdev is healthy again. Points
to be clear about:

* Fault tolerance does not change — a RAID-Z2 stays a RAID-Z2.
* Old blocks keep their original data-to-parity ratio, just spread over more
  disks; only new blocks use the wider ratio. Reported free space may
  therefore be slightly pessimistic until old data is rewritten.
* A raidz vdev can be expanded more than once.

Mirrors
~~~~~~~

``zpool attach`` on a mirror or a plain device adds another side: a single
disk becomes a two-way mirror, a two-way becomes three-way. The new device
resilvers immediately and any running scrub is cancelled. ``zpool detach``
removes a side.

.. code:: bash

   zpool attach pool sda sdb        # sda becomes a two-way mirror
   zpool attach -s pool sda sdb     # sequential reconstruction, then auto-scrub
   zpool detach pool sdb

``zpool split`` peels one device off every mirror into a new pool — an
instant, consistent copy of the whole pool. Every top-level vdev must be a
mirror and no resilver may be in progress.

.. code:: bash

   zpool split pool newpool

Replacing a failed device
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   zpool replace pool sda sdX       # new device in a different slot
   zpool replace pool sda           # same slot, device already swapped
   zpool set autoreplace=on pool

``autoreplace=on`` makes ZFS format and replace any new device appearing in
the physical location of one that previously belonged to the pool; the default
is ``off``. See
:doc:`Scrub and Resilver </Basic Concepts/Operations/Scrub and Resilver>` for
what happens next.

Hot spares
~~~~~~~~~~

A ``spare`` vdev sits idle until an active device fails, then takes its place
automatically.

.. code:: bash

   zpool create pool mirror sda sdb spare sdc
   zpool add pool spare sdd
   zpool remove pool sdd

Once a spare steps in, a new ``spare`` vdev appears in the configuration and
stays there until the original device is replaced for real — at which point
the spare goes back to being available. So a spare is a stopgap that buys
time, not a replacement: the failed disk still has to be swapped.

.. code:: bash

   zpool replace pool sda sdNEW    # then the spare frees itself
   zpool detach pool sdc           # cancel an in-progress spare replacement

Detaching the *original faulted device* instead makes the spare assume its
place permanently, and removes it from the spare list of every pool using it.

Spares can be shared between pools, and that carries real risk: a pool
currently using a shared spare cannot be exported, and if two pools are
imported on different hosts and both lose a device at once, both may claim
the same spare — which is not detected and can corrupt data. Share spares
only within one host.

dRAID has its own integrated distributed spare capacity, which resilvers far
faster; see :doc:`dRAID <dRAID Howto>`.

Removing devices
~~~~~~~~~~~~~~~~

``zpool remove`` handles hot spares, cache and log devices trivially. Removing
a **top-level data vdev** is the constrained case: it evacuates the vdev by
copying its allocated data elsewhere, in the background, and permanently
shrinks the pool.

.. code:: bash

   zpool remove pool mirror-1
   zpool remove -n -p pool mirror-1     # estimate the mapping table cost first
   zpool status pool                    # follow the evacuation

It works only if all of these hold:

* the pool contains **no** top-level raidz or draid vdev,
* all top-level vdevs have the same ``ashift``,
* keys for all encrypted datasets are loaded,
* the ``device_removal`` feature is enabled.

Removal leaves behind an in-memory mapping table for the relocated blocks,
which costs RAM for the life of the pool — ``-n -p`` reports how much. An I/O
error during evacuation cancels the removal.

To take a device out of a mirror, use ``zpool detach``, not ``remove``.

.. warning::

   **A raidz pool cannot shrink.** If the pool has any raidz or draid
   top-level vdev, no top-level vdev can ever be removed — including a
   ``special`` or ``dedup`` vdev added later, and including a plain disk added
   by mistake. The only fix is to recreate the pool and restore the data.
   Always ``zpool add -n`` first.

Import and export
~~~~~~~~~~~~~~~~~

.. code:: bash

   zpool export pool
   zpool import                     # list importable pools
   zpool import pool
   zpool import -d /dev/disk/by-id pool
   zpool import -o readonly=on -N pool

Exporting flushes everything and marks the pool as cleanly detached, which is
what makes moving it to another system safe. ``-d`` chooses which device paths
to scan — using ``/dev/disk/by-id`` avoids the classic problem of ``sdX``
names shuffling between boots. See the FAQ on
:doc:`selecting /dev/ names </Project and Community/FAQ>`.

Checkpoints
~~~~~~~~~~~

A pool checkpoint is a whole-pool undo point, intended for risky
administrative operations such as an upgrade:

.. code:: bash

   zpool checkpoint pool
   # ...if it went badly:
   zpool export pool
   zpool import --rewind-to-checkpoint pool
   # ...if it went well:
   zpool checkpoint -d pool

While a checkpoint exists, ``zpool remove``, ``attach``, ``detach``, ``split``
and ``reguid`` are all prohibited, and the space it pins may break reservation
boundaries on a pool short of free space. ``zpool status`` shows that a
checkpoint exists, and ``zpool list`` shows how much space it holds. Discard
it as soon as the operation is confirmed good.

Further reading
~~~~~~~~~~~~~~~

* `zpool-add(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-add.8.html>`__,
  `zpool-attach(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-attach.8.html>`__,
  `zpool-detach(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-detach.8.html>`__
* `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`__,
  `zpool-remove(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-remove.8.html>`__,
  `zpool-split(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-split.8.html>`__
* `zpool-import(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-import.8.html>`__,
  `zpool-export(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-export.8.html>`__,
  `zpool-checkpoint(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-checkpoint.8.html>`__
* `zpoolprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolprops.7.html>`__ —
  ``autoexpand``, ``autoreplace``
