Send and Receive
================

``zfs send`` serialises a snapshot into a byte stream, and ``zfs receive``
turns that stream back into a dataset. Together they are ZFS' native
replication and backup mechanism.

Because the stream is produced from ZFS' own block-level bookkeeping, an
incremental send has to read only the blocks that actually changed between two
snapshots — it never walks the directory tree looking for modified files. That
makes replication cost proportional to the amount of changed data rather than
to the size of the dataset, which is the main reason to prefer it over
file-based tools such as ``rsync`` on ZFS.

Streams are checksummed, so corruption introduced by the network or by
intermediate storage is detected on receive.

A full stream
~~~~~~~~~~~~~

Everything starts from a snapshot:

.. code:: bash

   zfs snapshot pool/data@2026-07-21
   zfs send pool/data@2026-07-21 | ssh backup zfs receive tank/data

The receiving side creates ``tank/data`` along with the snapshot
``tank/data@2026-07-21``. The target dataset must not already exist unless
you are receiving an incremental stream into it.

Streams are just bytes, so they can also be stored in a file or piped through
anything:

.. code:: bash

   zfs send pool/data@2026-07-21 | zstd -3 > /mnt/usb/data-full.zfs.zst

Storing streams in files is fine for transport, but it is a poor archive
format: a single damaged byte can render the whole stream unreceivable,
whereas a received dataset is checksummed, scrubable and repairable. Prefer
receiving into a real pool for anything you intend to keep.

Incremental streams
~~~~~~~~~~~~~~~~~~~

``-i`` sends the difference between two snapshots. The source snapshot must
still exist on the receiving side.

.. code:: bash

   zfs snapshot pool/data@2026-07-22
   zfs send -i pool/data@2026-07-21 pool/data@2026-07-22 \
       | ssh backup zfs receive tank/data

``-I`` sends every intermediate snapshot between the two, so the receiving
side ends up with the same snapshot history rather than just the endpoints:

.. code:: bash

   zfs send -I pool/data@2026-07-21 pool/data@2026-07-28 | ...

The incremental source may also be a bookmark, which lets the sending side
free the space held by the old snapshot while still being able to compute the
difference:

.. code:: bash

   zfs bookmark pool/data@2026-07-21 pool/data#2026-07-21
   zfs destroy pool/data@2026-07-21
   zfs send -i pool/data#2026-07-21 pool/data@2026-07-22 | ...

See :doc:`Snapshots, Clones and Bookmarks </Basic Concepts/Datasets/Snapshots and Clones>` for what
bookmarks are.

Replicating a whole hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``-R`` produces a replication stream package: the named dataset and all of its
descendants, up to the named snapshot. On receive, properties, snapshots,
descendant file systems and clones are preserved.

.. code:: bash

   zfs snapshot -r pool/home@2026-07-21
   zfs send -R pool/home@2026-07-21 | ssh backup zfs receive -u tank/home

Combined with ``-i``/``-I`` it becomes the usual "make the destination look
exactly like the source" tool. On the receiving side, ``-F`` then also destroys
snapshots and file systems that no longer exist on the sending side, and rolls
the target back to its most recent snapshot before receiving:

.. code:: bash

   zfs send -R -I pool/home@sunday pool/home@monday \
       | ssh backup zfs receive -F -u tank/home

``-F`` discards data on the destination. Use ``-n -v`` first if you are not
sure what a stream will do.

``-X`` excludes named datasets from a recursive send, and ``-s`` lets a
recursive send skip (with a warning) datasets whose snapshots are missing
instead of aborting.

Useful send options
~~~~~~~~~~~~~~~~~~~

``-c`` (``--compressed``)
    Send blocks that are compressed on disk in their compressed form. The
    stream is smaller and both sides do less work, since nothing has to be
    decompressed and recompressed. This is the usual default choice for
    datasets with compression enabled.

``-L`` (``--large-block``)
    Allow records larger than 128 KiB in the stream. Without it, a dataset
    with a larger ``recordsize`` is sent as smaller blocks, which is slower and
    changes the block layout on the receiving side. It has no effect if the
    ``large_blocks`` pool feature is disabled or ``recordsize`` was never set
    above 128 KiB.

``-e`` (``--embed``)
    Send blocks that use embedded data (very small blocks stored inside the
    block pointer) in that form. Requires the ``embedded_data`` feature on both
    sides.

``-p`` (``--props``)
    Include dataset properties in the stream. ``-R`` implies this.

``-w`` (``--raw``)
    Send the data exactly as it is on disk. For encrypted datasets this means
    the stream stays encrypted, so a backup can be taken without loading the
    keys, and the receiving machine never needs them. See
    :doc:`Encryption </Basic Concepts/Data Storage/Encryption>`.

``-h`` (``--holds``)
    Include user holds on the sent snapshots.

``-n -v`` / ``-P``
    Dry run with a size estimate; ``-P`` prints it in a machine-parsable form.
    Worth running before any large or destructive transfer.

Useful receive options
~~~~~~~~~~~~~~~~~~~~~~

``-u``
    Do not mount the received file system. On a backup server this is almost
    always what you want — the destination should not shadow local paths.

``-d`` / ``-e``
    Rewrite the target name: ``-d`` drops the first component of the source
    dataset name, ``-e`` keeps only the last one. Both are relative to the
    named target file system.

``-o property=value`` / ``-x property``
    Override a property carried in the stream, or exclude it so the local
    setting (or inheritance) wins. ``-o readonly=on`` on the destination
    prevents accidental writes that would force a rollback on the next
    incremental receive; ``-x mountpoint`` is a common way to keep a backup
    copy from claiming the source's mount point.

``-F``
    Roll the destination back to its most recent snapshot first, and for
    incremental replication streams destroy datasets and snapshots that are
    gone on the sending side.

``-s``
    Save the partially received state if the transfer is interrupted, so it
    can be resumed instead of restarted. See below.

Resuming an interrupted transfer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A multi-terabyte initial replication over an unreliable link does not have to
start over. When the receiving side used ``-s``, the partially received state
is kept and exposed as the ``receive_resume_token`` property of the target
dataset:

.. code:: bash

   # receiving side
   zfs receive -s tank/data
   # ... connection dies ...
   zfs get -H -o value receive_resume_token tank/data

   # sending side, with that token
   zfs send -t <token> | ssh backup zfs receive -s tank/data

This requires the ``extensible_dataset`` feature on the receiving pool. An
abandoned partial receive can be cleaned up with ``zfs receive -A``, which
frees the space it holds.

Practical notes
~~~~~~~~~~~~~~~

**Keep a common snapshot.** Retention on both sides must leave at least one
snapshot (or bookmark on the sender) in common, otherwise the next incremental
fails and a full resend is needed.

**Do not modify the destination.** Any write breaks the next incremental
receive until the dataset is rolled back; ``readonly=on`` avoids it.

**ssh is often the bottleneck.** Both send and receive are bursty, so
buffering the pipe on both sides (``mbuffer``, ``dd`` with a large block size)
usually helps.

**Feature options must match.** Streams made with ``-L``, ``-c``, ``-e`` or
``-w`` need the corresponding features on the receiving pool.

Doing the snapshot, retention, hold and resume-token bookkeeping by hand gets
tedious. Third-party tools built on ``zfs send``/``receive`` handle it — see
:ref:`scheduling snapshots <snapshot-scheduling>`, since the same tools
usually do both.

See the :doc:`FAQ </Project and Community/FAQ>` for stream caveats such as
``hole_birth``.

Further reading
~~~~~~~~~~~~~~~

* `zfs-send(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-send.8.html>`__,
  `zfs-receive(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-receive.8.html>`__
* `zfs-bookmark(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-bookmark.8.html>`__
* `zfs-redact(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-redact.8.html>`__ —
  sending a stream with selected data removed
* `zstream(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zstream.8.html>`__ —
  inspecting and manipulating stream files
* :doc:`FAQ: Sending and Receiving Streams </Project and Community/FAQ>`
