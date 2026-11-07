Deduplication
=============

Deduplication removes redundant data at the block level: identical blocks are
stored once and shared between files. It is synchronous — every write is
looked up in the dedup table (DDT) before it lands.

.. warning::

   Unless you have a specific reason, do not enable dedup. It is the most
   resource-intensive feature in ZFS, and enabling it on an
   improperly-sized system causes slow I/O, slow administrative operations,
   and in the worst case a pool that cannot be imported because the DDT does
   not fit in memory. Try ``compression`` first —
   see :doc:`Compression </Basic Concepts/Data Storage/Compression>`.

The cost
~~~~~~~~

Every unique block gets a DDT entry. Lookups happen on every write, and the
DDT must be consulted on every free as well. Plan for at least **1.25 GiB of
RAM per 1 TiB of stored data**; the real figure depends on block sizes and how
much of the data is actually duplicated.

Dedup only pays off when the duplication is real and substantial — VM images
from a common base, backup targets receiving many similar systems. For general
file storage, compression usually gives most of the benefit at a fraction of
the cost. Note also that clones and ``zfs send``-based workflows already share
blocks without dedup, as does block cloning (``copy_file_range``).

Enabling it
~~~~~~~~~~~

``dedup`` is a dataset property, so it can be limited to the datasets that
benefit. It defaults to ``off``, and changing it affects only newly-written
data.

.. code:: bash

   zfs set dedup=on pool/vmimages
   zfs set dedup=blake3,verify pool/vmimages

Values are ``off``, ``on``, ``verify``, or an explicit checksum —
``sha256``, ``sha512``, ``skein``, ``edonr`` or ``blake3`` — each optionally
with ``,verify``. The default dedup checksum is ``sha256``. When dedup is
enabled, this checksum overrides the ``checksum`` property.

``verify`` makes ZFS do a byte-for-byte comparison whenever two blocks have
the same signature, at the cost of a read per match. ``verify`` alone means
``sha256,verify``, and it is mandatory with ``edonr``.

Watching the table
~~~~~~~~~~~~~~~~~~

.. code:: bash

   zpool status -D pool
   zpool get dedupratio,dedup_table_size,dedupused,dedupsaved pool
   zdb -DD pool          # detailed DDT histogram

``dedupratio`` is the ratio of storage that would be needed without dedup to
what is actually used; ``dedupsaved`` is the same thing in bytes.

Before turning dedup on, ``zdb -S pool`` simulates the DDT for the data
already in the pool and prints the ratio you would have gotten. If it is not
comfortably above 2x, dedup is not worth it.

Keeping the table bounded
~~~~~~~~~~~~~~~~~~~~~~~~~

The failure mode of dedup is an unbounded DDT. Two mechanisms address it:

**Quota.** The pool property ``dedup_table_quota`` caps the on-disk size of
the DDT. Once reached, no new entries are added — existing entries still have
their reference counts updated. The default is ``auto``, which sizes the limit
from a dedicated dedup vdev if one exists; ``none`` disables the limit. The
enforced size may land slightly above or below the requested value. It applies
to both legacy and fast dedup tables.

.. code:: bash

   zpool set dedup_table_quota=100G pool

**Pruning.** ``zpool ddtprune`` removes older *unique* (non-duplicate) entries
to make room for newer duplicate ones, either by a target percentage of unique
entries or by age in days.

.. code:: bash

   zpool ddtprune -d 30 pool     # entries older than 30 days
   zpool ddtprune -p 25 pool     # 25% of unique entries

**Fast dedup** (the ``fast_dedup`` pool feature) enables the more advanced
dedup table format that these mechanisms are built around. It becomes
``active`` when the first deduplicated block is written to a new dedup table,
and returns to ``enabled`` once all such blocks are freed. Existing pools keep
their legacy tables; a new table is created on pool creation, or when a
dataset with dedup enabled starts using a new checksum.

A **dedicated dedup vdev** (``zpool add pool dedup <device>``) moves the DDT
onto fast storage, which is what makes dedup practical on larger pools. It
should be redundant — losing it loses the pool.

Interaction with encryption
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dedup works on encrypted datasets, but for security a dataset deduplicates
only against itself, its snapshots and its clones. It also leaks which blocks
within a dataset are identical, and adds CPU cost per written block. See
:doc:`Native Encryption </Basic Concepts/Data Storage/Encryption>`.

Turning it off
~~~~~~~~~~~~~~

Setting ``dedup=off`` stops new blocks from being deduplicated, but does not
undo anything: existing blocks stay deduplicated and the DDT stays until they
are all freed. Getting rid of it entirely means rewriting the data — for
example by copying it to a fresh dataset and destroying the old one.

Further reading
~~~~~~~~~~~~~~~

* `zfsconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsconcepts.7.html>`__ —
  ``Deduplication``
* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``dedup``
* `zpoolprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolprops.7.html>`__ —
  ``dedup_table_quota``, ``dedup_table_size``, ``dedupratio``
* `zpool-ddtprune(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-ddtprune.8.html>`__
* :doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`
