Compression
===========

ZFS compresses transparently, per record, per dataset. On most workloads
compression is a net win even on fast storage: less data written means fewer
I/Os, and modern algorithms compress faster than a disk can absorb the
difference.

Since OpenZFS 2.2.0 the ``compression`` property defaults to ``on``, so new
datasets are compressed unless you say otherwise. Pools and datasets created
under older releases defaulted to ``off`` and keep that setting — check
before assuming.

.. code:: bash

   zfs get -r compression pool             # what is actually set, and where from
   zfs set compression=zstd pool/data
   zfs set compression=off pool/incompressible

Changing the property affects only newly-written data. Existing blocks keep
whatever they were written with; rewriting them (``zfs send | zfs recv``, a
copy, or `zfs-rewrite(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-rewrite.8.html>`__)
is what re-compresses them.

Algorithms
~~~~~~~~~~

``on``
    The default. Unlike every other value it is not a fixed algorithm — it is
    ``lz4`` when the ``lz4_compress`` feature is enabled, otherwise ``lzjb``,
    and it may change as new algorithms are added.

``lz4``
    Very fast in both directions with a moderate ratio. The safe default for
    almost everything. Requires the ``lz4_compress`` feature.

``zstd`` / ``zstd-N``
    Higher ratios at higher CPU cost. ``N`` runs from 1 (fastest) to 19; plain
    ``zstd`` is ``zstd-3``. ``zstd-fast-N`` maps to negative zstd levels, with
    ``N`` in 1–10, 20, 30, …, 100, 500, 1000 — higher ``N`` means faster and
    weaker. ``zstd-fast`` is ``zstd-fast-1``.

``gzip`` / ``gzip-N``
    ``N`` from 1 to 9; plain ``gzip`` is ``gzip-6``. Largely superseded by
    ``zstd``, which gives similar ratios much faster.

``lzjb``
    The original algorithm, kept for compatibility.

``zle``
    Compresses runs of zeros only.

In practice: ``lz4`` when latency and CPU matter, ``zstd`` (level 3–7) when
capacity matters, ``off`` only for data that is already compressed or
encrypted.

How much actually gets saved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blocks are allocated in whole sectors of 2\ :sup:`ashift` bytes, and a
compressed record is rounded up to a sector boundary. If compression saves
less than one whole sector, the block is stored uncompressed. There is also a
12.5% minimum-saving threshold on top of the rounding.

The consequence is that small records compress poorly in accounting terms:
with ``recordsize=16K`` and 4K sectors, a record is four sectors, so
compression has to save at least 25% before any space is saved on disk. Large
records give compression more room to work.

Regardless of the algorithm, any setting other than ``off`` detects
all-zero blocks and stores them as holes.

Checking the result
~~~~~~~~~~~~~~~~~~~

.. code:: bash

   zfs get compression,compressratio,refcompressratio pool/data
   zfs list -o name,used,logicalused,compressratio -r pool

``compressratio`` is a multiplier over the dataset's ``used`` space including
descendants; ``refcompressratio`` covers only ``referenced`` space. Comparing
``logicalused`` with ``used`` shows the same thing in bytes.

Interaction with other features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Compression happens **before** encryption, so ratios are preserved on
  encrypted datasets. See :doc:`Native Encryption </Basic Concepts/Data Storage/Encryption>` for the
  CRIME-style caveat that follows from this.
* ``zfs send -c`` sends already-compressed blocks in their compressed form —
  smaller streams and less CPU on both sides. See
  :doc:`Send and Receive </Basic Concepts/Operations/Send and Receive>`.
* Compression interacts with ``recordsize``; see
  :doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`.

Further reading
~~~~~~~~~~~~~~~

* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``compression``, ``compressratio``, ``logicalused``
* :doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`
