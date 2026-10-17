RAIDZ
=====

Introduction
~~~~~~~~~~~~

RAIDZ is a variation on RAID-5 that allows for better distribution of parity
and eliminates the RAID-5 “write hole” (in which data and parity become
inconsistent after a power loss).
Data and parity is striped across all disks within a raidz group.

A raidz group can have single, double, or triple parity, meaning that the raidz
group can sustain one, two, or three failures, respectively, without losing any
data. The ``raidz1`` vdev type specifies a single-parity raidz group; the ``raidz2``
vdev type specifies a double-parity raidz group; and the ``raidz3`` vdev type
specifies a triple-parity raidz group. The ``raidz`` vdev type is an alias for
raidz1.

A raidz group of N disks of size X with P parity disks can hold
approximately (N-P)*X bytes and can withstand P devices failing without
losing data. The minimum number of devices in a raidz group is one more
than the number of parity disks. The recommended number is between 3 and 9
to help increase performance.


Space efficiency
~~~~~~~~~~~~~~~~

Actual used space for a block in RAIDZ is based on several points:

- minimal write size is disk sector size (can be set via `ashift` vdev parameter)

- stripe width in RAIDZ is dynamic, and starts with at least one data block part, or up to
  ``disks count`` minus ``parity number`` parts of data block

- one block of data with size of ``recordsize`` is
  split equally via ``sector size`` parts
  and written on each stripe on RAIDZ vdev
- each stripe of data will have a part of block

- in addition to data one, two or three blocks of parity should be written,
  one per disk; so, for raidz2 of 5 disks there will be 3 blocks of data and
  2 blocks of parity

Due to these inputs, if ``recordsize`` is less or equal to sector size,
then RAIDZ's parity size will be effectively equal to mirror with same redundancy.
For example, for raidz1 of 3 disks with ``ashift=12`` and ``recordsize=4K``
we will allocate on disk:

- one 4K block of data

- one 4K parity block

and usable space ratio will be 50%, same as with double mirror.


Another example for ``ashift=12`` and ``recordsize=128K`` for raidz1 of 3 disks:

- total stripe width is 3

- one stripe can have up to 2 data parts of 4K size because of 1 parity blocks

- we will have 128K/8k = 16 stripes with 8K of data and 4K of parity each

- 16 stripes each with 12k, means we write 192k to store 128k

so usable space ratio in this case will be 66%.


The more disks RAIDZ has, the wider the stripe, the greater the space
efficiency.

You can find actual parity cost per RAIDZ size here:

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRDgvK_cjwpLZBQcneGIS2cmEExUgqUQPblUmGGVXgG1zt-2YR3INFiWMMuYnbo5bK94t1aYGbtoLCS/pubhtml?widget=true&amp;headers=false" height="1000px" width="100%"></iframe>

(`source <https://docs.google.com/spreadsheets/d/1_CO8x03VICdiIMulDjQi9NDBd53qFpUreMQVrF1uS28/edit?usp=sharing>`__)


Performance considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

Write
^^^^^

A stripe spans across all drives in the array. A one block write will write the stripe part onto each disk.
A RAIDZ vdev has a write IOPS of the slowest disk in the array in the worst case because the write operation of all stripe parts must be completed on each disk.

Read
^^^^

A read touches only the columns the block actually occupies, not the whole
group. A block of ``N`` sectors that does not fill a complete stripe row is
laid out across ``N`` data columns; the rest of the group is untouched.
Parity is not read at all on a healthy read — it is fetched only when data is
missing, or during a scrub or resilver.

So the width of the vdev is not what decides read behavior — the ratio between
block size and stripe width is:

* When a block spans **all** data columns — the usual case, since the default
  ``recordsize`` of 128 KiB fills any realistic group — every read costs one
  I/O on every data disk. Random-read IOPS then works out roughly the same as
  a single disk's, however wide the group.
* When blocks are **small** relative to the group — a database with
  ``recordsize=8K`` or ``16K`` on a wide vdev — each read lands on only a few
  disks, and concurrent reads to different blocks proceed in parallel. IOPS
  does scale in that regime, at the cost of the poor space efficiency small
  records have on RAIDZ (see above).

Streaming bandwidth scales with the number of data disks in both cases.

The rule of thumb "RAIDZ gives you the IOPS of one disk" is therefore about
the default large-record configuration, not a property of RAIDZ itself. It is
still the right assumption for general-purpose pools, and mirrors remain the
better choice when random-read IOPS is the binding constraint.

One slow disk
"""""""""""""

Because a read completes only when every column it spans has returned, its
latency is that of the slowest disk involved. A single sick drive can
therefore drag down a whole group
(`#9375 <https://github.com/openzfs/zfs/issues/9375>`__).

Since OpenZFS 2.4 this is detected and worked around: a persistently slow
child is put in a *sit out* state, during which reads skip it and reconstruct
its data from parity. Writes still go to it, so redundancy is maintained, and
scrubs always read it. Up to ``nparity`` disks may sit out at once. The period
is set by ``vdev_read_sit_out_secs`` (default 600 s; ``0`` disables detection
entirely). Each sit-out bumps the vdev's ``slow_ios`` counter and posts an
``ereport.fs.zfs.delay`` event.

Expansion
~~~~~~~~~

A raidz vdev can be widened by attaching another device to it:

.. code:: bash

   zpool attach pool raidz2-0 sdX

Fault tolerance is unchanged — a RAID-Z2 stays a RAID-Z2 — and blocks written
before the expansion keep their original data-to-parity ratio, just spread
over more disks. Only newly written blocks use the wider ratio. See
:doc:`Changing Pool Layout </Basic Concepts/Pool Structure/Changing Pool Layout>`.
