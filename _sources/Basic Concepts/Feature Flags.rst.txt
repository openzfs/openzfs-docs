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

Compatibility
-------------

Where all *features* that are used by a pool are supported by multiple
implementations of OpenZFS, the on-disk format is portable across those
implementations.

Features that are exclusive when enabled should be periodically ported
to all distributions.

Reference materials
-------------------

`ZFS Feature Flags <http://web.archive.org/web/20160419064650/http://blog.delphix.com/csiden/files/2012/01/ZFS_Feature_Flags.pdf>`_
(Christopher Siden, 2012-01, in the Internet
Archive Wayback Machine) in particular: "… Legacy version numbers still
exist for pool versions 1-28 …".

`zpool-features(7) man page <../man/7/zpool-features.7.html>`_ - OpenZFS

`zpool-features <http://illumos.org/man/5/zpool-features>`__ (5) – illumos

Feature flags implementation per OS
-----------------------------------

.. raw:: html

   <div class="man_container">

.. raw:: html
   :file: ../_build/zfs_feature_matrix.html

.. raw:: html

   </div>
