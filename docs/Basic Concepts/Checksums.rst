Checksums and Their Use in ZFS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

End-to-end checksums are a key feature of ZFS and an important
differentiator for ZFS over other RAID implementations and filesystems.
Advantages of end-to-end checksums include:

-  detects data corruption upon reading from media
-  blocks that are detected as corrupt are automatically repaired if
   possible, by using the RAID protection in suitably configured pools,
   or redundant copies (see the zfs ``copies`` property)
-  periodic scrubs can check data to detect and repair latent media
   degradation (bit rot) and corruption from other sources
-  checksums on ZFS replication streams, ``zfs send`` and
   ``zfs receive``, ensure the data received is not corrupted by
   intervening storage or transport mechanisms

Checksum Algorithms
^^^^^^^^^^^^^^^^^^^

The checksum algorithms in ZFS can be changed for datasets (filesystems
or volumes). The checksum algorithm used for each block is stored in the
block pointer (metadata). The block checksum is calculated when the
block is written, so changing the algorithm only affects writes
occurring after the change.

The checksum algorithm for a dataset can be changed by setting the
``checksum`` property:

.. code:: bash

   zfs set checksum=sha256 pool_name/dataset_name

+-----------+--------------+------------------------+-------------------------+
| Checksum  | Ok for dedup | Compatible with        | Notes                   |
|           | and nopwrite?| other ZFS              |                         |
|           |              | implementations?       |                         |
+===========+==============+========================+=========================+
| on        | see notes    | yes                    | ``on`` is a             |
|           |              |                        | short hand for          |
|           |              |                        | ``fletcher4``           |
|           |              |                        | for non-deduped         |
|           |              |                        | datasets and            |
|           |              |                        | ``sha256`` for          |
|           |              |                        | deduped                 |
|           |              |                        | datasets                |
+-----------+--------------+------------------------+-------------------------+
| off       | no           | yes                    | Do not do use           |
|           |              |                        | ``off``                 |
+-----------+--------------+------------------------+-------------------------+
| fletcher2 | no           | yes                    | Deprecated              |
|           |              |                        | implementation          |
|           |              |                        | of Fletcher             |
|           |              |                        | checksum, use           |
|           |              |                        | ``fletcher4``           |
|           |              |                        | instead                 |
+-----------+--------------+------------------------+-------------------------+
| fletcher4 | no           | yes                    | Fletcher                |
|           |              |                        | algorithm, also         |
|           |              |                        | used for                |
|           |              |                        | ``zfs send``            |
|           |              |                        | streams                 |
+-----------+--------------+------------------------+-------------------------+
| sha256    | yes          | yes                    | Default for             |
|           |              |                        | deduped                 |
|           |              |                        | datasets                |
+-----------+--------------+------------------------+-------------------------+
| noparity  | no           | yes                    | Do not use              |
|           |              |                        | ``noparity``            |
+-----------+--------------+------------------------+-------------------------+
| sha512    | yes          | requires pool          | salted                  |
|           |              | feature                | ``sha512``              |
|           |              | ``org.illumos:sha512`` | currently not           |
|           |              |                        | supported for           |
|           |              |                        | any filesystem          |
|           |              |                        | on the boot             |
|           |              |                        | pools                   |
+-----------+--------------+------------------------+-------------------------+
| skein     | yes          | requires pool          | salted                  |
|           |              | feature                | ``skein``               |
|           |              | ``org.illumos:skein``  | currently not           |
|           |              |                        | supported for           |
|           |              |                        | any filesystem          |
|           |              |                        | on the boot             |
|           |              |                        | pools                   |
+-----------+--------------+------------------------+-------------------------+
| edonr     | see notes    | requires pool          | salted                  |
|           |              | feature                | ``edonr``               |
|           |              | ``org.illumos:edonr``  | currently not           |
|           |              |                        | supported for           |
|           |              |                        | any filesystem          |
|           |              |                        | on the boot             |
|           |              |                        | pools                   |
|           |              |                        |                         |
|           |              |                        | In an abundance of      |
|           |              |                        | caution, Edon-R requires|
|           |              |                        | verification when used  |
|           |              |                        | with dedup, so it will  |
|           |              |                        | automatically use       |
|           |              |                        | ``verify``.             |
|           |              |                        |                         |
+-----------+--------------+------------------------+-------------------------+

Checksum Accelerators
^^^^^^^^^^^^^^^^^^^^^

ZFS has the ability to offload checksum operations to the Intel
QuickAssist Technology (QAT) adapters.

Checksum Microbenchmarks
^^^^^^^^^^^^^^^^^^^^^^^^

Some ZFS features use microbenchmarks when the ``zfs.ko`` kernel module
is loaded to determine the optimal algorithm for checksums. The results
of the microbenchmarks are observable in the ``/proc/spl/kstat/zfs``
directory. The winning algorithm is reported as the "fastest" and
becomes the default. The default can be overridden by setting zfs module
parameters.

========= ==================================== ========================
Checksum  Results Filename                     ``zfs`` module parameter
========= ==================================== ========================
Fletcher4 /proc/spl/kstat/zfs/fletcher_4_bench zfs_fletcher_4_impl
========= ==================================== ========================

Disabling Checksums
^^^^^^^^^^^^^^^^^^^

While it may be tempting to disable checksums to improve CPU
performance, it is widely considered by the ZFS community to be an
extrodinarily bad idea. Don't disable checksums.
