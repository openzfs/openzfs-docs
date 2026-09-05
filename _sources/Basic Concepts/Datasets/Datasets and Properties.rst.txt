Datasets and Properties
=======================

A pool is a pile of space; datasets are how it is carved up. Creating a
dataset is cheap and does not preallocate anything, so the usual ZFS practice
is to create many of them — one per workload, per user, per application —
rather than one big file system with directories.

Dataset types
~~~~~~~~~~~~~

**File system**
    A POSIX file system, mounted somewhere. The default type.

**Volume (zvol)**
    A block device exported under ``/dev/zvol/<pool>/<name>``. Used for
    virtual machine disks, iSCSI targets, swap, or file systems ZFS does not
    implement.

**Snapshot** and **bookmark**
    Read-only, covered in
    :doc:`Snapshots, Clones and Bookmarks </Basic Concepts/Datasets/Snapshots and Clones>`.

.. code:: bash

   zfs create pool/home
   zfs create pool/home/alice
   zfs create -V 40G pool/vm/disk0        # a zvol

   zfs list                               # file systems and volumes
   zfs list -t all -r pool                # everything, recursively
   zfs destroy pool/home/alice

Datasets form a hierarchy that mirrors their names, and most properties are
inherited down that hierarchy — which is the main reason to nest them
deliberately.

Properties
~~~~~~~~~~

Everything about a dataset's behavior is a property: where it mounts, how it
compresses, whether it is read-only, how much space it may use.

.. code:: bash

   zfs get all pool/home/alice
   zfs get -r compression,recordsize pool
   zfs get -o name,property,value,source -s local all pool/home

   zfs set compression=zstd pool/home
   zfs inherit compression pool/home/alice     # fall back to the parent's value
   zfs inherit -S compression pool/home/alice  # revert to the received value

Some properties are read-only (``used``, ``available``, ``creation``,
``compressratio``), some can only be set at creation time (``casesensitivity``,
``normalization``, ``encryption``, ``volblocksize``), and the rest can be
changed at any time. Changes to properties that affect how data is written —
``recordsize``, ``compression``, ``checksum``, ``dedup``, ``copies`` — apply
only to newly-written blocks.

Property sources
^^^^^^^^^^^^^^^^

``zfs get`` reports where each value came from:

``local``
    Set directly on this dataset.
``inherited from <dataset>``
    Set on an ancestor.
``default``
    Never set anywhere; the built-in default.
``temporary``
    Set for the current mount only, via a mount option.
``received``
    Carried in a ``zfs receive`` stream.
``none``
    Read-only property with no source.

This is the first thing to check when a dataset does not behave as expected —
a value inherited from three levels up is easy to miss.

Properties worth knowing
~~~~~~~~~~~~~~~~~~~~~~~~

**Layout and mounting**

``mountpoint``
    Where the file system mounts. ``legacy`` hands control to ``/etc/fstab``
    or ``mount``; ``none`` means it is not mounted. Inherited children extend
    the parent's path automatically.
``canmount``
    ``on``, ``off`` or ``noauto``. ``off`` makes a dataset a pure
    property-inheritance container that is never mounted, while still having
    an inheritable ``mountpoint``. ``noauto`` means it mounts only when asked
    explicitly — the basis of boot environments.
``readonly``
    Blocks writes to the dataset. Standard on replication targets.

**Data layout**

``recordsize``
    The maximum block size for a file system. Default 128 KiB; matching it to
    the application's I/O size matters for databases and VM images.
``volblocksize``
    The fixed block size of a zvol. Set at creation only.
``compression``, ``checksum``, ``dedup``, ``copies``
    See :doc:`Compression </Basic Concepts/Data Storage/Compression>`,
    :doc:`Checksums </Basic Concepts/Data Storage/Checksums>` and :doc:`Deduplication </Basic Concepts/Data Storage/Deduplication>`.

**Behavior**

``atime`` / ``relatime``
    Access-time updates. ``atime=off`` removes a write for every read;
    ``relatime=on`` is the usual compromise.
``sync``
    ``standard``, ``always``, or ``disabled``. ``disabled`` ignores fsync —
    it does not corrupt the pool, but it does lose recently written data on a
    crash.
``exec``, ``setuid``, ``devices``
    The usual mount-option semantics, as properties.
``sharenfs``, ``sharesmb``
    Export the dataset; see :doc:`Sharing datasets </Basic Concepts/Operations/Sharing>`.
``quota``, ``refquota``, ``reservation``, ``refreservation``
    See :doc:`Quotas and Reservations </Basic Concepts/Datasets/Quotas and Reservations>`.

**Space accounting**

``used``
    Space charged to this dataset and its descendants.
``referenced``
    Space reachable from this dataset alone — what a snapshot of it would
    reference.
``available``
    Space still usable, after quotas and reservations.
``logicalused`` / ``logicalreferenced``
    The same before compression.
``usedby*``
    ``usedbydataset``, ``usedbysnapshots``, ``usedbychildren`` and
    ``usedbyrefreservation`` break ``used`` down — the fastest way to find
    where space went.

.. code:: bash

   zfs list -o name,used,usedbydataset,usedbysnapshots,usedbychildren -r pool

User properties
~~~~~~~~~~~~~~~

Arbitrary properties can be attached to datasets for use by tooling. They have
no effect on ZFS itself. A user property name must contain a colon, which is
what distinguishes it from a native one; the convention is
``module:property``, with the module part typically a reversed domain name.

.. code:: bash

   zfs set com.example:backup=daily pool/home
   zfs get -r -o name,value com.example:backup pool

Because they inherit like native properties, user properties are a convenient
way to drive snapshot and replication policy from the dataset tree itself.

Further reading
~~~~~~~~~~~~~~~

* `zfsconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsconcepts.7.html>`__
* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  the complete property reference
* `zfs-create(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-create.8.html>`__,
  `zfs-get(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-get.8.html>`__,
  `zfs-set(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-set.8.html>`__,
  `zfs-inherit(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-inherit.8.html>`__
* :doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`
