ZVOLs
=====

A zvol is a dataset exported as a block device instead of a file system. It
gets everything else a dataset gets — checksums, compression, snapshots,
clones, replication, encryption — while presenting a raw device to whatever
consumes it: a virtual machine disk, an iSCSI LUN, a file system ZFS does not
implement, or swap.

.. code:: bash

   zfs create -V 40G pool/vm/disk0
   ls -l /dev/zvol/pool/vm/disk0

Sizing: ``volsize`` and ``volblocksize``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``volsize``
    The logical size of the device. It must be a multiple of
    ``volblocksize`` and cannot be zero. It can be changed later, but
    shrinking it is as dangerous as shrinking any block device under a live
    file system.

``volblocksize``
    The fixed block size. **Set at creation only** — there is no changing it
    afterwards short of recreating the volume and copying the data. Valid
    values are powers of two from 512 B to 16 MiB; the default is 16 KiB.

Unlike a file system's ``recordsize``, which is a maximum that ZFS varies per
file, ``volblocksize`` is fixed for every block in the volume. That makes it
the single most consequential zvol decision.

The guiding rule is to match the consumer's I/O size:

* too **small**, and each guest I/O costs more metadata, and RAIDZ space
  efficiency collapses — small blocks on RAIDZ approach mirror-level overhead
  (see :doc:`RAIDZ </Basic Concepts/Pool Structure/RAIDZ>`);
* too **large**, and every small write becomes a read-modify-write of the
  whole block, and compression works on data the guest did not change.

For a guest file system using 4 KiB blocks, values between 8 KiB and 64 KiB
are the usual range; the default 16 KiB is a reasonable starting point. See
:doc:`Workload Tuning </Performance and Tuning/Workload Tuning>` for
per-workload advice.

Sparse versus thick
~~~~~~~~~~~~~~~~~~~

By default, creating a volume also establishes a ``refreservation`` equal to
its size, so the space is guaranteed up front. The reservation is kept equal
to the logical size deliberately: without it the volume can run out of space
mid-write, which most consumers handle badly.

``zfs create -s`` creates a **sparse** volume with no reservation:

.. code:: bash

   zfs create -s -V 100G pool/vm/thin      # sparse
   zfs create -V 100G pool/vm/thick        # reserved

   zfs set refreservation=auto pool/vm/thin   # make it thick afterwards
   zfs set refreservation=none pool/vm/thick  # make it sparse afterwards

``refreservation=auto`` is supported only on volumes and reserves enough for
the whole ``volsize`` plus metadata.

Sparse volumes let you overcommit, at the price that a write can fail with
``ENOSPC`` when the pool fills — and the guest will see that as a hardware
error, not as a full disk. Overcommitting means you must monitor pool space.

Note also that snapshots of a thick volume need room for the reservation, so
``volsize`` is not the whole cost. See
:doc:`Quotas and Reservations </Basic Concepts/Datasets/Quotas and Reservations>`.

How the device appears
~~~~~~~~~~~~~~~~~~~~~~

``volmode`` controls what the OS sees:

``full`` (alias ``geom``)
    A complete block device, partitions scanned and exposed.
``dev``
    The device without its partitions. Usually what you want for a VM disk or
    a LUN — the host has no business scanning the guest's partition table.
``none``
    Not exposed outside ZFS at all. Still snapshottable, clonable and
    replicable, which suits a pure backup target.
``default``
    Follow the system-wide ``zvol_volmode`` tunable.

Snapshot devices appear under ``/dev/zvol/<pool>`` only when ``snapdev`` is
``visible``; the default is ``hidden``. There is no ``.zfs/snapshot``
directory for volumes — to reach the contents of a volume snapshot, clone it
and mount the clone.

Reservations, snapshots and space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A zvol's ``used`` can exceed what the guest believes it is using, sometimes
dramatically. The reason is that ZFS has no way to know a block has been
freed inside the guest's file system unless it is told: file systems tend to
allocate into fresh blocks rather than reuse freed ones, so over time ZFS ends
up referencing every block the guest ever touched.

The fix is discard/TRIM from the consumer:

* mount the guest file system with ``discard``, or run ``fstrim``
  periodically;
* issue the trim **before** taking a snapshot, or the snapshot pins blocks
  the guest already considers free.

See :doc:`TRIM </Basic Concepts/Operations/TRIM>` and the
:doc:`FAQ </Project and Community/FAQ>` entry on zvol space usage.

Swap on a zvol
~~~~~~~~~~~~~~

Possible, but it needs care, and on Linux it can still deadlock under memory
pressure — see `issue #7734 <https://github.com/openzfs/zfs/issues/7734>`__.
If you do it:

.. code:: bash

   zfs create -V 4G -b $(getconf PAGESIZE) \
       -o logbias=throughput -o sync=always \
       -o primarycache=metadata \
       -o com.sun:auto-snapshot=false rpool/swap

Match ``volblocksize`` to the page size, keep swap data out of the ARC, and
never snapshot a swap device.

Further reading
~~~~~~~~~~~~~~~

* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``volsize``, ``volblocksize``, ``volmode``, ``refreservation``, ``snapdev``
* `zfs-create(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-create.8.html>`__
* :doc:`Datasets and Properties </Basic Concepts/Datasets/Datasets and Properties>`,
  :doc:`Sharing Datasets </Basic Concepts/Operations/Sharing>`
* :doc:`Workload Tuning </Performance and Tuning/Workload Tuning>` —
  virtual machine and database sections
