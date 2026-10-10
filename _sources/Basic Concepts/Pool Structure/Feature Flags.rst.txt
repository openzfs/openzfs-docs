Feature Flags
=============

ZFS on-disk formats were originally versioned with a single number,
which increased whenever the format changed. The numbered approach was
suitable when development of ZFS was driven by a single organisation.

For distributed development of OpenZFS, version numbering was
unsuitable. Any change to the number would have required agreement,
across all implementations, of each change to the on-disk format.

OpenZFS feature flags – an alternative to traditional version numbering
– allow **a uniquely named pool property for each change to the on-disk
format**. This approach supports:

-  format changes that are independent
-  format changes that depend on each other.

Feature states
--------------

Each feature is exposed as a pool property named ``feature@<short-name>`` and
is in one of three states:

``disabled``
    The on-disk format change has not been made and will not be, unless an
    administrator enables it.
``enabled``
    Marked as enabled, but the on-disk format change has **not happened yet**.
    The pool can still be imported by software that does not know the feature
    — until something triggers the change, which may happen at any time and
    moves the feature to ``active``.
``active``
    The format change is in effect. Software must support the feature to
    import the pool read-write.

.. code:: bash

   zpool get all pool | grep feature@
   zpool get feature@large_blocks pool

**Features cannot be disabled once enabled.** Some can return from ``active``
to ``enabled`` when whatever used them is freed — for example
``block_cloning`` once the last cloned block is gone — but that is
feature-specific.

Enabling a feature automatically enables anything it depends on.

Read-only compatibility
-----------------------

Some format changes do not prevent other software from *reading* the pool.
If every unsupported feature on a pool is read-only compatible, the pool can
still be imported read-only:

.. code:: bash

   zpool import -o readonly=on pool

For each unsupported feature on an imported pool, the property
``unsupported@<feature-name>`` explains why the import was allowed:
``inactive`` (the feature is only ``enabled``, so the format is still
compatible) or ``readonly`` (it is read-only compatible and the pool was
imported read-only).

Compatibility
-------------

Where all *features* that are used by a pool are supported by multiple
implementations of OpenZFS, the on-disk format is portable across those
implementations.

Features that are exclusive when enabled should be periodically ported
to all distributions.

Compatibility feature sets
--------------------------

The ``compatibility`` pool property pins a pool to a named on-disk format, so
it stays importable somewhere else — an older release, another OS, or a
bootloader.

``off`` (default)
    No restriction; any feature may be enabled.
``legacy``
    No features may be enabled at all — neither by ``zpool upgrade`` nor by
    setting ``feature@…=enabled``, and the pool cannot be upgraded to a newer
    on-disk version. A deliberate safety catch.
``file[,file…]``
    One or more feature-set files. Only features present in **all** of the
    listed files may be enabled.

.. code:: bash

   zpool create -o compatibility=grub2-2.12 bpool ...
   zpool set compatibility=openzfs-2.1-linux tank
   zpool get compatibility tank

Names are resolved relative to ``/etc/zfs/compatibility.d`` (local, takes
precedence) or ``/usr/share/zfs/compatibility.d`` (shipped by the
distribution), or given as absolute paths. The shipped sets cover OpenZFS
releases per platform (``openzfs-2.1-linux``, ``openzfs-2.2``,
``openzfs-2.3``, ``openzfs-2.4``, ``openzfs-2.0-freebsd``…), older ZoL and
FreeBSD versions, GRUB (``grub2-2.06``, ``grub2-2.12``), and yearly baselines
(``compat-2018`` … ``compat-2021``).

.. code:: bash

   ls /usr/share/zfs/compatibility.d/

Two practical uses dominate: a **boot pool** restricted to what the
bootloader understands, and a pool that must remain importable on an older
system. Setting ``compatibility`` also stops ``zpool status`` from nagging
about disabled features that are outside the chosen set.

Upgrading a pool
----------------

.. code:: bash

   zpool upgrade                   # list pools with features not yet enabled
   zpool upgrade -v                # what this build supports
   zpool upgrade pool              # enable them on one pool
   zpool upgrade -a                # ...on every pool

``zpool upgrade`` enables all supported features, subject to
``compatibility``: if a feature set is in force only features in that set are
enabled, and with ``legacy`` nothing happens at all.

.. warning::

   **Upgrading is one-way.** Features cannot be disabled afterwards. Once
   enabled features become ``active``, the pool is no longer importable by
   software that does not support them — which includes an older kernel you
   might need to boot back into, a rescue USB stick, and the bootloader on a
   root pool.

   Upgrade deliberately, not reflexively because ``zpool status`` suggested
   it. A pool that is not upgraded keeps working; it just does not offer the
   newer features.

Note that ``zpool status`` reporting "some supported features are not
enabled" is informational. On a root or boot pool in particular, check what
your bootloader supports first — see the
:doc:`Root on ZFS guides </Getting Started/index>`.

``zfs upgrade`` is a different thing
------------------------------------

Datasets carry their own on-disk version, independent of the pool's features.

.. code:: bash

   zfs upgrade                     # file systems not at the latest version
   zfs upgrade -v                  # versions this build supports
   zfs upgrade -r pool/data        # upgrade a subtree
   zfs upgrade -a                  # everything

The same one-way warning applies, with an extra consequence: after upgrading,
``zfs send`` streams generated from *new* snapshots of those file systems
cannot be received by older ZFS versions either. If you replicate to an older
system, that will break the replication, not just the local mount.

Reference materials
-------------------

`ZFS Feature Flags <http://web.archive.org/web/20160419064650/http://blog.delphix.com/csiden/files/2012/01/ZFS_Feature_Flags.pdf>`_
(Christopher Siden, 2012-01, in the Internet
Archive Wayback Machine) in particular: "… Legacy version numbers still
exist for pool versions 1-28 …".

`zpool-features(7) man page <../../man/master/7/zpool-features.7.html>`_ - OpenZFS

`zpool-features <http://illumos.org/man/5/zpool-features>`__ (5) – illumos

Feature flags implementation per OS
-----------------------------------

.. raw:: html

   <div class="man_container">

.. raw:: html
   :file: ../../_build/zfs_feature_matrix.html

.. raw:: html

   </div>
