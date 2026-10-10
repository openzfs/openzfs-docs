Block Cloning
=============

Block cloning makes a shallow copy of a file, or part of one: the new file
references the existing data blocks instead of copying them. A later write to
either side takes a private copy of the affected block. This is what
implements *reflinks*, or file-level copy-on-write.

Copying a 50 GiB file becomes near-instant and consumes no additional space,
because no data is read or written — only references are created.

Block cloning requires the ``block_cloning`` pool feature, which becomes
``active`` when the first block is cloned and returns to ``enabled`` when the
last cloned block is freed.

How it is triggered
~~~~~~~~~~~~~~~~~~~

Unlike deduplication, cloning is never automatic — a program has to ask for
it, normally via ``copy_file_range(2)``. Many common tools already do:

.. code:: bash

   cp --reflink=auto bigfile copy       # GNU coreutils
   cp bigfile copy                      # newer versions try this by default

Look for "clone", "reflink" or "dedupe" in a tool's documentation to find out
whether it will attempt block cloning.

Limitations
~~~~~~~~~~~

Blocks cannot be cloned when:

* only part of a block would be cloned — cloning works on whole blocks;
* the data has not been written to disk yet;
* the source and destination ``recordsize`` differ;
* the datasets do not share the same master encryption key.

ZFS does try to clone across datasets, including encrypted ones, but the OS
adds its own restrictions — most versions of Linux will not allow clones
across datasets at all. When cloning is not possible the copy silently falls
back to reading and writing the data, so a ``cp`` that seems slow is usually a
clone that did not happen.

Block cloning vs deduplication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both end up with multiple references to one block, but they are not
alternatives to each other:

+------------------+-------------------------+---------------------------+
|                  | Block cloning           | Deduplication             |
+==================+=========================+===========================+
| Triggered by     | an explicit request     | every write, synchronously|
|                  | from a program          |                           |
+------------------+-------------------------+---------------------------+
| Bookkeeping      | Block Reference Table   | dedup table (DDT)         |
|                  | (BRT), minimal overhead | large, RAM-hungry         |
+------------------+-------------------------+---------------------------+
| Safe to leave on | yes                     | only with careful sizing  |
+------------------+-------------------------+---------------------------+
| Finds duplicates | no — only what it is    | yes, anywhere in the pool |
|                  | told to clone           |                           |
+------------------+-------------------------+---------------------------+

Because the BRT's overhead is minimal, block cloning can reasonably stay
enabled all the time — which is not true of
:doc:`deduplication </Basic Concepts/Data Storage/Deduplication>`.

Checking the savings
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   zpool get bcloneused,bclonesaved,bcloneratio pool
   zdb -T pool          # BRT statistics

``bcloneused`` is the space occupied by cloned blocks, ``bclonesaved`` is what
would have been needed without cloning, and ``bcloneratio`` expresses the same
as a multiplier.

A related feature, ``block_cloning_endian``, corrects an endianness problem in
how BRT entries were originally stored; it activates when the first BRT ZAP is
created so that existing pools stay compatible.

Further reading
~~~~~~~~~~~~~~~

* `zfsconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsconcepts.7.html>`__ —
  ``Block cloning``
* `zpool-features(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpool-features.7.html>`__ —
  ``block_cloning``, ``block_cloning_endian``
* `zpoolprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolprops.7.html>`__ —
  ``bcloneused``, ``bclonesaved``, ``bcloneratio``
* :doc:`Deduplication </Basic Concepts/Data Storage/Deduplication>`,
  :doc:`Snapshots, Clones and Bookmarks </Basic Concepts/Datasets/Snapshots and Clones>`
