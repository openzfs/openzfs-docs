TRIM
====

TRIM (``BLKDISCARD``, ATA TRIM, SCSI UNMAP) tells a device which blocks the
pool no longer uses, so an SSD can reclaim them for wear levelling and a
thinly provisioned backing store can release the space. Without it, an SSD
eventually believes every block it has ever been written to is still in use,
and write performance degrades.

ZFS offers two modes: an automatic background one and an on-demand one. They
are independent — a manual TRIM can be run regardless of the ``autotrim``
setting.

Automatic TRIM
~~~~~~~~~~~~~~

.. code:: bash

   zpool set autotrim=on pool

Default is ``off``. When on, recently freed space is trimmed periodically.
ZFS deliberately delays this so that small ranges aggregate into fewer, larger
requests, which devices handle far better.

The caveat is real: continuous trimming can put significant stress on the
underlying devices, and how well that is absorbed varies enormously between
models. On lower-end hardware, periodic manual TRIM usually captures most of
the benefit with much less disruption.

TRIM on L2ARC devices is separate — it is enabled by setting the
``l2arc_trim_ahead`` module parameter above 0.

On-demand TRIM
~~~~~~~~~~~~~~

.. code:: bash

   zpool trim pool
   zpool trim -r 100M pool          # rate-limit, bytes/s per leaf vdev
   zpool trim -w pool               # wait for completion
   zpool trim -s pool               # suspend
   zpool trim pool                  # ...and resume (no flags)
   zpool trim -c pool               # cancel
   zpool trim -a                    # all pools

Without ``-r``, TRIM runs as fast as the devices allow, which on a busy pool
is worth limiting. Progress is shown per device in ``zpool status -t``.

``zpool trim -d`` (``--secure``) requests a *secure* TRIM: the device
guarantees the data on the trimmed blocks is erased. Not all SSDs support it.
This is the option referenced when clearing free space after an encryption key
compromise — see :doc:`Native Encryption </Basic Concepts/Data Storage/Encryption>`.

Periodic TRIM with systemd
~~~~~~~~~~~~~~~~~~~~~~~~~~

Per-pool weekly and monthly timer units ship with OpenZFS:

.. code:: bash

   systemctl enable zfs-trim-weekly@rpool.timer --now
   systemctl enable zfs-trim-monthly@tank.timer --now

Which devices can be trimmed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Block devices that support ``BLKDISCARD`` — SSDs, thin-provisioned LUNs — and
file vdevs on file systems that support hole punching. Trimming a spinning
disk does nothing.

If ``zpool trim`` reports that a device does not support TRIM, check the
storage path: some HBAs and USB bridges do not pass the command through. See
the ATA TRIM discussion in
:doc:`Hardware </Performance and Tuning/Hardware>`.

Further reading
~~~~~~~~~~~~~~~

* `zpool-trim(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-trim.8.html>`__
* `zpoolprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolprops.7.html>`__ —
  ``autotrim``
* `zpool-initialize(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-initialize.8.html>`__ —
  the write-everything counterpart
* :doc:`Hardware </Performance and Tuning/Hardware>`
