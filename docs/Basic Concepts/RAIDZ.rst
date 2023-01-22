RAIDZ
=====

tl;dr: RAIDZ is effective for large block sizes and sequential workloads.

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

A raidz group with N disks of size X with P parity disks can hold
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
  splitted equally via ``sector size`` parts
  and written on each stripe on RAIDZ vdev
- each stripe of data will have a part of block

- in addition to data one, two or three blocks of parity should be written,
  one per disk; so, for raidz2 of 5 disks there will be 3 blocks of data and
  2 blocks of parity

Due to these inputs, if ``recordsize`` is less or equal to sector size,
then RAIDZ's parity size will be effictively equal to mirror with same redundancy.
For example, for raidz1 of 3 disks with ``ashift=12`` and ``recordsize=4K``
we will allocate on disk:

- one 4K block of data

- one 4K padding block

, and usable space ratio will be 50%, same as with double mirror.


Another example for ``ashift=12`` and ``recordsize=128K`` for raidz1 of 3 disks:

- total stripe width is 3

- one stripe can have up to 2 data parts of 4K size because of 1 parity blocks

- we will have 128K/2 = 64 stripes with 8K of data and 4K of parity each

, so usable space ratio in this case will be 66%.


If RAIDZ will have more disks, it's stripe width will be larger, and space
efficiency better too.

You can find actual parity cost per RAIDZ size here:

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/1tf4qx1aMJp8Lo_R6gpT689wTjHv6CGVElrPqTA0w_ZY/pub?embed=true" height="1000px" width="100%"></iframe>

(`source <https://docs.google.com/spreadsheets/d/1tf4qx1aMJp8Lo_R6gpT689wTjHv6CGVElrPqTA0w_ZY/edit>`__)


Performance considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

Write
^^^^^

Because of full stripe width, one block write will write stripe part on each disk.
One RAIDZ vdev has a write IOPS of one slowest disk because of that in worst case.
