Workload Tuning
===============

Below are tips for various workloads.

.. contents:: Table of Contents
  :local:

.. _basic_concepts:

Basic concepts
--------------

Descriptions of ZFS internals that have an effect on application
performance follow.

.. _adaptive_replacement_cache:

Adaptive Replacement Cache
~~~~~~~~~~~~~~~~~~~~~~~~~~

For decades, operating systems have used RAM as a cache to avoid the
necessity of waiting on disk IO, which is extremely slow. This concept
is called page replacement. Until ZFS, virtually all filesystems used
the Least Recently Used (LRU) page replacement algorithm in which the
least recently used pages are the first to be replaced. Unfortunately,
the LRU algorithm is vulnerable to cache flushes, where a brief change
in workload that occurs occasionally removes all frequently used data
from cache. The Adaptive Replacement Cache (ARC) algorithm was
implemented in ZFS to replace LRU. It solves this problem by maintaining
four lists:

#. A list for recently cached entries.
#. A list for recently cached entries that have been accessed more than
   once.
#. A list for entries evicted from #1.
#. A list of entries evicited from #2.

Data is evicted from the first list while an effort is made to keep data
in the second list. In this way, ARC is able to outperform LRU by
providing a superior hit rate.

In addition, a dedicated cache device (typically a SSD) can be added to
the pool, with
``zpool add POOLNAME cache DEVICENAME``. The cache
device is managed by the L2ARC, which scans entries that are next to be
evicted and writes them to the cache device. The data stored in ARC and
L2ARC can be controlled via the ``primarycache`` and ``secondarycache``
zfs properties respectively, which can be set on both zvols and
datasets. Possible settings are ``all``, ``none`` and ``metadata``. It
is possible to improve performance when a zvol or dataset hosts an
application that does its own caching by caching only metadata. One
example is PostgreSQL. Another would be a virtual machine using ZFS.

.. _alignment_shift_ashift:

Alignment Shift (ashift)
~~~~~~~~~~~~~~~~~~~~~~~~

Top-level vdevs contain an internal property called ashift, which stands
for alignment shift. It is set at vdev creation and it is immutable. It
can be read using the ``zdb`` command. It is calculated as the maximum
base 2 logarithm of the physical sector size of any child vdev and it
alters the disk format such that writes are always done according to it.
This makes 2^ashift the smallest possible IO on a vdev. Configuring
ashift correctly is important because partial sector writes incur a
penalty where the sector must be read into a buffer before it can be
written. ZFS makes the implicit assumption that the sector size reported
by drives is correct and calculates ashift based on that.

In an ideal world, physical sector size is always reported correctly and
therefore, this requires no attention. Unfortunately, this is not the
case. The sector size on all storage devices was 512-bytes prior to the
creation of flash-based solid state drives. Some operating systems, such
as Windows XP, were written under this assumption and will not function
when drives report a different sector size.

Flash-based solid state drives came to market around 2007. These devices
report 512-byte sectors, but the actual flash pages, which roughly
correspond to sectors, are never 512-bytes. The early models used
4096-byte pages while the newer models have moved to an 8192-byte page.
In addition, "Advanced Format" hard drives have been created which also
use a 4096-byte sector size. Partial page writes suffer from similar
performance degradation as partial sector writes. In some cases, the
design of NAND-flash makes the performance degradation even worse, but
that is beyond the scope of this description.

Reporting the correct sector sizes is the responsibility the block
device layer. This unfortunately has made proper handling of devices
that misreport drives different across different platforms. The
respective methods are as follows:

-  `sd.conf <http://wiki.illumos.org/display/illumos/ZFS+and+Advanced+Format+disks#ZFSandAdvancedFormatdisks-OverridingthePhysicalBlockSize>`__
   on illumos
-  `gnop(8) <https://www.freebsd.org/cgi/man.cgi?query=gnop&sektion=8&manpath=FreeBSD+10.2-RELEASE>`__
   on FreeBSD; see for example `FreeBSD on 4K sector
   drives <http://web.archive.org/web/20151022020605/http://ivoras.sharanet.org/blog/tree/2011-01-01.freebsd-on-4k-sector-drives.html>`__
   (2011-01-01)
-  `ashift= <https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html#advanced-format-disks>`__
   on ZFS on Linux
-  -o ashift= also works with both MacZFS (pool version 8) and ZFS-OSX
   (pool version 5000).

-o ashift= is convenient, but it is flawed in that the creation of pools
containing top level vdevs that have multiple optimal sector sizes
require the use of multiple commands. `A newer
syntax <http://www.listbox.com/member/archive/182191/2013/07/search/YXNoaWZ0/sort/time_rev/page/2/entry/16:58/20130709002459:82E21654-E84F-11E2-A0FF-F6B47351D2F5/>`__
that will rely on the actual sector sizes has been discussed as a cross
platform replacement and will likely be implemented in the future.

In addition, there is a `database of
drives known to misreport sector
sizes <https://github.com/openzfs/zfs/blob/master/cmd/zpool/os/linux/zpool_vdev_os.c#L98>`__
to the ZFS on Linux project. It is used to automatically adjust ashift
without the assistance of the system administrator. This approach is
unable to fully compensate for misreported sector sizes whenever drive
identifiers are used ambiguously (e.g. virtual machines, iSCSI LUNs,
some rare SSDs), but it does a great amount of good. The format is
roughly compatible with illumos' sd.conf and it is expected that other
implementations will integrate the database in future releases. Strictly
speaking, this database does not belong in ZFS, but the difficulty of
patching the Linux kernel (especially older ones) necessitated that this
be implemented in ZFS itself for Linux. The same is true for MacZFS.
However, FreeBSD and illumos are both able to implement this in the
correct layer.

Compression
~~~~~~~~~~~

Internally, ZFS allocates data using multiples of the device's sector
size, typically either 512 bytes or 4KB (see above). When compression is
enabled, a smaller number of sectors can be allocated for each block.
The uncompressed block size is set by the ``recordsize`` (defaults to
128KB) or ``volblocksize`` (defaults to 8KB) property (for filesystems
vs volumes).

The following compression algorithms are available:

-  LZ4

   -  New algorithm added after feature flags were created. It is
      significantly superior to LZJB in all metrics tested. It is `new
      default compression algorithm <https://github.com/illumos/illumos-gate/commit/db1741f555ec79def5e9846e6bfd132248514ffe>`__
      (compression=on) in OpenZFS.
      It is available on all platforms have as of 2020.

-  LZJB

   -  Original default compression algorithm (compression=on) for ZFS.
      It was created to satisfy the desire for a compression algorithm
      suitable for use in filesystems. Specifically, that it provides
      fair compression, has a high compression speed, has a high
      decompression speed and detects incompressible data detection
      quickly.

-  GZIP (1 through 9)

   -  Classic Lempel-Ziv implementation. It provides high compression,
      but it often makes IO CPU-bound.

-  ZLE (Zero Length Encoding)

   -  A very simple algorithm that only compresses zeroes.

If you want to use compression and are uncertain which to use, use LZ4.
It averages a 2.1:1 compression ratio while gzip-1 averages 2.7:1, but
gzip is much slower. Both figures are obtained from `testing by the LZ4
project <https://github.com/lz4/lz4>`__ on the Silesia corpus. The
greater compression ratio of gzip is usually only worthwhile for rarely
accessed data.

.. _raid_z_stripe_width:

RAID-Z stripe width
~~~~~~~~~~~~~~~~~~~

Choose a RAID-Z stripe width based on your IOPS needs and the amount of
space you are willing to devote to parity information. If you need more
IOPS, use fewer disks per stripe. If you need more usable space, use
more disks per stripe. Trying to optimize your RAID-Z stripe width based
on exact numbers is irrelevant in nearly all cases. See this `blog
post <https://www.delphix.com/blog/delphix-engineering/zfs-raidz-stripe-width-or-how-i-learned-stop-worrying-and-love-raidz/>`__
for more details.

.. _dataset_recordsize:

Dataset recordsize
~~~~~~~~~~~~~~~~~~

ZFS datasets use an internal recordsize of 128KB by default. The dataset
recordsize is the basic unit of data used for internal copy-on-write on
files. Partial record writes require that data be read from either ARC
(cheap) or disk (expensive). recordsize can be set to any power of 2
from 512 bytes to 128 kilobytes. Software that writes in fixed record
sizes (e.g. databases) will benefit from the use of a matching
recordsize.

Changing the recordsize on a dataset will only take effect for new
files. If you change the recordsize because your application should
perform better with a different one, you will need to recreate its
files. A cp followed by a mv on each file is sufficient. Alternatively,
send/recv should recreate the files with the correct recordsize when a
full receive is done.

.. _larger_record_sizes:

Larger record sizes
^^^^^^^^^^^^^^^^^^^

Record sizes of up to 16M are supported with the large_blocks pool
feature, which is enabled by default on new pools on systems that
support it. However, record sizes larger than 1M is disabled by default
unless the zfs_max_recordsize kernel module parameter is set to allow
sizes higher than 1M. Larger record sizes than 1M are not well tested as
1M, although they should work. \`zfs send\` operations must specify -L
to ensure that larger than 128KB blocks are sent and the receiving pools
must support the large_blocks feature.

.. _zvol_volblocksize:

zvol volblocksize
~~~~~~~~~~~~~~~~~

Zvols have a volblocksize property that is analogous to record size. The
default size is 8KB, which is the size of a page on the SPARC
architecture. Workloads that use smaller sized IOs (such as swap on x86
which use 4096-byte pages) will benefit from a smaller volblocksize.

Deduplication
~~~~~~~~~~~~~

Deduplication uses an on-disk hash table, using `extensible
hashing <http://en.wikipedia.org/wiki/Extensible_hashing>`__ as
implemented in the ZAP (ZFS Attribute Processor). Each cached entry uses
slightly more than 320 bytes of memory. The DDT code relies on ARC for
caching the DDT entries, such that there is no double caching or
internal fragmentation from the kernel memory allocator. Each pool has a
global deduplication table shared across all datasets and zvols on which
deduplication is enabled. Each entry in the hash table is a record of a
unique block in the pool. (Where the block size is set by the
``recordsize`` or ``volblocksize`` properties.)

The hash table (also known as the DDT or DeDup Table) must be accessed
for every dedup-able block that is written or freed (regardless of
whether it has multiple references). If there is insufficient memory for
the DDT to be cached in memory, each cache miss will require reading a
random block from disk, resulting in poor performance. For example, if
operating on a single 7200RPM drive that can do 100 io/s, uncached DDT
reads would limit overall write throughput to 100 blocks per second, or
400KB/s with 4KB blocks.

The consequence is that sufficient memory to store deduplication data is
required for good performance. The deduplication data is considered
metadata and therefore can be cached if the ``primarycache`` or
``secondarycache`` properties are set to ``metadata``. In addition, the
deduplication table will compete with other metadata for metadata
storage, which can have a negative effect on performance. Simulation of
the number of deduplication table entries needed for a given pool can be
done using the -D option to zdb. Then a simple multiplication by
320-bytes can be done to get the approximate memory requirements.
Alternatively, you can estimate an upper bound on the number of unique
blocks by dividing the amount of storage you plan to use on each dataset
(taking into account that partial records each count as a full
recordsize for the purposes of deduplication) by the recordsize and each
zvol by the volblocksize, summing and then multiplying by 320-bytes.

.. _metaslab_allocator:

Metaslab Allocator
~~~~~~~~~~~~~~~~~~

ZFS top level vdevs are divided into metaslabs from which blocks can be
independently allocated so allow for concurrent IOs to perform
allocations without blocking one another. At present, `there is a
regression <https://github.com/zfsonlinux/zfs/pull/3643>`__ on the
Linux and Mac OS X ports that causes serialization to occur.

By default, the selection of a metaslab is biased toward lower LBAs to
improve performance of spinning disks, but this does not make sense on
solid state media. This behavior can be adjusted globally by setting the
ZFS module's global metaslab_lba_weighting_enabled tuanble to 0. This
tunable is only advisable on systems that only use solid state media for
pools.

The metaslab allocator will allocate blocks on a first-fit basis when a
metaslab has more than or equal to 4 percent free space and a best-fit
basis when a metaslab has less than 4 percent free space. The former is
much faster than the latter, but it is not possible to tell when this
behavior occurs from the pool's free space. However, the command ``zdb
-mmm $POOLNAME`` will provide this information.

.. _pool_geometry:

Pool Geometry
~~~~~~~~~~~~~

If small random IOPS are of primary importance, mirrored vdevs will
outperform raidz vdevs. Read IOPS on mirrors will scale with the number
of drives in each mirror while raidz vdevs will each be limited to the
IOPS of the slowest drive.

If sequential writes are of primary importance, raidz will outperform
mirrored vdevs. Sequential write throughput increases linearly with the
number of data disks in raidz while writes are limited to the slowest
drive in mirrored vdevs. Sequential read performance should be roughly
the same on each.

Both IOPS and throughput will increase by the respective sums of the
IOPS and throughput of each top level vdev, regardless of whether they
are raidz or mirrors.

.. _whole_disks_versus_partitions:

Whole Disks versus Partitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ZFS will behave differently on different platforms when given a whole
disk.

On illumos, ZFS attempts to enable the write cache on a whole disk. The
illumos UFS driver cannot ensure integrity with the write cache enabled,
so by default Sun/Solaris systems using UFS file system for boot were
shipped with drive write cache disabled (long ago, when Sun was still an
independent company). For safety on illumos, if ZFS is not given the
whole disk, it could be shared with UFS and thus it is not appropriate
for ZFS to enable write cache. In this case, the write cache setting is
not changed and will remain as-is. Today, most vendors ship drives with
write cache enabled by default.

On Linux, the Linux IO elevator is largely redundant given that ZFS has
its own IO elevator.

ZFS will also create a GPT partition table own partitions when given a
whole disk under illumos on x86/amd64 and on Linux. This is mainly to
make booting through UEFI possible because UEFI requires a small FAT
partition to be able to boot the system. The ZFS driver will be able to
tell the difference between whether the pool had been given the entire
disk or not via the whole_disk field in the label.

This is not done on FreeBSD. Pools created by FreeBSD will always have
the whole_disk field set to true, such that a pool imported on another
platform that was created on FreeBSD will always be treated as the whole
disks were given to ZFS.

.. _general_recommendations:

General recommendations
-----------------------

.. _alignment_shift:

Alignment shift
~~~~~~~~~~~~~~~

Make sure that you create your pools such that the vdevs have the
correct alignment shift for your storage device's size. if dealing with
flash media, this is going to be either 12 (4K sectors) or 13 (8K
sectors). For SSD ephemeral storage on Amazon EC2, the proper setting is
12.

.. _atime_updates:

Atime Updates
~~~~~~~~~~~~~

Set either relatime=on or atime=off to minimize IOs used to update
access time stamps. For backward compatibility with a small percentage
of software that supports it, relatime is preferred when available and
should be set on your entire pool. atime=off should be used more
selectively.

.. _free_space:

Free Space
~~~~~~~~~~

Keep pool free space above 10% to avoid many metaslabs from reaching the
4% free space threshold to switch from first-fit to best-fit allocation
strategies. When the threshold is hit, the :ref:`metaslab_allocator` becomes very CPU
intensive in an attempt to protect itself from fragmentation. This
reduces IOPS, especially as more metaslabs reach the 4% threshold.

The recommendation is 10% rather than 5% because metaslabs selection
considers both location and free space unless the global
metaslab_lba_weighting_enabled tunable is set to 0. When that tunable is
0, ZFS will consider only free space, so the the expense of the best-fit
allocator can be avoided by keeping free space above 5%. That setting
should only be used on systems with pools that consist of solid state
drives because it will reduce sequential IO performance on mechanical
disks.

.. _lz4_compression:

LZ4 compression
~~~~~~~~~~~~~~~

Set compression=lz4 on your pools' root datasets so that all datasets
inherit it unless you have a reason not to enable it. Userland tests of
LZ4 compression of incompressible data in a single thread has shown that
it can process 10GB/sec, so it is unlikely to be a bottleneck even on
incompressible data. Furthermore, incompressible data will be stored
without compression such that reads of incompressible data with
compression enabled will not be subject to decompression. Writes are so
fast that in-compressible data is unlikely to see a performance penalty
from the use of LZ4 compression. The reduction in IO from LZ4 will
typically be a performance win.

Note that larger record sizes will increase compression ratios on
compressible data by allowing compression algorithms to process more
data at a time.

.. _nvme_low_level_formatting_link:

NVMe low level formatting
~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`nvme_low_level_formatting`.

.. _pool_geometry_1:

Pool Geometry
~~~~~~~~~~~~~

Do not put more than ~16 disks in raidz. The rebuild times on mechanical
disks will be excessive when the pool is full.

.. _synchronous_io:

Synchronous I/O
~~~~~~~~~~~~~~~

If your workload involves fsync or O_SYNC and your pool is backed by
mechanical storage, consider adding one or more SLOG devices. Pools that
have multiple SLOG devices will distribute ZIL operations across them.
The best choice for SLOG device(s) are likely Optane / 3D XPoint SSDs.
See :ref:`optane_3d_xpoint_ssds`
for a description of them. If an Optane / 3D XPoint SSD is an option,
the rest of this section on synchronous I/O need not be read. If Optane
/ 3D XPoint SSDs is not an option, see
:ref:`nand_flash_ssds` for suggestions
for NAND flash SSDs and also read the information below.

To ensure maximum ZIL performance on NAND flash SSD-based SLOG devices,
you should also overprovison spare area to increase
IOPS [#ssd_iops]_. Only
about 4GB is needed, so the rest can be left as overprovisioned storage.
The choice of 4GB is somewhat arbitrary. Most systems do not write
anything close to 4GB to ZIL between transaction group commits, so
overprovisioning all storage beyond the 4GB partition should be alright.
If a workload needs more, then make it no more than the maximum ARC
size. Even under extreme workloads, ZFS will not benefit from more SLOG
storage than the maximum ARC size. That is half of system memory on
Linux and 3/4 of system memory on illumos.

.. _overprovisioning_by_secure_erase_and_partition_table_trick:

Overprovisioning by secure erase and partition table trick
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can do this with a mix of a secure erase and a partition table
trick, such as the following:

#. Run a secure erase on the NAND-flash SSD.
#. Create a partition table on the NAND-flash SSD.
#. Create a 4GB partition.
#. Give the partition to ZFS to use as a log device.

If using the secure erase and partition table trick, do *not* use the
unpartitioned space for other things, even temporarily. That will reduce
or eliminate the overprovisioning by marking pages as dirty.

Alternatively, some devices allow you to change the sizes that they
report.This would also work, although a secure erase should be done
prior to changing the reported size to ensure that the SSD recognizes
the additional spare area. Changing the reported size can be done on
drives that support it with \`hdparm -N \` on systems that have
laptop-mode-tools.

.. _nvme_overprovisioning:

NVMe overprovisioning
^^^^^^^^^^^^^^^^^^^^^

On NVMe, you can use namespaces to achieve overprovisioning:

#. Do a sanitize command as a precaution to ensure the device is
   completely clean.
#. Delete the default namespace.
#. Create a new namespace of size 4GB.
#. Give the namespace to ZFS to use as a log device. e.g. zfs add tank
   log /dev/nvme1n1

.. _whole_disks:

Whole disks
~~~~~~~~~~~

Whole disks should be given to ZFS rather than partitions. If you must
use a partition, make certain that the partition is properly aligned to
avoid read-modify-write overhead. See the section on
:ref:`Alignment Shift (ashift) <alignment_shift_ashift>`
for a description of proper alignment. Also, see the section on
:ref:`Whole Disks versus Partitions <whole_disks_versus_partitions>`
for a description of changes in ZFS behavior when operating on a
partition.

Single disk RAID 0 arrays from RAID controllers are not equivalent to
whole disks. The :ref:`hardware_raid_controllers` page
explains in detail.

.. _bit_torrent:

Bit Torrent
-----------

Bit torrent performs 16KB random reads/writes. The 16KB writes cause
read-modify-write overhead. The read-modify-write overhead can reduce
performance by a factor of 16 with 128KB record sizes when the amount of
data written exceeds system memory. This can be avoided by using a
dedicated dataset for bit torrent downloads with recordsize=16KB.

When the files are read sequentially through a HTTP server, the random
nature in which the files were generated creates fragmentation that has
been observed to reduce sequential read performance by a factor of two
on 7200RPM hard disks. If performance is a problem, fragmentation can be
eliminated by rewriting the files sequentially in either of two ways:

The first method is to configure your client to download the files to a
temporary directory and then copy them into their final location when
the downloads are finished, provided that your client supports this.

The second method is to use send/recv to recreate a dataset
sequentially.

In practice, defragmenting files obtained through bit torrent should
only improve performance when the files are stored on magnetic storage
and are subject to significant sequential read workloads after creation.

.. _database_workloads:

Database workloads
------------------

Setting ``redundant_metadata=mostly`` can increase IOPS by at least a few
percentage points by eliminating redundant metadata at the lowest level
of the indirect block tree. This comes with the caveat that data loss
will occur if a metadata block pointing to data blocks is corrupted and
there are no duplicate copies, but this is generally not a problem in
production on mirrored or raidz vdevs.

MySQL
~~~~~

InnoDB
^^^^^^

Make separate datasets for InnoDB's data files and log files. Set
``recordsize=16K`` on InnoDB's data files to avoid expensive partial record
writes and leave recordsize=128K on the log files. Set
``primarycache=metadata`` on both to prefer InnoDB's
caching [#mysql_basic]_.
Set ``logbias=throughput`` on the data to stop ZIL from writing twice.

Set ``skip-innodb_doublewrite`` in my.cnf to prevent innodb from writing
twice. The double writes are a data integrity feature meant to protect
against corruption from partially-written records, but those are not
possible on ZFS. It should be noted that `Percona’s
blog had advocated <https://www.percona.com/blog/2014/05/23/improve-innodb-performance-write-bound-loads/>`__
using an ext4 configuration where double writes were
turned off for a performance gain, but later recanted it because it
caused data corruption. Following a well timed power failure, an in
place filesystem such as ext4 can have half of a 8KB record be old while
the other half would be new. This would be the corruption that caused
Percona to recant its advice. However, ZFS’ copy on write design would
cause it to return the old correct data following a power failure (no
matter what the timing is). That prevents the corruption that the double
write feature is intended to prevent from ever happening. The double
write feature is therefore unnecessary on ZFS and can be safely turned
off for better performance.

On Linux, the driver's AIO implementation is a compatibility shim that
just barely passes the POSIX standard. InnoDB performance suffers when
using its default AIO codepath. Set ``innodb_use_native_aio=0`` and
``innodb_use_atomic_writes=0`` in my.cnf to disable AIO. Both of these
settings must be disabled to disable AIO.

PostgreSQL
~~~~~~~~~~

Make separate datasets for PostgreSQL's data and WAL. Set ``recordsize=8K``
on both to avoid expensive partial record writes. Set ``logbias=throughput``
on PostgreSQL's data to avoid writing twice.

SQLite
~~~~~~

Make a separate dataset for the database. Set the recordsize to 64K. Set
the SQLite page size to 65536
bytes [#sqlite_ps]_.

Note that SQLite databases typically are not exercised enough to merit
special tuning, but this will provide it. Note the side effect on cache
size mentioned at
SQLite.org [#sqlite_ps_change]_.

.. _file_servers:

File servers
------------

Create a dedicated dataset for files being served.

See
:ref:`Sequential workloads <sequential_workloads>`
for configuration recommendations.

.. _sequential_workloads:

Sequential workloads
--------------------

Set recordsize=1M on datasets that are subject to sequential workloads.
Read
:ref:`Larger record sizes <larger_record_sizes>`
for documentation on things that should be known before setting 1M
record sizes.

Set compression=lz4 as per the general recommendation for :ref:`LZ4
compression <lz4_compression>`.

.. _video_games_directories:

Video games directories
-----------------------

Create a dedicated dataset, use chown to make it user accessible (or
create a directory under it and use chown on that) and then configure
the game download application to place games there. Specific information
on how to configure various ones is below.

See
:ref:`Sequential workloads <sequential_workloads>`
for configuration recommendations before installing games.

Note that the performance gains from this tuning are likely to be small
and limited to load times. However, the combination of 1M records and
LZ4 will allow more games to be stored, which is why this tuning is
documented despite the performance gains being limited. A steam library
of 300 games (mostly from humble bundle) that had these tweaks applied
to it saw 20% space savings. Both faster load times and significant
space savings are possible on compressible games when this tuning has
been done. Games whose assets are already compressed will see little to
no benefit.

Lutris
~~~~~~

Open the context menu by left clicking on the triple bar icon in the
upper right. Go to "Preferences" and then the "System options" tab.
Change the default installation directory and click save.

Steam
~~~~~

Go to "Settings" -> "Downloads" -> "Steam Library Folders" and use "Add
Library Folder" to set the directory for steam to use to store games.
Make sure to set it to the default by right clicking on it and clicking
"Make Default Folder" before closing the dialogue.

.. _virtual_machines:

Virtual machines
----------------

Virtual machine images on ZFS should be stored using either zvols or raw
files to avoid unnecessary overhead. The recordsize/volblocksize and
guest filesystem should be configured to match to avoid overhead from
partial record modification. This would typically be 4K. If raw files
are used, a separate dataset should be used to make it easy to configure
recordsize independently of other things stored on ZFS.

.. _qemu_kvm_xen:

QEMU / KVM / Xen
~~~~~~~~~~~~~~~~

AIO should be used to maximize IOPS when using files for guest storage.

.. rubric:: Footnotes

.. [#ssd_iops] <http://www.anandtech.com/show/6489/playing-with-op>
.. [#mysql_basic] <https://www.patpro.net/blog/index.php/2014/03/09/2617-mysql-on-zfs-on-freebsd/>
.. [#sqlite_ps] <https://www.sqlite.org/pragma.html#pragma_page_size>
.. [#sqlite_ps_change] <https://www.sqlite.org/pgszchng2016.html>
