Hardware
********

.. contents:: Table of Contents
  :local:

Introduction
============

Storage before ZFS involved rather expensive hardware that was unable to
protect against silent corruption and did not scale very well. The
introduction of ZFS has enabled people to use far less expensive
hardware than previously used in the industry with superior scaling.
This page attempts to provide some basic guidance to people buying
hardware for use in ZFS-based servers and workstations.

Hardware that adheres to this guidance will enable ZFS to reach its full
potential for performance and reliability. Hardware that does not adhere
to it will serve as a handicap. Unless otherwise stated, such handicaps
apply to all storage stacks and are by no means specific to ZFS. Systems
built using competing storage stacks will also benefit from these
suggestions.

.. _bios_cpu_microcode_updates:

BIOS / CPU microcode updates
============================

Running the latest BIOS and CPU microcode is highly recommended.

Background
----------

Computer microprocessors are very complex designs that often have bugs,
which are called errata. Modern microprocessors are designed to utilize
microcode. This puts part of the hardware design into quasi-software
that can be patched without replacing the entire chip. Errata are often
resolved through CPU microcode updates. These are often bundled in BIOS
updates. In some cases, the BIOS interactions with the CPU through
machine registers can be modified to fix things with the same microcode.
If a newer microcode is not bundled as part of a BIOS update, it can
often be loaded by the operating system bootloader or the operating
system itself.

.. _ecc_memory:

ECC Memory
==========

Bit flips can have fairly dramatic consequences for all computer
filesystems and ZFS is no exception. No technique used in ZFS (or any
other filesystem) is capable of protecting against bit flips.
Consequently, ECC Memory is highly recommended.

.. _background_1:

Background
----------

Ordinary background radiation will randomly flip bits in computer
memory, which causes undefined behavior. These are known as "bit flips".
Each bit flip can have any of four possible consequences depending on
which bit is flipped:

-  Bit flips can have no effect.

   -  Bit flips that have no effect occur in unused memory.

-  Bit flips can cause runtime failures.

   -  This is the case when a bit flip occurs in something read from
      disk.
   -  Failures are typically observed when program code is altered.
   -  If the bit flip is in a routine within the system's kernel or
      /sbin/init, the system will likely crash. Otherwise, reloading the
      affected data can clear it. This is typically achieved by a
      reboot.

-  It can cause data corruption.

   -  This is the case when the bit is in use by data being written to
      disk.
   -  If the bit flip occurs before ZFS' checksum calculation, ZFS will
      not realize that the data is corrupt.
   -  If the bit flip occurs after ZFS' checksum calculation, but before
      write-out, ZFS will detect it, but it might not be able to correct
      it.

-  It can cause metadata corruption.

   -  This is the case when a bit flips in an on-disk structure being
      written to disk.
   -  If the bit flip occurs before ZFS' checksum calculation, ZFS will
      not realize that the metadata is corrupt.
   -  If the bit flip occurs after ZFS' checksum calculation, but before
      write-out, ZFS will detect it, but it might not be able to correct
      it.
   -  Recovery from such an event will depend on what was corrupted. In
      the worst, case, a pool could be rendered unimportable.

      -  All filesystems have poor reliability in their absolute worst
         case bit-flip failure scenarios. Such scenarios should be
         considered extraordinarily rare.

.. _drive_interfaces:

Drive Interfaces
================

.. _sas_versus_sata:

SAS versus SATA
---------------

ZFS depends on the block device layer for storage. Consequently, ZFS is
affected by the same things that affect other filesystems, such as
driver support and non-working hardware. Consequently, there are a few
things to note:

-  Never place SATA disks into a SAS expander without a SAS interposer.

   -  If you do this and it does work, it is the exception, rather than
      the rule.

-  Do not expect SAS controllers to be compatible with SATA port
   multipliers.

   -  This configuration is typically not tested.
   -  The disks could be unrecognized.

-  Support for SATA port multipliers is inconsistent across OpenZFS
   platforms

   -  Linux drivers generally support them.
   -  Illumos drivers generally do not support them.
   -  FreeBSD drivers are somewhere between Linux and Illumos in terms
      of support.

.. _usb_hard_drives_andor_adapters:

USB Hard Drives and/or Adapters
-------------------------------

These have problems involving sector size reporting, SMART passthrough,
the ability to set ERC and other areas. ZFS will perform as well on such
devices as they are capable of allowing, but try to avoid them. They
should not be expected to have the same up-time as SAS and SATA drives
and should be considered unreliable.

Controllers
===========

The ideal storage controller for ZFS has the following attributes:

-  Driver support on major OpenZFS platforms

   -  Stability is important.

-  High per-port bandwidth

   -  PCI Express interface bandwidth divided by the number of ports

-  Low cost

   -  Support for RAID, Battery Backup Units and hardware write caches
      is unnecessary.

Marc Bevand's blog post `From 32 to 2 ports: Ideal SATA/SAS Controllers
for ZFS & Linux MD RAID <http://blog.zorinaq.com/?e=10>`__ contains an
excellent list of storage controllers that meet these criteria. He
regularly updates it as newer controllers become available.

.. _hardware_raid_controllers:

Hardware RAID controllers
-------------------------

Hardware RAID controllers should not be used with ZFS. While ZFS will
likely be more reliable than other filesystems on Hardware RAID, it will
not be as reliable as it would be on its own.

-  Hardware RAID will limit opportunities for ZFS to perform self
   healing on checksum failures. When ZFS does RAID-Z or mirroring, a
   checksum failure on one disk can be corrected by treating the disk
   containing the sector as bad for the purpose of reconstructing the
   original information. This cannot be done when a RAID controller
   handles the redundancy unless a duplicate copy is stored by ZFS in
   the case that the corruption involving as metadata, the copies flag
   is set or the RAID array is part of a mirror/raid-z vdev within ZFS.

-  Sector size information is not necessarily passed correctly by
   hardware RAID on RAID 1 and cannot be passed correctly on RAID 5/6.
   Hardware RAID 1 is more likely to experience read-modify-write
   overhead from partial sector writes and Hardware RAID 5/6 will almost
   certainty suffer from partial stripe writes (i.e. the RAID write
   hole). Using ZFS with the disks directly will allow it to obtain the
   sector size information reported by the disks to avoid
   read-modify-write on sectors while ZFS avoids partial stripe writes
   on RAID-Z by desing from using copy-on-write.

   -  There can be sector alignment problems on ZFS when a drive
      misreports its sector size. Such drives are typically NAND-flash
      based solid state drives and older SATA drives from the advanced
      format (4K sector size) transition before Windows XP EoL occurred.
      This can be :ref:`manually corrected <alignment_shift_ashift>` at
      vdev creation.
   -  It is possible for the RAID header to cause misalignment of sector
      writes on RAID 1 by starting the array within a sector on an
      actual drive, such that manual correction of sector alignment at
      vdev creation does not solve the problem.

-  Controller failures can require that the controller be replaced with
   the same model, or in less extreme cases, a model from the same
   manufacturer. Using ZFS by itself allows any controller to be used.

-  If a hardware RAID controller's write cache is used, an additional
   failure point is introduced that can only be partially mitigated by
   additional complexity from adding flash to save data in power loss
   events. The data can still be lost if the battery fails when it is
   required to survive a power loss event or there is no flash and power
   is not restored in a timely manner. The loss of the data in the write
   cache can severely damage anything stored on a RAID array when many
   outstanding writes are cached. In addition, all writes are stored in
   the cache rather than just synchronous writes that require a write
   cache, which is inefficient, and the write cache is relatively small.
   ZFS allows synchronous writes to be written directly to flash, which
   should provide similar acceleration to hardware RAID and the ability
   to accelerate many more in-flight operations.

-  Behavior during RAID reconstruction when silent corruption damages
   data is undefined. There are reports of RAID 5 and 6 arrays being
   lost during reconstruction when the controller encounters silent
   corruption. ZFS' checksums allow it to avoid this situation by
   determining if not enough information exists to reconstruct data. In
   which case, the file is listed as damaged in zpool status and the
   system administrator has the opportunity to restore it from a backup.

-  IO response times will be reduced whenever the OS blocks on IO
   operations because the system CPU blocks on a much weaker embedded
   CPU used in the RAID controller. This lowers IOPS relative to what
   ZFS could have achieved.

-  The controller's firmware is an additional layer of complexity that
   cannot be inspected by arbitrary third parties. The ZFS source code
   is open source and can be inspected by anyone.

-  If multiple RAID arrays are formed by the same controller and one
   fails, the identifiers provided by the arrays exposed to the OS might
   become inconsistent. Giving the drives directly to the OS allows this
   to be avoided via naming that maps to a unique port or unique drive
   identifier.

   -  e.g. If you have arrays A, B, C and D; array B dies, the
      interaction between the hardware RAID controller and the OS might
      rename arrays C and D to look like arrays B and C respectively.
      This can fault pools verbatim imported from the cachefile.
   -  Not all RAID controllers behave this way. However, this issue has
      been observed on both Linux and FreeBSD when system administrators
      used single drive RAID 0 arrays. It has also been observed with
      controllers from different vendors.

One might be inclined to try using single-drive RAID 0 arrays to try to
use a RAID controller like a HBA, but this is not recommended for many
of the reasons listed for other hardware RAID types. It is best to use a
HBA instead of a RAID controller, for both performance and reliability.

.. _hard_drives:

Hard drives
===========

.. _sector_size:

Sector Size
-----------

Historically, all hard drives had 512-byte sectors, with the exception
of some SCSI drives that could be modified to support slightly larger
sectors. In 2009, the industry migrated from 512-byte sectors to
4096-byte "Advanced Format" sectors. Since Windows XP is not compatible
with 4096-byte sectors or drives larger than 2TB, some of the first
advanced format drives implemented hacks to maintain Windows XP
compatibility.

-  The first advanced format drives on the market misreported their
   sector size as 512-bytes for Windows XP compatibility. As of 2013, it
   is believed that such hard drives are no longer in production.
   Advanced format hard drives made during or after this time should
   report their true physical sector size.
-  Drives storing 2TB and smaller might have a jumper that can be set to
   map all sectors off by 1. This to provide proper alignment for
   Windows XP, which started its first partition at sector 63. This
   jumper setting should be off when using such drives with ZFS.

As of 2014, there are still 512-byte and 4096-byte drives on the market,
but they are known to properly identify themselves unless behind a USB
to SATA controller. Replacing a 512-byte sector drive with a 4096-byte
sector drives in a vdev created with 512-byte sector drives will
adversely affect performance. Replacing a 4096-byte sector drive with a
512-byte sector drive will have no negative effect on performance.

.. _error_recovery_control:

Error recovery control
----------------------

ZFS is said to be able to use cheap drives. This was true when it was
introduced and hard drives supported Error recovery control. Since ZFS'
introduction, error recovery control has been removed from low-end
drives from certain manufacturers, most notably Western Digital.
Consistent performance requires hard drives that support error recovery
control.

.. _background_2:

Background
~~~~~~~~~~

Hard drives store data using small polarized regions a magnetic surface.
Reading from and/or writing to this surface poses a few reliability
problems. One is that imperfections in the surface can corrupt bits.
Another is that vibrations can cause drive heads to miss their targets.
Consequently, hard drive sectors are composed of three regions:

-  A sector number
-  The actual data
-  ECC

The sector number and ECC enables hard drives to detect and respond to
such events. When either event occurs during a read, hard drives will
retry the read many times until they either succeed or conclude that the
data cannot be read. The latter case can take a substantial amount of
time and consequently, IO to the drive will stall.

Enterprise hard drives and some consumer hard drives implement a feature
called Time-Limited Error Recovery (TLER) by Western Digital, Error
Recovery Control (ERC) by Seagate and Command Completion Time Limit by
Hitachi and Samsung, which permits the time drives are willing to spend
on such events to be limited by the system administrator.

Drives that lack such functionality can be expected to have arbitrarily
high limits. Several minutes is not impossible. Drives with this
functionality typically default to 7 seconds. ZFS does not currently
adjust this setting on drives. However, it is advisable to write a
script to set the error recovery time to a low value, such as 0.1
seconds until ZFS is modified to control it. This must be done on every
boot.

.. _rpm_speeds:

RPM Speeds
----------

High RPM drives have lower seek times, which is historically regarded as
being desirable. They increase cost and sacrifice storage density in
order to achieve what is typically no more than a factor of 6
improvement over their lower RPM counterparts.

To provide some numbers, a 15k RPM drive from a major manufacturer is
rated for 3.4 millisecond average read and 3.9 millisecond average
write. Presumably, this number assumes that the target sector is at most
half the number of drive tracks away from the head and half the disk
away. Being even further away is worst-case 2 times slower. Manufacturer
numbers for 7200 RPM drives are not available, but they average 13 to 16
milliseconds in empirical measurements. 5400 RPM drives can be expected
to be slower.

ARC and ZIL are able to mitigate much of the benefit of lower seek
times. Far larger increases in IOPS performance can be obtained by
adding additional RAM for ARC, L2ARC devices and SLOG devices. Even
higher increases in performance can be obtained by replacing hard drives
with solid state storage entirely. Such things are typically more cost
effective than high RPM drives when considering IOPS.

.. _command_queuing:

Command Queuing
---------------

Drives with command queues are able to reorder IO operations to increase
IOPS. This is called Native Command Queuing on SATA and Tagged Command
Queuing on PATA/SCSI/SAS. ZFS stores objects in metaslabs and it can use
several metastabs at any given time. Consequently, ZFS is not only
designed to take advantage of command queuing, but good ZFS performance
requires command queuing. Almost all drives manufactured within the past
10 years can be expected to support command queuing. The exceptions are:

-  Consumer PATA/IDE drives
-  First generation SATA drives, which used IDE to SATA translation
   chips, from 2003 to 2004.
-  SATA drives operating under IDE emulation that was configured in the
   system BIOS.

Each OpenZFS system has different methods for checking whether command
queuing is supported. On Linux, ``hdparm -I /path/to/device \| grep
Queue`` is used. On FreeBSD, ``camcontrol identify $DEVICE`` is used.

.. _nand_flash_ssds:

NAND Flash SSDs
===============

As of 2014, Solid state storage is dominated by NAND-flash and most
articles on solid state storage focus on it exclusively. As of 2014, the
most popular form of flash storage used with ZFS involve drives with
SATA interfaces. Enterprise models with SAS interfaces are beginning to
become available.

As of 2017, Solid state storage using NAND-flash with PCI-E interfaces
are widely available on the market. They are predominantly enterprise
drives that utilize a NVMe interface that has lower overhead than the
ATA used in SATA or SCSI used in SAS. There is also an interface known
as M.2 that is primarily used by consumer SSDs, although not necessarily
limited to them. It can provide electrical connectivity for multiple
buses, such as SATA, PCI-E and USB. M.2 SSDs appear to use either SATA
or NVME.

.. _nvme_low_level_formatting:

NVMe low level formatting
-------------------------

Many NVMe SSDs support both 512-byte sectors and 4096-byte sectors. They
often ship with 512-byte sectors, which are less performant than
4096-byte sectors. Some also support metadata for T10/DIF CRC to try to
improve reliability, although this is unnecessary with ZFS.

NVMe drives should be
`formatted <https://filers.blogspot.com/2018/12/how-to-format-nvme-drive.html>`__
to use 4096-byte sectors without metadata prior to being given to ZFS
for best performance unless they indicate that 512-byte sectors are as
performant as 4096-byte sectors, although this is unlikely. Lower
numbers in the Rel_Perf of Supported LBA Sizes from ``smartctl -a
/dev/$device_namespace`` (for example ``smartctl -a /dev/nvme1n1``)
indicate higher performance low level formats, with 0 being the best.
The current formatting will be marked by a plus sign under the format
Fmt.

You may format a drive using ``nvme format /dev/nvme1n1 -l $ID``. The $ID
corresponds to the Id field value from the Supported LBA Sizes SMART
information.

.. _power_failure_protection:

Power Failure Protection
------------------------

.. _background_3:

Background
~~~~~~~~~~

On-flash data structures are highly complex and traditionally have been
highly vulnerable to corruption. In the past, such corruption would
result in the loss of \*all\* drive data and an event such as a PSU
failure could result in multiple drives simultaneously failing. Since
the drive firmware is not available for review, the traditional
conclusion was that all drives that lack hardware features to avoid
power failure events cannot be trusted, which was found to be the case
multiple times in the
past [#ssd_analysis]_ [#ssd_analysis2]_ [#ssd_analysis3]_.
Discussion of power failures bricking NAND flash SSDs appears to have
vanished from literature following the year 2015. SSD manufacturers now
claim that firmware power loss protection is robust enough to provide
equivalent protection to hardware power loss protection. `Kingston is one
example <https://www.kingston.com/us/solutions/servers-data-centers/ssd-power-loss-protection>`__.
Firmware power loss protection is used to guarantee the protection of
flushed data and the drives’ own metadata, which is all that filesystems
such as ZFS need.

However, those that either need or want strong guarantees that firmware
bugs are unlikely to be able to brick drives following power loss events
should continue to use drives that provide hardware power loss
protection. The basic concept behind how hardware power failure
protection works has been `documented by
Intel <https://www.intel.com/content/dam/www/public/us/en/documents/technology-briefs/ssd-power-loss-imminent-technology-brief.pdf>`__
for those who wish to read about the details. As of 2020, use of
hardware power loss protection is now a feature solely of enterprise
SSDs that attempt to protect unflushed data in addition to drive
metadata and flushed data. This additional protection beyond protecting
flushed data and the drive metadata provides no additional benefit to
ZFS, but it does not hurt it.

It should also be noted that drives in data centers and laptops are
unlikely to experience power loss events, reducing the usefulness of
hardware power loss protection. This is especially the case in
datacenters where redundant power, UPS power and the use of IPMI to do
forced reboots should prevent most drives from experiencing power loss
events.

Lists of drives that provide hardware power loss protection are
maintained below for those who need/want it. Since ZFS, like other
filesystems, only requires power failure protection for flushed data and
drive metadata, older drives that only protect these things are included
on the lists.

.. _nvme_drives_with_power_failure_protection:

NVMe drives with power failure protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A non-exhaustive list of NVMe drives with power failure protection is as
follows:

-  Intel 750
-  Intel DC P3500/P3600/P3608/P3700
-  Samsung PM963 (M.2 form factor)
-  Samsung PM1725/PM1725a
-  Samsung XS1715
-  Toshiba ZD6300
-  Seagate Nytro 5000 M.2 (XP1920LE30002 tested; **read notes below
   before buying**)

   -  Inexpensive 22110 M.2 enterprise drive using consumer MLC that is
      optimized for read mostly workloads. It is not a good choice for a
      SLOG device, which is a write mostly workload.
   -  The
      `manual <https://www.seagate.com/www-content/support-content/enterprise-storage/solid-state-drives/nytro-5000/_shared/docs/nytro-5000-mp2-pm-100810195d.pdf>`__
      for this drive specifies airflow requirements. If the drive does
      not receive sufficient airflow from case fans, it will overheat at
      idle. It's thermal throttling will severely degrade performance
      such that write throughput performance will be limited to 1/10 of
      the specification and read latencies will reach several hundred
      milliseconds. Under continuous load, the device will continue to
      become hotter until it suffers a "degraded reliability" event
      where all data on at least one NVMe namespace is lost. The NVMe
      namespace is then unusable until a secure erase is done. Even with
      sufficient airflow under normal circumstances, data loss is
      possible under load following the failure of fans in an enterprise
      environment. Anyone deploying this into production in an
      enterprise environment should be mindful of this failure mode.
   -  Those who wish to use this drive in a low airflow situation can
      workaround this failure mode by placing a passive heatsink such as
      `this <https://smile.amazon.com/gp/product/B07BDKN3XV>`__ on the
      NAND flash controller. It is the chip under the sticker closest to
      the capacitors. This was tested by placing the heatsink over the
      sticker (as removing it was considered undesirable). The heatsink
      will prevent the drive from overheating to the point of data loss,
      but it will not fully alleviate the overheating situation under
      load without active airflow. A scrub will cause it to overheat
      after a few hundred gigabytes are read. However, the thermal
      throttling will quickly cool the drive from 76 degrees Celsius to
      74 degrees Celsius, restoring performance.

      -  It might be possible to use the heatsink in an enterprise
         environment to provide protection against data loss following
         fan failures. However, this was not evaluated. Furthermore,
         operating temperatures for consumer NAND flash should be at or
         above 40 degrees Celsius for long term data integrity.
         Therefore, the use of a heatsink to provide protection against
         data loss following fan failures in an enterprise environment
         should be evaluated before deploying drives into production to
         ensure that the drive is not overcooled.

.. _sas_drives_with_power_failure_protection:

SAS drives with power failure protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A non-exhaustive list of SAS drives with power failure protection is as
follows:

-  Samsung PM1633/PM1633a
-  Samsung SM1625
-  Samsung PM853T
-  Toshiba PX05SHB***/PX04SHB***/PX04SHQ**\*
-  Toshiba PX05SLB***/PX04SLB***/PX04SLQ**\*
-  Toshiba PX05SMB***/PX04SMB***/PX04SMQ**\*
-  Toshiba PX05SRB***/PX04SRB***/PX04SRQ**\*
-  Toshiba PX05SVB***/PX04SVB***/PX04SVQ**\*

.. _sata_drives_with_power_failure_protection:

SATA drives with power failure protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A non-exhaustive list of SATA drives with power failure protection is as
follows:

-  Crucial MX100/MX200/MX300
-  Crucial M500/M550/M600
-  Intel 320

   -  Early reports claimed that the 330 and 335 had power failure
      protection too, `but they do
      not <https://engineering.nordeus.com/power-failure-testing-with-ssds>`__.

-  Intel 710
-  Intel 730
-  Intel DC S3500/S3510/S3610/S3700/S3710
-  Micron 5210 Ion

   -  First QLC drive on the list. High capacity with a low price per
      gigabyte.

-  Samsung PM863/PM863a
-  Samsung SM843T (do not confuse with SM843)
-  Samsung SM863/SM863a
-  Samsung 845DC Evo
-  Samsung 845DC Pro

   -  `High sustained write
      IOPS <http://www.anandtech.com/show/8319/samsung-ssd-845dc-evopro-preview-exploring-worstcase-iops/5>`__

-  Toshiba HK4E/HK3E2
-  Toshiba HK4R/HK3R2/HK3R

.. _criteriaprocess_for_inclusion_into_these_lists:

Criteria/process for inclusion into these lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These lists have been compiled on a volunteer basis by OpenZFS
contributors (mainly Richard Yao) from trustworthy sources of
information. The lists are intended to be vendor neutral and are not
intended to benefit any particular manufacturer. Any perceived bias
toward any manufacturer is caused by a lack of awareness and a lack of
time to research additional options. Confirmation of the presence of
adequate power loss protection by a reliable source is the only
requirement for inclusion into this list. Adequate power loss protection
means that the drive must protect both its own internal metadata and all
flushed data. Protection of unflushed data is irrelevant and therefore
not a requirement. ZFS only expects storage to protect flushed data.
Consequently, solid state drives whose power loss protection only
protects flushed data is sufficient for ZFS to ensure that data remains
safe.

Anyone who believes an unlisted drive to provide adequate power failure
protection may contact the :ref:`mailing_lists` with
a request for inclusion and substantiation for the claim that power
failure protection is provided. Examples of substantiation include
pictures of drive internals showing the presence of capacitors,
statements by well regarded independent review sites such as Anandtech
and manufacturer specification sheets. The latter are accepted on the
honor system until a manufacturer is found to misstate reality on the
protection of the drives' own internal metadata structures and/or the
protection of flushed data. Thus far, all manufacturers have been
honest.

.. _flash_pages:

Flash pages
-----------

The smallest unit on a NAND chip that can be written is a flash page.
The first NAND-flash SSDs on the market had 4096-byte pages. Further
complicating matters is that the the page size has been doubled twice
since then. NAND flash SSDs **should** report these pages as being
sectors, but so far, all of them incorrectly report 512-byte sectors for
Windows XP compatibility. The consequence is that we have a similar
situation to what we had with early advanced format hard drives.

As of 2014, most NAND-flash SSDs on the market have 8192-byte page
sizes. However, models using 128-Gbit NAND from certain manufacturers
have a 16384-byte page size. Maximum performance requires that vdevs be
created with correct ashift values (13 for 8192-byte and 14 for
16384-byte). However, not all OpenZFS platforms support this. The Linux
port supports ashift=13, while others are limited to ashift=12
(4096-byte).

As of 2017, NAND-flash SSDs are tuned for 4096-byte IOs. Matching the
flash page size is unnecessary and ashift=12 is usually the correct
choice. Public documentation on flash page size is also nearly
non-existent.

.. _ata_trim_scsi_unmap:

ATA TRIM / SCSI UNMAP
---------------------

It should be noted that this is a separate case from
discard on zvols or hole punching on filesystems. Those work regardless
of whether ATA TRIM / SCSI UNMAP is sent to the actual block devices.

.. _ata_trim_performance_issues:

ATA TRIM Performance Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ATA TRIM command in SATA 3.0 and earlier is a non-queued command.
Issuing a TRIM command on a SATA drive conforming to SATA 3.0 or earlier
will cause the drive to drain its IO queue and stop servicing requests
until it finishes, which hurts performance. SATA 3.1 removed this
limitation, but very few SATA drives on the market are conformant to
SATA 3.1 and it is difficult to distinguish them from SATA 3.0 drives.
At the same time, SCSI UNMAP has no such problems.

.. _optane_3d_xpoint_ssds:

Optane / 3D XPoint SSDs
=======================

These are SSDs with far better latencies and write endurance than NAND
flash SSDs. They are byte addressable, such that ashift=9 is fine for
use on them. Unlike NAND flash SSDs, they do not require any special
power failure protection circuitry for reliability. There is also no
need to run TRIM on them. However, they cost more per GB than NAND flash
(as of 2020). The enterprise models make excellent SLOG devices. Here is
a list of models that are known to perform well:

-  `Intel DC
   P4800X <https://www.servethehome.com/intel-optane-hands-on-real-world-benchmark-and-test-results/>`__

   -  This gives basically the highest performance you can get as of
      June 2020.

Also, at time of writing in June 2020, only one model is listed. This is
due to there being few such drives on the market. The client models are
likely to be outperformed by well configured NAND flash drives, so they
have not been listed (although they are likely cheaper than NAND flash).
More will likely be added in the future.

Note that SLOG devices rarely have more than 4GB in use at any given
time, so the smaller sized devices are generally the best choice in
terms of cost, with larger sizes giving no benefit. Larger sizes could
be a good choice for other vdev types, depending on performance needs
and cost considerations.

Power
=====

Ensuring that computers are properly grounded is highly recommended.
There have been cases in user homes where machines experienced random
failures when plugged into power receptacles that had open grounds (i.e.
no ground wire at all). This can cause random failures on any computer
system, whether it uses ZFS or not.

Power should also be relatively stable. Large dips in voltages from
brownouts are preferably avoided through the use of UPS units or line
conditioners. Systems subject to unstable power that do not outright
shutdown can exhibit undefined behavior. PSUs with longer hold-up times
should be able to provide partial protection against this, but hold up
times are often undocumented and are not a substitute for a UPS or line
conditioner.

.. _pwr_ok_signal:

PWR_OK signal
-------------

PSUs are supposed to deassert a PWR_OK signal to indicate that provided
voltages are no longer within the rated specification. This should force
an immediate shutdown. However, the system clock of a developer
workstation was observed to significantly deviate from the expected
value following during a series of ~1 second brown outs. This machine
did not use a UPS at the time. However, the PWR_OK mechanism should have
protected against this. The observation of the PWR_OK signal failing to
force a shutdown with adverse consequences (to the system clock in this
case) suggests that the PWR_OK mechanism is not a strict guarantee.

.. _psu_hold_up_times:

PSU Hold-up Times
-----------------

A PSU hold-up time is the amount of time that a PSU can continue to
output power at maximum output within standard voltage tolerances
following the loss of input power. This is important for supporting UPS
units because `the transfer
time <https://www.sunpower-uk.com/glossary/what-is-transfer-time/>`__
taken by a standard UPS to supply power from its battery can leave
machines without power for "5-12 ms". `Intel's ATX Power Supply design
guide <https://paginas.fe.up.pt/~asousa/pc-info/atxps09_atx_pc_pow_supply.pdf>`__
specifies a hold up time of 17 milliseconds at maximum continuous
output. The hold-up time is a inverse function of how much power is
being output by the PSU, with lower power output increasing holdup
times.

Capacitor aging in PSUs will lower the hold-up time below what it was
when new, which could cause reliability issues as equipment ages.
Machines using substandard PSUs with hold-up times below the
specification therefore require higher end UPS units for protection to
ensure that the transfer time does not exceed the hold-up time. A
hold-up time below the transfer time during a transfer to battery power
can cause undefined behavior should the PWR_OK signal not become
deasserted to force the machine to power off.

If in doubt, use a double conversion UPS unit. Double conversion UPS
units always run off the battery, such that the transfer time is 0. This
is unless they are high efficiency models that are hybrids between
standard UPS units and double conversion UPS units, although these are
reported to have much lower transfer times than standard PSUs. You could
also contact your PSU manufacturer for the hold up time specification,
but if reliability for years is a requirement, you should use a higher
end UPS with a low transfer time.

Note that double conversion units are at most 94% efficient unless they
support a high efficiency mode, which adds latency to the time to
transition to battery power.

.. _ups_batteries:

UPS batteries
-------------

The lead acid batteries in UPS units generally need to be replaced
regularly to ensure that they provide power during power outages. For
home systems, this is every 3 to 5 years, although this varies with
temperature [#ups_temp]_. For
enterprise systems, contact your vendor.


.. rubric:: Footnotes

.. [#ssd_analysis] <http://lkcl.net/reports/ssd_analysis.html>
.. [#ssd_analysis2] <https://www.usenix.org/system/files/conference/fast13/fast13-final80.pdf>
.. [#ssd_analysis3] <https://engineering.nordeus.com/power-failure-testing-with-ssds>
.. [#ups_temp] <https://www.apc.com/us/en/faqs/FA158934/>
