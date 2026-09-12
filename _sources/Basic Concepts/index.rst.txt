Basic Concepts
==============

How OpenZFS is put together and what its features actually do.

If you are new to ZFS, read
:doc:`Copy-on-Write </Basic Concepts/Copy-on-write>` first — most of what
follows is a consequence of it — and then
:doc:`VDEVs </Basic Concepts/Pool Structure/VDEVs>`, since pool layout is the
decision that is hardest to change later.

These pages explain concepts and trade-offs; the
`man pages <../man/index.html>`__ remain the reference for exact syntax and
options.

.. toctree::
   :maxdepth: 2

   Copy-on-write
   Pool Structure/index
   Datasets/index
   Data Storage/index
   Operations/index
