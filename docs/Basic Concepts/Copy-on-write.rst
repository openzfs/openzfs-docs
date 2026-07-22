Copy-on-Write
=============

Almost everything distinctive about ZFS follows from one rule: **a block that
is in use is never overwritten.** Changing data means writing it somewhere
else and then switching over to the new version. Understanding that rule makes
the rest of ZFS — snapshots, ``zfs send``, self-healing, the absence of
``fsck`` — stop looking like separate features and start looking like
consequences.

The tree
~~~~~~~~

A pool is one large tree. Leaves hold data; interior nodes hold *block
pointers*, each of which records where a child lives, how big it is, and — the
part that matters — its checksum. A block's checksum is therefore stored in
its parent, not next to the block itself, so a damaged block cannot vouch for
itself.

At the root sits the **uberblock**. Everything in the pool is reachable from
it.

Writing something
~~~~~~~~~~~~~~~~~

Modifying a block in the middle of the tree cannot happen in place, so ZFS:

#. writes the new data to free space;
#. writes a new version of the parent, pointing at the new block;
#. repeats up the tree, since each parent's checksum has now changed;
#. finally writes a new uberblock.

.. raw:: html

   <div style="overflow-x:auto; margin:1.5em 0;">
   <svg viewBox="0 0 760 400" width="100%" style="max-width:760px; height:auto;
        color:inherit;" role="img"
        aria-label="A ZFS block tree before and after a copy-on-write update.
        Modifying one data block causes new copies of that block, its parent
        indirect block, the root block and the uberblock to be written, while
        every unmodified block is shared by reference.">
     <defs>
       <marker id="cowarrow" viewBox="0 0 10 10" refX="9" refY="5"
               markerWidth="6" markerHeight="6" orient="auto-start-reverse">
         <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/>
       </marker>
     </defs>
     <g fill="none" stroke="currentColor" marker-end="url(#cowarrow)">
       <g opacity="0.45" stroke-width="1">
         <path d="M151 60 V110"/>
         <path d="M145 140 L74 195"/>
         <path d="M158 140 L242 195"/>
         <path d="M62 225 L39 285"/>
         <path d="M76 225 L99 285"/>
         <path d="M242 225 L199 285"/>
         <path d="M254 225 L269 285"/>
       </g>
       <g stroke-width="2.2">
         <path d="M523 60 V110"/>
         <path d="M519 140 L521 195"/>
         <path d="M521 225 L517 285"/>
       </g>
       <g stroke-width="2.2" stroke-dasharray="6 4">
         <path d="M490 128 C 380 150, 200 168, 99 197"/>
         <path d="M490 214 C 400 244, 300 258, 218 286"/>
       </g>
     </g>
     <g fill="none" stroke="currentColor">
       <g opacity="0.45" stroke-width="1">
         <rect x="120" y="30" width="62" height="30" rx="4"/>
         <rect x="120" y="110" width="62" height="30" rx="4"/>
         <rect x="40" y="195" width="56" height="30" rx="4"/>
         <rect x="220" y="195" width="56" height="30" rx="4"/>
         <rect x="10" y="285" width="46" height="28" rx="4"/>
         <rect x="80" y="285" width="46" height="28" rx="4"/>
         <rect x="250" y="285" width="46" height="28" rx="4"/>
       </g>
       <rect x="170" y="285" width="46" height="28" rx="4" stroke-width="2.2"/>
       <rect x="40" y="195" width="56" height="30" rx="4" stroke-width="2.2"/>
       <g stroke-width="2.2">
         <rect x="490" y="30" width="66" height="30" rx="4"/>
         <rect x="490" y="110" width="66" height="30" rx="4"/>
         <rect x="490" y="195" width="62" height="30" rx="4"/>
         <rect x="490" y="285" width="54" height="28" rx="4"/>
       </g>
     </g>
     <g fill="currentColor" font-family="monospace" font-size="13"
        text-anchor="middle">
       <g opacity="0.55">
         <text x="151" y="50">uberblock</text>
         <text x="151" y="130">root</text>
         <text x="68" y="215">ind 1</text>
         <text x="248" y="215">ind 2</text>
         <text x="33" y="304">D1</text>
         <text x="103" y="304">D2</text>
         <text x="273" y="304">D4</text>
       </g>
       <text x="193" y="304">D3</text>
       <text x="68" y="215">ind 1</text>
       <text x="523" y="50">uberblock'</text>
       <text x="523" y="130">root'</text>
       <text x="521" y="215">ind 2'</text>
       <text x="517" y="304">D4'</text>
     </g>
     <g fill="currentColor" font-family="sans-serif" font-size="12">
       <text x="10" y="352" opacity="0.55">faded: the previous tree, still
         intact and still consistent</text>
       <text x="10" y="372">solid: newly written blocks</text>
       <text x="10" y="392" font-style="italic">dashed: references to
         unmodified blocks &#8212; shared, not copied</text>
     </g>
   </svg>
   </div>

In the diagram, only ``D4`` was modified. That forced new copies of ``D4``,
its parent ``ind 2``, the ``root`` block and finally the uberblock — the
*path from the changed block to the root*, and nothing else. ``D1``, ``D2``,
``D3`` and ``ind 1`` are referenced by the new tree, not duplicated.

Until that last step, nothing has changed: the old uberblock still describes a
complete, consistent pool. The switch to the new tree is a single atomic
write. This is why a ZFS pool is always consistent on disk regardless of when
power is lost — there is no window in which the pool is half-updated, and so
no equivalent of the RAID-5 write hole and no need for a journal replay of
metadata.

The cost of a small write is therefore proportional to the *depth* of the
tree, not its size — and the old tree is left whole, which is exactly what a
snapshot needs.

The uberblock is not overwritten either. Each device label carries a
**128 KiB uberblock ring** written round-robin, and each device carries
**four copies of the label** — two at the start, two at the end — so that
losing either end of a disk, or a partition table rewrite, does not lose the
root of the tree. On import ZFS picks the valid uberblock with the highest
transaction number.

Transaction groups
~~~~~~~~~~~~~~~~~~

Writes are not committed one at a time. They are batched into a **transaction
group** (txg), and the whole group commits atomically or not at all.

Three transaction groups are in flight at once: one **open** and accepting new
writes, one **quiescing** (closed to new writes, waiting for stragglers), and
one **syncing** to disk. A group closes when ``zfs_txg_timeout`` elapses —
5 seconds by default — or when enough dirty data has accumulated.

The practical consequence is that an asynchronous write returns as soon as it
is in memory, and reaches disk up to a few seconds later. A crash loses the
groups that had not finished syncing, and the pool comes back at the last
committed one. It is consistent, just slightly older.

That is unacceptable for applications that called ``fsync()``, which is what
the :doc:`ZFS Intent Log </Basic Concepts/Pool Structure/Caching>` exists for:
it records synchronous writes immediately so they can be replayed if the
system dies before the txg commits. The ZIL is never read otherwise.

What follows from it
~~~~~~~~~~~~~~~~~~~~

**Snapshots are nearly free.** The old tree is already intact and complete —
a snapshot is just a reference that stops those blocks being freed. Nothing is
copied. See
:doc:`Snapshots, Clones and Bookmarks </Basic Concepts/Datasets/Snapshots and Clones>`.

**Clones and block cloning are cheap** for the same reason: multiple
references to the same block are normal, so sharing costs a reference rather
than a copy.

**Incremental replication is exact.** Because every block records the txg in
which it was born, ZFS can find precisely the blocks that changed between two
snapshots without scanning anything. See
:doc:`Send and Receive </Basic Concepts/Operations/Send and Receive>`.

**Corruption is detectable and often repairable.** The checksum lives in the
parent, so a block that comes back wrong is caught on read, and with
redundancy a good copy is used and the bad one rewritten. See
:doc:`Checksums </Basic Concepts/Data Storage/Checksums>` and
:doc:`Scrub and Resilver </Basic Concepts/Operations/Scrub and Resilver>`.

**There is no fsck.** ``fsck.zfs`` exists only to satisfy the interface and
does essentially nothing — its man page says so. Nothing needs to be checked
for consistency at mount time, because the pool is never left inconsistent.
Verifying *content* is a different job, and that is what
``zpool scrub`` does, online.

The costs
~~~~~~~~~

Copy-on-write is not free, and its costs explain several tuning topics:

**Fragmentation.** Rewriting a file scatters its new blocks wherever there was
free space, so data that was written sequentially and then modified randomly
does not stay sequential. This is why ZFS is sensitive to how full a pool is:
finding contiguous free space gets harder, and the allocator has to work
harder. See
:doc:`Workload Tuning </Performance and Tuning/Workload Tuning>`.

**Free space is needed to write at all.** Even deleting data requires
allocating, which is why ZFS reserves slop space — see
:doc:`Quotas and Reservations </Basic Concepts/Datasets/Quotas and Reservations>`.

**Partial writes are expensive.** Changing part of a record means reading the
whole record, modifying it, and writing a new one. Matching ``recordsize`` to
the application's I/O size is the usual remedy, and the reason databases and
VM images get their own settings.

Further reading
~~~~~~~~~~~~~~~

* `zfsconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zfsconcepts.7.html>`__,
  `zpoolconcepts(7) <https://openzfs.github.io/openzfs-docs/man/master/7/zpoolconcepts.7.html>`__
* :doc:`Checksums </Basic Concepts/Data Storage/Checksums>`,
  :doc:`Snapshots, Clones and Bookmarks </Basic Concepts/Datasets/Snapshots and Clones>`
* :doc:`ZFS Transaction Delay </Performance and Tuning/ZFS Transaction Delay>`,
  :doc:`ZIO Scheduler </Performance and Tuning/ZIO Scheduler>`
