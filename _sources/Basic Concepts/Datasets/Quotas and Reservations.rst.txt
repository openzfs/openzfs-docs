Quotas and Reservations
=======================

Datasets share the pool's free space, so by default any one of them can fill
it. Quotas cap what a dataset may consume; reservations guarantee what it may
always claim. Both are properties, both are inherited-by-position rather than
by value, and both come in two flavours: with descendants and snapshots
(``quota``, ``reservation``) or without (``refquota``, ``refreservation``).

Quotas
~~~~~~

``quota``
    Hard limit on the space used by the dataset **and all its descendants,
    including snapshots**.
``refquota``
    Hard limit on the dataset's own ``referenced`` space — descendants and
    snapshots do not count.

.. code:: bash

   zfs set quota=100G pool/home/alice
   zfs set refquota=80G pool/home/alice
   zfs get quota,refquota,used,referenced,available pool/home/alice

A quota set on a descendant does not override an ancestor's — it adds another
limit, and the tightest one wins. Quotas cannot be set on volumes: ``volsize``
already acts as an implicit quota.

The practical difference matters. Under a plain ``quota``, snapshots eat the
user's allowance, so an automatic snapshot schedule can make writes fail even
though the user deleted files. Under ``refquota`` the user sees a stable limit
and snapshot growth is charged to the parent instead. A common pattern is
``refquota`` for the user-visible limit plus ``quota`` on the parent dataset to
bound the total.

Reservations
~~~~~~~~~~~~

``reservation``
    Minimum space guaranteed to the dataset and its descendants.
``refreservation``
    Minimum space guaranteed to the dataset alone.

While usage is below the reservation, the dataset is accounted as if it were
using the full reserved amount. That space is charged to the parent's ``used``
and counts against the parent's quotas and reservations — which is exactly
what makes it a guarantee: nothing else in the pool can allocate it.

.. code:: bash

   zfs set reservation=50G pool/critical
   zfs set refreservation=none pool/vm/disk0

With ``refreservation`` set, a snapshot can only be taken if there is enough
free pool space outside the reservation for the dataset's current
``referenced`` bytes.

``refreservation=auto`` applies to volumes only: it thick-provisions the zvol,
reserving enough space for the whole ``volsize`` plus metadata. Setting it to
``none`` makes the volume sparse — faster to create and thin, but writes can
fail with ``ENOSPC`` when the pool fills.

User, group and project quotas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Within a single dataset, space can also be limited per user, per group, or per
project:

.. code:: bash

   zfs set userquota@alice=10G pool/home
   zfs set groupquota@staff=200G pool/home
   zfs set projectquota@42=50G pool/data

   zfs userspace pool/home
   zfs groupspace pool/home

``defaultuserquota``, ``defaultgroupquota`` and ``defaultprojectquota`` set a
fallback applied to everyone without a specific quota (``0`` disables them).
The ``*objquota@`` variants limit the *number of objects* rather than bytes.

Enforcement is asynchronous: a user can exceed their quota by a little before
writes start failing with ``EDQUOT``.

Limiting counts, not space
~~~~~~~~~~~~~~~~~~~~~~~~~~

``filesystem_limit`` and ``snapshot_limit`` cap how many datasets or snapshots
may exist below a point in the tree. Like quotas, a descendant's limit adds to
an ancestor's rather than replacing it, and the limit is not enforced against
a user who is permitted to change it. ``filesystem_limit`` requires the
``filesystem_limits`` pool feature.

.. code:: bash

   zfs set snapshot_limit=200 pool/home
   zfs get filesystem_count,snapshot_count pool/home

Slop space
~~~~~~~~~~

You do not need to reserve emergency space by hand — ZFS already does it. The
last ``1/2^spa_slop_shift`` of the pool, 3.2% by default, is held back and
cannot be consumed by normal writes. Once free space drops below it, ordinary
operations such as ``write`` and ``create`` return ``ENOSPC``.

The point of the reserve is that recovery still works:

* file removal and most administrative actions may use **half** the slop
  space;
* operations that are almost certain to free space, such as ``zfs destroy``,
  may use up to **three quarters** of it;
* a small set of internal operations is always permitted regardless of free
  space — these are what can, in principle, run a pool genuinely full and
  leave it permanently read-only.

On very small pools the reserve is raised to at least 128 MiB, and on very
large ones it is capped at 128 GiB, but it is never more than half the pool.

``spa_slop_shift`` can be raised to claw back some of that space on large
pools — 6 gives 1.6%, 7 gives 0.8% — at the cost of a thinner margin for
recovery. See
:doc:`Module Parameters </Performance and Tuning/Module Parameters>` and
:doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`, which
recommends keeping free space above 10% for allocation performance — a
separate concern from the slop reserve, and the one that usually bites first.

Further reading
~~~~~~~~~~~~~~~

* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``quota``, ``refquota``, ``reservation``, ``refreservation``,
  ``userquota@``, ``filesystem_limit``, ``snapshot_limit``
* `zfs-userspace(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-userspace.8.html>`__,
  `zfs-project(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-project.8.html>`__
* :doc:`Datasets and Properties </Basic Concepts/Datasets/Datasets and Properties>`
