Scrub and Resilver
==================

ZFS checksums every block, so it knows when data is wrong instead of
guessing. Scrub and resilver are the two background operations that act on
that knowledge: a scrub verifies everything, a resilver rebuilds what is known
to be missing.

Self-healing
~~~~~~~~~~~~

Every read verifies the block's checksum. On a mismatch, a pool with
redundancy — mirror, raidz, draid, or ``copies>1`` — fetches a good copy,
returns it to the application, and rewrites the bad one. The error is counted
in ``zpool status`` even though nothing was lost.

Without redundancy, ZFS can still detect the corruption and report exactly
which file is affected, but it cannot repair it. This is the whole argument
for redundant pools: checksums without a second copy only tell you what you
have already lost.

Scrub
~~~~~

A scrub walks all data in the pool and verifies each block's checksum,
repairing damage where redundancy allows. It is how latent corruption — bit
rot on media that nothing has read for a year — gets found while it is still
repairable.

.. code:: bash

   zpool scrub pool
   zpool scrub -p pool          # pause
   zpool scrub -s pool          # stop
   zpool scrub -w pool          # wait for completion before returning
   zpool status -v pool

A paused scrub stays paused across export and import, and resumes from its
last on-disk checkpoint when ``zpool scrub`` is issued again.

Useful variants:

``-t`` (thorough)
    Also decrypt and decompress each block, catching the rare corruption where
    the checksum matches but decryption or decompression fails. Encrypted
    datasets need their keys loaded; blocks whose keys are unavailable fall
    back to a normal scrub.

``-e`` (error scrub)
    Scrub only files already reported as damaged by ``zpool status -v``. The
    pool must have been scrubbed once with the ``head_errlog`` feature
    enabled.

``-C``
    Continue from the last saved txg (the ``last_scrubbed_txg`` pool
    property) instead of starting over.

``-S date`` / ``-E date``
    Scrub only blocks created in a date range, in ``"YYYY-MM-DD HH:MM"``
    format.

Notes:

* Scrubs are I/O-intensive; only one scrub or resilver runs at a time, and a
  scrub cannot start while a resilver is in progress.
* A scrub runs in two phases — metadata scanning, which sorts blocks into
  large sequential ranges, then the actual block reads.
* On a live pool, progress can exceed 100% because data keeps changing; no
  completion estimate is given during that period.
* Encryption keys are not needed for ordinary checksum verification, but
  without them an unrepairable error cannot be attributed to a file name in
  ``zpool status -v``.

How often? Monthly is a common baseline for consumer disks, quarterly for
enterprise ones. Most distributions ship a systemd timer or cron job for it —
check before adding your own.

Resilver
~~~~~~~~

A resilver is the same machinery restricted to data ZFS knows to be out of
date: after attaching a device to a mirror, replacing a failed one, or
bringing a device back online after an outage.

.. code:: bash

   zpool replace pool /dev/old /dev/new
   zpool attach pool /dev/existing /dev/new
   zpool status pool
   zpool resilver pool          # restart a running resilver from the beginning

``zpool resilver`` restarts a resilver from the beginning and picks up any
drives scheduled for a deferred resilver; that requires the ``resilver_defer``
pool feature.

Sequential reconstruction
^^^^^^^^^^^^^^^^^^^^^^^^^

``zpool replace -s`` and ``zpool attach -s`` rebuild the new device
sequentially rather than by walking the block tree. This restores redundancy
much faster, but checksums are not verified during the rebuild — so a scrub is
started automatically when it finishes. Sequential reconstruction is not
supported for raidz.

Reading ``zpool status``
~~~~~~~~~~~~~~~~~~~~~~~~

The per-device error counters mean different things:

``READ`` / ``WRITE``
    I/O errors reported by the device itself.
``CKSUM``
    The device returned data that did not match its checksum — silent
    corruption. Non-zero CKSUM on an otherwise healthy disk usually points at
    cabling, a controller, or memory rather than the disk.

``zpool status -v`` lists files with unrepairable errors. ``zpool clear``
resets the counters once the underlying cause is dealt with — it does not fix
anything by itself.

Persistent errors on a file mean the data is gone: restore that file from a
backup or a snapshot. See :doc:`Troubleshooting </Basic Concepts/Operations/Troubleshooting>`.

Further reading
~~~~~~~~~~~~~~~

* `zpool-scrub(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-scrub.8.html>`__,
  `zpool-resilver(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-resilver.8.html>`__
* `zpool-replace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html>`__,
  `zpool-attach(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-attach.8.html>`__,
  `zpool-status(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>`__
* :doc:`Checksums </Basic Concepts/Data Storage/Checksums>`, :doc:`VDEVs </Basic Concepts/Pool Structure/VDEVs>`,
  :doc:`Troubleshooting </Basic Concepts/Operations/Troubleshooting>`
