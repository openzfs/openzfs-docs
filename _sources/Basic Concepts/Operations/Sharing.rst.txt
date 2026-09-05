Sharing Datasets
================

ZFS can drive NFS and SMB exports from dataset properties, so a share follows
the dataset instead of living in a separate config file that has to be kept in
sync. Block-level export (iSCSI) works differently — it uses zvols and an
external target framework.

It is only a wrapper
~~~~~~~~~~~~~~~~~~~~

**ZFS does not implement NFS or SMB.** The ``sharenfs`` and ``sharesmb``
properties generate configuration for the platform's normal server and then
tell it to reload:

+----------+------------------------------+---------------------------------+
| Platform | ZFS writes                   | ZFS then runs                   |
+==========+==============================+=================================+
| Linux    | ``/etc/exports.d/            | ``/usr/sbin/exportfs``          |
| (NFS)    | zfs.exports``                |                                 |
+----------+------------------------------+---------------------------------+
| FreeBSD  | ``/etc/zfs/exports``         | signals ``mountd``              |
| (NFS)    |                              |                                 |
+----------+------------------------------+---------------------------------+
| Linux    | a Samba *usershare*          | ``net usershare add``           |
| (SMB)    |                              | / ``delete``                    |
+----------+------------------------------+---------------------------------+

Everything else — authentication, Kerberos, ACL semantics, performance,
tuning — is the server's job and is configured the server's way. The
convenience is real, but so are the consequences:

**The server must already be installed and configured.** ZFS checks whether
``exportfs`` exists and quietly does nothing if it does not. Setting
``sharenfs`` on a host without nfs-utils appears to succeed while exporting
nothing. Likewise ``sharesmb`` needs Samba listening on ``127.0.0.1`` with
usershares enabled (``usershare max shares``, ``usershare owner only``)
before it will work at all.

**Two config files now describe your exports.** ZFS owns
``/etc/exports.d/zfs.exports``; anything you wrote by hand is still in
``/etc/exports``. Both are live. When a share does not behave, look at both,
and at ``exportfs -v`` for what the kernel actually has.

**The option set is an allowlist, not passthrough.** Despite appearances,
``sharenfs`` does not accept arbitrary ``exports(5)`` options. On Linux the
accepted keys are ``sec``, ``ro``, ``rw`` plus: ``all_squash``, ``anongid``,
``anonuid``, ``async``, ``auth_nlm``, ``crossmnt``, ``fsid``, ``fsuid``,
``hide``, ``insecure``, ``insecure_locks``, ``mountpoint``, ``mp``,
``no_acl``, ``no_all_squash``, ``no_auth_nlm``, ``no_root_squash``,
``no_subtree_check``, ``no_wdelay``, ``nohide``, ``refer``, ``replicas``,
``root_squash``, ``secure``, ``secure_locks``, ``subtree_check``, ``sync``,
``wdelay``. Anything else is rejected as a syntax error.

**When you outgrow it, turn it off.** For per-share Samba tuning, Kerberos
beyond ``sec=``, or export options outside that list, set the property to
``off`` and manage the export natively. Mixing both for the same dataset is
what produces shares that reappear after a reboot or refuse to go away.

NFS
~~~

.. code:: bash

   zfs set sharenfs=on pool/export
   zfs set sharenfs=rw=@192.168.1.0/24,no_root_squash pool/export
   zfs set sharenfs=off pool/export

``sharenfs=on`` shares with the default options
``sec=sys,rw,crossmnt,no_subtree_check``. Any other value is an option list,
validated against the allowlist above and then translated into an
``/etc/exports``-style entry.

Note the syntax: options are **comma-separated**, unlike
`exports(5) <https://man7.org/linux/man-pages/man5/exports.5.html>`__. This
avoids quoting and makes the property easy to generate from scripts. On
FreeBSD several option sets may be given, separated by semicolons, each
applying to different hosts or networks.

With ``sharenfs=off``, the dataset is not managed by ZFS at all — export it
the traditional way through ``/etc/exports`` and ``exportfs``.

Because each dataset is its own file system, a client mounting a parent will
not automatically see child datasets unless ``crossmnt`` is in effect (it is,
with ``sharenfs=on``).

SMB
~~~

.. code:: bash

   zfs set sharesmb=on pool/export

On Linux this uses **Samba usershares**: ZFS invokes ``net(8)`` to create a
USERSHARE. Samba must be configured to permit usershares before this works.

Points to know:

* The share name is derived from the dataset name, with characters that are
  invalid in a resource name replaced by underscores.
* The share is created with the ACL ``Everyone:F`` and no guest access —
  Samba must be able to authenticate a real user. All finer-grained access
  control has to be done on the file system itself.
* Linux does not support the additional ``sharesmb`` options available on
  Solaris.

See also the Samba section of
:doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`.

Applying shares
~~~~~~~~~~~~~~~

Datasets are shared and unshared automatically at boot and shutdown, and
whenever the properties change:

.. code:: bash

   zfs share -a                 # share everything (part of the boot process)
   zfs share pool/export
   zfs unshare pool/export
   zfs unshare -a

``zfs share -l`` loads keys for encrypted file systems as they are mounted;
with ``keylocation=prompt`` that blocks on the terminal.

iSCSI and other block exports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no ``shareiscsi`` property in OpenZFS. Export a zvol instead, and
point an iSCSI target framework (LIO/``targetcli``, SCST, or ``ctld`` on
FreeBSD) at the resulting device:

.. code:: bash

   zfs create -V 100G pool/iscsi/lun0
   ls -l /dev/zvol/pool/iscsi/lun0

The ``volmode`` property controls how a zvol appears to the OS:

``full`` (alias ``geom``)
    A fully-fledged block device, partitions included.
``dev``
    A block device with its partitions hidden — usually what you want for a
    LUN or a VM disk, since the host should not be scanning the guest's
    partition table.
``none``
    Not exposed outside ZFS at all. Still snapshottable, clonable and
    replicable — useful for backup targets.
``default``
    Follow the system-wide ``zvol_volmode`` tunable.

Set ``volblocksize`` at creation to match the consumer's I/O size; see
:doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`.

Further reading
~~~~~~~~~~~~~~~

* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``sharenfs``, ``sharesmb``, ``volmode``, ``volsize``
* `zfs-share(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-share.8.html>`__ —
  documents both ``zfs share`` and ``zfs unshare``
* :doc:`Datasets and Properties </Basic Concepts/Datasets/Datasets and Properties>`
