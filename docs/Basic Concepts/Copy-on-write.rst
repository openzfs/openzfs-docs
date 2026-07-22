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

   <div style="margin:1.75em 0">
   <div style="overflow-x:auto">
   <svg id="cow-diagram" viewBox="0 0 600 410" width="100%"
        style="max-width:600px;height:auto" role="img"
        aria-label="A ZFS block tree being updated. Modifying data block D4
        causes a new copy of D4 to be written, then a new copy of its parent
        indirect block, then a new root block, then a new uberblock. Those
        four old blocks are superseded; every other block is referenced by
        the new tree rather than copied.">
     <style>
       #cow-diagram { --cow-new: #1f7a4d; }
       @media (prefers-color-scheme: dark) {
         #cow-diagram { --cow-new: #56c98d; }
       }
       #cow-diagram .cow-box { fill: currentColor; fill-opacity: .05;
         stroke: currentColor; stroke-width: 1.25; }
       #cow-diagram .cow-edge { fill: none; stroke: currentColor;
         stroke-width: 1.25; }
       #cow-diagram .cow-lbl { fill: currentColor;
         font-family: ui-monospace,SFMono-Regular,Menlo,monospace;
         font-size: 12px; text-anchor: middle; }
       #cow-diagram .cow-old { opacity: .38; }
       #cow-diagram .cow-new .cow-box { stroke: var(--cow-new);
         fill: var(--cow-new); fill-opacity: .1; stroke-width: 2; }
       #cow-diagram .cow-new .cow-edge { stroke: var(--cow-new);
         stroke-width: 2; }
       #cow-diagram .cow-new .cow-lbl { fill: var(--cow-new);
         font-weight: 600; }
       /* The old blocks on the path from the change to the root. They were
          not written -- they were replaced -- so they get the accent colour
          without the weight of a new block. */
       #cow-diagram .cow-sup .cow-box { stroke: var(--cow-new);
         stroke-width: 1.5; fill: none; }
       #cow-diagram .cow-sup .cow-lbl { fill: currentColor; opacity: .75; }
       #cow-diagram .cow-share { stroke: var(--cow-new); stroke-width: 1.75;
         stroke-dasharray: 5 4; fill: none; }
       #cow-diagram .cow-key { fill: currentColor;
         font-family: ui-monospace,SFMono-Regular,Menlo,monospace;
         font-size: 11px; }
       /* Without JS nothing is ever given .cow-hidden, so the figure shows
          the finished state -- which is what it should say anyway. */
       #cow-diagram .cow-step { transition: opacity .5s ease,
         transform .5s ease; transform-box: fill-box;
         transform-origin: center; }
       #cow-diagram .cow-step.cow-hidden { opacity: 0;
         transform: translateY(8px) scale(.94); }
       @media (prefers-reduced-motion: reduce) {
         #cow-diagram .cow-step { transition: none; }
       }
       .cow-play { font: inherit; font-size: .85em; cursor: pointer;
         margin-top: .5em; padding: .35em .9em; border-radius: 4px;
         border: 1px solid currentColor; background: transparent;
         color: inherit; opacity: .75; }
       .cow-play:hover, .cow-play:focus-visible { opacity: 1; }
     </style>
     <defs>
       <marker id="cow-a" viewBox="0 0 10 10" refX="9" refY="5"
               markerWidth="5" markerHeight="5" orient="auto-start-reverse">
         <path d="M0 0 L10 5 L0 10 z" fill="currentColor"/>
       </marker>
       <marker id="cow-b" viewBox="0 0 10 10" refX="9" refY="5"
               markerWidth="5" markerHeight="5" orient="auto-start-reverse">
         <path d="M0 0 L10 5 L0 10 z" fill="#1f7a4d"/>
       </marker>
     </defs>

     <g class="cow-old">
       <g marker-end="url(#cow-a)">
         <path class="cow-edge" d="M210 67 V120"/>
         <path class="cow-edge" d="M195 152 L127 205"/>
         <path class="cow-edge" d="M225 152 L293 205"/>
         <path class="cow-edge" d="M104 237 L79 290"/>
         <path class="cow-edge" d="M136 237 L161 290"/>
         <path class="cow-edge" d="M284 237 L259 290"/>
         <path class="cow-edge" d="M316 237 L341 290"/>
       </g>
       <rect class="cow-box" x="160" y="35" width="100" height="32" rx="6"/>
       <rect class="cow-box" x="170" y="120" width="80" height="32" rx="6"/>
       <rect class="cow-box" x="80" y="205" width="80" height="32" rx="6"/>
       <rect class="cow-box" x="260" y="205" width="80" height="32" rx="6"/>
       <rect class="cow-box" x="40" y="290" width="70" height="30" rx="6"/>
       <rect class="cow-box" x="130" y="290" width="70" height="30" rx="6"/>
       <rect class="cow-box" x="220" y="290" width="70" height="30" rx="6"/>
       <rect class="cow-box" x="310" y="290" width="70" height="30" rx="6"/>
       <text class="cow-lbl" x="210" y="56">uberblock</text>
       <text class="cow-lbl" x="210" y="141">root</text>
       <text class="cow-lbl" x="120" y="226">ind 1</text>
       <text class="cow-lbl" x="300" y="226">ind 2</text>
       <text class="cow-lbl" x="75" y="310">D1</text>
       <text class="cow-lbl" x="165" y="310">D2</text>
       <text class="cow-lbl" x="255" y="310">D3</text>
       <text class="cow-lbl" x="345" y="310">D4</text>
     </g>

     <g class="cow-sup">
       <g class="cow-step" data-step="1">
         <rect class="cow-box" x="310" y="290" width="70" height="30" rx="6"/>
         <text class="cow-lbl" x="345" y="310">D4</text>
       </g>
       <g class="cow-step" data-step="2">
         <rect class="cow-box" x="260" y="205" width="80" height="32" rx="6"/>
         <text class="cow-lbl" x="300" y="226">ind 2</text>
       </g>
       <g class="cow-step" data-step="3">
         <rect class="cow-box" x="170" y="120" width="80" height="32" rx="6"/>
         <text class="cow-lbl" x="210" y="141">root</text>
       </g>
       <g class="cow-step" data-step="4">
         <rect class="cow-box" x="160" y="35" width="100" height="32" rx="6"/>
         <text class="cow-lbl" x="210" y="56">uberblock</text>
       </g>
     </g>

     <g class="cow-new">
       <g class="cow-step" data-step="1">
         <rect class="cow-box" x="470" y="290" width="76" height="30" rx="6"/>
         <text class="cow-lbl" x="508" y="310">D4'</text>
       </g>
       <g class="cow-step" data-step="2">
         <rect class="cow-box" x="470" y="205" width="86" height="32" rx="6"/>
         <text class="cow-lbl" x="513" y="226">ind 2'</text>
         <path class="cow-edge" d="M513 237 V284" marker-end="url(#cow-b)"/>
       </g>
       <g class="cow-step" data-step="3">
         <rect class="cow-box" x="470" y="120" width="86" height="32" rx="6"/>
         <text class="cow-lbl" x="513" y="141">root'</text>
         <path class="cow-edge" d="M513 152 V199" marker-end="url(#cow-b)"/>
       </g>
       <g class="cow-step" data-step="4">
         <rect class="cow-box" x="458" y="35" width="110" height="32" rx="6"/>
         <text class="cow-lbl" x="513" y="56">uberblock'</text>
         <path class="cow-edge" d="M513 67 V114" marker-end="url(#cow-b)"/>
       </g>
       <g class="cow-step" data-step="5">
         <path class="cow-share" d="M470 140 L166 213" marker-end="url(#cow-b)"/>
         <path class="cow-share" d="M470 225 L296 295" marker-end="url(#cow-b)"/>
       </g>
     </g>

     <g class="cow-key">
       <rect x="10" y="330" width="22" height="11" rx="3" fill="currentColor"
             fill-opacity=".05" stroke="currentColor" opacity=".38"/>
       <text x="42" y="340" opacity=".7">untouched &#8212; still whole, still
         consistent</text>
       <rect x="10" y="349" width="22" height="11" rx="3" fill="none"
             stroke="var(--cow-new)" stroke-width="1.5"/>
       <text x="42" y="359" opacity=".85">superseded &#8212; freed, unless a
         snapshot holds it</text>
       <rect x="10" y="368" width="22" height="11" rx="3"
             fill="var(--cow-new)" fill-opacity=".1" stroke="var(--cow-new)"
             stroke-width="2"/>
       <text x="42" y="378" opacity=".85">written by this transaction</text>
       <path d="M11 391 H31" stroke="var(--cow-new)" stroke-width="1.75"
             stroke-dasharray="5 4"/>
       <text x="42" y="395" opacity=".85">shared by reference, not copied</text>
     </g>
   </svg>
   </div>
   <button type="button" id="cow-play" class="cow-play" hidden>
     Replay the write</button>
   <script>
   (function () {
     var svg = document.getElementById('cow-diagram');
     var btn = document.getElementById('cow-play');
     if (!svg || !btn) { return; }
     var groups = Array.prototype.slice.call(svg.querySelectorAll('.cow-step'));
     if (!groups.length) { return; }
     var calm = window.matchMedia &&
       window.matchMedia('(prefers-reduced-motion: reduce)').matches;
     var last = 0;
     groups.forEach(function (g) {
       last = Math.max(last, parseInt(g.getAttribute('data-step'), 10) || 0);
     });
     var timers = [];
     function play() {
       timers.forEach(clearTimeout);
       timers = [];
       groups.forEach(function (g) { g.classList.add('cow-hidden'); });
       svg.getBoundingClientRect();
       for (var s = 1; s <= last; s++) {
         (function (step) {
           timers.push(setTimeout(function () {
             groups.forEach(function (g) {
               if (parseInt(g.getAttribute('data-step'), 10) === step) {
                 g.classList.remove('cow-hidden');
               }
             });
           }, 500 + (step - 1) * (calm ? 320 : 1150)));
         })(s);
       }
     }
     btn.hidden = false;
     btn.addEventListener('click', play);
     if (!calm) { play(); }
   })();
   </script>
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
