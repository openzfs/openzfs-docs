Native Encryption
=================

ZFS can encrypt datasets itself, without a separate layer such as LUKS or
GELI. Encryption is a per-dataset property, so a single pool can hold both
encrypted and unencrypted datasets, each encrypted dataset can have its own
key, and the pool stays fully manageable — importable, scrubbable,
resilverable and replicable — while the keys are not loaded.

Native encryption requires the ``encryption`` pool feature.

What is and is not encrypted
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Encrypted:

* file and volume data
* file attributes, ACLs and permission bits
* directory listings
* FUID mappings and ``userused``/``groupused`` accounting data
* the ZFS intent log (ZIL)

Not encrypted:

* dataset and snapshot names
* the dataset hierarchy
* dataset properties
* file sizes and the location of holes in files
* deduplication tables (the deduplicated data itself is encrypted)

The dividing line is per object type, and the reason the second list looks the
way it does is the **block tree**. Only leaf blocks are encrypted; indirect
blocks (level > 0) are authenticated but left in the clear, carrying a MAC over
the MACs below them. Block pointers therefore stay readable without keys —
which is precisely what lets the pool be scrubbed, resilvered, freed and
replicated with the keys unloaded, and equally what leaks how large each file
is, where its holes are, and how much data a dataset holds.

This is the trade-off that keeps the pool administrable without keys. If the
existence and names of your datasets, or their sizes and change patterns, are
themselves sensitive, native encryption is not the right layer for that — use
full-disk encryption underneath ZFS instead, or in addition.

Creating an encrypted dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``encryption`` and ``keyformat`` must be given at creation time, optionally
with ``keylocation`` and ``pbkdf2iters``. The cipher suite cannot be changed
afterwards.

.. code:: bash

   # passphrase, entered interactively
   zfs create -o encryption=on -o keyformat=passphrase pool/secret

   # raw key from a file
   dd if=/dev/urandom bs=32 count=1 of=/root/pool.key
   zfs create -o encryption=on \
              -o keyformat=raw \
              -o keylocation=file:///root/pool.key \
              pool/secret

``encryption=on`` selects the current default suite, which is ``aes-256-gcm``.
The suites that can be named explicitly are ``aes-128-ccm``, ``aes-192-ccm``,
``aes-256-ccm``, ``aes-128-gcm``, ``aes-192-gcm`` and ``aes-256-gcm``. The GCM
modes are generally faster on hardware with AES acceleration.

``keyformat`` is one of:

``passphrase``
    8 to 512 bytes, run through PBKDF2 before use. The iteration count is set
    by ``pbkdf2iters`` — currently 350000 by default, with a minimum of
    100000.

``raw``
    Exactly 32 bytes of random data, regardless of the chosen suite.

``hex``
    The same 32 bytes, written as hex.

``keylocation`` is where the key is read from: ``prompt`` (the default —
interactive), ``file:///absolute/path``, or an ``http://`` / ``https://``
address, which is how a machine can fetch its key from a key server at boot.

Encryption roots and inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The dataset you supply a key for becomes an *encryption root*. Descendants
inherit its key by default, so loading, unloading or changing the key at the
root does the same for everything under it. The read-only ``encryptionroot``
property shows which root a dataset currently uses.

To break that relationship and give a child its own key, supply a
``keyformat`` when creating it, or run ``zfs change-key`` on it later. Note
that:

* the child's ``keyformat`` may be the same as the parent's and it still
  becomes a separate encryption root;
* setting the ``encryption`` property alone does *not* create a new encryption
  root — it just uses a different cipher suite with the same key;
* clones always use their origin's key.

Because of that last exception, ``keystatus``, ``keyformat``, ``keylocation``
and ``pbkdf2iters`` do not inherit the way other ZFS properties do: their
effective value comes from the encryption root.

Loading and unloading keys
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   zfs load-key pool/secret          # prompts, or reads keylocation
   zfs load-key -a                   # every encryption root in every imported pool
   zfs load-key -r pool              # recursively, all encryption roots below pool
   zfs load-key -n pool/secret       # dry run: just verify the key is correct

   zfs mount pool/secret             # loading a key does not mount

   zfs unload-key pool/secret        # dataset must not be open or mounted

``zfs mount -l`` asks for the key and mounts in one step. The ``keystatus``
property is ``available`` once the key is loaded and ``unavailable`` while it
is not:

.. code:: bash

   zfs get -r keystatus,encryptionroot pool

On systems with PAM, ``pam_zfs_key(8)`` can load a user's key and mount their
encrypted home directory at login.

Changing the key
~~~~~~~~~~~~~~~~

``zfs change-key`` rewraps the master key with a new user key. It does not
re-encrypt the data, so it is instantaneous regardless of dataset size. The
existing key must already be loaded (or use ``-l`` to load it first).

.. code:: bash

   zfs change-key pool/secret
   zfs change-key -o keyformat=passphrase -o pbkdf2iters=500000 pool/secret
   zfs change-key -i pool/secret/child      # give up own key, inherit parent's

This is also the only way to change ``keyformat`` and ``pbkdf2iters`` after
creation.

**Changing the key does not undo a compromise.** Newly written data keeps
using the same master key as the existing data, so an attacker who obtained a
user key *and* the corresponding wrapped master key can still read what is
written later. The old wrapped master key is not overwritten on disk and may
remain recoverable by forensic analysis for an indeterminate time.

If the master key is compromised, the correct response is to securely erase
the drives, create a new pool and copy the data back. This can be approximated
in place by creating new datasets, copying the data into them (for example
with ``zfs send | zfs recv``), and then clearing the free space with
``zpool trim --secure`` if the hardware supports it, or ``zpool initialize``
otherwise.

Raw sends
~~~~~~~~~

``zfs send -w`` (``--raw``) sends the data exactly as it is on disk, still
encrypted. This means:

* backups can be taken without loading any keys;
* the receiving machine need not be trusted — it cannot read the data, and it
  cannot alter it without that being detected on the next read;
* the received dataset keeps its encryption, and its key, from the source.

.. code:: bash

   zfs send -w pool/secret@daily | ssh backup zfs receive -u tank/secret

A non-raw send of an encrypted dataset requires the keys to be loaded and
produces a plaintext stream, which is then encrypted (or not) according to the
destination's own properties. See :doc:`Send and Receive </Basic Concepts/Operations/Send and Receive>`.

Interaction with other features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Compression.** Encryption is applied after compression, so compression
ratios are preserved. The flip side is that a dataset can be vulnerable to a
CRIME-like attack if the applications accessing it let an attacker influence
what gets compressed alongside secret data.

**Checksums.** For encrypted data, the usual 256-bit checksum becomes 128 bits
of the chosen checksum plus 128 bits of MAC from the cipher suite. The MAC is
what gives protection against *maliciously* altered data, not just accidental
corruption.

**Deduplication** still works, but for security a dataset deduplicates only
against itself, its snapshots and its clones. Dedup with encryption leaks
which blocks within a dataset are identical, and costs extra CPU per written
block.

**Embedded data.** Encrypted data cannot use the ``embedded_data`` feature.

**copies=3** is not available on encrypted datasets — the implementation
stores encryption metadata where the third copy would go.

Further reading
~~~~~~~~~~~~~~~

* `zfs-load-key(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-load-key.8.html>`__ —
  including the full ``Encryption`` section
* `zfs-change-key(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-change-key.8.html>`__,
  `zfs-unload-key(8) <https://openzfs.github.io/openzfs-docs/man/master/8/zfs-unload-key.8.html>`__
* `zfsprops(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html>`__ —
  ``encryption``, ``keyformat``, ``keylocation``, ``pbkdf2iters``,
  ``keystatus``, ``encryptionroot``
* `pam_zfs_key(8) <https://openzfs.github.io/openzfs-docs/man/master/8/pam_zfs_key.8.html>`__
