FAQ
===

.. contents:: Table of Contents
   :local:

What is OpenZFS
---------------

OpenZFS is an outstanding storage platform that
encompasses the functionality of traditional filesystems, volume
managers, and more, with consistent reliability, functionality and
performance across all distributions. Additional information about
OpenZFS can be found in the `OpenZFS wikipedia
article <https://en.wikipedia.org/wiki/OpenZFS>`__.

Hardware Requirements
---------------------

Because ZFS was originally designed for Sun Solaris it was long
considered a filesystem for large servers and for companies that could
afford the best and most powerful hardware available. But since the
porting of ZFS to numerous OpenSource platforms (The BSDs, Illumos and
Linux - under the umbrella organization "OpenZFS"), these requirements
have been lowered.

The suggested hardware requirements are:

-  ECC memory. This isn't really a requirement, but it's highly
   recommended.
-  8GB+ of memory for the best performance. It's perfectly possible to
   run with 2GB or less (and people do), but you'll need more if using
   deduplication.

Do I have to use ECC memory for ZFS?
------------------------------------

Using ECC memory for OpenZFS is strongly recommended for enterprise
environments where the strongest data integrity guarantees are required.
Without ECC memory rare random bit flips caused by cosmic rays or by
faulty memory can go undetected. If this were to occur OpenZFS (or any
other filesystem) will write the damaged data to disk and be unable to
automatically detect the corruption.

Unfortunately, ECC memory is not always supported by consumer grade
hardware. And even when it is, ECC memory will be more expensive. For
home users the additional safety brought by ECC memory might not justify
the cost. It's up to you to determine what level of protection your data
requires.

Installation
------------

OpenZFS is available for FreeBSD and all major Linux distributions. Refer to
the :doc:`getting started <../Getting Started/index>` section of the wiki for
links to installations instructions. If your distribution/OS isn't
listed you can always build OpenZFS from the latest official
`tarball <https://github.com/openzfs/zfs/releases>`__.

Supported Architectures
-----------------------

OpenZFS is regularly compiled for the following architectures:
aarch64, arm, ppc, ppc64, x86, x86_64.

Supported Linux Kernels
-----------------------

The `notes <https://github.com/openzfs/zfs/releases>`__ for a given
OpenZFS release will include a range of supported kernels. Point
releases will be tagged as needed in order to support the *stable*
kernel available from `kernel.org <https://www.kernel.org/>`__. The
oldest supported kernel is 2.6.32 due to its prominence in Enterprise
Linux distributions.

.. _32-bit-vs-64-bit-systems:

32-bit vs 64-bit Systems
------------------------

You are **strongly** encouraged to use a 64-bit kernel. OpenZFS
will build for 32-bit systems but you may encounter stability problems.

ZFS was originally developed for the Solaris kernel which differs from
some OpenZFS platforms in several significant ways. Perhaps most importantly
for ZFS it is common practice in the Solaris kernel to make heavy use of
the virtual address space. However, use of the virtual address space is
strongly discouraged in the Linux kernel. This is particularly true on
32-bit architectures where the virtual address space is limited to 100M
by default. Using the virtual address space on 64-bit Linux kernels is
also discouraged but the address space is so much larger than physical
memory that it is less of an issue.

If you are bumping up against the virtual memory limit on a 32-bit
system you will see the following message in your system logs. You can
increase the virtual address size with the boot option ``vmalloc=512M``.

::

   vmap allocation for size 4198400 failed: use vmalloc=<size> to increase size.

However, even after making this change your system will likely not be
entirely stable. Proper support for 32-bit systems is contingent upon
the OpenZFS code being weaned off its dependence on virtual memory. This
will take some time to do correctly but it is planned for OpenZFS. This
change is also expected to improve how efficiently OpenZFS manages the
ARC cache and allow for tighter integration with the standard Linux page
cache.

Booting from ZFS
----------------

Booting from ZFS on Linux is possible and many people do it. There are
excellent walk throughs available for
:doc:`Debian <../Getting Started/Debian/index>`,
:doc:`Ubuntu <../Getting Started/Ubuntu/index>`, and
`Gentoo <https://github.com/pendor/gentoo-zfs-install/tree/master/install>`__.

On FreeBSD 13+ booting from ZFS is supported out of the box.

Selecting /dev/ names when creating a pool (Linux)
--------------------------------------------------

There are different /dev/ names that can be used when creating a ZFS
pool. Each option has advantages and drawbacks, the right choice for
your ZFS pool really depends on your requirements. For development and
testing using /dev/sdX naming is quick and easy. A typical home server
might prefer /dev/disk/by-id/ naming for simplicity and readability.
While very large configurations with multiple controllers, enclosures,
and switches will likely prefer /dev/disk/by-vdev naming for maximum
control. But in the end, how you choose to identify your disks is up to
you.

-  **/dev/sdX, /dev/hdX:** Best for development/test pools

   -  Summary: The top level /dev/ names are the default for consistency
      with other ZFS implementations. They are available under all Linux
      distributions and are commonly used. However, because they are not
      persistent they should only be used with ZFS for development/test
      pools.
   -  Benefits: This method is easy for a quick test, the names are
      short, and they will be available on all Linux distributions.
   -  Drawbacks: The names are not persistent and will change depending
      on what order the disks are detected in. Adding or removing
      hardware for your system can easily cause the names to change. You
      would then need to remove the zpool.cache file and re-import the
      pool using the new names.
   -  Example: ``zpool create tank sda sdb``

-  **/dev/disk/by-id/:** Best for small pools (less than 10 disks)

   -  Summary: This directory contains disk identifiers with more human
      readable names. The disk identifier usually consists of the
      interface type, vendor name, model number, device serial number,
      and partition number. This approach is more user friendly because
      it simplifies identifying a specific disk.
   -  Benefits: Nice for small systems with a single disk controller.
      Because the names are persistent and guaranteed not to change, it
      doesn't matter how the disks are attached to the system. You can
      take them all out, randomly mix them up on the desk, put them
      back anywhere in the system and your pool will still be
      automatically imported correctly.
   -  Drawbacks: Configuring redundancy groups based on physical
      location becomes difficult and error prone.
   -  Example:
      ``zpool create tank scsi-SATA_Hitachi_HTS7220071201DP1D10DGG6HMRP``

-  **/dev/disk/by-path/:** Good for large pools (greater than 10 disks)

   -  Summary: This approach is to use device names which include the
      physical cable layout in the system, which means that a particular
      disk is tied to a specific location. The name describes the PCI
      bus number, as well as enclosure names and port numbers. This
      allows the most control when configuring a large pool.
   -  Benefits: Encoding the storage topology in the name is not only
      helpful for locating a disk in large installations. But it also
      allows you to explicitly layout your redundancy groups over
      multiple adapters or enclosures.
   -  Drawbacks: These names are long, cumbersome, and difficult for a
      human to manage.
   -  Example:
      ``zpool create tank pci-0000:00:1f.2-scsi-0:0:0:0 pci-0000:00:1f.2-scsi-1:0:0:0``

-  **/dev/disk/by-vdev/:** Best for large pools (greater than 10 disks)

   -  Summary: This approach provides administrative control over device
      naming using the configuration file /etc/zfs/vdev_id.conf. Names
      for disks in JBODs can be generated automatically to reflect their
      physical location by enclosure IDs and slot numbers. The names can
      also be manually assigned based on existing udev device links,
      including those in /dev/disk/by-path or /dev/disk/by-id. This
      allows you to pick your own unique meaningful names for the disks.
      These names will be displayed by all the zfs utilities so it can
      be used to clarify the administration of a large complex pool. See
      the vdev_id and vdev_id.conf man pages for further details.
   -  Benefits: The main benefit of this approach is that it allows you
      to choose meaningful human-readable names. Beyond that, the
      benefits depend on the naming method employed. If the names are
      derived from the physical path the benefits of /dev/disk/by-path
      are realized. On the other hand, aliasing the names based on drive
      identifiers or WWNs has the same benefits as using
      /dev/disk/by-id.
   -  Drawbacks: This method relies on having a /etc/zfs/vdev_id.conf
      file properly configured for your system. To configure this file
      please refer to section `Setting up the /etc/zfs/vdev_id.conf
      file <#setting-up-the-etczfsvdev_idconf-file>`__. As with
      benefits, the drawbacks of /dev/disk/by-id or /dev/disk/by-path
      may apply depending on the naming method employed.
   -  Example: ``zpool create tank mirror A1 B1 mirror A2 B2``

.. _setting-up-the-etczfsvdev_idconf-file:

Setting up the /etc/zfs/vdev_id.conf file
-----------------------------------------

In order to use /dev/disk/by-vdev/ naming the ``/etc/zfs/vdev_id.conf``
must be configured. The format of this file is described in the
vdev_id.conf man page. Several examples follow.

A non-multipath configuration with direct-attached SAS enclosures and an
arbitrary slot re-mapping.

::

               multipath     no
               topology      sas_direct
               phys_per_port 4

               #       PCI_SLOT HBA PORT  CHANNEL NAME
               channel 85:00.0  1         A
               channel 85:00.0  0         B

               #    Linux      Mapped
               #    Slot       Slot
               slot 0          2
               slot 1          6
               slot 2          0
               slot 3          3
               slot 4          5
               slot 5          7
               slot 6          4
               slot 7          1

A SAS-switch topology. Note that the channel keyword takes only two
arguments in this example.

::

               topology      sas_switch

               #       SWITCH PORT  CHANNEL NAME
               channel 1            A
               channel 2            B
               channel 3            C
               channel 4            D

A multipath configuration. Note that channel names have multiple
definitions - one per physical path.

::

               multipath yes

               #       PCI_SLOT HBA PORT  CHANNEL NAME
               channel 85:00.0  1         A
               channel 85:00.0  0         B
               channel 86:00.0  1         A
               channel 86:00.0  0         B

A configuration using device link aliases.

::

               #     by-vdev
               #     name     fully qualified or base name of device link
               alias d1       /dev/disk/by-id/wwn-0x5000c5002de3b9ca
               alias d2       wwn-0x5000c5002def789e

After defining the new disk names run ``udevadm trigger`` to prompt udev
to parse the configuration file. This will result in a new
/dev/disk/by-vdev directory which is populated with symlinks to /dev/sdX
names. Following the first example above, you could then create the new
pool of mirrors with the following command:

::

   $ zpool create tank \
       mirror A0 B0 mirror A1 B1 mirror A2 B2 mirror A3 B3 \
       mirror A4 B4 mirror A5 B5 mirror A6 B6 mirror A7 B7

   $ zpool status
     pool: tank
    state: ONLINE
    scan: none requested
   config:

       NAME        STATE     READ WRITE CKSUM
       tank        ONLINE       0     0     0
         mirror-0  ONLINE       0     0     0
           A0      ONLINE       0     0     0
           B0      ONLINE       0     0     0
         mirror-1  ONLINE       0     0     0
           A1      ONLINE       0     0     0
           B1      ONLINE       0     0     0
         mirror-2  ONLINE       0     0     0
           A2      ONLINE       0     0     0
           B2      ONLINE       0     0     0
         mirror-3  ONLINE       0     0     0
           A3      ONLINE       0     0     0
           B3      ONLINE       0     0     0
         mirror-4  ONLINE       0     0     0
           A4      ONLINE       0     0     0
           B4      ONLINE       0     0     0
         mirror-5  ONLINE       0     0     0
           A5      ONLINE       0     0     0
           B5      ONLINE       0     0     0
         mirror-6  ONLINE       0     0     0
           A6      ONLINE       0     0     0
           B6      ONLINE       0     0     0
         mirror-7  ONLINE       0     0     0
           A7      ONLINE       0     0     0
           B7      ONLINE       0     0     0

   errors: No known data errors

Changing /dev/ names on an existing pool
----------------------------------------

Changing the /dev/ names on an existing pool can be done by simply
exporting the pool and re-importing it with the -d option to specify
which new names should be used. For example, to use the custom names in
/dev/disk/by-vdev:

::

   $ zpool export tank
   $ zpool import -d /dev/disk/by-vdev tank

.. _the-etczfszpoolcache-file:

The /etc/zfs/zpool.cache file
-----------------------------

Whenever a pool is imported on the system it will be added to the
``/etc/zfs/zpool.cache file``. This file stores pool configuration
information, such as the device names and pool state. If this file
exists when running the ``zpool import`` command then it will be used to
determine the list of pools available for import. When a pool is not
listed in the cache file it will need to be detected and imported using
the ``zpool import -d /dev/disk/by-id`` command.

.. _generating-a-new-etczfszpoolcache-file:

Generating a new /etc/zfs/zpool.cache file
------------------------------------------

The ``/etc/zfs/zpool.cache`` file will be automatically updated when
your pool configuration is changed. However, if for some reason it
becomes stale you can force the generation of a new
``/etc/zfs/zpool.cache`` file by setting the cachefile property on the
pool.

::

   $ zpool set cachefile=/etc/zfs/zpool.cache tank

Conversely the cache file can be disabled by setting ``cachefile=none``.
This is useful for failover configurations where the pool should always
be explicitly imported by the failover software.

::

   $ zpool set cachefile=none tank

Sending and Receiving Streams
-----------------------------

hole_birth Bugs
~~~~~~~~~~~~~~~

The hole_birth feature has/had bugs, the result of which is that, if you
do a ``zfs send -i`` (or ``-R``, since it uses ``-i``) from an affected
dataset, the receiver *will not see any checksum or other errors, but
will not match the source*.

ZoL versions 0.6.5.8 and 0.7.0-rc1 (and above) default to ignoring the
faulty metadata which causes this issue *on the sender side*.

For more details, see the :doc:`hole_birth FAQ <./FAQ hole birth>`.

Sending Large Blocks
~~~~~~~~~~~~~~~~~~~~

When sending incremental streams which contain large blocks (>128K) the
``--large-block`` flag must be specified. Inconsistent use of the flag
between incremental sends can result in files being incorrectly zeroed
when they are received. Raw encrypted send/recvs automatically imply the
``--large-block`` flag and are therefore unaffected.

For more details, see `issue
6224 <https://github.com/zfsonlinux/zfs/issues/6224>`__.

CEPH/ZFS
--------

There is a lot of tuning that can be done that's dependent on the
workload that is being put on CEPH/ZFS, as well as some general
guidelines. Some are as follow;

ZFS Configuration
~~~~~~~~~~~~~~~~~

The CEPH filestore back-end heavily relies on xattrs, for optimal
performance all CEPH workloads will benefit from the following ZFS
dataset parameters

-  ``xattr=sa``
-  ``dnodesize=auto``

Beyond that typically rbd/cephfs focused workloads benefit from small
recordsize({16K-128K), while objectstore/s3/rados focused workloads
benefit from large recordsize (128K-1M).

.. _ceph-configuration-cephconf:

CEPH Configuration (ceph.conf}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally CEPH sets various values internally for handling xattrs
based on the underlying filesystem. As CEPH only officially
supports/detects XFS and BTRFS, for all other filesystems it falls back
to rather `limited "safe"
values <https://github.com/ceph/ceph/blob/4fe7e2a458a1521839bc390c2e3233dd809ec3ac/src/common/config_opts.h#L1125-L1148>`__.
On newer releases, the need for larger xattrs will prevent OSD's from even
starting.

The officially recommended workaround (`see
here <http://docs.ceph.com/docs/jewel/rados/configuration/filesystem-recommendations/#not-recommended>`__)
has some severe downsides, and more specifically is geared toward
filesystems with "limited" xattr support such as ext4.

ZFS does not have a limit internally to xattrs length, as such we can
treat it similarly to how CEPH treats XFS. We can set overrides to set 3
internal values to the same as those used with XFS(`see
here <https://github.com/ceph/ceph/blob/9b317f7322848802b3aab9fec3def81dddd4a49b/src/os/filestore/FileStore.cc#L5714-L5737>`__
and
`here <https://github.com/ceph/ceph/blob/4fe7e2a458a1521839bc390c2e3233dd809ec3ac/src/common/config_opts.h#L1125-L1148>`__)
and allow it be used without the severe limitations of the "official"
workaround.

::

   [osd]
   filestore_max_inline_xattrs = 10
   filestore_max_inline_xattr_size = 65536
   filestore_max_xattr_value_size = 65536

Other General Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

-  Use a separate journal device. Do not don't collocate CEPH journal on
   ZFS dataset if at all possible, this will quickly lead to terrible
   fragmentation, not to mention terrible performance upfront even
   before fragmentation (CEPH journal does a dsync for every write).
-  Use a SLOG device, even with a separate CEPH journal device. For some
   workloads, skipping SLOG and setting ``logbias=throughput`` may be
   acceptable.
-  Use a high-quality SLOG/CEPH journal device.  A consumer based SSD, or
   even NVMe WILL NOT DO (Samsung 830, 840, 850, etc) for a variety of
   reasons. CEPH will kill them quickly, on-top of the performance being
   quite low in this use. Generally recommended devices are [Intel DC S3610,
   S3700, S3710, P3600, P3700], or [Samsung SM853, SM863], or better.
-  If using a high quality SSD or NVMe device (as mentioned above), you
   CAN share SLOG and CEPH Journal to good results on single device. A
   ratio of 4 HDDs to 1 SSD (Intel DC S3710 200GB), with each SSD
   partitioned (remember to align!) to 4x10GB (for ZIL/SLOG) + 4x20GB
   (for CEPH journal) has been reported to work well.

Again - CEPH + ZFS will KILL a consumer based SSD VERY quickly. Even
ignoring the lack of power-loss protection, and endurance ratings, you
will be very disappointed with performance of consumer based SSD under
such a workload.

Performance Considerations
--------------------------

To achieve good performance with your pool there are some easy best
practices you should follow.

-  **Evenly balance your disks across controllers:** Often the limiting
   factor for performance is not the disks but the controller. By
   balancing your disks evenly across controllers you can often improve
   throughput.
-  **Create your pool using whole disks:** When running zpool create use
   whole disk names. This will allow ZFS to automatically partition the
   disk to ensure correct alignment. It will also improve
   interoperability with other OpenZFS implementations which honor the
   wholedisk property.
-  **Have enough memory:** A minimum of 2GB of memory is recommended for
   ZFS. Additional memory is strongly recommended when the compression
   and deduplication features are enabled.
-  **Improve performance by setting ashift=12:** You may be able to
   improve performance for some workloads by setting ``ashift=12``. This
   tuning can only be set when block devices are first added to a pool,
   such as when the pool is first created or when a new vdev is added to
   the pool. This tuning parameter can result in a decrease of capacity
   for RAIDZ configurations.

Advanced Format Disks
---------------------

Advanced Format (AF) is a new disk format which natively uses a 4,096
byte, instead of 512 byte, sector size. To maintain compatibility with
legacy systems many AF disks emulate a sector size of 512 bytes. By
default, ZFS will automatically detect the sector size of the drive.
This combination can result in poorly aligned disk accesses which will
greatly degrade the pool performance.

Therefore, the ability to set the ashift property has been added to the
zpool command. This allows users to explicitly assign the sector size
when devices are first added to a pool (typically at pool creation time
or adding a vdev to the pool). The ashift values range from 9 to 16 with
the default value 0 meaning that zfs should auto-detect the sector size.
This value is actually a bit shift value, so an ashift value for 512
bytes is 9 (2^9 = 512) while the ashift value for 4,096 bytes is 12
(2^12 = 4,096).

To force the pool to use 4,096 byte sectors at pool creation time, you
may run:

::

   $ zpool create -o ashift=12 tank mirror sda sdb

To force the pool to use 4,096 byte sectors when adding a vdev to a
pool, you may run:

::

   $ zpool add -o ashift=12 tank mirror sdc sdd

ZVOL used space larger than expected
------------------------------------

| Depending on the filesystem used on the zvol (e.g. ext4) and the usage
  (e.g. deletion and creation of many files) the ``used`` and
  ``referenced`` properties reported by the zvol may be larger than the
  "actual" space that is being used as reported by the consumer.
| This can happen due to the way some filesystems work, in which they
  prefer to allocate files in new untouched blocks rather than the
  fragmented used blocks marked as free. This forces zfs to reference
  all blocks that the underlying filesystem has ever touched.
| This is in itself not much of a problem, as when the ``used`` property
  reaches the configured ``volsize`` the underlying filesystem will
  start reusing blocks. But the problem arises if it is desired to
  snapshot the zvol, as the space referenced by the snapshots will
  contain the unused blocks.

| This issue can be prevented, by issuing the so-called trim
  (for ex. ``fstrim`` command on Linux) to allow
  the kernel to specify to zfs which blocks are unused.
| Issuing a trim before a snapshot is taken will ensure
  a minimum snapshot size.
| For Linux adding the ``discard`` option for the mounted ZVOL in ``/etc/fstab``
  effectively enables the kernel to issue the trim commands
  continuously, without the need to execute fstrim on-demand.

Using a zvol for a swap device on Linux
---------------------------------------

You may use a zvol as a swap device but you'll need to configure it
appropriately.

**CAUTION:** for now swap on zvol may lead to deadlock, in this case
please send your logs
`here <https://github.com/zfsonlinux/zfs/issues/7734>`__.

-  Set the volume block size to match your systems page size. This
   tuning prevents ZFS from having to perform read-modify-write options
   on a larger block while the system is already low on memory.
-  Set the ``logbias=throughput`` and ``sync=always`` properties. Data
   written to the volume will be flushed immediately to disk freeing up
   memory as quickly as possible.
-  Set ``primarycache=metadata`` to avoid keeping swap data in RAM via
   the ARC.
-  Disable automatic snapshots of the swap device.

::

   $ zfs create -V 4G -b $(getconf PAGESIZE) \
       -o logbias=throughput -o sync=always \
       -o primarycache=metadata \
       -o com.sun:auto-snapshot=false rpool/swap

Using ZFS on Xen Hypervisor or Xen Dom0 (Linux)
-----------------------------------------------

It is usually recommended to keep virtual machine storage and hypervisor
pools, quite separate. Although few people have managed to successfully
deploy and run OpenZFS using the same machine configured as Dom0.
There are few caveats:

-  Set a fair amount of memory in grub.conf, dedicated to Dom0.

   -  dom0_mem=16384M,max:16384M

-  Allocate no more of 30-40% of Dom0's memory to ZFS in
   ``/etc/modprobe.d/zfs.conf``.

   -  options zfs zfs_arc_max=6442450944

-  Disable Xen's auto-ballooning in ``/etc/xen/xl.conf``
-  Watch out for any Xen bugs, such as `this
   one <https://github.com/zfsonlinux/zfs/issues/1067>`__ related to
   ballooning

udisks2 creating /dev/mapper/ entries for zvol (Linux)
------------------------------------------------------

To prevent udisks2 from creating /dev/mapper entries that must be
manually removed or maintained during zvol remove / rename, create a
udev rule such as ``/etc/udev/rules.d/80-udisks2-ignore-zfs.rules`` with
the following contents:

::

   ENV{ID_PART_ENTRY_SCHEME}=="gpt", ENV{ID_FS_TYPE}=="zfs_member", ENV{ID_PART_ENTRY_TYPE}=="6a898cc3-1dd2-11b2-99a6-080020736631", ENV{UDISKS_IGNORE}="1"

Licensing
---------

License information can be found `here <https://openzfs.github.io/openzfs-docs/License.html>`__.

Reporting a problem
-------------------

You can open a new issue and search existing issues using the public
`issue tracker <https://github.com/zfsonlinux/zfs/issues>`__. The issue
tracker is used to organize outstanding bug reports, feature requests,
and other development tasks. Anyone may post comments after signing up
for a github account.

Please make sure that what you're actually seeing is a bug and not a
support issue. If in doubt, please ask on the mailing list first, and if
you're then asked to file an issue, do so.

When opening a new issue include this information at the top of the
issue:

-  What distribution you're using and the version.
-  What spl/zfs packages you're using and the version.
-  Describe the problem you're observing.
-  Describe how to reproduce the problem.
-  Including any warning/errors/backtraces from the system logs.

When a new issue is opened it's not uncommon for a developer to request
additional information about the problem. In general, the more detail
you share about a problem the quicker a developer can resolve it. For
example, providing a simple test case is always exceptionally helpful.
Be prepared to work with the developer looking in to your bug in order
to get it resolved. They may ask for information like:

-  Your pool configuration as reported by ``zdb`` or ``zpool status``.
-  Your hardware configuration, such as

   -  Number of CPUs.
   -  Amount of memory.
   -  Whether your system has ECC memory.
   -  Whether it is running under a VMM/Hypervisor.
   -  Kernel version.
   -  Values of the spl/zfs module parameters.

-  Stack traces which may be logged to ``dmesg``.

Does OpenZFS have a Code of Conduct?
------------------------------------

Yes, the OpenZFS community has a code of conduct. See the `Code of
Conduct <https://openzfs.org/wiki/Code_of_Conduct>`__ for details.
