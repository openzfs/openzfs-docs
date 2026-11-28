ACLs and Extended Attributes
============================

ZFS supports two unrelated ACL models — NFSv4-style ACLs, which are part of
ZFS itself, and POSIX ACLs, which are a Linux facility stored as extended
attributes. Which one is available depends on the platform, and getting this
wrong is a common source of "my permissions do not survive" surprises.

Choosing an ACL type
~~~~~~~~~~~~~~~~~~~~

The ``acltype`` property selects the model:

``off``
    ACLs disabled. **The default on Linux.** (``noacl`` and ``disabled`` are
    accepted as aliases.)
``posix``
    POSIX ACLs, Linux-only, stored as extended attributes. (``posixacl`` is an
    alias.) Requires a kernel built with ``CONFIG_FS_POSIX_ACL``; without it,
    ZFS falls back to ``off``.
``nfsv4``
    NFSv4-style ZFS ACLs, managed with ``getfacl``/``setfacl``. **The default
    on FreeBSD**; not supported on Linux.

.. warning::

   Setting a type the platform does not support does **not** produce an error.
   On Linux, ``acltype=nfsv4`` is handled identically to ``off`` — but ``zfs
   get acltype`` still reports ``nfsv4``. A dataset can therefore look as
   though it has ACLs enabled while silently having none.

.. code:: bash

   zfs set acltype=posix pool/home        # Linux
   zfs set acltype=nfsv4 pool/data        # FreeBSD

Because POSIX ACLs live in an extended attribute, they do not overwrite any
NFSv4 ACLs that may already be set.

On Linux, remember to set ``xattr=sa`` alongside ``acltype=posix`` — see
below.

NFSv4 ACL behavior
~~~~~~~~~~~~~~~~~~

Two properties govern how ZFS ACLs interact with the traditional Unix mode.
Neither applies to POSIX ACLs.

``aclinherit`` — how ACEs are inherited when files and directories are
created:

``discard``
    Inherit nothing.
``noallow``
    Inherit only inheritable ACEs that specify *deny* permissions.
``restricted``
    The default. Strips ``write_acl`` and ``write_owner`` on inheritance.
    (``secure`` is accepted as a legacy alias.)
``passthrough``
    Inherit everything unmodified. Files are then created with a mode
    determined by the inheritable ACEs; if none affect the mode, the
    application's requested mode is used.
``passthrough-x``
    Like ``passthrough``, except ``owner@``, ``group@`` and ``everyone@``
    inherit the execute bit only if the creation mode asked for it.

``aclmode`` — what ``chmod(2)`` does to an existing ACL:

``discard``
    The default. Deletes every ACE except those representing the requested
    mode.
``groupmask``
    Reduces the permissions in all ALLOW entries so they do not exceed the
    group permissions given to ``chmod``.
``passthrough``
    Changes nothing beyond the entries needed to represent the new mode.
``restricted``
    Makes ``chmod`` fail on any file with a non-trivial ACL that cannot be
    represented as a mode.

For a Samba or NFS server where clients manage ACLs, ``aclinherit=passthrough``
with ``aclmode=passthrough`` is the combination that stops a stray ``chmod``
from silently discarding the ACL. The defaults (``restricted`` /``discard``)
favour Unix mode semantics instead.

Extended attributes
~~~~~~~~~~~~~~~~~~~

The ``xattr`` property picks how extended attributes are stored:

``sa``
    System-attribute-based (``on`` is an alias for it). Stored inline in the
    space reserved for system attributes, which significantly reduces disk
    I/O. Two limits apply: a single attribute may be at most **32 KiB**
    (``DXATTR_MAX_ENTRY_SIZE``), and all SA xattrs on one file at most
    **64 KiB** (``DXATTR_MAX_SA_SIZE``). Exceeding either is not an error —
    the attribute is transparently written as a directory-based xattr
    instead.
``dir``
    Directory-based: each file with xattrs gets a hidden directory holding
    them. No practical limit on size or count (though Linux's
    ``getxattr(2)``/``setxattr(2)`` cap a single attribute at 64K). The most
    compatible style, supported by every ZFS implementation.
``off``
    Disabled.

.. note::

   **The default changed.** ``xattr`` defaults to ``sa`` from OpenZFS 2.3.0
   onward; on 2.2.x and earlier the default was ``dir``. Datasets created
   under an older release keep ``dir`` — check with ``zfs get xattr`` rather
   than assuming.

This matters for POSIX ACLs in particular, because on Linux they *are*
extended attributes: ZFS stores them under the standard names
``system.posix_acl_access`` and ``system.posix_acl_default``, through the same
code path as any other xattr. With ``xattr=dir`` every ACL lookup means
opening and reading that hidden directory; with ``xattr=sa`` the ACL comes
along with the dnode. That is why ``xattr=sa`` is the standard pairing with
``acltype=posix`` on Linux.

It also follows that ``xattr=off`` disables POSIX ACLs entirely, whatever
``acltype`` says.

.. code:: bash

   zfs set xattr=sa pool/home
   zfs set acltype=posix pool/home

Note that ``sa``-based xattrs are not readable by ZFS implementations that
predate the feature — relevant if the pool must be importable elsewhere.

Since both properties only affect newly-written data and newly-created files,
set them at dataset creation where possible:

.. code:: bash

   zfs create -o xattr=sa -o acltype=posix pool/home/alice

Further reading
~~~~~~~~~~~~~~~

* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``acltype``, ``aclinherit``, ``aclmode``, ``xattr``, ``nbmand``
* :doc:`Datasets and Properties </Basic Concepts/Datasets/Datasets and Properties>`,
  :doc:`Sharing Datasets </Basic Concepts/Operations/Sharing>`
