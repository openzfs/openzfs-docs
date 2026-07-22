Delegated Administration
========================

``zfs allow`` lets non-privileged users run ZFS operations on specific
datasets — take their own snapshots, set their own properties, receive their
own replication streams — without handing out root.

Delegation is controlled by the pool property ``delegation``, which is ``on``
by default:

.. code:: bash

   zpool get delegation pool

Granting and revoking
~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   zfs allow alice snapshot,destroy,mount pool/home/alice
   zfs allow -g devs create,mount,snapshot pool/scratch
   zfs allow pool/home/alice              # show what is delegated
   zfs unallow alice snapshot pool/home/alice

Who:

* a bare name is interpreted as ``everyone``, then a user, then a group —
  use ``-u`` or ``-g`` to be explicit;
* ``-e`` (or the literal ``everyone``) grants to all users.

Where:

* ``-l`` — this dataset only ("locally");
* ``-d`` — descendants only;
* neither or both — the dataset and all its descendants (the default).

``zfs unallow`` takes the same selectors, plus ``-r`` to remove the delegation
recursively.

What can be delegated
~~~~~~~~~~~~~~~~~~~~~

Permission names are just ZFS subcommand and property names: ``snapshot``,
``clone``, ``send``, ``receive``, ``rollback``, ``destroy``, ``hold``,
``load-key``, ``compression``, ``quota``, ``recordsize``, and so on. ``zfs
allow`` with no arguments on a dataset prints the current grants.

Several permissions imply others, and this is the usual source of confusion:

* ``create`` also needs ``mount`` (and ``refreservation`` for non-sparse
  volumes);
* ``destroy``, ``rollback`` and ``snapshot`` also need ``mount``;
* ``clone`` needs ``create`` plus ``mount`` in the origin file system;
* ``rename`` needs ``mount`` and ``create`` in the new parent;
* ``receive`` needs ``mount`` and ``create``, and is what allows ``zfs
  receive -F`` — use ``receive:append`` for a receive permission that cannot
  force a rollback;
* ``allow`` lets a user delegate onward, but only permissions they hold
  themselves.

Narrower send variants exist for encrypted data: ``send:raw`` permits only raw
streams, and ``send:encrypted`` permits raw streams of encrypted datasets only
— both prevent an encrypted dataset from being sent in decrypted form. See
:doc:`Native Encryption </Basic Concepts/Data Storage/Encryption>`.

.. note::

   On Linux the ``mount``, ``unmount``, ``mountpoint``, ``canmount``,
   ``rename`` and ``share`` permissions cannot be delegated, because
   ``mount(8)`` restricts changes to the global namespace to root. Since
   ``create``, ``destroy``, ``snapshot`` and friends require ``mount``, a
   fully self-service setup on Linux still needs help from root or from a
   setuid helper.

Permission sets
~~~~~~~~~~~~~~~

A named set groups permissions so they can be granted as a unit and changed
later in one place. Set names begin with ``@``.

.. code:: bash

   zfs allow -s @backup send,snapshot,hold,destroy pool/data
   zfs allow backupuser @backup pool/data
   zfs unallow -s @backup pool/data

Create-time permissions
~~~~~~~~~~~~~~~~~~~~~~~

``zfs allow -c`` sets create-time permissions: they are granted locally to
whoever creates a new descendant file system. This is how a user who is
allowed to create datasets automatically becomes able to administer the ones
they created.

.. code:: bash

   zfs allow -c snapshot,destroy,mount pool/scratch

Further reading
~~~~~~~~~~~~~~~

* `zfs-allow(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-allow.8.html>`__ —
  the full permission table
* `zfs-unallow(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-unallow.8.html>`__
* `zpoolprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolprops.7.html>`__ —
  ``delegation``
