Module Parameters
=================

Most of the ZFS kernel module parameters are accessible in the SysFS
``/sys/module/zfs/parameters`` directory. Current value can be observed
by

.. code:: shell

   cat /sys/module/zfs/parameters/PARAMETER

Many of these can be changed by writing new values. These are denoted by
Change|Dynamic in the PARAMETER details below.

.. code:: shell

   echo NEWVALUE >> /sys/module/zfs/parameters/PARAMETER

If the parameter is not dynamically adjustable, an error can occur and
the value will not be set. It can be helpful to check the permissions
for the PARAMETER file in SysFS.

In some cases, the parameter must be set prior to loading the kernel
modules or it is desired to have the parameters set automatically at
boot time. For many distros, this can be accomplished by creating a file
named ``/etc/modprobe.d/zfs.conf`` containing a text line for each
module parameter using the format:

::

   # change PARAMETER for workload XZY to solve problem PROBLEM_DESCRIPTION
   # changed by YOUR_NAME on DATE
   options zfs PARAMETER=VALUE

Some parameters related to ZFS operations are located in module
parameters other than in the ``zfs`` kernel module. These are documented
in the individual parameter description. Unless otherwise noted, the
tunable applies to the ``zfs`` kernel module. For example, the ``icp``
kernel module parameters are visible in the
``/sys/module/icp/parameters`` directory and can be set by default at
boot time by changing the ``/etc/modprobe.d/icp.conf`` file.

See the man page for *modprobe.d* for more information.

zfs-module-parameters Manual Page
---------------------------------

The `zfs-module-parameters(5) <../man/5/zfs-module-parameters.5.html>`_
man page contains brief descriptions of
the module parameters. Alas, man pages are not as suitable for quick
reference as documentation pages. This page is intended to be a better
cross-reference and capture some of the wisdom of ZFS developers and
practitioners.

ZFS Module Parameters
---------------------

The ZFS kernel module, ``zfs.ko``, parameters are detailed below.

To observe the list of parameters along with a short synopsis of each
parameter, use the ``modinfo`` command:

.. code:: bash

   modinfo zfs

Tags
----

The list of parameters is quite large and resists hierarchical
representation. To assist in quickly finding relevant information
quickly, each module parameter has a "Tags" row with keywords for
frequent searches.

ABD
~~~

-  `zfs_abd_scatter_enabled <#zfs-abd-scatter-enabled>`__
-  `zfs_abd_scatter_max_order <#zfs-abd-scatter-max-order>`__
-  `zfs_compressed_arc_enabled <#zfs-compressed-arc-enabled>`__

allocation
~~~~~~~~~~

-  `dmu_object_alloc_chunk_shift <#dmu-object-alloc-chunk-shift>`__
-  `metaslab_aliquot <#metaslab-aliquot>`__
-  `metaslab_bias_enabled <#metaslab-bias-enabled>`__
-  `metaslab_debug_load <#metaslab-debug-load>`__
-  `metaslab_debug_unload <#metaslab-debug-unload>`__
-  `metaslab_force_ganging <#metaslab-force-ganging>`__
-  `metaslab_fragmentation_factor_enabled <#metaslab-fragmentation-factor-enabled>`__
-  `zfs_metaslab_fragmentation_threshold <#zfs-metaslab-fragmentation-threshold>`__
-  `metaslab_lba_weighting_enabled <#metaslab-lba-weighting-enabled>`__
-  `metaslab_preload_enabled <#metaslab-preload-enabled>`__
-  `zfs_metaslab_segment_weight_enabled <#zfs-metaslab-segment-weight-enabled>`__
-  `zfs_metaslab_switch_threshold <#zfs-metaslab-switch-threshold>`__
-  `metaslabs_per_vdev <#metaslabs-per-vdev>`__
-  `zfs_mg_fragmentation_threshold <#zfs-mg-fragmentation-threshold>`__
-  `zfs_mg_noalloc_threshold <#zfs-mg-noalloc-threshold>`__
-  `spa_asize_inflation <#spa-asize-inflation>`__
-  `spa_load_verify_data <#spa-load-verify-data>`__
-  `spa_slop_shift <#spa-slop-shift>`__
-  `zfs_vdev_default_ms_count <#zfs-vdev-default-ms-count>`__

ARC
~~~

-  `zfs_abd_scatter_min_size <#zfs-abd-scatter-min-size>`__
-  `zfs_arc_average_blocksize <#zfs-arc-average-blocksize>`__
-  `zfs_arc_dnode_limit <#zfs-arc-dnode-limit>`__
-  `zfs_arc_dnode_limit_percent <#zfs-arc-dnode-limit-percent>`__
-  `zfs_arc_dnode_reduce_percent <#zfs-arc-dnode-reduce-percent>`__
-  `zfs_arc_evict_batch_limit <#zfs-arc-evict-batch-limit>`__
-  `zfs_arc_grow_retry <#zfs-arc-grow-retry>`__
-  `zfs_arc_lotsfree_percent <#zfs-arc-lotsfree-percent>`__
-  `zfs_arc_max <#zfs-arc-max>`__
-  `zfs_arc_meta_adjust_restarts <#zfs-arc-meta-adjust-restarts>`__
-  `zfs_arc_meta_limit <#zfs-arc-meta-limit>`__
-  `zfs_arc_meta_limit_percent <#zfs-arc-meta-limit-percent>`__
-  `zfs_arc_meta_min <#zfs-arc-meta-min>`__
-  `zfs_arc_meta_prune <#zfs-arc-meta-prune>`__
-  `zfs_arc_meta_strategy <#zfs-arc-meta-strategy>`__
-  `zfs_arc_min <#zfs-arc-min>`__
-  `zfs_arc_min_prefetch_lifespan <#zfs-arc-min-prefetch-lifespan>`__
-  `zfs_arc_min_prefetch_ms <#zfs-arc-min-prefetch-ms>`__
-  `zfs_arc_min_prescient_prefetch_ms <#zfs-arc-min-prescient-prefetch-ms>`__
-  `zfs_arc_overflow_shift <#zfs-arc-overflow-shift>`__
-  `zfs_arc_p_dampener_disable <#zfs-arc-p-dampener-disable>`__
-  `zfs_arc_p_min_shift <#zfs-arc-p-min-shift>`__
-  `zfs_arc_pc_percent <#zfs-arc-pc-percent>`__
-  `zfs_arc_shrink_shift <#zfs-arc-shrink-shift>`__
-  `zfs_arc_sys_free <#zfs-arc-sys-free>`__
-  `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__
-  `dbuf_cache_shift <#dbuf-cache-shift>`__
-  `dbuf_metadata_cache_shift <#dbuf-metadata-cache-shift>`__
-  `zfs_disable_dup_eviction <#zfs-disable-dup-eviction>`__
-  `l2arc_feed_again <#l2arc-feed-again>`__
-  `l2arc_feed_min_ms <#l2arc-feed-min-ms>`__
-  `l2arc_feed_secs <#l2arc-feed-secs>`__
-  `l2arc_headroom <#l2arc-headroom>`__
-  `l2arc_headroom_boost <#l2arc-headroom-boost>`__
-  `l2arc_meta_percent <#l2arc-meta-percent>`__
-  `l2arc_mfuonly <#l2arc-mfuonly>`__
-  `l2arc_nocompress <#l2arc-nocompress>`__
-  `l2arc_noprefetch <#l2arc-noprefetch>`__
-  `l2arc_norw <#l2arc-norw>`__
-  `l2arc_rebuild_blocks_min_l2size <#l2arc-rebuild-blocks-min-l2size>`__
-  `l2arc_rebuild_enabled <#l2arc-rebuild-enabled>`__
-  `l2arc_trim_ahead <#l2arc-trim-ahead>`__
-  `l2arc_write_boost <#l2arc-write-boost>`__
-  `l2arc_write_max <#l2arc-write-max>`__
-  `zfs_multilist_num_sublists <#zfs-multilist-num-sublists>`__
-  `spa_load_verify_shift <#spa-load-verify-shift>`__

channel_programs
~~~~~~~~~~~~~~~~

-  `zfs_lua_max_instrlimit <#zfs-lua-max-instrlimit>`__
-  `zfs_lua_max_memlimit <#zfs-lua-max-memlimit>`__

checkpoint
~~~~~~~~~~

-  `zfs_spa_discard_memory_limit <#zfs-spa-discard-memory-limit>`__

checksum
~~~~~~~~

-  `zfs_checksums_per_second <#zfs-checksums-per-second>`__
-  `zfs_fletcher_4_impl <#zfs-fletcher-4-impl>`__
-  `zfs_nopwrite_enabled <#zfs-nopwrite-enabled>`__
-  `zfs_qat_checksum_disable <#zfs-qat-checksum-disable>`__

compression
~~~~~~~~~~~

-  `zfs_compressed_arc_enabled <#zfs-compressed-arc-enabled>`__
-  `zfs_qat_compress_disable <#zfs-qat-compress-disable>`__
-  `zfs_qat_disable <#zfs-qat-disable>`__

CPU
~~~

-  `zfs_fletcher_4_impl <#zfs-fletcher-4-impl>`__
-  `zfs_mdcomp_disable <#zfs-mdcomp-disable>`__
-  `spl_kmem_cache_kmem_threads <#spl-kmem-cache-kmem-threads>`__
-  `spl_kmem_cache_magazine_size <#spl-kmem-cache-magazine-size>`__
-  `spl_taskq_thread_bind <#spl-taskq-thread-bind>`__
-  `spl_taskq_thread_priority <#spl-taskq-thread-priority>`__
-  `spl_taskq_thread_sequential <#spl-taskq-thread-sequential>`__
-  `zfs_vdev_raidz_impl <#zfs-vdev-raidz-impl>`__

dataset
~~~~~~~

-  `zfs_max_dataset_nesting <#zfs-max-dataset-nesting>`__

dbuf_cache
~~~~~~~~~~

-  `dbuf_cache_hiwater_pct <#dbuf-cache-hiwater-pct>`__
-  `dbuf_cache_lowater_pct <#dbuf-cache-lowater-pct>`__
-  `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__
-  `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__
-  `dbuf_cache_max_shift <#dbuf-cache-max-shift>`__
-  `dbuf_cache_shift <#dbuf-cache-shift>`__
-  `dbuf_metadata_cache_max_bytes <#dbuf-metadata-cache-max-bytes>`__
-  `dbuf_metadata_cache_shift <#dbuf-metadata-cache-shift>`__

debug
~~~~~

-  `zfs_dbgmsg_enable <#zfs-dbgmsg-enable>`__
-  `zfs_dbgmsg_maxsize <#zfs-dbgmsg-maxsize>`__
-  `zfs_dbuf_state_index <#zfs-dbuf-state-index>`__
-  `zfs_deadman_checktime_ms <#zfs-deadman-checktime-ms>`__
-  `zfs_deadman_enabled <#zfs-deadman-enabled>`__
-  `zfs_deadman_failmode <#zfs-deadman-failmode>`__
-  `zfs_deadman_synctime_ms <#zfs-deadman-synctime-ms>`__
-  `zfs_deadman_ziotime_ms <#zfs-deadman-ziotime-ms>`__
-  `zfs_flags <#zfs-flags>`__
-  `zfs_free_leak_on_eio <#zfs-free-leak-on-eio>`__
-  `zfs_nopwrite_enabled <#zfs-nopwrite-enabled>`__
-  `zfs_object_mutex_size <#zfs-object-mutex-size>`__
-  `zfs_read_history <#zfs-read-history>`__
-  `zfs_read_history_hits <#zfs-read-history-hits>`__
-  `spl_panic_halt <#spl-panic-halt>`__
-  `zfs_txg_history <#zfs-txg-history>`__
-  `zfs_zevent_cols <#zfs-zevent-cols>`__
-  `zfs_zevent_console <#zfs-zevent-console>`__
-  `zfs_zevent_len_max <#zfs-zevent-len-max>`__
-  `zil_replay_disable <#zil-replay-disable>`__
-  `zio_deadman_log_all <#zio-deadman-log-all>`__
-  `zio_decompress_fail_fraction <#zio-decompress-fail-fraction>`__
-  `zio_delay_max <#zio-delay-max>`__

dedup
~~~~~

-  `zfs_ddt_data_is_special <#zfs-ddt-data-is-special>`__
-  `zfs_disable_dup_eviction <#zfs-disable-dup-eviction>`__

delay
~~~~~

-  `zfs_delays_per_second <#zfs-delays-per-second>`__

delete
~~~~~~

-  `zfs_async_block_max_blocks <#zfs-async-block-max-blocks>`__
-  `zfs_delete_blocks <#zfs-delete-blocks>`__
-  `zfs_free_bpobj_enabled <#zfs-free-bpobj-enabled>`__
-  `zfs_free_max_blocks <#zfs-free-max-blocks>`__
-  `zfs_free_min_time_ms <#zfs-free-min-time-ms>`__
-  `zfs_obsolete_min_time_ms <#zfs-obsolete-min-time-ms>`__
-  `zfs_per_txg_dirty_frees_percent <#zfs-per-txg-dirty-frees-percent>`__

discard
~~~~~~~

-  `zvol_max_discard_blocks <#zvol-max-discard-blocks>`__

disks
~~~~~

-  `zfs_nocacheflush <#zfs-nocacheflush>`__
-  `zil_nocacheflush <#zil-nocacheflush>`__

DMU
~~~

-  `zfs_async_block_max_blocks <#zfs-async-block-max-blocks>`__
-  `dmu_object_alloc_chunk_shift <#dmu-object-alloc-chunk-shift>`__
-  `zfs_dmu_offset_next_sync <#zfs-dmu-offset-next-sync>`__

encryption
~~~~~~~~~~

-  `icp_aes_impl <#icp-aes-impl>`__
-  `icp_gcm_impl <#icp-gcm-impl>`__
-  `zfs_key_max_salt_uses <#zfs-key-max-salt-uses>`__
-  `zfs_qat_encrypt_disable <#zfs-qat-encrypt-disable>`__

filesystem
~~~~~~~~~~

-  `zfs_admin_snapshot <#zfs-admin-snapshot>`__
-  `zfs_delete_blocks <#zfs-delete-blocks>`__
-  `zfs_expire_snapshot <#zfs-expire-snapshot>`__
-  `zfs_free_max_blocks <#zfs-free-max-blocks>`__
-  `zfs_max_recordsize <#zfs-max-recordsize>`__
-  `zfs_read_chunk_size <#zfs-read-chunk-size>`__

fragmentation
~~~~~~~~~~~~~

-  `zfs_metaslab_fragmentation_threshold <#zfs-metaslab-fragmentation-threshold>`__
-  `zfs_mg_fragmentation_threshold <#zfs-mg-fragmentation-threshold>`__
-  `zfs_mg_noalloc_threshold <#zfs-mg-noalloc-threshold>`__

HDD
~~~

-  `metaslab_lba_weighting_enabled <#metaslab-lba-weighting-enabled>`__
-  `zfs_vdev_mirror_rotating_inc <#zfs-vdev-mirror-rotating-inc>`__
-  `zfs_vdev_mirror_rotating_seek_inc <#zfs-vdev-mirror-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_seek_offset <#zfs-vdev-mirror-rotating-seek-offset>`__

hostid
~~~~~~

-  `spl_hostid <#spl-hostid>`__
-  `spl_hostid_path <#spl-hostid-path>`__

import
~~~~~~

-  `zfs_autoimport_disable <#zfs-autoimport-disable>`__
-  `zfs_max_missing_tvds <#zfs-max-missing-tvds>`__
-  `zfs_multihost_fail_intervals <#zfs-multihost-fail-intervals>`__
-  `zfs_multihost_history <#zfs-multihost-history>`__
-  `zfs_multihost_import_intervals <#zfs-multihost-import-intervals>`__
-  `zfs_multihost_interval <#zfs-multihost-interval>`__
-  `zfs_recover <#zfs-recover>`__
-  `spa_config_path <#spa-config-path>`__
-  `spa_load_print_vdev_tree <#spa-load-print-vdev-tree>`__
-  `spa_load_verify_maxinflight <#spa-load-verify-maxinflight>`__
-  `spa_load_verify_metadata <#spa-load-verify-metadata>`__
-  `spa_load_verify_shift <#spa-load-verify-shift>`__
-  `zvol_inhibit_dev <#zvol-inhibit-dev>`__

L2ARC
~~~~~

-  `l2arc_feed_again <#l2arc-feed-again>`__
-  `l2arc_feed_min_ms <#l2arc-feed-min-ms>`__
-  `l2arc_feed_secs <#l2arc-feed-secs>`__
-  `l2arc_headroom <#l2arc-headroom>`__
-  `l2arc_headroom_boost <#l2arc-headroom-boost>`__
-  `l2arc_meta_percent <#l2arc-meta-percent>`__
-  `l2arc_mfuonly <#l2arc-mfuonly>`__
-  `l2arc_nocompress <#l2arc-nocompress>`__
-  `l2arc_noprefetch <#l2arc-noprefetch>`__
-  `l2arc_norw <#l2arc-norw>`__
-  `l2arc_rebuild_blocks_min_l2size <#l2arc-rebuild-blocks-min-l2size>`__
-  `l2arc_rebuild_enabled <#l2arc-rebuild-enabled>`__
-  `l2arc_trim_ahead <#l2arc-trim-ahead>`__
-  `l2arc_write_boost <#l2arc-write-boost>`__
-  `l2arc_write_max <#l2arc-write-max>`__

memory
~~~~~~

-  `zfs_abd_scatter_enabled <#zfs-abd-scatter-enabled>`__
-  `zfs_abd_scatter_max_order <#zfs-abd-scatter-max-order>`__
-  `zfs_arc_average_blocksize <#zfs-arc-average-blocksize>`__
-  `zfs_arc_grow_retry <#zfs-arc-grow-retry>`__
-  `zfs_arc_lotsfree_percent <#zfs-arc-lotsfree-percent>`__
-  `zfs_arc_max <#zfs-arc-max>`__
-  `zfs_arc_pc_percent <#zfs-arc-pc-percent>`__
-  `zfs_arc_shrink_shift <#zfs-arc-shrink-shift>`__
-  `zfs_arc_sys_free <#zfs-arc-sys-free>`__
-  `zfs_dedup_prefetch <#zfs-dedup-prefetch>`__
-  `zfs_max_recordsize <#zfs-max-recordsize>`__
-  `metaslab_debug_load <#metaslab-debug-load>`__
-  `metaslab_debug_unload <#metaslab-debug-unload>`__
-  `zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__
-  `zfs_scan_strict_mem_lim <#zfs-scan-strict-mem-lim>`__
-  `spl_kmem_alloc_max <#spl-kmem-alloc-max>`__
-  `spl_kmem_alloc_warn <#spl-kmem-alloc-warn>`__
-  `spl_kmem_cache_expire <#spl-kmem-cache-expire>`__
-  `spl_kmem_cache_kmem_limit <#spl-kmem-cache-kmem-limit>`__
-  `spl_kmem_cache_kmem_threads <#spl-kmem-cache-kmem-threads>`__
-  `spl_kmem_cache_magazine_size <#spl-kmem-cache-magazine-size>`__
-  `spl_kmem_cache_max_size <#spl-kmem-cache-max-size>`__
-  `spl_kmem_cache_obj_per_slab <#spl-kmem-cache-obj-per-slab>`__
-  `spl_kmem_cache_obj_per_slab_min <#spl-kmem-cache-obj-per-slab-min>`__
-  `spl_kmem_cache_reclaim <#spl-kmem-cache-reclaim>`__
-  `spl_kmem_cache_slab_limit <#spl-kmem-cache-slab-limit>`__

metadata
~~~~~~~~

-  `zfs_mdcomp_disable <#zfs-mdcomp-disable>`__

metaslab
~~~~~~~~

-  `metaslab_aliquot <#metaslab-aliquot>`__
-  `metaslab_bias_enabled <#metaslab-bias-enabled>`__
-  `metaslab_debug_load <#metaslab-debug-load>`__
-  `metaslab_debug_unload <#metaslab-debug-unload>`__
-  `metaslab_fragmentation_factor_enabled <#metaslab-fragmentation-factor-enabled>`__
-  `metaslab_lba_weighting_enabled <#metaslab-lba-weighting-enabled>`__
-  `metaslab_preload_enabled <#metaslab-preload-enabled>`__
-  `zfs_metaslab_segment_weight_enabled <#zfs-metaslab-segment-weight-enabled>`__
-  `zfs_metaslab_switch_threshold <#zfs-metaslab-switch-threshold>`__
-  `metaslabs_per_vdev <#metaslabs-per-vdev>`__
-  `zfs_vdev_min_ms_count <#zfs-vdev-min-ms-count>`__
-  `zfs_vdev_ms_count_limit <#zfs-vdev-ms-count-limit>`__

mirror
~~~~~~

-  `zfs_vdev_mirror_non_rotating_inc <#zfs-vdev-mirror-non-rotating-inc>`__
-  `zfs_vdev_mirror_non_rotating_seek_inc <#zfs-vdev-mirror-non-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_inc <#zfs-vdev-mirror-rotating-inc>`__
-  `zfs_vdev_mirror_rotating_seek_inc <#zfs-vdev-mirror-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_seek_offset <#zfs-vdev-mirror-rotating-seek-offset>`__

MMP
~~~

-  `zfs_multihost_fail_intervals <#zfs-multihost-fail-intervals>`__
-  `zfs_multihost_history <#zfs-multihost-history>`__
-  `zfs_multihost_import_intervals <#zfs-multihost-import-intervals>`__
-  `zfs_multihost_interval <#zfs-multihost-interval>`__
-  `spl_hostid <#spl-hostid>`__
-  `spl_hostid_path <#spl-hostid-path>`__

panic
~~~~~

-  `spl_panic_halt <#spl-panic-halt>`__

prefetch
~~~~~~~~

-  `zfs_arc_min_prefetch_ms <#zfs-arc-min-prefetch-ms>`__
-  `zfs_arc_min_prescient_prefetch_ms <#zfs-arc-min-prescient-prefetch-ms>`__
-  `zfs_dedup_prefetch <#zfs-dedup-prefetch>`__
-  `l2arc_noprefetch <#l2arc-noprefetch>`__
-  `zfs_no_scrub_prefetch <#zfs-no-scrub-prefetch>`__
-  `zfs_pd_bytes_max <#zfs-pd-bytes-max>`__
-  `zfs_prefetch_disable <#zfs-prefetch-disable>`__
-  `zfetch_array_rd_sz <#zfetch-array-rd-sz>`__
-  `zfetch_max_distance <#zfetch-max-distance>`__
-  `zfetch_max_streams <#zfetch-max-streams>`__
-  `zfetch_min_sec_reap <#zfetch-min-sec-reap>`__
-  `zvol_prefetch_bytes <#zvol-prefetch-bytes>`__

QAT
~~~

-  `zfs_qat_checksum_disable <#zfs-qat-checksum-disable>`__
-  `zfs_qat_compress_disable <#zfs-qat-compress-disable>`__
-  `zfs_qat_disable <#zfs-qat-disable>`__
-  `zfs_qat_encrypt_disable <#zfs-qat-encrypt-disable>`__

raidz
~~~~~

-  `zfs_vdev_raidz_impl <#zfs-vdev-raidz-impl>`__

receive
~~~~~~~

-  `zfs_disable_ivset_guid_check <#zfs-disable-ivset-guid-check>`__
-  `zfs_recv_queue_length <#zfs-recv-queue-length>`__

remove
~~~~~~

-  `zfs_obsolete_min_time_ms <#zfs-obsolete-min-time-ms>`__
-  `zfs_remove_max_segment <#zfs-remove-max-segment>`__

resilver
~~~~~~~~

-  `zfs_resilver_delay <#zfs-resilver-delay>`__
-  `zfs_resilver_disable_defer <#zfs-resilver-disable-defer>`__
-  `zfs_resilver_min_time_ms <#zfs-resilver-min-time-ms>`__
-  `zfs_scan_checkpoint_intval <#zfs-scan-checkpoint-intval>`__
-  `zfs_scan_fill_weight <#zfs-scan-fill-weight>`__
-  `zfs_scan_idle <#zfs-scan-idle>`__
-  `zfs_scan_ignore_errors <#zfs-scan-ignore-errors>`__
-  `zfs_scan_issue_strategy <#zfs-scan-issue-strategy>`__
-  `zfs_scan_legacy <#zfs-scan-legacy>`__
-  `zfs_scan_max_ext_gap <#zfs-scan-max-ext-gap>`__
-  `zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__
-  `zfs_scan_mem_lim_soft_fact <#zfs-scan-mem-lim-soft-fact>`__
-  `zfs_scan_strict_mem_lim <#zfs-scan-strict-mem-lim>`__
-  `zfs_scan_suspend_progress <#zfs-scan-suspend-progress>`__
-  `zfs_scan_vdev_limit <#zfs-scan-vdev-limit>`__
-  `zfs_top_maxinflight <#zfs-top-maxinflight>`__
-  `zfs_vdev_scrub_max_active <#zfs-vdev-scrub-max-active>`__
-  `zfs_vdev_scrub_min_active <#zfs-vdev-scrub-min-active>`__

scrub
~~~~~

-  `zfs_no_scrub_io <#zfs-no-scrub-io>`__
-  `zfs_no_scrub_prefetch <#zfs-no-scrub-prefetch>`__
-  `zfs_scan_checkpoint_intval <#zfs-scan-checkpoint-intval>`__
-  `zfs_scan_fill_weight <#zfs-scan-fill-weight>`__
-  `zfs_scan_idle <#zfs-scan-idle>`__
-  `zfs_scan_issue_strategy <#zfs-scan-issue-strategy>`__
-  `zfs_scan_legacy <#zfs-scan-legacy>`__
-  `zfs_scan_max_ext_gap <#zfs-scan-max-ext-gap>`__
-  `zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__
-  `zfs_scan_mem_lim_soft_fact <#zfs-scan-mem-lim-soft-fact>`__
-  `zfs_scan_min_time_ms <#zfs-scan-min-time-ms>`__
-  `zfs_scan_strict_mem_lim <#zfs-scan-strict-mem-lim>`__
-  `zfs_scan_suspend_progress <#zfs-scan-suspend-progress>`__
-  `zfs_scan_vdev_limit <#zfs-scan-vdev-limit>`__
-  `zfs_scrub_delay <#zfs-scrub-delay>`__
-  `zfs_scrub_min_time_ms <#zfs-scrub-min-time-ms>`__
-  `zfs_top_maxinflight <#zfs-top-maxinflight>`__
-  `zfs_vdev_scrub_max_active <#zfs-vdev-scrub-max-active>`__
-  `zfs_vdev_scrub_min_active <#zfs-vdev-scrub-min-active>`__

send
~~~~

-  `ignore_hole_birth <#ignore-hole-birth>`__
-  `zfs_override_estimate_recordsize <#zfs-override-estimate-recordsize>`__
-  `zfs_pd_bytes_max <#zfs-pd-bytes-max>`__
-  `zfs_send_corrupt_data <#zfs-send-corrupt-data>`__
-  `zfs_send_queue_length <#zfs-send-queue-length>`__
-  `zfs_send_unmodified_spill_blocks <#zfs-send-unmodified-spill-blocks>`__

snapshot
~~~~~~~~

-  `zfs_admin_snapshot <#zfs-admin-snapshot>`__
-  `zfs_expire_snapshot <#zfs-expire-snapshot>`__

SPA
~~~

-  `spa_asize_inflation <#spa-asize-inflation>`__
-  `spa_load_print_vdev_tree <#spa-load-print-vdev-tree>`__
-  `spa_load_verify_data <#spa-load-verify-data>`__
-  `spa_load_verify_shift <#spa-load-verify-shift>`__
-  `spa_slop_shift <#spa-slop-shift>`__
-  `zfs_sync_pass_deferred_free <#zfs-sync-pass-deferred-free>`__
-  `zfs_sync_pass_dont_compress <#zfs-sync-pass-dont-compress>`__
-  `zfs_sync_pass_rewrite <#zfs-sync-pass-rewrite>`__
-  `zfs_sync_taskq_batch_pct <#zfs-sync-taskq-batch-pct>`__
-  `zfs_txg_timeout <#zfs-txg-timeout>`__

special_vdev
~~~~~~~~~~~~

-  `zfs_ddt_data_is_special <#zfs-ddt-data-is-special>`__
-  `zfs_special_class_metadata_reserve_pct <#zfs-special-class-metadata-reserve-pct>`__
-  `zfs_user_indirect_is_special <#zfs-user-indirect-is-special>`__

SSD
~~~

-  `metaslab_lba_weighting_enabled <#metaslab-lba-weighting-enabled>`__
-  `zfs_vdev_mirror_non_rotating_inc <#zfs-vdev-mirror-non-rotating-inc>`__
-  `zfs_vdev_mirror_non_rotating_seek_inc <#zfs-vdev-mirror-non-rotating-seek-inc>`__

taskq
~~~~~

-  `spl_max_show_tasks <#spl-max-show-tasks>`__
-  `spl_taskq_kick <#spl-taskq-kick>`__
-  `spl_taskq_thread_bind <#spl-taskq-thread-bind>`__
-  `spl_taskq_thread_dynamic <#spl-taskq-thread-dynamic>`__
-  `spl_taskq_thread_priority <#spl-taskq-thread-priority>`__
-  `spl_taskq_thread_sequential <#spl-taskq-thread-sequential>`__
-  `zfs_zil_clean_taskq_nthr_pct <#zfs-zil-clean-taskq-nthr-pct>`__
-  `zio_taskq_batch_pct <#zio-taskq-batch-pct>`__

trim
~~~~

-  `zfs_trim_extent_bytes_max <#zfs-trim-extent-bytes-max>`__
-  `zfs_trim_extent_bytes_min <#zfs-trim-extent-bytes-min>`__
-  `zfs_trim_metaslab_skip <#zfs-trim-metaslab-skip>`__
-  `zfs_trim_queue_limit <#zfs-trim-queue-limit>`__
-  `zfs_trim_txg_batch <#zfs-trim-txg-batch>`__
-  `zfs_vdev_aggregate_trim <#zfs-vdev-aggregate-trim>`__

vdev
~~~~

-  `zfs_checksum_events_per_second <#zfs-checksum-events-per-second>`__
-  `metaslab_aliquot <#metaslab-aliquot>`__
-  `metaslab_bias_enabled <#metaslab-bias-enabled>`__
-  `zfs_metaslab_fragmentation_threshold <#zfs-metaslab-fragmentation-threshold>`__
-  `metaslabs_per_vdev <#metaslabs-per-vdev>`__
-  `zfs_mg_fragmentation_threshold <#zfs-mg-fragmentation-threshold>`__
-  `zfs_mg_noalloc_threshold <#zfs-mg-noalloc-threshold>`__
-  `zfs_multihost_interval <#zfs-multihost-interval>`__
-  `zfs_scan_vdev_limit <#zfs-scan-vdev-limit>`__
-  `zfs_slow_io_events_per_second <#zfs-slow-io-events-per-second>`__
-  `zfs_vdev_aggregate_trim <#zfs-vdev-aggregate-trim>`__
-  `zfs_vdev_aggregation_limit <#zfs-vdev-aggregation-limit>`__
-  `zfs_vdev_aggregation_limit_non_rotating <#zfs-vdev-aggregation-limit-non-rotating>`__
-  `zfs_vdev_async_read_max_active <#zfs-vdev-async-read-max-active>`__
-  `zfs_vdev_async_read_min_active <#zfs-vdev-async-read-min-active>`__
-  `zfs_vdev_async_write_active_max_dirty_percent <#zfs-vdev-async-write-active-max-dirty-percent>`__
-  `zfs_vdev_async_write_active_min_dirty_percent <#zfs-vdev-async-write-active-min-dirty-percent>`__
-  `zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__
-  `zfs_vdev_async_write_min_active <#zfs-vdev-async-write-min-active>`__
-  `zfs_vdev_cache_bshift <#zfs-vdev-cache-bshift>`__
-  `zfs_vdev_cache_max <#zfs-vdev-cache-max>`__
-  `zfs_vdev_cache_size <#zfs-vdev-cache-size>`__
-  `zfs_vdev_initializing_max_active <#zfs-vdev-initializing-max-active>`__
-  `zfs_vdev_initializing_min_active <#zfs-vdev-initializing-min-active>`__
-  `zfs_vdev_max_active <#zfs-vdev-max-active>`__
-  `zfs_vdev_min_ms_count <#zfs-vdev-min-ms-count>`__
-  `zfs_vdev_mirror_non_rotating_inc <#zfs-vdev-mirror-non-rotating-inc>`__
-  `zfs_vdev_mirror_non_rotating_seek_inc <#zfs-vdev-mirror-non-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_inc <#zfs-vdev-mirror-rotating-inc>`__
-  `zfs_vdev_mirror_rotating_seek_inc <#zfs-vdev-mirror-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_seek_offset <#zfs-vdev-mirror-rotating-seek-offset>`__
-  `zfs_vdev_ms_count_limit <#zfs-vdev-ms-count-limit>`__
-  `zfs_vdev_queue_depth_pct <#zfs-vdev-queue-depth-pct>`__
-  `zfs_vdev_raidz_impl <#zfs-vdev-raidz-impl>`__
-  `zfs_vdev_read_gap_limit <#zfs-vdev-read-gap-limit>`__
-  `zfs_vdev_removal_max_active <#zfs-vdev-removal-max-active>`__
-  `zfs_vdev_removal_min_active <#zfs-vdev-removal-min-active>`__
-  `zfs_vdev_scheduler <#zfs-vdev-scheduler>`__
-  `zfs_vdev_scrub_max_active <#zfs-vdev-scrub-max-active>`__
-  `zfs_vdev_scrub_min_active <#zfs-vdev-scrub-min-active>`__
-  `zfs_vdev_sync_read_max_active <#zfs-vdev-sync-read-max-active>`__
-  `zfs_vdev_sync_read_min_active <#zfs-vdev-sync-read-min-active>`__
-  `zfs_vdev_sync_write_max_active <#zfs-vdev-sync-write-max-active>`__
-  `zfs_vdev_sync_write_min_active <#zfs-vdev-sync-write-min-active>`__
-  `zfs_vdev_trim_max_active <#zfs-vdev-trim-max-active>`__
-  `zfs_vdev_trim_min_active <#zfs-vdev-trim-min-active>`__
-  `vdev_validate_skip <#vdev-validate-skip>`__
-  `zfs_vdev_write_gap_limit <#zfs-vdev-write-gap-limit>`__
-  `zio_dva_throttle_enabled <#zio-dva-throttle-enabled>`__
-  `zio_slow_io_ms <#zio-slow-io-ms>`__

vdev_cache
~~~~~~~~~~

-  `zfs_vdev_cache_bshift <#zfs-vdev-cache-bshift>`__
-  `zfs_vdev_cache_max <#zfs-vdev-cache-max>`__
-  `zfs_vdev_cache_size <#zfs-vdev-cache-size>`__

vdev_initialize
~~~~~~~~~~~~~~~

-  `zfs_initialize_value <#zfs-initialize-value>`__

vdev_removal
~~~~~~~~~~~~

-  `zfs_condense_indirect_commit_entry_delay_ms <#zfs-condense-indirect-commit-entry-delay-ms>`__
-  `zfs_condense_indirect_vdevs_enable <#zfs-condense-indirect-vdevs-enable>`__
-  `zfs_condense_max_obsolete_bytes <#zfs-condense-max-obsolete-bytes>`__
-  `zfs_condense_min_mapping_bytes <#zfs-condense-min-mapping-bytes>`__
-  `zfs_reconstruct_indirect_combinations_max <#zfs-reconstruct-indirect-combinations-max>`__
-  `zfs_removal_ignore_errors <#zfs-removal-ignore-errors>`__
-  `zfs_removal_suspend_progress <#zfs-removal-suspend-progress>`__
-  `vdev_removal_max_span <#vdev-removal-max-span>`__

volume
~~~~~~

-  `zfs_max_recordsize <#zfs-max-recordsize>`__
-  `zvol_inhibit_dev <#zvol-inhibit-dev>`__
-  `zvol_major <#zvol-major>`__
-  `zvol_max_discard_blocks <#zvol-max-discard-blocks>`__
-  `zvol_prefetch_bytes <#zvol-prefetch-bytes>`__
-  `zvol_request_sync <#zvol-request-sync>`__
-  `zvol_threads <#zvol-threads>`__
-  `zvol_volmode <#zvol-volmode>`__

write_throttle
~~~~~~~~~~~~~~

-  `zfs_delay_min_dirty_percent <#zfs-delay-min-dirty-percent>`__
-  `zfs_delay_scale <#zfs-delay-scale>`__
-  `zfs_dirty_data_max <#zfs-dirty-data-max>`__
-  `zfs_dirty_data_max_max <#zfs-dirty-data-max-max>`__
-  `zfs_dirty_data_max_max_percent <#zfs-dirty-data-max-max-percent>`__
-  `zfs_dirty_data_max_percent <#zfs-dirty-data-max-percent>`__
-  `zfs_dirty_data_sync <#zfs-dirty-data-sync>`__
-  `zfs_dirty_data_sync_percent <#zfs-dirty-data-sync-percent>`__

zed
~~~

-  `zfs_checksums_per_second <#zfs-checksums-per-second>`__
-  `zfs_delays_per_second <#zfs-delays-per-second>`__
-  `zio_slow_io_ms <#zio-slow-io-ms>`__

ZIL
~~~

-  `zfs_commit_timeout_pct <#zfs-commit-timeout-pct>`__
-  `zfs_immediate_write_sz <#zfs-immediate-write-sz>`__
-  `zfs_zil_clean_taskq_maxalloc <#zfs-zil-clean-taskq-maxalloc>`__
-  `zfs_zil_clean_taskq_minalloc <#zfs-zil-clean-taskq-minalloc>`__
-  `zfs_zil_clean_taskq_nthr_pct <#zfs-zil-clean-taskq-nthr-pct>`__
-  `zil_nocacheflush <#zil-nocacheflush>`__
-  `zil_replay_disable <#zil-replay-disable>`__
-  `zil_slog_bulk <#zil-slog-bulk>`__

ZIO_scheduler
~~~~~~~~~~~~~

-  `zfs_dirty_data_sync <#zfs-dirty-data-sync>`__
-  `zfs_dirty_data_sync_percent <#zfs-dirty-data-sync-percent>`__
-  `zfs_resilver_delay <#zfs-resilver-delay>`__
-  `zfs_scan_idle <#zfs-scan-idle>`__
-  `zfs_scrub_delay <#zfs-scrub-delay>`__
-  `zfs_top_maxinflight <#zfs-top-maxinflight>`__
-  `zfs_txg_timeout <#zfs-txg-timeout>`__
-  `zfs_vdev_aggregate_trim <#zfs-vdev-aggregate-trim>`__
-  `zfs_vdev_aggregation_limit <#zfs-vdev-aggregation-limit>`__
-  `zfs_vdev_aggregation_limit_non_rotating <#zfs-vdev-aggregation-limit-non-rotating>`__
-  `zfs_vdev_async_read_max_active <#zfs-vdev-async-read-max-active>`__
-  `zfs_vdev_async_read_min_active <#zfs-vdev-async-read-min-active>`__
-  `zfs_vdev_async_write_active_max_dirty_percent <#zfs-vdev-async-write-active-max-dirty-percent>`__
-  `zfs_vdev_async_write_active_min_dirty_percent <#zfs-vdev-async-write-active-min-dirty-percent>`__
-  `zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__
-  `zfs_vdev_async_write_min_active <#zfs-vdev-async-write-min-active>`__
-  `zfs_vdev_initializing_max_active <#zfs-vdev-initializing-max-active>`__
-  `zfs_vdev_initializing_min_active <#zfs-vdev-initializing-min-active>`__
-  `zfs_vdev_max_active <#zfs-vdev-max-active>`__
-  `zfs_vdev_queue_depth_pct <#zfs-vdev-queue-depth-pct>`__
-  `zfs_vdev_read_gap_limit <#zfs-vdev-read-gap-limit>`__
-  `zfs_vdev_removal_max_active <#zfs-vdev-removal-max-active>`__
-  `zfs_vdev_removal_min_active <#zfs-vdev-removal-min-active>`__
-  `zfs_vdev_scheduler <#zfs-vdev-scheduler>`__
-  `zfs_vdev_scrub_max_active <#zfs-vdev-scrub-max-active>`__
-  `zfs_vdev_scrub_min_active <#zfs-vdev-scrub-min-active>`__
-  `zfs_vdev_sync_read_max_active <#zfs-vdev-sync-read-max-active>`__
-  `zfs_vdev_sync_read_min_active <#zfs-vdev-sync-read-min-active>`__
-  `zfs_vdev_sync_write_max_active <#zfs-vdev-sync-write-max-active>`__
-  `zfs_vdev_sync_write_min_active <#zfs-vdev-sync-write-min-active>`__
-  `zfs_vdev_trim_max_active <#zfs-vdev-trim-max-active>`__
-  `zfs_vdev_trim_min_active <#zfs-vdev-trim-min-active>`__
-  `zfs_vdev_write_gap_limit <#zfs-vdev-write-gap-limit>`__
-  `zio_dva_throttle_enabled <#zio-dva-throttle-enabled>`__
-  `zio_requeue_io_start_cut_in_line <#zio-requeue-io-start-cut-in-line>`__
-  `zio_taskq_batch_pct <#zio-taskq-batch-pct>`__

Index
-----

-  `zfs_abd_scatter_enabled <#zfs-abd-scatter-enabled>`__
-  `zfs_abd_scatter_max_order <#zfs-abd-scatter-max-order>`__
-  `zfs_abd_scatter_min_size <#zfs-abd-scatter-min-size>`__
-  `zfs_admin_snapshot <#zfs-admin-snapshot>`__
-  `zfs_arc_average_blocksize <#zfs-arc-average-blocksize>`__
-  `zfs_arc_dnode_limit <#zfs-arc-dnode-limit>`__
-  `zfs_arc_dnode_limit_percent <#zfs-arc-dnode-limit-percent>`__
-  `zfs_arc_dnode_reduce_percent <#zfs-arc-dnode-reduce-percent>`__
-  `zfs_arc_evict_batch_limit <#zfs-arc-evict-batch-limit>`__
-  `zfs_arc_grow_retry <#zfs-arc-grow-retry>`__
-  `zfs_arc_lotsfree_percent <#zfs-arc-lotsfree-percent>`__
-  `zfs_arc_max <#zfs-arc-max>`__
-  `zfs_arc_meta_adjust_restarts <#zfs-arc-meta-adjust-restarts>`__
-  `zfs_arc_meta_limit <#zfs-arc-meta-limit>`__
-  `zfs_arc_meta_limit_percent <#zfs-arc-meta-limit-percent>`__
-  `zfs_arc_meta_min <#zfs-arc-meta-min>`__
-  `zfs_arc_meta_prune <#zfs-arc-meta-prune>`__
-  `zfs_arc_meta_strategy <#zfs-arc-meta-strategy>`__
-  `zfs_arc_min <#zfs-arc-min>`__
-  `zfs_arc_min_prefetch_lifespan <#zfs-arc-min-prefetch-lifespan>`__
-  `zfs_arc_min_prefetch_ms <#zfs-arc-min-prefetch-ms>`__
-  `zfs_arc_min_prescient_prefetch_ms <#zfs-arc-min-prescient-prefetch-ms>`__
-  `zfs_arc_overflow_shift <#zfs-arc-overflow-shift>`__
-  `zfs_arc_p_dampener_disable <#zfs-arc-p-dampener-disable>`__
-  `zfs_arc_p_min_shift <#zfs-arc-p-min-shift>`__
-  `zfs_arc_pc_percent <#zfs-arc-pc-percent>`__
-  `zfs_arc_shrink_shift <#zfs-arc-shrink-shift>`__
-  `zfs_arc_sys_free <#zfs-arc-sys-free>`__
-  `zfs_async_block_max_blocks <#zfs-async-block-max-blocks>`__
-  `zfs_autoimport_disable <#zfs-autoimport-disable>`__
-  `zfs_checksum_events_per_second <#zfs-checksum-events-per-second>`__
-  `zfs_checksums_per_second <#zfs-checksums-per-second>`__
-  `zfs_commit_timeout_pct <#zfs-commit-timeout-pct>`__
-  `zfs_compressed_arc_enabled <#zfs-compressed-arc-enabled>`__
-  `zfs_condense_indirect_commit_entry_delay_ms <#zfs-condense-indirect-commit-entry-delay-ms>`__
-  `zfs_condense_indirect_vdevs_enable <#zfs-condense-indirect-vdevs-enable>`__
-  `zfs_condense_max_obsolete_bytes <#zfs-condense-max-obsolete-bytes>`__
-  `zfs_condense_min_mapping_bytes <#zfs-condense-min-mapping-bytes>`__
-  `zfs_dbgmsg_enable <#zfs-dbgmsg-enable>`__
-  `zfs_dbgmsg_maxsize <#zfs-dbgmsg-maxsize>`__
-  `dbuf_cache_hiwater_pct <#dbuf-cache-hiwater-pct>`__
-  `dbuf_cache_lowater_pct <#dbuf-cache-lowater-pct>`__
-  `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__
-  `dbuf_cache_max_shift <#dbuf-cache-max-shift>`__
-  `dbuf_cache_shift <#dbuf-cache-shift>`__
-  `dbuf_metadata_cache_max_bytes <#dbuf-metadata-cache-max-bytes>`__
-  `dbuf_metadata_cache_shift <#dbuf-metadata-cache-shift>`__
-  `zfs_dbuf_state_index <#zfs-dbuf-state-index>`__
-  `zfs_ddt_data_is_special <#zfs-ddt-data-is-special>`__
-  `zfs_deadman_checktime_ms <#zfs-deadman-checktime-ms>`__
-  `zfs_deadman_enabled <#zfs-deadman-enabled>`__
-  `zfs_deadman_failmode <#zfs-deadman-failmode>`__
-  `zfs_deadman_synctime_ms <#zfs-deadman-synctime-ms>`__
-  `zfs_deadman_ziotime_ms <#zfs-deadman-ziotime-ms>`__
-  `zfs_dedup_prefetch <#zfs-dedup-prefetch>`__
-  `zfs_delay_min_dirty_percent <#zfs-delay-min-dirty-percent>`__
-  `zfs_delay_scale <#zfs-delay-scale>`__
-  `zfs_delays_per_second <#zfs-delays-per-second>`__
-  `zfs_delete_blocks <#zfs-delete-blocks>`__
-  `zfs_dirty_data_max <#zfs-dirty-data-max>`__
-  `zfs_dirty_data_max_max <#zfs-dirty-data-max-max>`__
-  `zfs_dirty_data_max_max_percent <#zfs-dirty-data-max-max-percent>`__
-  `zfs_dirty_data_max_percent <#zfs-dirty-data-max-percent>`__
-  `zfs_dirty_data_sync <#zfs-dirty-data-sync>`__
-  `zfs_dirty_data_sync_percent <#zfs-dirty-data-sync-percent>`__
-  `zfs_disable_dup_eviction <#zfs-disable-dup-eviction>`__
-  `zfs_disable_ivset_guid_check <#zfs-disable-ivset-guid-check>`__
-  `dmu_object_alloc_chunk_shift <#dmu-object-alloc-chunk-shift>`__
-  `zfs_dmu_offset_next_sync <#zfs-dmu-offset-next-sync>`__
-  `zfs_expire_snapshot <#zfs-expire-snapshot>`__
-  `zfs_flags <#zfs-flags>`__
-  `zfs_fletcher_4_impl <#zfs-fletcher-4-impl>`__
-  `zfs_free_bpobj_enabled <#zfs-free-bpobj-enabled>`__
-  `zfs_free_leak_on_eio <#zfs-free-leak-on-eio>`__
-  `zfs_free_max_blocks <#zfs-free-max-blocks>`__
-  `zfs_free_min_time_ms <#zfs-free-min-time-ms>`__
-  `icp_aes_impl <#icp-aes-impl>`__
-  `icp_gcm_impl <#icp-gcm-impl>`__
-  `ignore_hole_birth <#ignore-hole-birth>`__
-  `zfs_immediate_write_sz <#zfs-immediate-write-sz>`__
-  `zfs_initialize_value <#zfs-initialize-value>`__
-  `zfs_key_max_salt_uses <#zfs-key-max-salt-uses>`__
-  `l2arc_feed_again <#l2arc-feed-again>`__
-  `l2arc_feed_min_ms <#l2arc-feed-min-ms>`__
-  `l2arc_feed_secs <#l2arc-feed-secs>`__
-  `l2arc_headroom <#l2arc-headroom>`__
-  `l2arc_headroom_boost <#l2arc-headroom-boost>`__
-  `l2arc_meta_percent <#l2arc-meta-percent>`__
-  `l2arc_mfuonly <#l2arc-mfuonly>`__
-  `l2arc_nocompress <#l2arc-nocompress>`__
-  `l2arc_noprefetch <#l2arc-noprefetch>`__
-  `l2arc_norw <#l2arc-norw>`__
-  `l2arc_rebuild_blocks_min_l2size <#l2arc-rebuild-blocks-min-l2size>`__
-  `l2arc_rebuild_enabled <#l2arc-rebuild-enabled>`__
-  `l2arc_trim_ahead <#l2arc-trim-ahead>`__
-  `l2arc_write_boost <#l2arc-write-boost>`__
-  `l2arc_write_max <#l2arc-write-max>`__
-  `zfs_lua_max_instrlimit <#zfs-lua-max-instrlimit>`__
-  `zfs_lua_max_memlimit <#zfs-lua-max-memlimit>`__
-  `zfs_max_dataset_nesting <#zfs-max-dataset-nesting>`__
-  `zfs_max_missing_tvds <#zfs-max-missing-tvds>`__
-  `zfs_max_recordsize <#zfs-max-recordsize>`__
-  `zfs_mdcomp_disable <#zfs-mdcomp-disable>`__
-  `metaslab_aliquot <#metaslab-aliquot>`__
-  `metaslab_bias_enabled <#metaslab-bias-enabled>`__
-  `metaslab_debug_load <#metaslab-debug-load>`__
-  `metaslab_debug_unload <#metaslab-debug-unload>`__
-  `metaslab_force_ganging <#metaslab-force-ganging>`__
-  `metaslab_fragmentation_factor_enabled <#metaslab-fragmentation-factor-enabled>`__
-  `zfs_metaslab_fragmentation_threshold <#zfs-metaslab-fragmentation-threshold>`__
-  `metaslab_lba_weighting_enabled <#metaslab-lba-weighting-enabled>`__
-  `metaslab_preload_enabled <#metaslab-preload-enabled>`__
-  `zfs_metaslab_segment_weight_enabled <#zfs-metaslab-segment-weight-enabled>`__
-  `zfs_metaslab_switch_threshold <#zfs-metaslab-switch-threshold>`__
-  `metaslabs_per_vdev <#metaslabs-per-vdev>`__
-  `zfs_mg_fragmentation_threshold <#zfs-mg-fragmentation-threshold>`__
-  `zfs_mg_noalloc_threshold <#zfs-mg-noalloc-threshold>`__
-  `zfs_multihost_fail_intervals <#zfs-multihost-fail-intervals>`__
-  `zfs_multihost_history <#zfs-multihost-history>`__
-  `zfs_multihost_import_intervals <#zfs-multihost-import-intervals>`__
-  `zfs_multihost_interval <#zfs-multihost-interval>`__
-  `zfs_multilist_num_sublists <#zfs-multilist-num-sublists>`__
-  `zfs_no_scrub_io <#zfs-no-scrub-io>`__
-  `zfs_no_scrub_prefetch <#zfs-no-scrub-prefetch>`__
-  `zfs_nocacheflush <#zfs-nocacheflush>`__
-  `zfs_nopwrite_enabled <#zfs-nopwrite-enabled>`__
-  `zfs_object_mutex_size <#zfs-object-mutex-size>`__
-  `zfs_obsolete_min_time_ms <#zfs-obsolete-min-time-ms>`__
-  `zfs_override_estimate_recordsize <#zfs-override-estimate-recordsize>`__
-  `zfs_pd_bytes_max <#zfs-pd-bytes-max>`__
-  `zfs_per_txg_dirty_frees_percent <#zfs-per-txg-dirty-frees-percent>`__
-  `zfs_prefetch_disable <#zfs-prefetch-disable>`__
-  `zfs_qat_checksum_disable <#zfs-qat-checksum-disable>`__
-  `zfs_qat_compress_disable <#zfs-qat-compress-disable>`__
-  `zfs_qat_disable <#zfs-qat-disable>`__
-  `zfs_qat_encrypt_disable <#zfs-qat-encrypt-disable>`__
-  `zfs_read_chunk_size <#zfs-read-chunk-size>`__
-  `zfs_read_history <#zfs-read-history>`__
-  `zfs_read_history_hits <#zfs-read-history-hits>`__
-  `zfs_reconstruct_indirect_combinations_max <#zfs-reconstruct-indirect-combinations-max>`__
-  `zfs_recover <#zfs-recover>`__
-  `zfs_recv_queue_length <#zfs-recv-queue-length>`__
-  `zfs_removal_ignore_errors <#zfs-removal-ignore-errors>`__
-  `zfs_removal_suspend_progress <#zfs-removal-suspend-progress>`__
-  `zfs_remove_max_segment <#zfs-remove-max-segment>`__
-  `zfs_resilver_delay <#zfs-resilver-delay>`__
-  `zfs_resilver_disable_defer <#zfs-resilver-disable-defer>`__
-  `zfs_resilver_min_time_ms <#zfs-resilver-min-time-ms>`__
-  `zfs_scan_checkpoint_intval <#zfs-scan-checkpoint-intval>`__
-  `zfs_scan_fill_weight <#zfs-scan-fill-weight>`__
-  `zfs_scan_idle <#zfs-scan-idle>`__
-  `zfs_scan_ignore_errors <#zfs-scan-ignore-errors>`__
-  `zfs_scan_issue_strategy <#zfs-scan-issue-strategy>`__
-  `zfs_scan_legacy <#zfs-scan-legacy>`__
-  `zfs_scan_max_ext_gap <#zfs-scan-max-ext-gap>`__
-  `zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__
-  `zfs_scan_mem_lim_soft_fact <#zfs-scan-mem-lim-soft-fact>`__
-  `zfs_scan_min_time_ms <#zfs-scan-min-time-ms>`__
-  `zfs_scan_strict_mem_lim <#zfs-scan-strict-mem-lim>`__
-  `zfs_scan_suspend_progress <#zfs-scan-suspend-progress>`__
-  `zfs_scan_vdev_limit <#zfs-scan-vdev-limit>`__
-  `zfs_scrub_delay <#zfs-scrub-delay>`__
-  `zfs_scrub_min_time_ms <#zfs-scrub-min-time-ms>`__
-  `zfs_send_corrupt_data <#zfs-send-corrupt-data>`__
-  `send_holes_without_birth_time <#send-holes-without-birth-time>`__
-  `zfs_send_queue_length <#zfs-send-queue-length>`__
-  `zfs_send_unmodified_spill_blocks <#zfs-send-unmodified-spill-blocks>`__
-  `zfs_slow_io_events_per_second <#zfs-slow-io-events-per-second>`__
-  `spa_asize_inflation <#spa-asize-inflation>`__
-  `spa_config_path <#spa-config-path>`__
-  `zfs_spa_discard_memory_limit <#zfs-spa-discard-memory-limit>`__
-  `spa_load_print_vdev_tree <#spa-load-print-vdev-tree>`__
-  `spa_load_verify_data <#spa-load-verify-data>`__
-  `spa_load_verify_maxinflight <#spa-load-verify-maxinflight>`__
-  `spa_load_verify_metadata <#spa-load-verify-metadata>`__
-  `spa_load_verify_shift <#spa-load-verify-shift>`__
-  `spa_slop_shift <#spa-slop-shift>`__
-  `zfs_special_class_metadata_reserve_pct <#zfs-special-class-metadata-reserve-pct>`__
-  `spl_hostid <#spl-hostid>`__
-  `spl_hostid_path <#spl-hostid-path>`__
-  `spl_kmem_alloc_max <#spl-kmem-alloc-max>`__
-  `spl_kmem_alloc_warn <#spl-kmem-alloc-warn>`__
-  `spl_kmem_cache_expire <#spl-kmem-cache-expire>`__
-  `spl_kmem_cache_kmem_limit <#spl-kmem-cache-kmem-limit>`__
-  `spl_kmem_cache_kmem_threads <#spl-kmem-cache-kmem-threads>`__
-  `spl_kmem_cache_magazine_size <#spl-kmem-cache-magazine-size>`__
-  `spl_kmem_cache_max_size <#spl-kmem-cache-max-size>`__
-  `spl_kmem_cache_obj_per_slab <#spl-kmem-cache-obj-per-slab>`__
-  `spl_kmem_cache_obj_per_slab_min <#spl-kmem-cache-obj-per-slab-min>`__
-  `spl_kmem_cache_reclaim <#spl-kmem-cache-reclaim>`__
-  `spl_kmem_cache_slab_limit <#spl-kmem-cache-slab-limit>`__
-  `spl_max_show_tasks <#spl-max-show-tasks>`__
-  `spl_panic_halt <#spl-panic-halt>`__
-  `spl_taskq_kick <#spl-taskq-kick>`__
-  `spl_taskq_thread_bind <#spl-taskq-thread-bind>`__
-  `spl_taskq_thread_dynamic <#spl-taskq-thread-dynamic>`__
-  `spl_taskq_thread_priority <#spl-taskq-thread-priority>`__
-  `spl_taskq_thread_sequential <#spl-taskq-thread-sequential>`__
-  `zfs_sync_pass_deferred_free <#zfs-sync-pass-deferred-free>`__
-  `zfs_sync_pass_dont_compress <#zfs-sync-pass-dont-compress>`__
-  `zfs_sync_pass_rewrite <#zfs-sync-pass-rewrite>`__
-  `zfs_sync_taskq_batch_pct <#zfs-sync-taskq-batch-pct>`__
-  `zfs_top_maxinflight <#zfs-top-maxinflight>`__
-  `zfs_trim_extent_bytes_max <#zfs-trim-extent-bytes-max>`__
-  `zfs_trim_extent_bytes_min <#zfs-trim-extent-bytes-min>`__
-  `zfs_trim_metaslab_skip <#zfs-trim-metaslab-skip>`__
-  `zfs_trim_queue_limit <#zfs-trim-queue-limit>`__
-  `zfs_trim_txg_batch <#zfs-trim-txg-batch>`__
-  `zfs_txg_history <#zfs-txg-history>`__
-  `zfs_txg_timeout <#zfs-txg-timeout>`__
-  `zfs_unlink_suspend_progress <#zfs-unlink-suspend-progress>`__
-  `zfs_user_indirect_is_special <#zfs-user-indirect-is-special>`__
-  `zfs_vdev_aggregate_trim <#zfs-vdev-aggregate-trim>`__
-  `zfs_vdev_aggregation_limit <#zfs-vdev-aggregation-limit>`__
-  `zfs_vdev_aggregation_limit_non_rotating <#zfs-vdev-aggregation-limit-non-rotating>`__
-  `zfs_vdev_async_read_max_active <#zfs-vdev-async-read-max-active>`__
-  `zfs_vdev_async_read_min_active <#zfs-vdev-async-read-min-active>`__
-  `zfs_vdev_async_write_active_max_dirty_percent <#zfs-vdev-async-write-active-max-dirty-percent>`__
-  `zfs_vdev_async_write_active_min_dirty_percent <#zfs-vdev-async-write-active-min-dirty-percent>`__
-  `zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__
-  `zfs_vdev_async_write_min_active <#zfs-vdev-async-write-min-active>`__
-  `zfs_vdev_cache_bshift <#zfs-vdev-cache-bshift>`__
-  `zfs_vdev_cache_max <#zfs-vdev-cache-max>`__
-  `zfs_vdev_cache_size <#zfs-vdev-cache-size>`__
-  `zfs_vdev_default_ms_count <#zfs-vdev-default-ms-count>`__
-  `zfs_vdev_initializing_max_active <#zfs-vdev-initializing-max-active>`__
-  `zfs_vdev_initializing_min_active <#zfs-vdev-initializing-min-active>`__
-  `zfs_vdev_max_active <#zfs-vdev-max-active>`__
-  `zfs_vdev_min_ms_count <#zfs-vdev-min-ms-count>`__
-  `zfs_vdev_mirror_non_rotating_inc <#zfs-vdev-mirror-non-rotating-inc>`__
-  `zfs_vdev_mirror_non_rotating_seek_inc <#zfs-vdev-mirror-non-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_inc <#zfs-vdev-mirror-rotating-inc>`__
-  `zfs_vdev_mirror_rotating_seek_inc <#zfs-vdev-mirror-rotating-seek-inc>`__
-  `zfs_vdev_mirror_rotating_seek_offset <#zfs-vdev-mirror-rotating-seek-offset>`__
-  `zfs_vdev_ms_count_limit <#zfs-vdev-ms-count-limit>`__
-  `zfs_vdev_queue_depth_pct <#zfs-vdev-queue-depth-pct>`__
-  `zfs_vdev_raidz_impl <#zfs-vdev-raidz-impl>`__
-  `zfs_vdev_read_gap_limit <#zfs-vdev-read-gap-limit>`__
-  `zfs_vdev_removal_max_active <#zfs-vdev-removal-max-active>`__
-  `vdev_removal_max_span <#vdev-removal-max-span>`__
-  `zfs_vdev_removal_min_active <#zfs-vdev-removal-min-active>`__
-  `zfs_vdev_scheduler <#zfs-vdev-scheduler>`__
-  `zfs_vdev_scrub_max_active <#zfs-vdev-scrub-max-active>`__
-  `zfs_vdev_scrub_min_active <#zfs-vdev-scrub-min-active>`__
-  `zfs_vdev_sync_read_max_active <#zfs-vdev-sync-read-max-active>`__
-  `zfs_vdev_sync_read_min_active <#zfs-vdev-sync-read-min-active>`__
-  `zfs_vdev_sync_write_max_active <#zfs-vdev-sync-write-max-active>`__
-  `zfs_vdev_sync_write_min_active <#zfs-vdev-sync-write-min-active>`__
-  `zfs_vdev_trim_max_active <#zfs-vdev-trim-max-active>`__
-  `zfs_vdev_trim_min_active <#zfs-vdev-trim-min-active>`__
-  `vdev_validate_skip <#vdev-validate-skip>`__
-  `zfs_vdev_write_gap_limit <#zfs-vdev-write-gap-limit>`__
-  `zfs_zevent_cols <#zfs-zevent-cols>`__
-  `zfs_zevent_console <#zfs-zevent-console>`__
-  `zfs_zevent_len_max <#zfs-zevent-len-max>`__
-  `zfetch_array_rd_sz <#zfetch-array-rd-sz>`__
-  `zfetch_max_distance <#zfetch-max-distance>`__
-  `zfetch_max_streams <#zfetch-max-streams>`__
-  `zfetch_min_sec_reap <#zfetch-min-sec-reap>`__
-  `zfs_zil_clean_taskq_maxalloc <#zfs-zil-clean-taskq-maxalloc>`__
-  `zfs_zil_clean_taskq_minalloc <#zfs-zil-clean-taskq-minalloc>`__
-  `zfs_zil_clean_taskq_nthr_pct <#zfs-zil-clean-taskq-nthr-pct>`__
-  `zil_nocacheflush <#zil-nocacheflush>`__
-  `zil_replay_disable <#zil-replay-disable>`__
-  `zil_slog_bulk <#zil-slog-bulk>`__
-  `zio_deadman_log_all <#zio-deadman-log-all>`__
-  `zio_decompress_fail_fraction <#zio-decompress-fail-fraction>`__
-  `zio_delay_max <#zio-delay-max>`__
-  `zio_dva_throttle_enabled <#zio-dva-throttle-enabled>`__
-  `zio_requeue_io_start_cut_in_line <#zio-requeue-io-start-cut-in-line>`__
-  `zio_slow_io_ms <#zio-slow-io-ms>`__
-  `zio_taskq_batch_pct <#zio-taskq-batch-pct>`__
-  `zvol_inhibit_dev <#zvol-inhibit-dev>`__
-  `zvol_major <#zvol-major>`__
-  `zvol_max_discard_blocks <#zvol-max-discard-blocks>`__
-  `zvol_prefetch_bytes <#zvol-prefetch-bytes>`__
-  `zvol_request_sync <#zvol-request-sync>`__
-  `zvol_threads <#zvol-threads>`__
-  `zvol_volmode <#zvol-volmode>`__

.. _zfs-module-parameters-1:

Module Parameters
---------------------

ignore_hole_birth
~~~~~~~~~~~~~~~~~

When set, the hole_birth optimization will not be used and all holes
will always be sent by ``zfs send`` In the source code,
ignore_hole_birth is an alias for and SysFS PARAMETER for
`send_holes_without_birth_time <#send-holes-without-birth-time>`__.

+-------------------+-------------------------------------------------+
| ignore_hole_birth | Notes                                           |
+===================+=================================================+
| Tags              | `send <#send>`__                                |
+-------------------+-------------------------------------------------+
| When to change    | Enable if you suspect your datasets are         |
|                   | affected by a bug in hole_birth during          |
|                   | ``zfs send`` operations                         |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=disabled, 1=enabled                           |
+-------------------+-------------------------------------------------+
| Default           | 1 (hole birth optimization is ignored)          |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | TBD                                             |
+-------------------+-------------------------------------------------+

l2arc_feed_again
~~~~~~~~~~~~~~~~

Turbo L2ARC cache warm-up. When the L2ARC is cold the fill interval will
be set to aggressively fill as fast as possible.

+-------------------+-------------------------------------------------+
| l2arc_feed_again  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | If cache devices exist and it is desired to     |
|                   | fill them as fast as possible                   |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=disabled, 1=enabled                           |
+-------------------+-------------------------------------------------+
| Default           | 1                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | TBD                                             |
+-------------------+-------------------------------------------------+

l2arc_feed_min_ms
~~~~~~~~~~~~~~~~~

Minimum time period for aggressively feeding the L2ARC. The L2ARC feed
thread wakes up once per second (see
`l2arc_feed_secs <#l2arc-feed-secs>`__) to look for data to feed into
the L2ARC. ``l2arc_feed_min_ms`` only affects the turbo L2ARC cache
warm-up and allows the aggressiveness to be adjusted.

+-------------------+-------------------------------------------------+
| l2arc_feed_min_ms | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | If cache devices exist and                      |
|                   | `l2arc_feed_again <#l2arc-feed-again>`__ and    |
|                   | the feed is too aggressive, then this tunable   |
|                   | can be adjusted to reduce the impact of the     |
|                   | fill                                            |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | milliseconds                                    |
+-------------------+-------------------------------------------------+
| Range             | 0 to (1000 \* l2arc_feed_secs)                  |
+-------------------+-------------------------------------------------+
| Default           | 200                                             |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | 0.6 and later                                   |
+-------------------+-------------------------------------------------+

l2arc_feed_secs
~~~~~~~~~~~~~~~

Seconds between waking the L2ARC feed thread. One feed thread works for
all cache devices in turn.

If the pool that owns a cache device is imported readonly, then the feed
thread is delayed 5 \* `l2arc_feed_secs <#l2arc-feed-secs>`__ before
moving onto the next cache device. If multiple pools are imported with
cache devices and one pool with cache is imported readonly, the L2ARC
feed rate to all caches can be slowed.

================= ==================================
l2arc_feed_secs   Notes
================= ==================================
Tags              `ARC <#arc>`__, `L2ARC <#l2arc>`__
When to change    Do not change
Data Type         uint64
Units             seconds
Range             1 to UINT64_MAX
Default           1
Change            Dynamic
Versions Affected 0.6 and later
================= ==================================

l2arc_headroom
~~~~~~~~~~~~~~

How far through the ARC lists to search for L2ARC cacheable content,
expressed as a multiplier of `l2arc_write_max <#l2arc-write-max>`__

+-------------------+-------------------------------------------------+
| l2arc_headroom    | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | If the rate of change in the ARC is faster than |
|                   | the overall L2ARC feed rate, then increasing    |
|                   | l2arc_headroom can increase L2ARC efficiency.   |
|                   | Setting the value too large can cause the L2ARC |
|                   | feed thread to consume more CPU time looking    |
|                   | for data to feed.                               |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | unit                                            |
+-------------------+-------------------------------------------------+
| Range             | 0 to UINT64_MAX                                 |
+-------------------+-------------------------------------------------+
| Default           | 2                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | 0.6 and later                                   |
+-------------------+-------------------------------------------------+

l2arc_headroom_boost
~~~~~~~~~~~~~~~~~~~~

Percentage scale for `l2arc_headroom <#l2arc-headroom>`__ when L2ARC
contents are being successfully compressed before writing.

+----------------------+----------------------------------------------+
| l2arc_headroom_boost | Notes                                        |
+======================+==============================================+
| Tags                 | `ARC <#arc>`__, `L2ARC <#l2arc>`__           |
+----------------------+----------------------------------------------+
| When to change       | If average compression efficiency is greater |
|                      | than 2:1, then increasing                    |
|                      | `l2a                                         |
|                      | rc_headroom_boost <#l2arc-headroom-boost>`__ |
|                      | can increase the L2ARC feed rate             |
+----------------------+----------------------------------------------+
| Data Type            | uint64                                       |
+----------------------+----------------------------------------------+
| Units                | percent                                      |
+----------------------+----------------------------------------------+
| Range                | 100 to UINT64_MAX, when set to 100, the      |
|                      | L2ARC headroom boost feature is effectively  |
|                      | disabled                                     |
+----------------------+----------------------------------------------+
| Default              | 200                                          |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | all                                          |
+----------------------+----------------------------------------------+

l2arc_nocompress
~~~~~~~~~~~~~~~~

Disable writing compressed data to cache devices. Disabling allows the
legacy behavior of writing decompressed data to cache devices.

+-------------------+-------------------------------------------------+
| l2arc_nocompress  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | When testing compressed L2ARC feature           |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=store compressed blocks in cache device,      |
|                   | 1=store uncompressed blocks in cache device     |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | deprecated in v0.7.0 by new compressed ARC      |
|                   | design                                          |
+-------------------+-------------------------------------------------+

l2arc_meta_percent
~~~~~~~~~~~~~~~~~~

Percent of ARC size allowed for L2ARC-only headers.
Since L2ARC buffers are not evicted on memory pressure, too large amount of
headers on system with irrationaly large L2ARC can render it slow or unusable.
This parameter limits L2ARC writes and rebuild to achieve it.

+-------------------+-------------------------------------------------+
| l2arc_nocompress  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | When workload really require enormous L2ARC.    |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Range             | 0 to 100                                        |
+-------------------+-------------------------------------------------+
| Default           | 33                                              |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v2.0 and later                                  |
+-------------------+-------------------------------------------------+

l2arc_mfuonly
~~~~~~~~~~~~~

Controls whether only MFU metadata and data are cached from ARC into L2ARC.
This may be desirable to avoid wasting space on L2ARC when reading/writing
large amounts of data that are not expected to be accessed more than once.
By default both MRU and MFU data and metadata are cached in the L2ARC.

+-------------------+-------------------------------------------------+
| l2arc_mfuonly     | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | When accessing a large amount of data only      |
|                   | once.                                           |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=store MRU and MFU blocks in cache device,     |
|                   | 1=store MFU blocks in cache device              |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v2.0 and later                                  |
+-------------------+-------------------------------------------------+

l2arc_noprefetch
~~~~~~~~~~~~~~~~

Disables writing prefetched, but unused, buffers to cache devices.

+-------------------+-------------------------------------------------+
| l2arc_noprefetch  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__,             |
|                   | `prefetch <#prefetch>`__                        |
+-------------------+-------------------------------------------------+
| When to change    | Setting to 0 can increase L2ARC hit rates for   |
|                   | workloads where the ARC is too small for a read |
|                   | workload that benefits from prefetching. Also,  |
|                   | if the main pool devices are very slow, setting |
|                   | to 0 can improve some workloads such as         |
|                   | backups.                                        |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=write prefetched but unused buffers to cache  |
|                   | devices, 1=do not write prefetched but unused   |
|                   | buffers to cache devices                        |
+-------------------+-------------------------------------------------+
| Default           | 1                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.0 and later                                |
+-------------------+-------------------------------------------------+

l2arc_norw
~~~~~~~~~~

Disables writing to cache devices while they are being read.

+-------------------+-------------------------------------------------+
| l2arc_norw        | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | In the early days of SSDs, some devices did not |
|                   | perform well when reading and writing           |
|                   | simultaneously. Modern SSDs do not have these   |
|                   | issues.                                         |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=read and write simultaneously, 1=avoid writes |
|                   | when reading for antique SSDs                   |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

l2arc_rebuild_blocks_min_l2size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The minimum required size (in bytes) of an L2ARC device in order to
write log blocks in it. The log blocks are used upon importing the pool
to rebuild the persistent L2ARC.  For L2ARC devices less than 1GB the
overhead involved offsets most of benefit so log blocks are not written
for cache devices smaller than this.

+---------------------------------+-----------------------------------+
| l2arc_rebuild_blocks_min_l2size | Notes                             |
+=================================+===================================+
| Tags                            | `ARC <#arc>`__,                   |
|                                 | `L2ARC <#l2arc>`__                |
+---------------------------------+-----------------------------------+
| When to change                  | The cache device is small and     |
|                                 | the pool is frequently imported.  |
+---------------------------------+-----------------------------------+
| Data Type                       | bytes                             |
+---------------------------------+-----------------------------------+
| Range                           | 0 to UINT64_MAX                   |
+---------------------------------+-----------------------------------+
| Default                         | 1,073,741,824                     |
+---------------------------------+-----------------------------------+
| Change                          | Dynamic                           |
+---------------------------------+-----------------------------------+
| Versions Affected               | v2.0 and later                    |
+---------------------------------+-----------------------------------+

l2arc_rebuild_enabled
~~~~~~~~~~~~~~~~~~~~~

Rebuild the persistent L2ARC when importing a pool.

+-----------------------+---------------------------------------------+
| l2arc_rebuild_enabled | Notes                                       |
+=======================+=============================================+
| Tags                  | `ARC <#arc>`__, `L2ARC <#l2arc>`__          |
+-----------------------+---------------------------------------------+
| When to change        | If there are problems importing a pool or   |
|                       | attaching an L2ARC device.                  |
+-----------------------+---------------------------------------------+
| Data Type             | boolean                                     |
+-----------------------+---------------------------------------------+
| Range                 | 0=disable persistent L2ARC rebuild,         |
|                       | 1=enable persistent L2ARC rebuild           |
+-----------------------+---------------------------------------------+
| Default               | 1                                           |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v2.0 and later                              |
+-----------------------+---------------------------------------------+

l2arc_trim_ahead
~~~~~~~~~~~~~~~~

Once the cache device has been filled TRIM ahead of the current write size
``l2arc_write_max`` on L2ARC devices by this percentage.  This can speed
up future writes depending on the performance characteristics of the
cache device.

When set to 100% TRIM twice the space required to accommodate upcoming
writes.  A minimum of 64MB will be trimmed.  If set it enables TRIM of
the whole L2ARC device when it is added to a pool.  By default, this
option is disabled since it can put significant stress on the underlying
storage devices.

+-------------------+-------------------------------------------------+
| l2arc_trim_ahead  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | Consider setting for cache devices which        |
|                   | effeciently handle TRIM commands.               |
+-------------------+-------------------------------------------------+
| Data Type         | ulong                                           |
+-------------------+-------------------------------------------------+
| Units             | percent of l2arc_write_max                      |
+-------------------+-------------------------------------------------+
| Range             | 0 to 100                                        |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v2.0 and later                                  |
+-------------------+-------------------------------------------------+

l2arc_write_boost
~~~~~~~~~~~~~~~~~

Until the ARC fills, increases the L2ARC fill rate
`l2arc_write_max <#l2arc-write-max>`__ by ``l2arc_write_boost``.

+-------------------+-------------------------------------------------+
| l2arc_write_boost | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | To fill the cache devices more aggressively     |
|                   | after pool import.                              |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 0 to UINT64_MAX                                 |
+-------------------+-------------------------------------------------+
| Default           | 8,388,608                                       |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

l2arc_write_max
~~~~~~~~~~~~~~~

Maximum number of bytes to be written to each cache device for each
L2ARC feed thread interval (see `l2arc_feed_secs <#l2arc-feed-secs>`__).
The actual limit can be adjusted by
`l2arc_write_boost <#l2arc-write-boost>`__. By default
`l2arc_feed_secs <#l2arc-feed-secs>`__ is 1 second, delivering a maximum
write workload to cache devices of 8 MiB/sec.

+-------------------+-------------------------------------------------+
| l2arc_write_max   | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `L2ARC <#l2arc>`__              |
+-------------------+-------------------------------------------------+
| When to change    | If the cache devices can sustain the write      |
|                   | workload, increasing the rate of cache device   |
|                   | fill when workloads generate new data at a rate |
|                   | higher than l2arc_write_max can increase L2ARC  |
|                   | hit rate                                        |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 1 to UINT64_MAX                                 |
+-------------------+-------------------------------------------------+
| Default           | 8,388,608                                       |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

metaslab_aliquot
~~~~~~~~~~~~~~~~

Sets the metaslab granularity. Nominally, ZFS will try to allocate this
amount of data to a top-level vdev before moving on to the next
top-level vdev. This is roughly similar to what would be referred to as
the "stripe size" in traditional RAID arrays.

When tuning for HDDs, it can be more efficient to have a few larger,
sequential writes to a device rather than switching to the next device.
Monitoring the size of contiguous writes to the disks relative to the
write throughput can be used to determine if increasing
``metaslab_aliquot`` can help. For modern devices, it is unlikely that
decreasing ``metaslab_aliquot`` from the default will help.

If there is only one top-level vdev, this tunable is not used.

+-------------------+-------------------------------------------------+
| metaslab_aliquot  | Notes                                           |
+===================+=================================================+
| Tags              | `allocation <#allocation>`__,                   |
|                   | `metaslab <#metaslab>`__, `vdev <#vdev>`__      |
+-------------------+-------------------------------------------------+
| When to change    | If write performance increases as devices more  |
|                   | efficiently write larger, contiguous blocks     |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 0 to UINT64_MAX                                 |
+-------------------+-------------------------------------------------+
| Default           | 524,288                                         |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

metaslab_bias_enabled
~~~~~~~~~~~~~~~~~~~~~

Enables metaslab group biasing based on a top-level vdev's utilization
relative to the pool. Nominally, all top-level devs are the same size
and the allocation is spread evenly. When the top-level vdevs are not of
the same size, for example if a new (empty) top-level is added to the
pool, this allows the new top-level vdev to get a larger portion of new
allocations.

+-----------------------+---------------------------------------------+
| metaslab_bias_enabled | Notes                                       |
+=======================+=============================================+
| Tags                  | `allocation <#allocation>`__,               |
|                       | `metaslab <#metaslab>`__, `vdev <#vdev>`__  |
+-----------------------+---------------------------------------------+
| When to change        | If a new top-level vdev is added and you do |
|                       | not want to bias new allocations to the new |
|                       | top-level vdev                              |
+-----------------------+---------------------------------------------+
| Data Type             | boolean                                     |
+-----------------------+---------------------------------------------+
| Range                 | 0=spread evenly across top-level vdevs,     |
|                       | 1=bias spread to favor less full top-level  |
|                       | vdevs                                       |
+-----------------------+---------------------------------------------+
| Default               | 1                                           |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.6.4 and later                            |
+-----------------------+---------------------------------------------+

zfs_metaslab_segment_weight_enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enables metaslab allocation based on largest free segment rather than
total amount of free space. The goal is to avoid metaslabs that exhibit
free space fragmentation: when there is a lot of small free spaces, but
few larger free spaces.

If ``zfs_metaslab_segment_weight_enabled`` is enabled, then
`metaslab_fragmentation_factor_enabled <#metaslab-fragmentation-factor-enabled>`__
is ignored.

+----------------------------------+----------------------------------+
| zfs                              | Notes                            |
| _metaslab_segment_weight_enabled |                                  |
+==================================+==================================+
| Tags                             | `allocation <#allocation>`__,    |
|                                  | `metaslab <#metaslab>`__         |
+----------------------------------+----------------------------------+
| When to change                   | When testing allocation and      |
|                                  | fragmentation                    |
+----------------------------------+----------------------------------+
| Data Type                        | boolean                          |
+----------------------------------+----------------------------------+
| Range                            | 0=do not consider metaslab       |
|                                  | fragmentation, 1=avoid metaslabs |
|                                  | where free space is highly       |
|                                  | fragmented                       |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.7.0 and later                 |
+----------------------------------+----------------------------------+

zfs_metaslab_switch_threshold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using segment-based metaslab selection (see
`zfs_metaslab_segment_weight_enabled <#zfs-metaslab-segment-weight-enabled>`__),
continue allocating from the active metaslab until
``zfs_metaslab_switch_threshold`` worth of free space buckets have been
exhausted.

+-------------------------------+-------------------------------------+
| zfs_metaslab_switch_threshold | Notes                               |
+===============================+=====================================+
| Tags                          | `allocation <#allocation>`__,       |
|                               | `metaslab <#metaslab>`__            |
+-------------------------------+-------------------------------------+
| When to change                | When testing allocation and         |
|                               | fragmentation                       |
+-------------------------------+-------------------------------------+
| Data Type                     | uint64                              |
+-------------------------------+-------------------------------------+
| Units                         | free spaces                         |
+-------------------------------+-------------------------------------+
| Range                         | 0 to UINT64_MAX                     |
+-------------------------------+-------------------------------------+
| Default                       | 2                                   |
+-------------------------------+-------------------------------------+
| Change                        | Dynamic                             |
+-------------------------------+-------------------------------------+
| Versions Affected             | v0.7.0 and later                    |
+-------------------------------+-------------------------------------+

metaslab_debug_load
~~~~~~~~~~~~~~~~~~~

When enabled, all metaslabs are loaded into memory during pool import.
Nominally, metaslab space map information is loaded and unloaded as
needed (see `metaslab_debug_unload <#metaslab-debug-unload>`__)

It is difficult to predict how much RAM is required to store a space
map. An empty or completely full metaslab has a small space map.
However, a highly fragmented space map can consume significantly more
memory.

Enabling ``metaslab_debug_load`` can increase pool import time.

+---------------------+-----------------------------------------------+
| metaslab_debug_load | Notes                                         |
+=====================+===============================================+
| Tags                | `allocation <#allocation>`__,                 |
|                     | `memory <#memory>`__,                         |
|                     | `metaslab <#metaslab>`__                      |
+---------------------+-----------------------------------------------+
| When to change      | When RAM is plentiful and pool import time is |
|                     | not a consideration                           |
+---------------------+-----------------------------------------------+
| Data Type           | boolean                                       |
+---------------------+-----------------------------------------------+
| Range               | 0=do not load all metaslab info at pool       |
|                     | import, 1=dynamically load metaslab info as   |
|                     | needed                                        |
+---------------------+-----------------------------------------------+
| Default             | 0                                             |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.6.4 and later                              |
+---------------------+-----------------------------------------------+

metaslab_debug_unload
~~~~~~~~~~~~~~~~~~~~~

When enabled, prevents metaslab information from being dynamically
unloaded from RAM. Nominally, metaslab space map information is loaded
and unloaded as needed (see
`metaslab_debug_load <#metaslab-debug-load>`__)

It is difficult to predict how much RAM is required to store a space
map. An empty or completely full metaslab has a small space map.
However, a highly fragmented space map can consume significantly more
memory.

Enabling ``metaslab_debug_unload`` consumes RAM that would otherwise be
freed.

+-----------------------+---------------------------------------------+
| metaslab_debug_unload | Notes                                       |
+=======================+=============================================+
| Tags                  | `allocation <#allocation>`__,               |
|                       | `memory <#memory>`__,                       |
|                       | `metaslab <#metaslab>`__                    |
+-----------------------+---------------------------------------------+
| When to change        | When RAM is plentiful and the penalty for   |
|                       | dynamically reloading metaslab info from    |
|                       | the pool is high                            |
+-----------------------+---------------------------------------------+
| Data Type             | boolean                                     |
+-----------------------+---------------------------------------------+
| Range                 | 0=dynamically unload metaslab info,         |
|                       | 1=unload metaslab info only upon pool       |
|                       | export                                      |
+-----------------------+---------------------------------------------+
| Default               | 0                                           |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.6.4 and later                            |
+-----------------------+---------------------------------------------+

metaslab_fragmentation_factor_enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable use of the fragmentation metric in computing metaslab weights.

In version v0.7.0, if
`zfs_metaslab_segment_weight_enabled <#zfs-metaslab-segment-weight-enabled>`__
is enabled, then ``metaslab_fragmentation_factor_enabled`` is ignored.

+----------------------------------+----------------------------------+
| metas                            | Notes                            |
| lab_fragmentation_factor_enabled |                                  |
+==================================+==================================+
| Tags                             | `allocation <#allocation>`__,    |
|                                  | `metaslab <#metaslab>`__         |
+----------------------------------+----------------------------------+
| When to change                   | To test metaslab fragmentation   |
+----------------------------------+----------------------------------+
| Data Type                        | boolean                          |
+----------------------------------+----------------------------------+
| Range                            | 0=do not consider metaslab free  |
|                                  | space fragmentation, 1=try to    |
|                                  | avoid fragmented metaslabs       |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.6.4 and later                 |
+----------------------------------+----------------------------------+

metaslabs_per_vdev
~~~~~~~~~~~~~~~~~~

When a vdev is added, it will be divided into approximately, but no more
than, this number of metaslabs.

+--------------------+------------------------------------------------+
| metaslabs_per_vdev | Notes                                          |
+====================+================================================+
| Tags               | `allocation <#allocation>`__,                  |
|                    | `metaslab <#metaslab>`__, `vdev <#vdev>`__     |
+--------------------+------------------------------------------------+
| When to change     | When testing metaslab allocation               |
+--------------------+------------------------------------------------+
| Data Type          | uint64                                         |
+--------------------+------------------------------------------------+
| Units              | metaslabs                                      |
+--------------------+------------------------------------------------+
| Range              | 16 to UINT64_MAX                               |
+--------------------+------------------------------------------------+
| Default            | 200                                            |
+--------------------+------------------------------------------------+
| Change             | Prior to pool creation or adding new top-level |
|                    | vdevs                                          |
+--------------------+------------------------------------------------+
| Versions Affected  | all                                            |
+--------------------+------------------------------------------------+

metaslab_preload_enabled
~~~~~~~~~~~~~~~~~~~~~~~~

Enable metaslab group preloading. Each top-level vdev has a metaslab
group. By default, up to 3 copies of metadata can exist and are
distributed across multiple top-level vdevs.
``metaslab_preload_enabled`` allows the corresponding metaslabs to be
preloaded, thus improving allocation efficiency.

+--------------------------+------------------------------------------+
| metaslab_preload_enabled | Notes                                    |
+==========================+==========================================+
| Tags                     | `allocation <#allocation>`__,            |
|                          | `metaslab <#metaslab>`__                 |
+--------------------------+------------------------------------------+
| When to change           | When testing metaslab allocation         |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=do not preload metaslab info,          |
|                          | 1=preload up to 3 metaslabs              |
+--------------------------+------------------------------------------+
| Default                  | 1                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.6.4 and later                         |
+--------------------------+------------------------------------------+

metaslab_lba_weighting_enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modern HDDs have uniform bit density and constant angular velocity.
Therefore, the outer recording zones are faster (higher bandwidth) than
the inner zones by the ratio of outer to inner track diameter. The
difference in bandwidth can be 2:1, and is often available in the HDD
detailed specifications or drive manual. For HDDs when
``metaslab_lba_weighting_enabled`` is true, write allocation preference
is given to the metaslabs representing the outer recording zones. Thus
the allocation to metaslabs prefers faster bandwidth over free space.

If the devices are not rotational, yet misrepresent themselves to the OS
as rotational, then disabling ``metaslab_lba_weighting_enabled`` can
result in more even, free-space-based allocation.

+--------------------------------+------------------------------------+
| metaslab_lba_weighting_enabled | Notes                              |
+================================+====================================+
| Tags                           | `allocation <#allocation>`__,      |
|                                | `metaslab <#metaslab>`__,          |
|                                | `HDD <#hdd>`__, `SSD <#ssd>`__     |
+--------------------------------+------------------------------------+
| When to change                 | disable if using only SSDs and     |
|                                | version v0.6.4 or earlier          |
+--------------------------------+------------------------------------+
| Data Type                      | boolean                            |
+--------------------------------+------------------------------------+
| Range                          | 0=do not use LBA weighting, 1=use  |
|                                | LBA weighting                      |
+--------------------------------+------------------------------------+
| Default                        | 1                                  |
+--------------------------------+------------------------------------+
| Change                         | Dynamic                            |
+--------------------------------+------------------------------------+
| Verification                   | The rotational setting described   |
|                                | by a block device in sysfs by      |
|                                | observing                          |
|                                | ``/sys/                            |
|                                | block/DISK_NAME/queue/rotational`` |
+--------------------------------+------------------------------------+
| Versions Affected              | prior to v0.6.5, the check for     |
|                                | non-rotation media did not exist   |
+--------------------------------+------------------------------------+

spa_config_path
~~~~~~~~~~~~~~~

By default, the ``zpool import`` command searches for pool information
in the ``zpool.cache`` file. If the pool to be imported has an entry in
``zpool.cache`` then the devices do not have to be scanned to determine
if they are pool members. The path to the cache file is spa_config_path.

For more information on ``zpool import`` and the ``-o cachefile`` and
``-d`` options, see the man page for zpool(8)

See also `zfs_autoimport_disable <#zfs-autoimport-disable>`__

+-------------------+-------------------------------------------------+
| spa_config_path   | Notes                                           |
+===================+=================================================+
| Tags              | `import <#import>`__                            |
+-------------------+-------------------------------------------------+
| When to change    | If creating a non-standard distribution and the |
|                   | cachefile property is inconvenient              |
+-------------------+-------------------------------------------------+
| Data Type         | string                                          |
+-------------------+-------------------------------------------------+
| Default           | ``/etc/zfs/zpool.cache``                        |
+-------------------+-------------------------------------------------+
| Change            | Dynamic, applies only to the next invocation of |
|                   | ``zpool import``                                |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

spa_asize_inflation
~~~~~~~~~~~~~~~~~~~

Multiplication factor used to estimate actual disk consumption from the
size of data being written. The default value is a worst case estimate,
but lower values may be valid for a given pool depending on its
configuration. Pool administrators who understand the factors involved
may wish to specify a more realistic inflation factor, particularly if
they operate close to quota or capacity limits.

The worst case space requirement for allocation is single-sector
max-parity RAIDZ blocks, in which case the space requirement is exactly
4 times the size, accounting for a maximum of 3 parity blocks. This is
added to the maximum number of ZFS ``copies`` parameter (copies max=3).
Additional space is required if the block could impact deduplication
tables. Altogether, the worst case is 24.

If the estimation is not correct, then quotas or out-of-space conditions
can lead to optimistic expectations of the ability to allocate.
Applications are typically not prepared to deal with such failures and
can misbehave.

+---------------------+-----------------------------------------------+
| spa_asize_inflation | Notes                                         |
+=====================+===============================================+
| Tags                | `allocation <#allocation>`__, `SPA <#spa>`__  |
+---------------------+-----------------------------------------------+
| When to change      | If the allocation requirements for the        |
|                     | workload are well known and quotas are used   |
+---------------------+-----------------------------------------------+
| Data Type           | uint64                                        |
+---------------------+-----------------------------------------------+
| Units               | unit                                          |
+---------------------+-----------------------------------------------+
| Range               | 1 to 24                                       |
+---------------------+-----------------------------------------------+
| Default             | 24                                            |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.6.3 and later                              |
+---------------------+-----------------------------------------------+

spa_load_verify_data
~~~~~~~~~~~~~~~~~~~~

An extreme rewind import (see ``zpool import -X``) normally performs a
full traversal of all blocks in the pool for verification. If this
parameter is set to 0, the traversal skips non-metadata blocks. It can
be toggled once the import has started to stop or start the traversal of
non-metadata blocks. See also
`spa_load_verify_metadata <#spa-load-verify-metadata>`__.

+----------------------+----------------------------------------------+
| spa_load_verify_data | Notes                                        |
+======================+==============================================+
| Tags                 | `allocation <#allocation>`__, `SPA <#spa>`__ |
+----------------------+----------------------------------------------+
| When to change       | At the risk of data integrity, to speed      |
|                      | extreme import of large pool                 |
+----------------------+----------------------------------------------+
| Data Type            | boolean                                      |
+----------------------+----------------------------------------------+
| Range                | 0=do not verify data upon pool import,       |
|                      | 1=verify pool data upon import               |
+----------------------+----------------------------------------------+
| Default              | 1                                            |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | v0.6.4 and later                             |
+----------------------+----------------------------------------------+

spa_load_verify_metadata
~~~~~~~~~~~~~~~~~~~~~~~~

An extreme rewind import (see ``zpool import -X``) normally performs a
full traversal of all blocks in the pool for verification. If this
parameter is set to 0, the traversal is not performed. It can be toggled
once the import has started to stop or start the traversal. See
`spa_load_verify_data <#spa-load-verify-data>`__

+--------------------------+------------------------------------------+
| spa_load_verify_metadata | Notes                                    |
+==========================+==========================================+
| Tags                     | `import <#import>`__                     |
+--------------------------+------------------------------------------+
| When to change           | At the risk of data integrity, to speed  |
|                          | extreme import of large pool             |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=do not verify metadata upon pool       |
|                          | import, 1=verify pool metadata upon      |
|                          | import                                   |
+--------------------------+------------------------------------------+
| Default                  | 1                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.6.4 and later                         |
+--------------------------+------------------------------------------+

spa_load_verify_maxinflight
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Maximum number of concurrent I/Os during the data verification performed
during an extreme rewind import (see ``zpool import -X``)

+-----------------------------+---------------------------------------+
| spa_load_verify_maxinflight | Notes                                 |
+=============================+=======================================+
| Tags                        | `import <#import>`__                  |
+-----------------------------+---------------------------------------+
| When to change              | During an extreme rewind import, to   |
|                             | match the concurrent I/O capabilities |
|                             | of the pool devices                   |
+-----------------------------+---------------------------------------+
| Data Type                   | int                                   |
+-----------------------------+---------------------------------------+
| Units                       | I/Os                                  |
+-----------------------------+---------------------------------------+
| Range                       | 1 to MAX_INT                          |
+-----------------------------+---------------------------------------+
| Default                     | 10,000                                |
+-----------------------------+---------------------------------------+
| Change                      | Dynamic                               |
+-----------------------------+---------------------------------------+
| Versions Affected           | v0.6.4 and later                      |
+-----------------------------+---------------------------------------+

spa_slop_shift
~~~~~~~~~~~~~~

Normally, the last 3.2% (1/(2^\ ``spa_slop_shift``)) of pool space is
reserved to ensure the pool doesn't run completely out of space, due to
unaccounted changes (e.g. to the MOS). This also limits the worst-case
time to allocate space. When less than this amount of free space exists,
most ZPL operations (e.g. write, create) return error:no space (ENOSPC).

Changing spa_slop_shift affects the currently loaded ZFS module and all
imported pools. spa_slop_shift is not stored on disk. Beware when
importing full pools on systems with larger spa_slop_shift can lead to
over-full conditions.

The minimum SPA slop space is limited to 128 MiB.

+-------------------+-------------------------------------------------+
| spa_slop_shift    | Notes                                           |
+===================+=================================================+
| Tags              | `allocation <#allocation>`__, `SPA <#spa>`__    |
+-------------------+-------------------------------------------------+
| When to change    | For large pools, when 3.2% may be too           |
|                   | conservative and more usable space is desired,  |
|                   | consider increasing ``spa_slop_shift``          |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Units             | shift                                           |
+-------------------+-------------------------------------------------+
| Range             | 1 to MAX_INT, however the practical upper limit |
|                   | is 15 for a system with 4TB of RAM              |
+-------------------+-------------------------------------------------+
| Default           | 5                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.5 and later                                |
+-------------------+-------------------------------------------------+

zfetch_array_rd_sz
~~~~~~~~~~~~~~~~~~

If prefetching is enabled, do not prefetch blocks larger than
``zfetch_array_rd_sz`` size.

================== =================================================
zfetch_array_rd_sz Notes
================== =================================================
Tags               `prefetch <#prefetch>`__
When to change     To allow prefetching when using large block sizes
Data Type          unsigned long
Units              bytes
Range              0 to MAX_ULONG
Default            1,048,576 (1 MiB)
Change             Dynamic
Versions Affected  all
================== =================================================

zfetch_max_distance
~~~~~~~~~~~~~~~~~~~

Limits the maximum number of bytes to prefetch per stream.

+---------------------+-----------------------------------------------+
| zfetch_max_distance | Notes                                         |
+=====================+===============================================+
| Tags                | `prefetch <#prefetch>`__                      |
+---------------------+-----------------------------------------------+
| When to change      | Consider increasing read workloads that use   |
|                     | large blocks and exhibit high prefetch hit    |
|                     | ratios                                        |
+---------------------+-----------------------------------------------+
| Data Type           | uint                                          |
+---------------------+-----------------------------------------------+
| Units               | bytes                                         |
+---------------------+-----------------------------------------------+
| Range               | 0 to UINT_MAX                                 |
+---------------------+-----------------------------------------------+
| Default             | 8,388,608                                     |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.7.0                                        |
+---------------------+-----------------------------------------------+

zfetch_max_streams
~~~~~~~~~~~~~~~~~~

Maximum number of prefetch streams per file.

For version v0.7.0 and later, when prefetching small files the number of
prefetch streams is automatically reduced below to prevent the streams
from overlapping.

+--------------------+------------------------------------------------+
| zfetch_max_streams | Notes                                          |
+====================+================================================+
| Tags               | `prefetch <#prefetch>`__                       |
+--------------------+------------------------------------------------+
| When to change     | If the workload benefits from prefetching and  |
|                    | has more than ``zfetch_max_streams``           |
|                    | concurrent reader threads                      |
+--------------------+------------------------------------------------+
| Data Type          | uint                                           |
+--------------------+------------------------------------------------+
| Units              | streams                                        |
+--------------------+------------------------------------------------+
| Range              | 1 to MAX_UINT                                  |
+--------------------+------------------------------------------------+
| Default            | 8                                              |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| Versions Affected  | all                                            |
+--------------------+------------------------------------------------+

zfetch_min_sec_reap
~~~~~~~~~~~~~~~~~~~

Prefetch streams that have been accessed in ``zfetch_min_sec_reap``
seconds are automatically stopped.

=================== ===========================
zfetch_min_sec_reap Notes
=================== ===========================
Tags                `prefetch <#prefetch>`__
When to change      To test prefetch efficiency
Data Type           uint
Units               seconds
Range               0 to MAX_UINT
Default             2
Change              Dynamic
Versions Affected   all
=================== ===========================

zfs_arc_dnode_limit_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Percentage of ARC metadata space that can be used for dnodes.

The value calculated for ``zfs_arc_dnode_limit_percent`` can be
overridden by `zfs_arc_dnode_limit <#zfs-arc-dnode-limit>`__.

+-----------------------------+---------------------------------------+
| zfs_arc_dnode_limit_percent | Notes                                 |
+=============================+=======================================+
| Tags                        | `ARC <#arc>`__                        |
+-----------------------------+---------------------------------------+
| When to change              | Consider increasing if ``arc_prune``  |
|                             | is using excessive system time and    |
|                             | ``/proc/spl/kstat/zfs/arcstats``      |
|                             | shows ``arc_dnode_size`` is near or   |
|                             | over ``arc_dnode_limit``              |
+-----------------------------+---------------------------------------+
| Data Type                   | int                                   |
+-----------------------------+---------------------------------------+
| Units                       | percent of arc_meta_limit             |
+-----------------------------+---------------------------------------+
| Range                       | 0 to 100                              |
+-----------------------------+---------------------------------------+
| Default                     | 10                                    |
+-----------------------------+---------------------------------------+
| Change                      | Dynamic                               |
+-----------------------------+---------------------------------------+
| Versions Affected           | v0.7.0 and later                      |
+-----------------------------+---------------------------------------+

zfs_arc_dnode_limit
~~~~~~~~~~~~~~~~~~~

When the number of bytes consumed by dnodes in the ARC exceeds
``zfs_arc_dnode_limit`` bytes, demand for new metadata can take from the
space consumed by dnodes.

The default value 0, indicates that a percent which is based on
`zfs_arc_dnode_limit_percent <#zfs-arc-dnode-limit-percent>`__ of the
ARC meta buffers that may be used for dnodes.

``zfs_arc_dnode_limit`` is similar to
`zfs_arc_meta_prune <#zfs-arc-meta-prune>`__ which serves a similar
purpose for metadata.

+---------------------+-----------------------------------------------+
| zfs_arc_dnode_limit | Notes                                         |
+=====================+===============================================+
| Tags                | `ARC <#arc>`__                                |
+---------------------+-----------------------------------------------+
| When to change      | Consider increasing if ``arc_prune`` is using |
|                     | excessive system time and                     |
|                     | ``/proc/spl/kstat/zfs/arcstats`` shows        |
|                     | ``arc_dnode_size`` is near or over            |
|                     | ``arc_dnode_limit``                           |
+---------------------+-----------------------------------------------+
| Data Type           | uint64                                        |
+---------------------+-----------------------------------------------+
| Units               | bytes                                         |
+---------------------+-----------------------------------------------+
| Range               | 0 to MAX_UINT64                               |
+---------------------+-----------------------------------------------+
| Default             | 0 (uses                                       |
|                     | `zfs_arc_dnode_lim                            |
|                     | it_percent <#zfs-arc-dnode-limit-percent>`__) |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.7.0 and later                              |
+---------------------+-----------------------------------------------+

zfs_arc_dnode_reduce_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Percentage of ARC dnodes to try to evict in response to demand for
non-metadata when the number of bytes consumed by dnodes exceeds
`zfs_arc_dnode_limit <#zfs-arc-dnode-limit>`__.

+------------------------------+--------------------------------------+
| zfs_arc_dnode_reduce_percent | Notes                                |
+==============================+======================================+
| Tags                         | `ARC <#arc>`__                       |
+------------------------------+--------------------------------------+
| When to change               | Testing dnode cache efficiency       |
+------------------------------+--------------------------------------+
| Data Type                    | uint64                               |
+------------------------------+--------------------------------------+
| Units                        | percent of size of dnode space used  |
|                              | above                                |
|                              | `zfs_arc_d                           |
|                              | node_limit <#zfs-arc-dnode-limit>`__ |
+------------------------------+--------------------------------------+
| Range                        | 0 to 100                             |
+------------------------------+--------------------------------------+
| Default                      | 10                                   |
+------------------------------+--------------------------------------+
| Change                       | Dynamic                              |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.7.0 and later                     |
+------------------------------+--------------------------------------+

zfs_arc_average_blocksize
~~~~~~~~~~~~~~~~~~~~~~~~~

The ARC's buffer hash table is sized based on the assumption of an
average block size of ``zfs_arc_average_blocksize``. The default of 8
KiB uses approximately 1 MiB of hash table per 1 GiB of physical memory
with 8-byte pointers.

+---------------------------+-----------------------------------------+
| zfs_arc_average_blocksize | Notes                                   |
+===========================+=========================================+
| Tags                      | `ARC <#arc>`__, `memory <#memory>`__    |
+---------------------------+-----------------------------------------+
| When to change            | For workloads where the known average   |
|                           | blocksize is larger, increasing         |
|                           | ``zfs_arc_average_blocksize`` can       |
|                           | reduce memory usage                     |
+---------------------------+-----------------------------------------+
| Data Type                 | int                                     |
+---------------------------+-----------------------------------------+
| Units                     | bytes                                   |
+---------------------------+-----------------------------------------+
| Range                     | 512 to 16,777,216                       |
+---------------------------+-----------------------------------------+
| Default                   | 8,192                                   |
+---------------------------+-----------------------------------------+
| Change                    | Prior to zfs module load                |
+---------------------------+-----------------------------------------+
| Versions Affected         | all                                     |
+---------------------------+-----------------------------------------+

zfs_arc_evict_batch_limit
~~~~~~~~~~~~~~~~~~~~~~~~~

Number ARC headers to evict per sublist before proceeding to another
sublist. This batch-style operation prevents entire sublists from being
evicted at once but comes at a cost of additional unlocking and locking.

========================= ==============================
zfs_arc_evict_batch_limit Notes
========================= ==============================
Tags                      `ARC <#arc>`__
When to change            Testing ARC multilist features
Data Type                 int
Units                     count of ARC headers
Range                     1 to INT_MAX
Default                   10
Change                    Dynamic
Versions Affected         v0.6.5 and later
========================= ==============================

zfs_arc_grow_retry
~~~~~~~~~~~~~~~~~~

When the ARC is shrunk due to memory demand, do not retry growing the
ARC for ``zfs_arc_grow_retry`` seconds. This operates as a damper to
prevent oscillating grow/shrink cycles when there is memory pressure.

If ``zfs_arc_grow_retry`` = 0, the internal default of 5 seconds is
used.

================== ====================================
zfs_arc_grow_retry Notes
================== ====================================
Tags               `ARC <#arc>`__, `memory <#memory>`__
When to change     TBD
Data Type          int
Units              seconds
Range              1 to MAX_INT
Default            0
Change             Dynamic
Versions Affected  v0.6.5 and later
================== ====================================

zfs_arc_lotsfree_percent
~~~~~~~~~~~~~~~~~~~~~~~~

Throttle ARC memory consumption, effectively throttling I/O, when free
system memory drops below this percentage of total system memory.
Setting ``zfs_arc_lotsfree_percent`` to 0 disables the throttle.

The arcstat_memory_throttle_count counter in
``/proc/spl/kstat/arcstats`` can indicate throttle activity.

======================== ====================================
zfs_arc_lotsfree_percent Notes
======================== ====================================
Tags                     `ARC <#arc>`__, `memory <#memory>`__
When to change           TBD
Data Type                int
Units                    percent
Range                    0 to 100
Default                  10
Change                   Dynamic
Versions Affected        v0.6.5 and later
======================== ====================================

zfs_arc_max
~~~~~~~~~~~

Maximum size of ARC in bytes. If set to 0 then the maximum ARC size is
set to 1/2 of system RAM.

``zfs_arc_max`` can be changed dynamically with some caveats. It cannot
be set back to 0 while running and reducing it below the current ARC
size will not cause the ARC to shrink without memory pressure to induce
shrinking.

+-------------------+-------------------------------------------------+
| zfs_arc_max       | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `memory <#memory>`__            |
+-------------------+-------------------------------------------------+
| When to change    | Reduce if ARC competes too much with other      |
|                   | applications, increase if ZFS is the primary    |
|                   | application and can use more RAM                |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 67,108,864 to RAM size in bytes                 |
+-------------------+-------------------------------------------------+
| Default           | 0 (uses default of RAM size in bytes / 2)       |
+-------------------+-------------------------------------------------+
| Change            | Dynamic (see description above)                 |
+-------------------+-------------------------------------------------+
| Verification      | ``c`` column in ``arcstats.py`` or              |
|                   | ``/proc/spl/kstat/zfs/arcstats`` entry          |
|                   | ``c_max``                                       |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

zfs_arc_meta_adjust_restarts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The number of restart passes to make while scanning the ARC attempting
the free buffers in order to stay below the
`zfs_arc_meta_limit <#zfs-arc-meta-limit>`__.

============================ =======================================
zfs_arc_meta_adjust_restarts Notes
============================ =======================================
Tags                         `ARC <#arc>`__
When to change               Testing ARC metadata adjustment feature
Data Type                    int
Units                        restarts
Range                        0 to INT_MAX
Default                      4,096
Change                       Dynamic
Versions Affected            v0.6.5 and later
============================ =======================================

zfs_arc_meta_limit
~~~~~~~~~~~~~~~~~~

Sets the maximum allowed size metadata buffers in the ARC. When
`zfs_arc_meta_limit <#zfs-arc-meta-limit>`__ is reached metadata buffers
are reclaimed, even if the overall ``c_max`` has not been reached.

In version v0.7.0, with a default value = 0,
``zfs_arc_meta_limit_percent`` is used to set ``arc_meta_limit``

+--------------------+------------------------------------------------+
| zfs_arc_meta_limit | Notes                                          |
+====================+================================================+
| Tags               | `ARC <#arc>`__                                 |
+--------------------+------------------------------------------------+
| When to change     | For workloads where the metadata to data ratio |
|                    | in the ARC can be changed to improve ARC hit   |
|                    | rates                                          |
+--------------------+------------------------------------------------+
| Data Type          | uint64                                         |
+--------------------+------------------------------------------------+
| Units              | bytes                                          |
+--------------------+------------------------------------------------+
| Range              | 0 to ``c_max``                                 |
+--------------------+------------------------------------------------+
| Default            | 0                                              |
+--------------------+------------------------------------------------+
| Change             | Dynamic, except that it cannot be set back to  |
|                    | 0 for a specific percent of the ARC; it must   |
|                    | be set to an explicit value                    |
+--------------------+------------------------------------------------+
| Verification       | ``/proc/spl/kstat/zfs/arcstats`` entry         |
|                    | ``arc_meta_limit``                             |
+--------------------+------------------------------------------------+
| Versions Affected  | all                                            |
+--------------------+------------------------------------------------+

zfs_arc_meta_limit_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~

Sets the limit to ARC metadata, ``arc_meta_limit``, as a percentage of
the maximum size target of the ARC, ``c_max``

Prior to version v0.7.0, the
`zfs_arc_meta_limit <#zfs-arc-meta-limit>`__ was used to set the limit
as a fixed size. ``zfs_arc_meta_limit_percent`` provides a more
convenient interface for setting the limit.

+----------------------------+----------------------------------------+
| zfs_arc_meta_limit_percent | Notes                                  |
+============================+========================================+
| Tags                       | `ARC <#arc>`__                         |
+----------------------------+----------------------------------------+
| When to change             | For workloads where the metadata to    |
|                            | data ratio in the ARC can be changed   |
|                            | to improve ARC hit rates               |
+----------------------------+----------------------------------------+
| Data Type                  | uint64                                 |
+----------------------------+----------------------------------------+
| Units                      | percent of ``c_max``                   |
+----------------------------+----------------------------------------+
| Range                      | 0 to 100                               |
+----------------------------+----------------------------------------+
| Default                    | 75                                     |
+----------------------------+----------------------------------------+
| Change                     | Dynamic                                |
+----------------------------+----------------------------------------+
| Verification               | ``/proc/spl/kstat/zfs/arcstats`` entry |
|                            | ``arc_meta_limit``                     |
+----------------------------+----------------------------------------+
| Versions Affected          | v0.7.0 and later                       |
+----------------------------+----------------------------------------+

zfs_arc_meta_min
~~~~~~~~~~~~~~~~

The minimum allowed size in bytes that metadata buffers may consume in
the ARC. This value defaults to 0 which disables a floor on the amount
of the ARC devoted meta data.

When evicting data from the ARC, if the ``metadata_size`` is less than
``arc_meta_min`` then data is evicted instead of metadata.

+-------------------+---------------------------------------------------------+
| zfs_arc_meta_min  | Notes                                                   |
+===================+=========================================================+
| Tags              | `ARC <#arc>`__                                          |
+-------------------+---------------------------------------------------------+
| When to change    |                                                         |
+-------------------+---------------------------------------------------------+
| Data Type         | uint64                                                  |
+-------------------+---------------------------------------------------------+
| Units             | bytes                                                   |
+-------------------+---------------------------------------------------------+
| Range             | 16,777,216 to ``c_max``                                 |
+-------------------+---------------------------------------------------------+
| Default           | 0 (use internal default 16 MiB)                         |
+-------------------+---------------------------------------------------------+
| Change            | Dynamic                                                 |
+-------------------+---------------------------------------------------------+
| Verification      | ``/proc/spl/kstat/zfs/arcstats`` entry ``arc_meta_min`` |
+-------------------+---------------------------------------------------------+
| Versions Affected | all                                                     |
+-------------------+---------------------------------------------------------+

zfs_arc_meta_prune
~~~~~~~~~~~~~~~~~~

``zfs_arc_meta_prune`` sets the number of dentries and znodes to be
scanned looking for entries which can be dropped. This provides a
mechanism to ensure the ARC can honor the ``arc_meta_limit and`` reclaim
otherwise pinned ARC buffers. Pruning may be required when the ARC size
drops to ``arc_meta_limit`` because dentries and znodes can pin buffers
in the ARC. Increasing this value will cause to dentry and znode caches
to be pruned more aggressively and the arc_prune thread becomes more
active. Setting ``zfs_arc_meta_prune`` to 0 will disable pruning.

+--------------------+------------------------------------------------+
| zfs_arc_meta_prune | Notes                                          |
+====================+================================================+
| Tags               | `ARC <#arc>`__                                 |
+--------------------+------------------------------------------------+
| When to change     | TBD                                            |
+--------------------+------------------------------------------------+
| Data Type          | uint64                                         |
+--------------------+------------------------------------------------+
| Units              | entries                                        |
+--------------------+------------------------------------------------+
| Range              | 0 to INT_MAX                                   |
+--------------------+------------------------------------------------+
| Default            | 10,000                                         |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| ! Verification     | Prune activity is counted by the               |
|                    | ``/proc/spl/kstat/zfs/arcstats`` entry         |
|                    | ``arc_prune``                                  |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.6.5 and later                               |
+--------------------+------------------------------------------------+

zfs_arc_meta_strategy
~~~~~~~~~~~~~~~~~~~~~

Defines the strategy for ARC metadata eviction (meta reclaim strategy).
A value of 0 (META_ONLY) will evict only the ARC metadata. A value of 1
(BALANCED) indicates that additional data may be evicted if required in
order to evict the requested amount of metadata.

+-----------------------+---------------------------------------------+
| zfs_arc_meta_strategy | Notes                                       |
+=======================+=============================================+
| Tags                  | `ARC <#arc>`__                              |
+-----------------------+---------------------------------------------+
| When to change        | Testing ARC metadata eviction               |
+-----------------------+---------------------------------------------+
| Data Type             | int                                         |
+-----------------------+---------------------------------------------+
| Units                 | enum                                        |
+-----------------------+---------------------------------------------+
| Range                 | 0=evict metadata only, 1=also evict data    |
|                       | buffers if they can free metadata buffers   |
|                       | for eviction                                |
+-----------------------+---------------------------------------------+
| Default               | 1 (BALANCED)                                |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.6.5 and later                            |
+-----------------------+---------------------------------------------+

zfs_arc_min
~~~~~~~~~~~

Minimum ARC size limit. When the ARC is asked to shrink, it will stop
shrinking at ``c_min`` as tuned by ``zfs_arc_min``.

+-------------------+-------------------------------------------------+
| zfs_arc_min       | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__                                  |
+-------------------+-------------------------------------------------+
| When to change    | If the primary focus of the system is ZFS, then |
|                   | increasing can ensure the ARC gets a minimum    |
|                   | amount of RAM                                   |
+-------------------+-------------------------------------------------+
| Data Type         | uint64                                          |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 33,554,432 to ``c_max``                         |
+-------------------+-------------------------------------------------+
| Default           | For kernel: greater of 33,554,432 (32 MiB) and  |
|                   | memory size / 32. For user-land: greater of     |
|                   | 33,554,432 (32 MiB) and ``c_max`` / 2.          |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Verification      | ``/proc/spl/kstat/zfs/arcstats`` entry          |
|                   | ``c_min``                                       |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

zfs_arc_min_prefetch_ms
~~~~~~~~~~~~~~~~~~~~~~~

Minimum time prefetched blocks are locked in the ARC.

A value of 0 represents the default of 1 second. However, once changed,
dynamically setting to 0 will not return to the default.

======================= ========================================
zfs_arc_min_prefetch_ms Notes
======================= ========================================
Tags                    `ARC <#arc>`__, `prefetch <#prefetch>`__
When to change          TBD
Data Type               int
Units                   milliseconds
Range                   1 to INT_MAX
Default                 0 (use internal default of 1000 ms)
Change                  Dynamic
Versions Affected       v0.8.0 and later
======================= ========================================

zfs_arc_min_prescient_prefetch_ms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minimum time "prescient prefetched" blocks are locked in the ARC. These
blocks are meant to be prefetched fairly aggressively ahead of the code
that may use them.

A value of 0 represents the default of 6 seconds. However, once changed,
dynamically setting to 0 will not return to the default.

+----------------------------------+----------------------------------+
| z                                | Notes                            |
| fs_arc_min_prescient_prefetch_ms |                                  |
+==================================+==================================+
| Tags                             | `ARC <#arc>`__,                  |
|                                  | `prefetch <#prefetch>`__         |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | milliseconds                     |
+----------------------------------+----------------------------------+
| Range                            | 1 to INT_MAX                     |
+----------------------------------+----------------------------------+
| Default                          | 0 (use internal default of 6000  |
|                                  | ms)                              |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.8.0 and later                 |
+----------------------------------+----------------------------------+

zfs_multilist_num_sublists
~~~~~~~~~~~~~~~~~~~~~~~~~~

To allow more fine-grained locking, each ARC state contains a series of
lists (sublists) for both data and metadata objects. Locking is
performed at the sublist level. This parameters controls the number of
sublists per ARC state, and also applies to other uses of the multilist
data structure.

+----------------------------+----------------------------------------+
| zfs_multilist_num_sublists | Notes                                  |
+============================+========================================+
| Tags                       | `ARC <#arc>`__                         |
+----------------------------+----------------------------------------+
| When to change             | TBD                                    |
+----------------------------+----------------------------------------+
| Data Type                  | int                                    |
+----------------------------+----------------------------------------+
| Units                      | lists                                  |
+----------------------------+----------------------------------------+
| Range                      | 1 to INT_MAX                           |
+----------------------------+----------------------------------------+
| Default                    | 0 (internal value is greater of number |
|                            | of online CPUs or 4)                   |
+----------------------------+----------------------------------------+
| Change                     | Prior to zfs module load               |
+----------------------------+----------------------------------------+
| Versions Affected          | v0.7.0 and later                       |
+----------------------------+----------------------------------------+

zfs_arc_overflow_shift
~~~~~~~~~~~~~~~~~~~~~~

The ARC size is considered to be overflowing if it exceeds the current
ARC target size (``/proc/spl/kstat/zfs/arcstats`` entry ``c``) by a
threshold determined by ``zfs_arc_overflow_shift``. The threshold is
calculated as a fraction of c using the formula: (ARC target size)
``c >> zfs_arc_overflow_shift``

The default value of 8 causes the ARC to be considered to be overflowing
if it exceeds the target size by 1/256th (0.3%) of the target size.

When the ARC is overflowing, new buffer allocations are stalled until
the reclaim thread catches up and the overflow condition no longer
exists.

====================== ================
zfs_arc_overflow_shift Notes
====================== ================
Tags                   `ARC <#arc>`__
When to change         TBD
Data Type              int
Units                  shift
Range                  1 to INT_MAX
Default                8
Change                 Dynamic
Versions Affected      v0.6.5 and later
====================== ================

zfs_arc_p_min_shift
~~~~~~~~~~~~~~~~~~~

arc_p_min_shift is used to shift of ARC target size
(``/proc/spl/kstat/zfs/arcstats`` entry ``c``) for calculating both
minimum and maximum most recently used (MRU) target size
(``/proc/spl/kstat/zfs/arcstats`` entry ``p``)

A value of 0 represents the default setting of ``arc_p_min_shift`` = 4.
However, once changed, dynamically setting ``zfs_arc_p_min_shift`` to 0
will not return to the default.

+---------------------+-----------------------------------------------+
| zfs_arc_p_min_shift | Notes                                         |
+=====================+===============================================+
| Tags                | `ARC <#arc>`__                                |
+---------------------+-----------------------------------------------+
| When to change      | TBD                                           |
+---------------------+-----------------------------------------------+
| Data Type           | int                                           |
+---------------------+-----------------------------------------------+
| Units               | shift                                         |
+---------------------+-----------------------------------------------+
| Range               | 1 to INT_MAX                                  |
+---------------------+-----------------------------------------------+
| Default             | 0 (internal default = 4)                      |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Verification        | Observe changes to                            |
|                     | ``/proc/spl/kstat/zfs/arcstats`` entry ``p``  |
+---------------------+-----------------------------------------------+
| Versions Affected   | all                                           |
+---------------------+-----------------------------------------------+

zfs_arc_p_dampener_disable
~~~~~~~~~~~~~~~~~~~~~~~~~~

When data is being added to the ghost lists, the MRU target size is
adjusted. The amount of adjustment is based on the ratio of the MRU/MFU
sizes. When enabled, the ratio is capped to 10, avoiding large
adjustments.

+----------------------------+----------------------------------------+
| zfs_arc_p_dampener_disable | Notes                                  |
+============================+========================================+
| Tags                       | `ARC <#arc>`__                         |
+----------------------------+----------------------------------------+
| When to change             | Testing ARC ghost list behaviour       |
+----------------------------+----------------------------------------+
| Data Type                  | boolean                                |
+----------------------------+----------------------------------------+
| Range                      | 0=avoid large adjustments, 1=permit    |
|                            | large adjustments                      |
+----------------------------+----------------------------------------+
| Default                    | 1                                      |
+----------------------------+----------------------------------------+
| Change                     | Dynamic                                |
+----------------------------+----------------------------------------+
| Versions Affected          | v0.6.4 and later                       |
+----------------------------+----------------------------------------+

zfs_arc_shrink_shift
~~~~~~~~~~~~~~~~~~~~

``arc_shrink_shift`` is used to adjust the ARC target sizes when large
reduction is required. The current ARC target size, ``c``, and MRU size
``p`` can be reduced by by the current ``size >> arc_shrink_shift``. For
the default value of 7, this reduces the target by approximately 0.8%.

A value of 0 represents the default setting of arc_shrink_shift = 7.
However, once changed, dynamically setting arc_shrink_shift to 0 will
not return to the default.

+----------------------+----------------------------------------------+
| zfs_arc_shrink_shift | Notes                                        |
+======================+==============================================+
| Tags                 | `ARC <#arc>`__, `memory <#memory>`__         |
+----------------------+----------------------------------------------+
| When to change       | During memory shortfall, reducing            |
|                      | ``zfs_arc_shrink_shift`` increases the rate  |
|                      | of ARC shrinkage                             |
+----------------------+----------------------------------------------+
| Data Type            | int                                          |
+----------------------+----------------------------------------------+
| Units                | shift                                        |
+----------------------+----------------------------------------------+
| Range                | 1 to INT_MAX                                 |
+----------------------+----------------------------------------------+
| Default              | 0 (``arc_shrink_shift`` = 7)                 |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | all                                          |
+----------------------+----------------------------------------------+

zfs_arc_pc_percent
~~~~~~~~~~~~~~~~~~

``zfs_arc_pc_percent`` allows ZFS arc to play more nicely with the
kernel's LRU pagecache. It can guarantee that the arc size won't
collapse under scanning pressure on the pagecache, yet still allows arc
to be reclaimed down to zfs_arc_min if necessary. This value is
specified as percent of pagecache size (as measured by
``NR_FILE_PAGES``) where that percent may exceed 100. This only operates
during memory pressure/reclaim.

+--------------------+------------------------------------------------+
| zfs_arc_pc_percent | Notes                                          |
+====================+================================================+
| Tags               | `ARC <#arc>`__, `memory <#memory>`__           |
+--------------------+------------------------------------------------+
| When to change     | When using file systems under memory           |
|                    | shortfall, if the page scanner causes the ARC  |
|                    | to shrink too fast, then adjusting             |
|                    | ``zfs_arc_pc_percent`` can reduce the shrink   |
|                    | rate                                           |
+--------------------+------------------------------------------------+
| Data Type          | int                                            |
+--------------------+------------------------------------------------+
| Units              | percent                                        |
+--------------------+------------------------------------------------+
| Range              | 0 to 100                                       |
+--------------------+------------------------------------------------+
| Default            | 0 (disabled)                                   |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.7.0 and later                               |
+--------------------+------------------------------------------------+

zfs_arc_sys_free
~~~~~~~~~~~~~~~~

``zfs_arc_sys_free`` is the target number of bytes the ARC should leave
as free memory on the system. Defaults to the larger of 1/64 of physical
memory or 512K. Setting this option to a non-zero value will override
the default.

A value of 0 represents the default setting of larger of 1/64 of
physical memory or 512 KiB. However, once changed, dynamically setting
zfs_arc_sys_free to 0 will not return to the default.

+-------------------+-------------------------------------------------+
| zfs_arc_sys_free  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#arc>`__, `memory <#memory>`__            |
+-------------------+-------------------------------------------------+
| When to change    | Change if more free memory is desired as a      |
|                   | margin against memory demand by applications    |
+-------------------+-------------------------------------------------+
| Data Type         | ulong                                           |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 0 to ULONG_MAX                                  |
+-------------------+-------------------------------------------------+
| Default           | 0 (default to larger of 1/64 of physical memory |
|                   | or 512 KiB)                                     |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.5 and later                                |
+-------------------+-------------------------------------------------+

zfs_autoimport_disable
~~~~~~~~~~~~~~~~~~~~~~

Disable reading zpool.cache file (see
`spa_config_path <#spa-config-path>`__) when loading the zfs module.

+------------------------+--------------------------------------------+
| zfs_autoimport_disable | Notes                                      |
+========================+============================================+
| Tags                   | `import <#import>`__                       |
+------------------------+--------------------------------------------+
| When to change         | Leave as default so that zfs behaves as    |
|                        | other Linux kernel modules                 |
+------------------------+--------------------------------------------+
| Data Type              | boolean                                    |
+------------------------+--------------------------------------------+
| Range                  | 0=read ``zpool.cache`` at module load,     |
|                        | 1=do not read ``zpool.cache`` at module    |
|                        | load                                       |
+------------------------+--------------------------------------------+
| Default                | 1                                          |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | v0.6.4 and later                           |
+------------------------+--------------------------------------------+

zfs_commit_timeout_pct
~~~~~~~~~~~~~~~~~~~~~~

``zfs_commit_timeout_pct`` controls the amount of time that a log (ZIL)
write block (lwb) remains "open" when it isn't "full" and it has a
thread waiting to commit to stable storage. The timeout is scaled based
on a percentage of the last lwb latency to avoid significantly impacting
the latency of each individual intent log transaction (itx).

====================== ==============
zfs_commit_timeout_pct Notes
====================== ==============
Tags                   `ZIL <#zil>`__
When to change         TBD
Data Type              int
Units                  percent
Range                  1 to 100
Default                5
Change                 Dynamic
Versions Affected      v0.8.0
====================== ==============

zfs_dbgmsg_enable
~~~~~~~~~~~~~~~~~

| Internally ZFS keeps a small log to facilitate debugging. The contents
  of the log are in the ``/proc/spl/kstat/zfs/dbgmsg`` file.
| Writing 0 to ``/proc/spl/kstat/zfs/dbgmsg`` file clears the log.

See also `zfs_dbgmsg_maxsize <#zfs-dbgmsg-maxsize>`__

================= =================================================
zfs_dbgmsg_enable Notes
================= =================================================
Tags              `debug <#debug>`__
When to change    To view ZFS internal debug log
Data Type         boolean
Range             0=do not log debug messages, 1=log debug messages
Default           0 (1 for debug builds)
Change            Dynamic
Versions Affected v0.6.5 and later
================= =================================================

zfs_dbgmsg_maxsize
~~~~~~~~~~~~~~~~~~

The ``/proc/spl/kstat/zfs/dbgmsg`` file size limit is set by
zfs_dbgmsg_maxsize.

See also zfs_dbgmsg_enable

================== ==================
zfs_dbgmsg_maxsize Notes
================== ==================
Tags               `debug <#debug>`__
When to change     TBD
Data Type          int
Units              bytes
Range              0 to INT_MAX
Default            4 MiB
Change             Dynamic
Versions Affected  v0.6.5 and later
================== ==================

zfs_dbuf_state_index
~~~~~~~~~~~~~~~~~~~~

The ``zfs_dbuf_state_index`` feature is currently unused. It is normally
used for controlling values in the ``/proc/spl/kstat/zfs/dbufs`` file.

==================== ==================
zfs_dbuf_state_index Notes
==================== ==================
Tags                 `debug <#debug>`__
When to change       Do not change
Data Type            int
Units                TBD
Range                TBD
Default              0
Change               Dynamic
Versions Affected    v0.6.5 and later
==================== ==================

zfs_deadman_enabled
~~~~~~~~~~~~~~~~~~~

When a pool sync operation takes longer than zfs_deadman_synctime_ms
milliseconds, a "slow spa_sync" message is logged to the debug log (see
`zfs_dbgmsg_enable <#zfs-dbgmsg-enable>`__). If ``zfs_deadman_enabled``
is set to 1, then all pending IO operations are also checked and if any
haven't completed within zfs_deadman_synctime_ms milliseconds, a "SLOW
IO" message is logged to the debug log and a "deadman" system event (see
zpool events command) with the details of the hung IO is posted.

=================== =====================================
zfs_deadman_enabled Notes
=================== =====================================
Tags                `debug <#debug>`__
When to change      To disable logging of slow I/O
Data Type           boolean
Range               0=do not log slow I/O, 1=log slow I/O
Default             1
Change              Dynamic
Versions Affected   v0.8.0
=================== =====================================

zfs_deadman_checktime_ms
~~~~~~~~~~~~~~~~~~~~~~~~

Once a pool sync operation has taken longer than
`zfs_deadman_synctime_ms <#zfs-deadman-synctime-ms>`__ milliseconds,
continue to check for slow operations every
`zfs_deadman_checktime_ms <#zfs-deadman-synctime-ms>`__ milliseconds.

======================== =======================
zfs_deadman_checktime_ms Notes
======================== =======================
Tags                     `debug <#debug>`__
When to change           When debugging slow I/O
Data Type                ulong
Units                    milliseconds
Range                    1 to ULONG_MAX
Default                  60,000 (1 minute)
Change                   Dynamic
Versions Affected        v0.8.0
======================== =======================

zfs_deadman_ziotime_ms
~~~~~~~~~~~~~~~~~~~~~~

When an individual I/O takes longer than ``zfs_deadman_ziotime_ms``
milliseconds, then the operation is considered to be "hung". If
`zfs_deadman_enabled <#zfs-deadman-enabled>`__ is set then the deadman
behaviour is invoked as described by the
`zfs_deadman_failmode <#zfs-deadman-failmode>`__ option.

====================== ====================
zfs_deadman_ziotime_ms Notes
====================== ====================
Tags                   `debug <#debug>`__
When to change         Testing ABD features
Data Type              ulong
Units                  milliseconds
Range                  1 to ULONG_MAX
Default                300,000 (5 minutes)
Change                 Dynamic
Versions Affected      v0.8.0
====================== ====================

zfs_deadman_synctime_ms
~~~~~~~~~~~~~~~~~~~~~~~

The I/O deadman timer expiration time has two meanings

1. determines when the ``spa_deadman()`` logic should fire, indicating
   the txg sync has not completed in a timely manner
2. determines if an I/O is considered "hung"

In version v0.8.0, any I/O that has not completed in
``zfs_deadman_synctime_ms`` is considered "hung" resulting in one of
three behaviors controlled by the
`zfs_deadman_failmode <#zfs-deadman-failmode>`__ parameter.

``zfs_deadman_synctime_ms`` takes effect if
`zfs_deadman_enabled <#zfs-deadman-enabled>`__ = 1.

======================= =======================
zfs_deadman_synctime_ms Notes
======================= =======================
Tags                    `debug <#debug>`__
When to change          When debugging slow I/O
Data Type               ulong
Units                   milliseconds
Range                   1 to ULONG_MAX
Default                 600,000 (10 minutes)
Change                  Dynamic
Versions Affected       v0.6.5 and later
======================= =======================

zfs_deadman_failmode
~~~~~~~~~~~~~~~~~~~~

zfs_deadman_failmode controls the behavior of the I/O deadman timer when
it detects a "hung" I/O. Valid values are:

-  wait - Wait for the "hung" I/O (default)
-  continue - Attempt to recover from a "hung" I/O
-  panic - Panic the system

==================== ===============================================
zfs_deadman_failmode Notes
==================== ===============================================
Tags                 `debug <#debug>`__
When to change       In some cluster cases, panic can be appropriate
Data Type            string
Range                *wait*, *continue*, or *panic*
Default              wait
Change               Dynamic
Versions Affected    v0.8.0
==================== ===============================================

zfs_dedup_prefetch
~~~~~~~~~~~~~~~~~~

ZFS can prefetch deduplication table (DDT) entries.
``zfs_dedup_prefetch`` allows DDT prefetches to be enabled.

+--------------------+------------------------------------------------+
| zfs_dedup_prefetch | Notes                                          |
+====================+================================================+
| Tags               | `prefetch <#prefetch>`__, `memory <#memory>`__ |
+--------------------+------------------------------------------------+
| When to change     | For systems with limited RAM using the dedup   |
|                    | feature, disabling deduplication table         |
|                    | prefetch can reduce memory pressure            |
+--------------------+------------------------------------------------+
| Data Type          | boolean                                        |
+--------------------+------------------------------------------------+
| Range              | 0=do not prefetch, 1=prefetch dedup table      |
|                    | entries                                        |
+--------------------+------------------------------------------------+
| Default            | 0                                              |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.6.5 and later                               |
+--------------------+------------------------------------------------+

zfs_delete_blocks
~~~~~~~~~~~~~~~~~

``zfs_delete_blocks`` defines a large file for the purposes of delete.
Files containing more than ``zfs_delete_blocks`` will be deleted
asynchronously while smaller files are deleted synchronously. Decreasing
this value reduces the time spent in an ``unlink(2)`` system call at the
expense of a longer delay before the freed space is available.

The ``zfs_delete_blocks`` value is specified in blocks, not bytes. The
size of blocks can vary and is ultimately limited by the filesystem's
recordsize property.

+-------------------+-------------------------------------------------+
| zfs_delete_blocks | Notes                                           |
+===================+=================================================+
| Tags              | `filesystem <#filesystem>`__,                   |
|                   | `delete <#delete>`__                            |
+-------------------+-------------------------------------------------+
| When to change    | If applications delete large files and blocking |
|                   | on ``unlink(2)`` is not desired                 |
+-------------------+-------------------------------------------------+
| Data Type         | ulong                                           |
+-------------------+-------------------------------------------------+
| Units             | blocks                                          |
+-------------------+-------------------------------------------------+
| Range             | 1 to ULONG_MAX                                  |
+-------------------+-------------------------------------------------+
| Default           | 20,480                                          |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

zfs_delay_min_dirty_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ZFS write throttle begins to delay each transaction when the amount
of dirty data reaches the threshold ``zfs_delay_min_dirty_percent`` of
`zfs_dirty_data_max <#zfs-dirty-data-max>`__. This value should be >=
`zfs_vdev_async_write_active_max_dirty_percent <#zfs-vdev-async-write-active-max-dirty-percent>`__.

=========================== ====================================
zfs_delay_min_dirty_percent Notes
=========================== ====================================
Tags                        `write_throttle <#write-throttle>`__
When to change              See section "ZFS TRANSACTION DELAY"
Data Type                   int
Units                       percent
Range                       0 to 100
Default                     60
Change                      Dynamic
Versions Affected           v0.6.4 and later
=========================== ====================================

zfs_delay_scale
~~~~~~~~~~~~~~~

``zfs_delay_scale`` controls how quickly the ZFS write throttle
transaction delay approaches infinity. Larger values cause longer delays
for a given amount of dirty data.

For the smoothest delay, this value should be about 1 billion divided by
the maximum number of write operations per second the pool can sustain.
The throttle will smoothly handle between 10x and 1/10th
``zfs_delay_scale``.

Note: ``zfs_delay_scale`` \*
`zfs_dirty_data_max <#zfs-dirty-data-max>`__ must be < 2^64.

================= ====================================
zfs_delay_scale   Notes
================= ====================================
Tags              `write_throttle <#write-throttle>`__
When to change    See section "ZFS TRANSACTION DELAY"
Data Type         ulong
Units             scalar (nanoseconds)
Range             0 to ULONG_MAX
Default           500,000
Change            Dynamic
Versions Affected v0.6.4 and later
================= ====================================

zfs_dirty_data_max
~~~~~~~~~~~~~~~~~~

``zfs_dirty_data_max`` is the ZFS write throttle dirty space limit. Once
this limit is exceeded, new writes are delayed until space is freed by
writes being committed to the pool.

zfs_dirty_data_max takes precedence over
`zfs_dirty_data_max_percent <#zfs-dirty-data-max-percent>`__.

+--------------------+------------------------------------------------+
| zfs_dirty_data_max | Notes                                          |
+====================+================================================+
| Tags               | `write_throttle <#write-throttle>`__           |
+--------------------+------------------------------------------------+
| When to change     | See section "ZFS TRANSACTION DELAY"            |
+--------------------+------------------------------------------------+
| Data Type          | ulong                                          |
+--------------------+------------------------------------------------+
| Units              | bytes                                          |
+--------------------+------------------------------------------------+
| Range              | 1 to                                           |
|                    | `zfs_d                                         |
|                    | irty_data_max_max <#zfs-dirty-data-max-max>`__ |
+--------------------+------------------------------------------------+
| Default            | 10% of physical RAM                            |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.6.4 and later                               |
+--------------------+------------------------------------------------+

zfs_dirty_data_max_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_dirty_data_max_percent`` is an alternative method of specifying
`zfs_dirty_data_max <#zfs-dirty-data-max>`__, the ZFS write throttle
dirty space limit. Once this limit is exceeded, new writes are delayed
until space is freed by writes being committed to the pool.

`zfs_dirty_data_max <#zfs-dirty-data-max>`__ takes precedence over
``zfs_dirty_data_max_percent``.

+----------------------------+----------------------------------------+
| zfs_dirty_data_max_percent | Notes                                  |
+============================+========================================+
| Tags                       | `write_throttle <#write-throttle>`__   |
+----------------------------+----------------------------------------+
| When to change             | See section "ZFS TRANSACTION DELAY"    |
+----------------------------+----------------------------------------+
| Data Type                  | int                                    |
+----------------------------+----------------------------------------+
| Units                      | percent                                |
+----------------------------+----------------------------------------+
| Range                      | 1 to 100                               |
+----------------------------+----------------------------------------+
| Default                    | 10% of physical RAM                    |
+----------------------------+----------------------------------------+
| Change                     | Prior to zfs module load or a memory   |
|                            | hot plug event                         |
+----------------------------+----------------------------------------+
| Versions Affected          | v0.6.4 and later                       |
+----------------------------+----------------------------------------+

zfs_dirty_data_max_max
~~~~~~~~~~~~~~~~~~~~~~

``zfs_dirty_data_max_max`` is the maximum allowable value of
`zfs_dirty_data_max <#zfs-dirty-data-max>`__.

``zfs_dirty_data_max_max`` takes precedence over
`zfs_dirty_data_max_max_percent <#zfs-dirty-data-max-max-percent>`__.

====================== ====================================
zfs_dirty_data_max_max Notes
====================== ====================================
Tags                   `write_throttle <#write-throttle>`__
When to change         See section "ZFS TRANSACTION DELAY"
Data Type              ulong
Units                  bytes
Range                  1 to physical RAM size
Default                25% of physical RAM
Change                 Prior to zfs module load
Versions Affected      v0.6.4 and later
====================== ====================================

zfs_dirty_data_max_max_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_dirty_data_max_max_percent`` an alternative to
`zfs_dirty_data_max_max <#zfs-dirty-data-max-max>`__ for setting the
maximum allowable value of `zfs_dirty_data_max <#zfs-dirty-data-max>`__

`zfs_dirty_data_max_max <#zfs-dirty-data-max-max>`__ takes precedence
over ``zfs_dirty_data_max_max_percent``

============================== ====================================
zfs_dirty_data_max_max_percent Notes
============================== ====================================
Tags                           `write_throttle <#write-throttle>`__
When to change                 See section "ZFS TRANSACTION DELAY"
Data Type                      int
Units                          percent
Range                          1 to 100
Default                        25% of physical RAM
Change                         Prior to zfs module load
Versions Affected              v0.6.4 and later
============================== ====================================

zfs_dirty_data_sync
~~~~~~~~~~~~~~~~~~~

When there is at least ``zfs_dirty_data_sync`` dirty data, a transaction
group sync is started. This allows a transaction group sync to occur
more frequently than the transaction group timeout interval (see
`zfs_txg_timeout <#zfs-txg-timeout>`__) when there is dirty data to be
written.

+---------------------+-----------------------------------------------+
| zfs_dirty_data_sync | Notes                                         |
+=====================+===============================================+
| Tags                | `write_throttle <#write-throttle>`__,         |
|                     | `ZIO_scheduler <#ZIO-scheduler>`__            |
+---------------------+-----------------------------------------------+
| When to change      | TBD                                           |
+---------------------+-----------------------------------------------+
| Data Type           | ulong                                         |
+---------------------+-----------------------------------------------+
| Units               | bytes                                         |
+---------------------+-----------------------------------------------+
| Range               | 1 to ULONG_MAX                                |
+---------------------+-----------------------------------------------+
| Default             | 67,108,864 (64 MiB)                           |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.6.4 through v0.8.x, deprecation planned    |
|                     | for v2                                        |
+---------------------+-----------------------------------------------+

zfs_dirty_data_sync_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When there is at least ``zfs_dirty_data_sync_percent`` of
`zfs_dirty_data_max <#zfs-dirty-data-max>`__ dirty data, a transaction
group sync is started. This allows a transaction group sync to occur
more frequently than the transaction group timeout interval (see
`zfs_txg_timeout <#zfs-txg-timeout>`__) when there is dirty data to be
written.

+-----------------------------+---------------------------------------+
| zfs_dirty_data_sync_percent | Notes                                 |
+=============================+=======================================+
| Tags                        | `write_throttle <#write-throttle>`__, |
|                             | `ZIO_scheduler <#ZIO-scheduler>`__    |
+-----------------------------+---------------------------------------+
| When to change              | TBD                                   |
+-----------------------------+---------------------------------------+
| Data Type                   | int                                   |
+-----------------------------+---------------------------------------+
| Units                       | percent                               |
+-----------------------------+---------------------------------------+
| Range                       | 1 to                                  |
|                             | `zfs_vdev_async_write_ac              |
|                             | tive_min_dirty_percent <#zfs_vdev_asy |
|                             | nc_write_active_min_dirty_percent>`__ |
+-----------------------------+---------------------------------------+
| Default                     | 20                                    |
+-----------------------------+---------------------------------------+
| Change                      | Dynamic                               |
+-----------------------------+---------------------------------------+
| Versions Affected           | planned for v2, deprecates            |
|                             | `zfs_dirt                             |
|                             | y_data_sync <#zfs-dirty-data-sync>`__ |
+-----------------------------+---------------------------------------+

zfs_fletcher_4_impl
~~~~~~~~~~~~~~~~~~~

Fletcher-4 is the default checksum algorithm for metadata and data. When
the zfs kernel module is loaded, a set of microbenchmarks are run to
determine the fastest algorithm for the current hardware. The
``zfs_fletcher_4_impl`` parameter allows a specific implementation to be
specified other than the default (fastest). Selectors other than
*fastest* and *scalar* require instruction set extensions to be
available and will only appear if ZFS detects their presence. The
*scalar* implementation works on all processors.

The results of the microbenchmark are visible in the
``/proc/spl/kstat/zfs/fletcher_4_bench`` file. Larger numbers indicate
better performance. Since ZFS is processor endian-independent, the
microbenchmark is run against both big and little-endian transformation.

+---------------------+-----------------------------------------------+
| zfs_fletcher_4_impl | Notes                                         |
+=====================+===============================================+
| Tags                | `CPU <#cpu>`__, `checksum <#checksum>`__      |
+---------------------+-----------------------------------------------+
| When to change      | Testing Fletcher-4 algorithms                 |
+---------------------+-----------------------------------------------+
| Data Type           | string                                        |
+---------------------+-----------------------------------------------+
| Range               | *fastest*, *scalar*, *superscalar*,           |
|                     | *superscalar4*, *sse2*, *ssse3*, *avx2*,      |
|                     | *avx512f*, or *aarch64_neon* depending on     |
|                     | hardware support                              |
+---------------------+-----------------------------------------------+
| Default             | fastest                                       |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.7.0 and later                              |
+---------------------+-----------------------------------------------+

zfs_free_bpobj_enabled
~~~~~~~~~~~~~~~~~~~~~~

The processing of the free_bpobj object can be enabled by
``zfs_free_bpobj_enabled``

+------------------------+--------------------------------------------+
| zfs_free_bpobj_enabled | Notes                                      |
+========================+============================================+
| Tags                   | `delete <#delete>`__                       |
+------------------------+--------------------------------------------+
| When to change         | If there's a problem with processing       |
|                        | free_bpobj (e.g. i/o error or bug)         |
+------------------------+--------------------------------------------+
| Data Type              | boolean                                    |
+------------------------+--------------------------------------------+
| Range                  | 0=do not process free_bpobj objects,       |
|                        | 1=process free_bpobj objects               |
+------------------------+--------------------------------------------+
| Default                | 1                                          |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | v0.7.0 and later                           |
+------------------------+--------------------------------------------+

zfs_free_max_blocks
~~~~~~~~~~~~~~~~~~~

``zfs_free_max_blocks`` sets the maximum number of blocks to be freed in
a single transaction group (txg). For workloads that delete (free) large
numbers of blocks in a short period of time, the processing of the frees
can negatively impact other operations, including txg commits.
``zfs_free_max_blocks`` acts as a limit to reduce the impact.

+---------------------+-----------------------------------------------+
| zfs_free_max_blocks | Notes                                         |
+=====================+===============================================+
| Tags                | `filesystem <#filesystem>`__,                 |
|                     | `delete <#delete>`__                          |
+---------------------+-----------------------------------------------+
| When to change      | For workloads that delete large files,        |
|                     | ``zfs_free_max_blocks`` can be adjusted to    |
|                     | meet performance requirements while reducing  |
|                     | the impacts of deletion                       |
+---------------------+-----------------------------------------------+
| Data Type           | ulong                                         |
+---------------------+-----------------------------------------------+
| Units               | blocks                                        |
+---------------------+-----------------------------------------------+
| Range               | 1 to ULONG_MAX                                |
+---------------------+-----------------------------------------------+
| Default             | 100,000                                       |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.7.0 and later                              |
+---------------------+-----------------------------------------------+

zfs_vdev_async_read_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Maximum asynchronous read I/Os active to each device.

+--------------------------------+------------------------------------+
| zfs_vdev_async_read_max_active | Notes                              |
+================================+====================================+
| Tags                           | `vdev <#vdev>`__,                  |
|                                | `ZIO_scheduler <#zio-scheduler>`__ |
+--------------------------------+------------------------------------+
| When to change                 | See `ZFS I/O                       |
|                                | Scheduler <https://github.com/zfs  |
|                                | onlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------------+------------------------------------+
| Data Type                      | uint32                             |
+--------------------------------+------------------------------------+
| Units                          | I/O operations                     |
+--------------------------------+------------------------------------+
| Range                          | 1 to                               |
|                                | `zfs_vdev_ma                       |
|                                | x_active <#zfs-vdev-max-active>`__ |
+--------------------------------+------------------------------------+
| Default                        | 3                                  |
+--------------------------------+------------------------------------+
| Change                         | Dynamic                            |
+--------------------------------+------------------------------------+
| Versions Affected              | v0.6.4 and later                   |
+--------------------------------+------------------------------------+

zfs_vdev_async_read_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minimum asynchronous read I/Os active to each device.

+--------------------------------+------------------------------------+
| zfs_vdev_async_read_min_active | Notes                              |
+================================+====================================+
| Tags                           | `vdev <#vdev>`__,                  |
|                                | `ZIO_scheduler <#zio-scheduler>`__ |
+--------------------------------+------------------------------------+
| When to change                 | See `ZFS I/O                       |
|                                | Scheduler <https://github.com/zfs  |
|                                | onlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------------+------------------------------------+
| Data Type                      | uint32                             |
+--------------------------------+------------------------------------+
| Units                          | I/O operations                     |
+--------------------------------+------------------------------------+
| Range                          | 1 to                               |
|                                | (                                  |
|                                | `zfs_vdev_async_read_max_active <# |
|                                | zfs_vdev_async_read_max_active>`__ |
|                                | - 1)                               |
+--------------------------------+------------------------------------+
| Default                        | 1                                  |
+--------------------------------+------------------------------------+
| Change                         | Dynamic                            |
+--------------------------------+------------------------------------+
| Versions Affected              | v0.6.4 and later                   |
+--------------------------------+------------------------------------+

zfs_vdev_async_write_active_max_dirty_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the amount of dirty data exceeds the threshold
``zfs_vdev_async_write_active_max_dirty_percent`` of
`zfs_dirty_data_max <#zfs-dirty-data-max>`__ dirty data, then
`zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__
is used to limit active async writes. If the dirty data is between
`zfs_vdev_async_write_active_min_dirty_percent <#zfs-vdev-async-write-active-min-dirty-percent>`__
and ``zfs_vdev_async_write_active_max_dirty_percent``, the active I/O
limit is linearly interpolated between
`zfs_vdev_async_write_min_active <#zfs-vdev-async-write-min-active>`__
and
`zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__

+----------------------------------+----------------------------------+
| zfs_vdev_asyn                    | Notes                            |
| c_write_active_max_dirty_percent |                                  |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `Z                               |
|                                  | IO_scheduler <#zio-scheduler>`__ |
+----------------------------------+----------------------------------+
| When to change                   | See `ZFS I/O                     |
|                                  | Sch                              |
|                                  | eduler <https://github.com/zfson |
|                                  | linux/zfs/wiki/ZIO-Scheduler>`__ |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | percent of                       |
|                                  | `zfs_dirty_d                     |
|                                  | ata_max <#zfs-dirty-data-max>`__ |
+----------------------------------+----------------------------------+
| Range                            | 0 to 100                         |
+----------------------------------+----------------------------------+
| Default                          | 60                               |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.6.4 and later                 |
+----------------------------------+----------------------------------+

zfs_vdev_async_write_active_min_dirty_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the amount of dirty data is between
``zfs_vdev_async_write_active_min_dirty_percent`` and
`zfs_vdev_async_write_active_max_dirty_percent <#zfs-vdev-async-write-active-max-dirty-percent>`__
of `zfs_dirty_data_max <#zfs-dirty-data-max>`__, the active I/O limit is
linearly interpolated between
`zfs_vdev_async_write_min_active <#zfs-vdev-async-write-min-active>`__
and
`zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__

+----------------------------------+----------------------------------+
| zfs_vdev_asyn                    | Notes                            |
| c_write_active_min_dirty_percent |                                  |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `Z                               |
|                                  | IO_scheduler <#zio-scheduler>`__ |
+----------------------------------+----------------------------------+
| When to change                   | See `ZFS I/O                     |
|                                  | Sch                              |
|                                  | eduler <https://github.com/zfson |
|                                  | linux/zfs/wiki/ZIO-Scheduler>`__ |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | percent of zfs_dirty_data_max    |
+----------------------------------+----------------------------------+
| Range                            | 0 to                             |
|                                  | (`z                              |
|                                  | fs_vdev_async_write_active_max_d |
|                                  | irty_percent <#zfs_vdev_async_wr |
|                                  | ite_active_max_dirty_percent>`__ |
|                                  | - 1)                             |
+----------------------------------+----------------------------------+
| Default                          | 30                               |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.6.4 and later                 |
+----------------------------------+----------------------------------+

zfs_vdev_async_write_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_async_write_max_active`` sets the maximum asynchronous write
I/Os active to each device.

+---------------------------------+-----------------------------------+
| zfs_vdev_async_write_max_active | Notes                             |
+=================================+===================================+
| Tags                            | `vdev <#vdev>`__,                 |
|                                 | `                                 |
|                                 | ZIO_scheduler <#zio-scheduler>`__ |
+---------------------------------+-----------------------------------+
| When to change                  | See `ZFS I/O                      |
|                                 | S                                 |
|                                 | cheduler <https://github.com/zfso |
|                                 | nlinux/zfs/wiki/ZIO-Scheduler>`__ |
+---------------------------------+-----------------------------------+
| Data Type                       | uint32                            |
+---------------------------------+-----------------------------------+
| Units                           | I/O operations                    |
+---------------------------------+-----------------------------------+
| Range                           | 1 to                              |
|                                 | `zfs_vdev_max                     |
|                                 | _active <#zfs-vdev-max-active>`__ |
+---------------------------------+-----------------------------------+
| Default                         | 10                                |
+---------------------------------+-----------------------------------+
| Change                          | Dynamic                           |
+---------------------------------+-----------------------------------+
| Versions Affected               | v0.6.4 and later                  |
+---------------------------------+-----------------------------------+

zfs_vdev_async_write_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_async_write_min_active`` sets the minimum asynchronous write
I/Os active to each device.

Lower values are associated with better latency on rotational media but
poorer resilver performance. The default value of 2 was chosen as a
compromise. A value of 3 has been shown to improve resilver performance
further at a cost of further increasing latency.

+---------------------------------+-----------------------------------+
| zfs_vdev_async_write_min_active | Notes                             |
+=================================+===================================+
| Tags                            | `vdev <#vdev>`__,                 |
|                                 | `                                 |
|                                 | ZIO_scheduler <#zio-scheduler>`__ |
+---------------------------------+-----------------------------------+
| When to change                  | See `ZFS I/O                      |
|                                 | S                                 |
|                                 | cheduler <https://github.com/zfso |
|                                 | nlinux/zfs/wiki/ZIO-Scheduler>`__ |
+---------------------------------+-----------------------------------+
| Data Type                       | uint32                            |
+---------------------------------+-----------------------------------+
| Units                           | I/O operations                    |
+---------------------------------+-----------------------------------+
| Range                           | 1 to                              |
|                                 | `zfs                              |
|                                 | _vdev_async_write_max_active <#zf |
|                                 | s_vdev_async_write_max_active>`__ |
+---------------------------------+-----------------------------------+
| Default                         | 1 for v0.6.x, 2 for v0.7.0 and    |
|                                 | later                             |
+---------------------------------+-----------------------------------+
| Change                          | Dynamic                           |
+---------------------------------+-----------------------------------+
| Versions Affected               | v0.6.4 and later                  |
+---------------------------------+-----------------------------------+

zfs_vdev_max_active
~~~~~~~~~~~~~~~~~~~

The maximum number of I/Os active to each device. Ideally,
``zfs_vdev_max_active`` >= the sum of each queue's max_active.

Once queued to the device, the ZFS I/O scheduler is no longer able to
prioritize I/O operations. The underlying device drivers have their own
scheduler and queue depth limits. Values larger than the device's
maximum queue depth can have the affect of increased latency as the I/Os
are queued in the intervening device driver layers.

+---------------------+-----------------------------------------------+
| zfs_vdev_max_active | Notes                                         |
+=====================+===============================================+
| Tags                | `vdev <#vdev>`__,                             |
|                     | `ZIO_scheduler <#zio-scheduler>`__            |
+---------------------+-----------------------------------------------+
| When to change      | See `ZFS I/O                                  |
|                     | Scheduler <https://git                        |
|                     | hub.com/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+---------------------+-----------------------------------------------+
| Data Type           | uint32                                        |
+---------------------+-----------------------------------------------+
| Units               | I/O operations                                |
+---------------------+-----------------------------------------------+
| Range               | sum of each queue's min_active to UINT32_MAX  |
+---------------------+-----------------------------------------------+
| Default             | 1,000                                         |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.6.4 and later                              |
+---------------------+-----------------------------------------------+

zfs_vdev_scrub_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_scrub_max_active`` sets the maximum scrub or scan read I/Os
active to each device.

+---------------------------+-----------------------------------------+
| zfs_vdev_scrub_max_active | Notes                                   |
+===========================+=========================================+
| Tags                      | `vdev <#vdev>`__,                       |
|                           | `ZIO_scheduler <#zio-scheduler>`__,     |
|                           | `scrub <#scrub>`__,                     |
|                           | `resilver <#resilver>`__                |
+---------------------------+-----------------------------------------+
| When to change            | See `ZFS I/O                            |
|                           | Scheduler <https://github.co            |
|                           | m/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+---------------------------+-----------------------------------------+
| Data Type                 | uint32                                  |
+---------------------------+-----------------------------------------+
| Units                     | I/O operations                          |
+---------------------------+-----------------------------------------+
| Range                     | 1 to                                    |
|                           | `zfs_vd                                 |
|                           | ev_max_active <#zfs-vdev-max-active>`__ |
+---------------------------+-----------------------------------------+
| Default                   | 2                                       |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | v0.6.4 and later                        |
+---------------------------+-----------------------------------------+

zfs_vdev_scrub_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_scrub_min_active`` sets the minimum scrub or scan read I/Os
active to each device.

+---------------------------+-----------------------------------------+
| zfs_vdev_scrub_min_active | Notes                                   |
+===========================+=========================================+
| Tags                      | `vdev <#vdev>`__,                       |
|                           | `ZIO_scheduler <#zio-scheduler>`__,     |
|                           | `scrub <#scrub>`__,                     |
|                           | `resilver <#resilver>`__                |
+---------------------------+-----------------------------------------+
| When to change            | See `ZFS I/O                            |
|                           | Scheduler <https://github.co            |
|                           | m/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+---------------------------+-----------------------------------------+
| Data Type                 | uint32                                  |
+---------------------------+-----------------------------------------+
| Units                     | I/O operations                          |
+---------------------------+-----------------------------------------+
| Range                     | 1 to                                    |
|                           | `zfs_vdev_scrub_max                     |
|                           | _active <#zfs-vdev-scrub-max-active>`__ |
+---------------------------+-----------------------------------------+
| Default                   | 1                                       |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | v0.6.4 and later                        |
+---------------------------+-----------------------------------------+

zfs_vdev_sync_read_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Maximum synchronous read I/Os active to each device.

+-------------------------------+-------------------------------------+
| zfs_vdev_sync_read_max_active | Notes                               |
+===============================+=====================================+
| Tags                          | `vdev <#vdev>`__,                   |
|                               | `ZIO_scheduler <#zio-scheduler>`__  |
+-------------------------------+-------------------------------------+
| When to change                | See `ZFS I/O                        |
|                               | Scheduler <https://github.com/zf    |
|                               | sonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+-------------------------------+-------------------------------------+
| Data Type                     | uint32                              |
+-------------------------------+-------------------------------------+
| Units                         | I/O operations                      |
+-------------------------------+-------------------------------------+
| Range                         | 1 to                                |
|                               | `zfs_vdev_m                         |
|                               | ax_active <#zfs-vdev-max-active>`__ |
+-------------------------------+-------------------------------------+
| Default                       | 10                                  |
+-------------------------------+-------------------------------------+
| Change                        | Dynamic                             |
+-------------------------------+-------------------------------------+
| Versions Affected             | v0.6.4 and later                    |
+-------------------------------+-------------------------------------+

zfs_vdev_sync_read_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_sync_read_min_active`` sets the minimum synchronous read I/Os
active to each device.

+-------------------------------+-------------------------------------+
| zfs_vdev_sync_read_min_active | Notes                               |
+===============================+=====================================+
| Tags                          | `vdev <#vdev>`__,                   |
|                               | `ZIO_scheduler <#zio-scheduler>`__  |
+-------------------------------+-------------------------------------+
| When to change                | See `ZFS I/O                        |
|                               | Scheduler <https://github.com/zf    |
|                               | sonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+-------------------------------+-------------------------------------+
| Data Type                     | uint32                              |
+-------------------------------+-------------------------------------+
| Units                         | I/O operations                      |
+-------------------------------+-------------------------------------+
| Range                         | 1 to                                |
|                               | `zfs_vdev_sync_read_max_active      |
|                               | <#zfs-vdev-sync-read-max-active>`__ |
+-------------------------------+-------------------------------------+
| Default                       | 10                                  |
+-------------------------------+-------------------------------------+
| Change                        | Dynamic                             |
+-------------------------------+-------------------------------------+
| Versions Affected             | v0.6.4 and later                    |
+-------------------------------+-------------------------------------+

zfs_vdev_sync_write_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_sync_write_max_active`` sets the maximum synchronous write
I/Os active to each device.

+--------------------------------+------------------------------------+
| zfs_vdev_sync_write_max_active | Notes                              |
+================================+====================================+
| Tags                           | `vdev <#vdev>`__,                  |
|                                | `ZIO_scheduler <#zio-scheduler>`__ |
+--------------------------------+------------------------------------+
| When to change                 | See `ZFS I/O                       |
|                                | Scheduler <https://github.com/zfs  |
|                                | onlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------------+------------------------------------+
| Data Type                      | uint32                             |
+--------------------------------+------------------------------------+
| Units                          | I/O operations                     |
+--------------------------------+------------------------------------+
| Range                          | 1 to                               |
|                                | `zfs_vdev_ma                       |
|                                | x_active <#zfs-vdev-max-active>`__ |
+--------------------------------+------------------------------------+
| Default                        | 10                                 |
+--------------------------------+------------------------------------+
| Change                         | Dynamic                            |
+--------------------------------+------------------------------------+
| Versions Affected              | v0.6.4 and later                   |
+--------------------------------+------------------------------------+

zfs_vdev_sync_write_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_sync_write_min_active`` sets the minimum synchronous write
I/Os active to each device.

+--------------------------------+------------------------------------+
| zfs_vdev_sync_write_min_active | Notes                              |
+================================+====================================+
| Tags                           | `vdev <#vdev>`__,                  |
|                                | `ZIO_scheduler <#zio-scheduler>`__ |
+--------------------------------+------------------------------------+
| When to change                 | See `ZFS I/O                       |
|                                | Scheduler <https://github.com/zfs  |
|                                | onlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------------+------------------------------------+
| Data Type                      | uint32                             |
+--------------------------------+------------------------------------+
| Units                          | I/O operations                     |
+--------------------------------+------------------------------------+
| Range                          | 1 to                               |
|                                | `zfs_vdev_sync_write_max_active <# |
|                                | zfs_vdev_sync_write_max_active>`__ |
+--------------------------------+------------------------------------+
| Default                        | 10                                 |
+--------------------------------+------------------------------------+
| Change                         | Dynamic                            |
+--------------------------------+------------------------------------+
| Versions Affected              | v0.6.4 and later                   |
+--------------------------------+------------------------------------+

zfs_vdev_queue_depth_pct
~~~~~~~~~~~~~~~~~~~~~~~~

Maximum number of queued allocations per top-level vdev expressed as a
percentage of
`zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__.
This allows the system to detect devices that are more capable of
handling allocations and to allocate more blocks to those devices. It
also allows for dynamic allocation distribution when devices are
imbalanced as fuller devices will tend to be slower than empty devices.
Once the queue depth reaches (``zfs_vdev_queue_depth_pct`` \*
`zfs_vdev_async_write_max_active <#zfs-vdev-async-write-max-active>`__ /
100) then allocator will stop allocating blocks on that top-level device
and switch to the next.

See also `zio_dva_throttle_enabled <#zio-dva-throttle-enabled>`__

+--------------------------+------------------------------------------+
| zfs_vdev_queue_depth_pct | Notes                                    |
+==========================+==========================================+
| Tags                     | `vdev <#vdev>`__,                        |
|                          | `ZIO_scheduler <#zio-scheduler>`__       |
+--------------------------+------------------------------------------+
| When to change           | See `ZFS I/O                             |
|                          | Scheduler <https://github.c              |
|                          | om/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------+------------------------------------------+
| Data Type                | uint32                                   |
+--------------------------+------------------------------------------+
| Units                    | I/O operations                           |
+--------------------------+------------------------------------------+
| Range                    | 1 to UINT32_MAX                          |
+--------------------------+------------------------------------------+
| Default                  | 1,000                                    |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.0 and later                         |
+--------------------------+------------------------------------------+

zfs_disable_dup_eviction
~~~~~~~~~~~~~~~~~~~~~~~~

Disable duplicate buffer eviction from ARC.

+--------------------------+------------------------------------------+
| zfs_disable_dup_eviction | Notes                                    |
+==========================+==========================================+
| Tags                     | `ARC <#arc>`__, `dedup <#dedup>`__       |
+--------------------------+------------------------------------------+
| When to change           | TBD                                      |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=duplicate buffers can be evicted, 1=do |
|                          | not evict duplicate buffers              |
+--------------------------+------------------------------------------+
| Default                  | 0                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.6.5, deprecated in v0.7.0             |
+--------------------------+------------------------------------------+

zfs_expire_snapshot
~~~~~~~~~~~~~~~~~~~

Snapshots of filesystems are normally automounted under the filesystem's
``.zfs/snapshot`` subdirectory. When not in use, snapshots are unmounted
after zfs_expire_snapshot seconds.

+---------------------+-----------------------------------------------+
| zfs_expire_snapshot | Notes                                         |
+=====================+===============================================+
| Tags                | `filesystem <#filesystem>`__,                 |
|                     | `snapshot <#snapshot>`__                      |
+---------------------+-----------------------------------------------+
| When to change      | TBD                                           |
+---------------------+-----------------------------------------------+
| Data Type           | int                                           |
+---------------------+-----------------------------------------------+
| Units               | seconds                                       |
+---------------------+-----------------------------------------------+
| Range               | 0 disables automatic unmounting, maximum time |
|                     | is INT_MAX                                    |
+---------------------+-----------------------------------------------+
| Default             | 300                                           |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.6.1 and later                              |
+---------------------+-----------------------------------------------+

zfs_admin_snapshot
~~~~~~~~~~~~~~~~~~

Allow the creation, removal, or renaming of entries in the
``.zfs/snapshot`` subdirectory to cause the creation, destruction, or
renaming of snapshots. When enabled this functionality works both
locally and over NFS exports which have the "no_root_squash" option set.

+--------------------+------------------------------------------------+
| zfs_admin_snapshot | Notes                                          |
+====================+================================================+
| Tags               | `filesystem <#filesystem>`__,                  |
|                    | `snapshot <#snapshot>`__                       |
+--------------------+------------------------------------------------+
| When to change     | TBD                                            |
+--------------------+------------------------------------------------+
| Data Type          | boolean                                        |
+--------------------+------------------------------------------------+
| Range              | 0=do not allow snapshot manipulation via the   |
|                    | filesystem, 1=allow snapshot manipulation via  |
|                    | the filesystem                                 |
+--------------------+------------------------------------------------+
| Default            | 1                                              |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.6.5 and later                               |
+--------------------+------------------------------------------------+

zfs_flags
~~~~~~~~~

Set additional debugging flags (see
`zfs_dbgmsg_enable <#zfs-dbgmsg-enable>`__)

+------------+---------------------------+---------------------------+
| flag value | symbolic name             | description               |
+============+===========================+===========================+
| 0x1        | ZFS_DEBUG_DPRINTF         | Enable dprintf entries in |
|            |                           | the debug log             |
+------------+---------------------------+---------------------------+
| 0x2        | ZFS_DEBUG_DBUF_VERIFY     | Enable extra dnode        |
|            |                           | verifications             |
+------------+---------------------------+---------------------------+
| 0x4        | ZFS_DEBUG_DNODE_VERIFY    | Enable extra dnode        |
|            |                           | verifications             |
+------------+---------------------------+---------------------------+
| 0x8        | ZFS_DEBUG_SNAPNAMES       | Enable snapshot name      |
|            |                           | verification              |
+------------+---------------------------+---------------------------+
| 0x10       | ZFS_DEBUG_MODIFY          | Check for illegally       |
|            |                           | modified ARC buffers      |
+------------+---------------------------+---------------------------+
| 0x20       | ZFS_DEBUG_SPA             | Enable spa_dbgmsg entries |
|            |                           | in the debug log          |
+------------+---------------------------+---------------------------+
| 0x40       | ZFS_DEBUG_ZIO_FREE        | Enable verification of    |
|            |                           | block frees               |
+------------+---------------------------+---------------------------+
| 0x80       | Z                         | Enable extra spacemap     |
|            | FS_DEBUG_HISTOGRAM_VERIFY | histogram verifications   |
+------------+---------------------------+---------------------------+
| 0x100      | ZFS_DEBUG_METASLAB_VERIFY | Verify space accounting   |
|            |                           | on disk matches in-core   |
|            |                           | range_trees               |
+------------+---------------------------+---------------------------+
| 0x200      | ZFS_DEBUG_SET_ERROR       | Enable SET_ERROR and      |
|            |                           | dprintf entries in the    |
|            |                           | debug log                 |
+------------+---------------------------+---------------------------+

+-------------------+-------------------------------------------------+
| zfs_flags         | Notes                                           |
+===================+=================================================+
| Tags              | `debug <#debug>`__                              |
+-------------------+-------------------------------------------------+
| When to change    | When debugging ZFS                              |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Default           | 0 no debug flags set, for debug builds: all     |
|                   | except ZFS_DEBUG_DPRINTF and ZFS_DEBUG_SPA      |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.4 and later                                |
+-------------------+-------------------------------------------------+

zfs_free_leak_on_eio
~~~~~~~~~~~~~~~~~~~~

If destroy encounters an I/O error (EIO) while reading metadata (eg
indirect blocks), space referenced by the missing metadata cannot be
freed. Normally, this causes the background destroy to become "stalled",
as the destroy is unable to make forward progress. While in this stalled
state, all remaining space to free from the error-encountering
filesystem is temporarily leaked. Set ``zfs_free_leak_on_eio = 1`` to
ignore the EIO, permanently leak the space from indirect blocks that can
not be read, and continue to free everything else that it can.

The default, stalling behavior is useful if the storage partially fails
(eg some but not all I/Os fail), and then later recovers. In this case,
we will be able to continue pool operations while it is partially
failed, and when it recovers, we can continue to free the space, with no
leaks. However, note that this case is rare.

Typically pools either:

1. fail completely (but perhaps temporarily (eg a top-level vdev going
   offline)

2. have localized, permanent errors (eg disk returns the wrong data due
   to bit flip or firmware bug)

In case (1), the ``zfs_free_leak_on_eio`` setting does not matter
because the pool will be suspended and the sync thread will not be able
to make forward progress. In case (2), because the error is permanent,
the best effort do is leak the minimum amount of space. Therefore, it is
reasonable for ``zfs_free_leak_on_eio`` be set, but by default the more
conservative approach is taken, so that there is no possibility of
leaking space in the "partial temporary" failure case.

+----------------------+----------------------------------------------+
| zfs_free_leak_on_eio | Notes                                        |
+======================+==============================================+
| Tags                 | `debug <#debug>`__                           |
+----------------------+----------------------------------------------+
| When to change       | When debugging I/O errors during destroy     |
+----------------------+----------------------------------------------+
| Data Type            | boolean                                      |
+----------------------+----------------------------------------------+
| Range                | 0=normal behavior, 1=ignore error and        |
|                      | permanently leak space                       |
+----------------------+----------------------------------------------+
| Default              | 0                                            |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | v0.6.5 and later                             |
+----------------------+----------------------------------------------+

zfs_free_min_time_ms
~~~~~~~~~~~~~~~~~~~~

During a ``zfs destroy`` operation using ``feature@async_destroy`` a
minimum of ``zfs_free_min_time_ms`` time will be spent working on
freeing blocks per txg commit.

==================== ==============================
zfs_free_min_time_ms Notes
==================== ==============================
Tags                 `delete <#delete>`__
When to change       TBD
Data Type            int
Units                milliseconds
Range                1 to (zfs_txg_timeout \* 1000)
Default              1,000
Change               Dynamic
Versions Affected    v0.6.0 and later
==================== ==============================

zfs_immediate_write_sz
~~~~~~~~~~~~~~~~~~~~~~

If a pool does not have a log device, data blocks equal to or larger
than ``zfs_immediate_write_sz`` are treated as if the dataset being
written to had the property setting ``logbias=throughput``

Terminology note: ``logbias=throughput`` writes the blocks in "indirect
mode" to the ZIL where the data is written to the pool and a pointer to
the data is written to the ZIL.

+------------------------+--------------------------------------------+
| zfs_immediate_write_sz | Notes                                      |
+========================+============================================+
| Tags                   | `ZIL <#zil>`__                             |
+------------------------+--------------------------------------------+
| When to change         | TBD                                        |
+------------------------+--------------------------------------------+
| Data Type              | long                                       |
+------------------------+--------------------------------------------+
| Units                  | bytes                                      |
+------------------------+--------------------------------------------+
| Range                  | 512 to 16,777,216 (valid block sizes)      |
+------------------------+--------------------------------------------+
| Default                | 32,768 (32 KiB)                            |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Verification           | Data blocks that exceed                    |
|                        | ``zfs_immediate_write_sz`` or are written  |
|                        | as ``logbias=throughput`` increment the    |
|                        | ``zil_itx_indirect_count`` entry in        |
|                        | ``/proc/spl/kstat/zfs/zil``                |
+------------------------+--------------------------------------------+
| Versions Affected      | all                                        |
+------------------------+--------------------------------------------+

zfs_max_recordsize
~~~~~~~~~~~~~~~~~~

ZFS supports logical record (block) sizes from 512 bytes to 16 MiB. The
benefits of larger blocks, and thus larger average I/O sizes, can be
weighed against the cost of copy-on-write of large block to modify one
byte. Additionally, very large blocks can have a negative impact on both
I/O latency at the device level and the memory allocator. The
``zfs_max_recordsize`` parameter limits the upper bound of the dataset
volblocksize and recordsize properties.

Larger blocks can be created by enabling ``zpool`` ``large_blocks``
feature and changing this ``zfs_max_recordsize``. Pools with larger
blocks can always be imported and used, regardless of the value of
``zfs_max_recordsize``.

For 32-bit systems, ``zfs_max_recordsize`` also limits the size of
kernel virtual memory caches used in the ZFS I/O pipeline (``zio_buf_*``
and ``zio_data_buf_*``).

See also the ``zpool`` ``large_blocks`` feature.

+--------------------+------------------------------------------------+
| zfs_max_recordsize | Notes                                          |
+====================+================================================+
| Tags               | `filesystem <#filesystem>`__,                  |
|                    | `memory <#memory>`__, `volume <#volume>`__     |
+--------------------+------------------------------------------------+
| When to change     | To create datasets with larger volblocksize or |
|                    | recordsize                                     |
+--------------------+------------------------------------------------+
| Data Type          | int                                            |
+--------------------+------------------------------------------------+
| Units              | bytes                                          |
+--------------------+------------------------------------------------+
| Range              | 512 to 16,777,216 (valid block sizes)          |
+--------------------+------------------------------------------------+
| Default            | 1,048,576                                      |
+--------------------+------------------------------------------------+
| Change             | Dynamic, set prior to creating volumes or      |
|                    | changing filesystem recordsize                 |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.6.5 and later                               |
+--------------------+------------------------------------------------+

zfs_mdcomp_disable
~~~~~~~~~~~~~~~~~~

``zfs_mdcomp_disable`` allows metadata compression to be disabled.

================== ===============================================
zfs_mdcomp_disable Notes
================== ===============================================
Tags               `CPU <#cpu>`__, `metadata <#metadata>`__
When to change     When CPU cycles cost less than I/O
Data Type          boolean
Range              0=compress metadata, 1=do not compress metadata
Default            0
Change             Dynamic
Versions Affected  from v0.6.0 to v0.8.0
================== ===============================================

zfs_metaslab_fragmentation_threshold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Allow metaslabs to keep their active state as long as their
fragmentation percentage is less than or equal to this value. When
writing, an active metaslab whose fragmentation percentage exceeds
``zfs_metaslab_fragmentation_threshold`` is avoided allowing metaslabs
with less fragmentation to be preferred.

Metaslab fragmentation is used to calculate the overall pool
``fragmentation`` property value. However, individual metaslab
fragmentation levels are observable using the ``zdb`` with the ``-mm``
option.

``zfs_metaslab_fragmentation_threshold`` works at the metaslab level and
each top-level vdev has approximately
`metaslabs_per_vdev <#metaslabs-per-vdev>`__ metaslabs. See also
`zfs_mg_fragmentation_threshold <#zfs-mg-fragmentation-threshold>`__

+----------------------------------+----------------------------------+
| zfs_metaslab_fragmentation_thresh| Notes                            |
| old                              |                                  |
+==================================+==================================+
| Tags                             | `allocation <#allocation>`__,    |
|                                  | `fr                              |
|                                  | agmentation <#fragmentation>`__, |
|                                  | `vdev <#vdev>`__                 |
+----------------------------------+----------------------------------+
| When to change                   | Testing metaslab allocation      |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | percent                          |
+----------------------------------+----------------------------------+
| Range                            | 1 to 100                         |
+----------------------------------+----------------------------------+
| Default                          | 70                               |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.6.4 and later                 |
+----------------------------------+----------------------------------+

zfs_mg_fragmentation_threshold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Metaslab groups (top-level vdevs) are considered eligible for
allocations if their fragmentation percentage metric is less than or
equal to ``zfs_mg_fragmentation_threshold``. If a metaslab group exceeds
this threshold then it will be skipped unless all metaslab groups within
the metaslab class have also crossed the
``zfs_mg_fragmentation_threshold`` threshold.

+--------------------------------+------------------------------------+
| zfs_mg_fragmentation_threshold | Notes                              |
+================================+====================================+
| Tags                           | `allocation <#allocation>`__,      |
|                                | `                                  |
|                                | fragmentation <#fragmentation>`__, |
|                                | `vdev <#vdev>`__                   |
+--------------------------------+------------------------------------+
| When to change                 | Testing metaslab allocation        |
+--------------------------------+------------------------------------+
| Data Type                      | int                                |
+--------------------------------+------------------------------------+
| Units                          | percent                            |
+--------------------------------+------------------------------------+
| Range                          | 1 to 100                           |
+--------------------------------+------------------------------------+
| Default                        | 85                                 |
+--------------------------------+------------------------------------+
| Change                         | Dynamic                            |
+--------------------------------+------------------------------------+
| Versions Affected              | v0.6.4 and later                   |
+--------------------------------+------------------------------------+

zfs_mg_noalloc_threshold
~~~~~~~~~~~~~~~~~~~~~~~~

Metaslab groups (top-level vdevs) with free space percentage greater
than ``zfs_mg_noalloc_threshold`` are eligible for new allocations. If a
metaslab group's free space is less than or equal to the threshold, the
allocator avoids allocating to that group unless all groups in the pool
have reached the threshold. Once all metaslab groups have reached the
threshold, all metaslab groups are allowed to accept allocations. The
default value of 0 disables the feature and causes all metaslab groups
to be eligible for allocations.

This parameter allows one to deal with pools having heavily imbalanced
vdevs such as would be the case when a new vdev has been added. Setting
the threshold to a non-zero percentage will stop allocations from being
made to vdevs that aren't filled to the specified percentage and allow
lesser filled vdevs to acquire more allocations than they otherwise
would under the older ``zfs_mg_alloc_failures`` facility.

+--------------------------+------------------------------------------+
| zfs_mg_noalloc_threshold | Notes                                    |
+==========================+==========================================+
| Tags                     | `allocation <#allocation>`__,            |
|                          | `fragmentation <#fragmentation>`__,      |
|                          | `vdev <#vdev>`__                         |
+--------------------------+------------------------------------------+
| When to change           | To force rebalancing as top-level vdevs  |
|                          | are added or expanded                    |
+--------------------------+------------------------------------------+
| Data Type                | int                                      |
+--------------------------+------------------------------------------+
| Units                    | percent                                  |
+--------------------------+------------------------------------------+
| Range                    | 0 to 100                                 |
+--------------------------+------------------------------------------+
| Default                  | 0 (disabled)                             |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.0 and later                         |
+--------------------------+------------------------------------------+

zfs_multihost_history
~~~~~~~~~~~~~~~~~~~~~

The pool ``multihost`` multimodifier protection (MMP) subsystem can
record historical updates in the
``/proc/spl/kstat/zfs/POOL_NAME/multihost`` file for debugging purposes.
The number of lines of history is determined by zfs_multihost_history.

===================== ====================================
zfs_multihost_history Notes
===================== ====================================
Tags                  `MMP <#mmp>`__, `import <#import>`__
When to change        When testing multihost feature
Data Type             int
Units                 lines
Range                 0 to INT_MAX
Default               0
Change                Dynamic
Versions Affected     v0.7.0 and later
===================== ====================================

zfs_multihost_interval
~~~~~~~~~~~~~~~~~~~~~~

``zfs_multihost_interval`` controls the frequency of multihost writes
performed by the pool multihost multimodifier protection (MMP)
subsystem. The multihost write period is (``zfs_multihost_interval`` /
number of leaf-vdevs) milliseconds. Thus on average a multihost write
will be issued for each leaf vdev every ``zfs_multihost_interval``
milliseconds. In practice, the observed period can vary with the I/O
load and this observed value is the delay which is stored in the
uberblock.

On import the multihost activity check waits a minimum amount of time
determined by (``zfs_multihost_interval`` \*
`zfs_multihost_import_intervals <#zfs-multihost-import-intervals>`__)
with a lower bound of 1 second. The activity check time may be further
extended if the value of mmp delay found in the best uberblock indicates
actual multihost updates happened at longer intervals than
``zfs_multihost_interval``

Note: the multihost protection feature applies to storage devices that
can be shared between multiple systems.

+------------------------+--------------------------------------------+
| zfs_multihost_interval | Notes                                      |
+========================+============================================+
| Tags                   | `MMP <#mmp>`__, `import <#import>`__,      |
|                        | `vdev <#vdev>`__                           |
+------------------------+--------------------------------------------+
| When to change         | To optimize pool import time against       |
|                        | possibility of simultaneous import by      |
|                        | another system                             |
+------------------------+--------------------------------------------+
| Data Type              | ulong                                      |
+------------------------+--------------------------------------------+
| Units                  | milliseconds                               |
+------------------------+--------------------------------------------+
| Range                  | 100 to ULONG_MAX                           |
+------------------------+--------------------------------------------+
| Default                | 1000                                       |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | v0.7.0 and later                           |
+------------------------+--------------------------------------------+

zfs_multihost_import_intervals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_multihost_import_intervals`` controls the duration of the activity
test on pool import for the multihost multimodifier protection (MMP)
subsystem. The activity test can be expected to take a minimum time of
(``zfs_multihost_import_interval``\ s \*
`zfs_multihost_interval <#zfs-multihost-interval>`__ \* ``random(25%)``)
milliseconds. The random period of up to 25% improves simultaneous
import detection. For example, if two hosts are rebooted at the same
time and automatically attempt to import the pool, then is is highly
probable that one host will win.

Smaller values of ``zfs_multihost_import_intervals`` reduces the import
time but increases the risk of failing to detect an active pool. The
total activity check time is never allowed to drop below one second.

Note: the multihost protection feature applies to storage devices that
can be shared between multiple systems.

============================== ====================================
zfs_multihost_import_intervals Notes
============================== ====================================
Tags                           `MMP <#mmp>`__, `import <#import>`__
When to change                 TBD
Data Type                      uint
Units                          intervals
Range                          1 to UINT_MAX
Default                        10
Change                         Dynamic
Versions Affected              v0.7.0 and later
============================== ====================================

zfs_multihost_fail_intervals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_multihost_fail_intervals`` controls the behavior of the pool when
write failures are detected in the multihost multimodifier protection
(MMP) subsystem.

If ``zfs_multihost_fail_intervals = 0`` then multihost write failures
are ignored. The write failures are reported to the ZFS event daemon
(``zed``) which can take action such as suspending the pool or offlining
a device.

| If ``zfs_multihost_fail_intervals > 0`` then sequential multihost
  write failures will cause the pool to be suspended. This occurs when
  (``zfs_multihost_fail_intervals`` \*
  `zfs_multihost_interval <#zfs-multihost-interval>`__) milliseconds
  have passed since the last successful multihost write.
| This guarantees the activity test will see multihost writes if the
  pool is attempted to be imported by another system.

============================ ====================================
zfs_multihost_fail_intervals Notes
============================ ====================================
Tags                         `MMP <#mmp>`__, `import <#import>`__
When to change               TBD
Data Type                    uint
Units                        intervals
Range                        0 to UINT_MAX
Default                      5
Change                       Dynamic
Versions Affected            v0.7.0 and later
============================ ====================================

zfs_delays_per_second
~~~~~~~~~~~~~~~~~~~~~

The ZFS Event Daemon (zed) processes events from ZFS. However, it can be
overwhelmed by high rates of error reports which can be generated by
failing, high-performance devices. ``zfs_delays_per_second`` limits the
rate of delay events reported to zed.

+-----------------------+---------------------------------------------+
| zfs_delays_per_second | Notes                                       |
+=======================+=============================================+
| Tags                  | `zed <#zed>`__, `delay <#delay>`__          |
+-----------------------+---------------------------------------------+
| When to change        | If processing delay events at a higher rate |
|                       | is desired                                  |
+-----------------------+---------------------------------------------+
| Data Type             | uint                                        |
+-----------------------+---------------------------------------------+
| Units                 | events per second                           |
+-----------------------+---------------------------------------------+
| Range                 | 0 to UINT_MAX                               |
+-----------------------+---------------------------------------------+
| Default               | 20                                          |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.7.7 and later                            |
+-----------------------+---------------------------------------------+

zfs_checksums_per_second
~~~~~~~~~~~~~~~~~~~~~~~~

The ZFS Event Daemon (zed) processes events from ZFS. However, it can be
overwhelmed by high rates of error reports which can be generated by
failing, high-performance devices. ``zfs_checksums_per_second`` limits
the rate of checksum events reported to zed.

Note: do not set this value lower than the SERD limit for ``checksum``
in zed. By default, ``checksum_N`` = 10 and ``checksum_T`` = 10 minutes,
resulting in a practical lower limit of 1.

+--------------------------+------------------------------------------+
| zfs_checksums_per_second | Notes                                    |
+==========================+==========================================+
| Tags                     | `zed <#zed>`__, `checksum <#checksum>`__ |
+--------------------------+------------------------------------------+
| When to change           | If processing checksum error events at a |
|                          | higher rate is desired                   |
+--------------------------+------------------------------------------+
| Data Type                | uint                                     |
+--------------------------+------------------------------------------+
| Units                    | events per second                        |
+--------------------------+------------------------------------------+
| Range                    | 0 to UINT_MAX                            |
+--------------------------+------------------------------------------+
| Default                  | 20                                       |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.7 and later                         |
+--------------------------+------------------------------------------+

zfs_no_scrub_io
~~~~~~~~~~~~~~~

When ``zfs_no_scrub_io = 1`` scrubs do not actually scrub data and
simply doing a metadata crawl of the pool instead.

================= ===============================================
zfs_no_scrub_io   Notes
================= ===============================================
Tags              `scrub <#scrub>`__
When to change    Testing scrub feature
Data Type         boolean
Range             0=perform scrub I/O, 1=do not perform scrub I/O
Default           0
Change            Dynamic
Versions Affected v0.6.0 and later
================= ===============================================

zfs_no_scrub_prefetch
~~~~~~~~~~~~~~~~~~~~~

When ``zfs_no_scrub_prefetch = 1``, prefetch is disabled for scrub I/Os.

+-----------------------+-----------------------------------------------------+
| zfs_no_scrub_prefetch | Notes                                               |
+=======================+=====================================================+
| Tags                  | `prefetch <#prefetch>`__, `scrub <#scrub>`__        |
+-----------------------+-----------------------------------------------------+
| When to change        | Testing scrub feature                               |
+-----------------------+-----------------------------------------------------+
| Data Type             | boolean                                             |
+-----------------------+-----------------------------------------------------+
| Range                 | 0=prefetch scrub I/Os, 1=do not prefetch scrub I/Os |
+-----------------------+-----------------------------------------------------+
| Default               | 0                                                   |
+-----------------------+-----------------------------------------------------+
| Change                | Dynamic                                             |
+-----------------------+-----------------------------------------------------+
| Versions Affected     | v0.6.4 and later                                    |
+-----------------------+-----------------------------------------------------+

zfs_nocacheflush
~~~~~~~~~~~~~~~~

ZFS uses barriers (volatile cache flush commands) to ensure data is
committed to permanent media by devices. This ensures consistent
on-media state for devices where caches are volatile (eg HDDs).

For devices with nonvolatile caches, the cache flush operation can be a
no-op. However, in some RAID arrays, cache flushes can cause the entire
cache to be flushed to the backing devices.

To ensure on-media consistency, keep cache flush enabled.

+-------------------+-------------------------------------------------+
| zfs_nocacheflush  | Notes                                           |
+===================+=================================================+
| Tags              | `disks <#disks>`__                              |
+-------------------+-------------------------------------------------+
| When to change    | If the storage device has nonvolatile cache,    |
|                   | then disabling cache flush can save the cost of |
|                   | occasional cache flush commands                 |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=send cache flush commands, 1=do not send      |
|                   | cache flush commands                            |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

zfs_nopwrite_enabled
~~~~~~~~~~~~~~~~~~~~

The NOP-write feature is enabled by default when a
crytographically-secure checksum algorithm is in use by the dataset.
``zfs_nopwrite_enabled`` allows the NOP-write feature to be completely
disabled.

+----------------------+----------------------------------------------+
| zfs_nopwrite_enabled | Notes                                        |
+======================+==============================================+
| Tags                 | `checksum <#checksum>`__, `debug <#debug>`__ |
+----------------------+----------------------------------------------+
| When to change       | TBD                                          |
+----------------------+----------------------------------------------+
| Data Type            | boolean                                      |
+----------------------+----------------------------------------------+
| Range                | 0=disable NOP-write feature, 1=enable        |
|                      | NOP-write feature                            |
+----------------------+----------------------------------------------+
| Default              | 1                                            |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | v0.6.0 and later                             |
+----------------------+----------------------------------------------+

zfs_dmu_offset_next_sync
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_dmu_offset_next_sync`` enables forcing txg sync to find holes.
This causes ZFS to act like older versions when ``SEEK_HOLE`` or
``SEEK_DATA`` flags are used: when a dirty dnode causes txgs to be
synced so the previous data can be found.

+--------------------------+------------------------------------------+
| zfs_dmu_offset_next_sync | Notes                                    |
+==========================+==========================================+
| Tags                     | `DMU <#dmu>`__                           |
+--------------------------+------------------------------------------+
| When to change           | TBD                                      |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=do not force txg sync to find holes,   |
|                          | 1=force txg sync to find holes           |
+--------------------------+------------------------------------------+
| Default                  | 0                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.0 and later                         |
+--------------------------+------------------------------------------+

zfs_pd_bytes_max
~~~~~~~~~~~~~~~~

``zfs_pd_bytes_max`` limits the number of bytes prefetched during a pool
traversal (eg ``zfs send`` or other data crawling operations). These
prefetches are referred to as "prescient prefetches" and are always 100%
hit rate. The traversal operations do not use the default data or
metadata prefetcher.

================= ==========================================
zfs_pd_bytes_max  Notes
================= ==========================================
Tags              `prefetch <#prefetch>`__, `send <#send>`__
When to change    TBD
Data Type         int32
Units             bytes
Range             0 to INT32_MAX
Default           52,428,800 (50 MiB)
Change            Dynamic
Versions Affected TBD
================= ==========================================

zfs_per_txg_dirty_frees_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_per_txg_dirty_frees_percent`` as a percentage of
`zfs_dirty_data_max <#zfs-dirty-data-max>`__ controls the percentage of
dirtied blocks from frees in one txg. After the threshold is crossed,
additional dirty blocks from frees wait until the next txg. Thus, when
deleting large files, filling consecutive txgs with deletes/frees, does
not throttle other, perhaps more important, writes.

A side effect of this throttle can impact ``zfs receive`` workloads that
contain a large number of frees and the
`ignore_hole_birth <#ignore-hole-birth>`__ optimization is disabled. The
symptom is that the receive workload causes an increase in the frequency
of txg commits. The frequency of txg commits is observable via the
``otime`` column of ``/proc/spl/kstat/zfs/POOLNAME/txgs``. Since txg
commits also flush data from volatile caches in HDDs to media, HDD
performance can be negatively impacted. Also, since the frees do not
consume much bandwidth over the pipe, the pipe can appear to stall. Thus
the overall progress of receives is slower than expected.

A value of zero will disable this throttle.

+---------------------------------+-----------------------------------+
| zfs_per_txg_dirty_frees_percent | Notes                             |
+=================================+===================================+
| Tags                            | `delete <#delete>`__              |
+---------------------------------+-----------------------------------+
| When to change                  | For ``zfs receive`` workloads,    |
|                                 | consider increasing or disabling. |
|                                 | See section `ZFS I/O              |
|                                 | S                                 |
|                                 | cheduler <https://github.com/zfso |
|                                 | nlinux/zfs/wiki/ZIO-Scheduler>`__ |
+---------------------------------+-----------------------------------+
| Data Type                       | ulong                             |
+---------------------------------+-----------------------------------+
| Units                           | percent                           |
+---------------------------------+-----------------------------------+
| Range                           | 0 to 100                          |
+---------------------------------+-----------------------------------+
| Default                         | 30                                |
+---------------------------------+-----------------------------------+
| Change                          | Dynamic                           |
+---------------------------------+-----------------------------------+
| Versions Affected               | v0.7.0 and later                  |
+---------------------------------+-----------------------------------+

zfs_prefetch_disable
~~~~~~~~~~~~~~~~~~~~

``zfs_prefetch_disable`` controls the predictive prefetcher.

Note that it leaves "prescient" prefetch (eg prefetch for ``zfs send``)
intact (see `zfs_pd_bytes_max <#zfs-pd-bytes-max>`__)

+----------------------+----------------------------------------------+
| zfs_prefetch_disable | Notes                                        |
+======================+==============================================+
| Tags                 | `prefetch <#prefetch>`__                     |
+----------------------+----------------------------------------------+
| When to change       | In some case where the workload is           |
|                      | completely random reads, overall performance |
|                      | can be better if prefetch is disabled        |
+----------------------+----------------------------------------------+
| Data Type            | boolean                                      |
+----------------------+----------------------------------------------+
| Range                | 0=prefetch enabled, 1=prefetch disabled      |
+----------------------+----------------------------------------------+
| Default              | 0                                            |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Verification         | prefetch efficacy is observed by             |
|                      | ``arcstat``, ``arc_summary``, and the        |
|                      | relevant entries in                          |
|                      | ``/proc/spl/kstat/zfs/arcstats``             |
+----------------------+----------------------------------------------+
| Versions Affected    | all                                          |
+----------------------+----------------------------------------------+

zfs_read_chunk_size
~~~~~~~~~~~~~~~~~~~

``zfs_read_chunk_size`` is the limit for ZFS filesystem reads. If an
application issues a ``read()`` larger than ``zfs_read_chunk_size``,
then the ``read()`` is divided into multiple operations no larger than
``zfs_read_chunk_size``

=================== ============================
zfs_read_chunk_size Notes
=================== ============================
Tags                `filesystem <#filesystem>`__
When to change      TBD
Data Type           ulong
Units               bytes
Range               512 to ULONG_MAX
Default             1,048,576
Change              Dynamic
Versions Affected   all
=================== ============================

zfs_read_history
~~~~~~~~~~~~~~~~

Historical statistics for the last ``zfs_read_history`` reads are
available in ``/proc/spl/kstat/zfs/POOL_NAME/reads``

================= =================================
zfs_read_history  Notes
================= =================================
Tags              `debug <#debug>`__
When to change    To observe read operation details
Data Type         int
Units             lines
Range             0 to INT_MAX
Default           0
Change            Dynamic
Versions Affected all
================= =================================

zfs_read_history_hits
~~~~~~~~~~~~~~~~~~~~~

When `zfs_read_history <#zfs-read-history>`__\ ``> 0``,
zfs_read_history_hits controls whether ARC hits are displayed in the
read history file, ``/proc/spl/kstat/zfs/POOL_NAME/reads``

+-----------------------+---------------------------------------------+
| zfs_read_history_hits | Notes                                       |
+=======================+=============================================+
| Tags                  | `debug <#debug>`__                          |
+-----------------------+---------------------------------------------+
| When to change        | To observe read operation details with ARC  |
|                       | hits                                        |
+-----------------------+---------------------------------------------+
| Data Type             | boolean                                     |
+-----------------------+---------------------------------------------+
| Range                 | 0=do not include data for ARC hits,         |
|                       | 1=include ARC hit data                      |
+-----------------------+---------------------------------------------+
| Default               | 0                                           |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | all                                         |
+-----------------------+---------------------------------------------+

zfs_recover
~~~~~~~~~~~

``zfs_recover`` can be set to true (1) to attempt to recover from
otherwise-fatal errors, typically caused by on-disk corruption. When
set, calls to ``zfs_panic_recover()`` will turn into warning messages
rather than calling ``panic()``

+-------------------+-------------------------------------------------+
| zfs_recover       | Notes                                           |
+===================+=================================================+
| Tags              | `import <#import>`__                            |
+-------------------+-------------------------------------------------+
| When to change    | zfs_recover should only be used as a last       |
|                   | resort, as it typically results in leaked       |
|                   | space, or worse                                 |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=normal operation, 1=attempt recovery zpool    |
|                   | import                                          |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Verification      | check output of ``dmesg`` and other logs for    |
|                   | details                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.4 or later                                 |
+-------------------+-------------------------------------------------+

zfs_resilver_min_time_ms
~~~~~~~~~~~~~~~~~~~~~~~~

Resilvers are processed by the sync thread in syncing context. While
resilvering, ZFS spends at least ``zfs_resilver_min_time_ms`` time
working on a resilver between txg commits.

The `zfs_txg_timeout <#zfs-txg-timeout>`__ tunable sets a nominal
timeout value for the txg commits. By default, this timeout is 5 seconds
and the ``zfs_resilver_min_time_ms`` is 3 seconds. However, many
variables contribute to changing the actual txg times. The measured txg
interval is observed as the ``otime`` column (in nanoseconds) in the
``/proc/spl/kstat/zfs/POOL_NAME/txgs`` file.

See also `zfs_txg_timeout <#zfs-txg-timeout>`__ and
`zfs_scan_min_time_ms <#zfs-scan-min-time-ms>`__

+--------------------------+------------------------------------------+
| zfs_resilver_min_time_ms | Notes                                    |
+==========================+==========================================+
| Tags                     | `resilver <#resilver>`__                 |
+--------------------------+------------------------------------------+
| When to change           | In some resilvering cases, increasing    |
|                          | ``zfs_resilver_min_time_ms`` can result  |
|                          | in faster completion                     |
+--------------------------+------------------------------------------+
| Data Type                | int                                      |
+--------------------------+------------------------------------------+
| Units                    | milliseconds                             |
+--------------------------+------------------------------------------+
| Range                    | 1 to                                     |
|                          | `zfs_txg_timeout <#zfs-txg-timeout>`__   |
|                          | converted to milliseconds                |
+--------------------------+------------------------------------------+
| Default                  | 3,000                                    |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | all                                      |
+--------------------------+------------------------------------------+

zfs_scan_min_time_ms
~~~~~~~~~~~~~~~~~~~~

Scrubs are processed by the sync thread in syncing context. While
scrubbing, ZFS spends at least ``zfs_scan_min_time_ms`` time working on
a scrub between txg commits.

See also `zfs_txg_timeout <#zfs-txg-timeout>`__ and
`zfs_resilver_min_time_ms <#zfs-resilver-min-time-ms>`__

+----------------------+----------------------------------------------+
| zfs_scan_min_time_ms | Notes                                        |
+======================+==============================================+
| Tags                 | `scrub <#scrub>`__                           |
+----------------------+----------------------------------------------+
| When to change       | In some scrub cases, increasing              |
|                      | ``zfs_scan_min_time_ms`` can result in       |
|                      | faster completion                            |
+----------------------+----------------------------------------------+
| Data Type            | int                                          |
+----------------------+----------------------------------------------+
| Units                | milliseconds                                 |
+----------------------+----------------------------------------------+
| Range                | 1 to `zfs_txg_timeout <#zfs-txg-timeout>`__  |
|                      | converted to milliseconds                    |
+----------------------+----------------------------------------------+
| Default              | 1,000                                        |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | all                                          |
+----------------------+----------------------------------------------+

zfs_scan_checkpoint_intval
~~~~~~~~~~~~~~~~~~~~~~~~~~

To preserve progress across reboots the sequential scan algorithm
periodically needs to stop metadata scanning and issue all the
verifications I/Os to disk every ``zfs_scan_checkpoint_intval`` seconds.

========================== ============================================
zfs_scan_checkpoint_intval Notes
========================== ============================================
Tags                       `resilver <#resilver>`__, `scrub <#scrub>`__
When to change             TBD
Data Type                  int
Units                      seconds
Range                      1 to INT_MAX
Default                    7,200 (2 hours)
Change                     Dynamic
Versions Affected          v0.8.0 and later
========================== ============================================

zfs_scan_fill_weight
~~~~~~~~~~~~~~~~~~~~

This tunable affects how scrub and resilver I/O segments are ordered. A
higher number indicates that we care more about how filled in a segment
is, while a lower number indicates we care more about the size of the
extent without considering the gaps within a segment.

==================== ============================================
zfs_scan_fill_weight Notes
==================== ============================================
Tags                 `resilver <#resilver>`__, `scrub <#scrub>`__
When to change       Testing sequential scrub and resilver
Data Type            int
Units                scalar
Range                0 to INT_MAX
Default              3
Change               Prior to zfs module load
Versions Affected    v0.8.0 and later
==================== ============================================

zfs_scan_issue_strategy
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_scan_issue_strategy`` controls the order of data verification
while scrubbing or resilvering.

+-------+-------------------------------------------------------------+
| value | description                                                 |
+=======+=============================================================+
| 0     | fs will use strategy 1 during normal verification and       |
|       | strategy 2 while taking a checkpoint                        |
+-------+-------------------------------------------------------------+
| 1     | data is verified as sequentially as possible, given the     |
|       | amount of memory reserved for scrubbing (see                |
|       | `zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__). This   |
|       | can improve scrub performance if the pool's data is heavily |
|       | fragmented.                                                 |
+-------+-------------------------------------------------------------+
| 2     | the largest mostly-contiguous chunk of found data is        |
|       | verified first. By deferring scrubbing of small segments,   |
|       | we may later find adjacent data to coalesce and increase    |
|       | the segment size.                                           |
+-------+-------------------------------------------------------------+

======================= ============================================
zfs_scan_issue_strategy Notes
======================= ============================================
Tags                    `resilver <#resilver>`__, `scrub <#scrub>`__
When to change          TBD
Data Type               enum
Range                   0 to 2
Default                 0
Change                  Dynamic
Versions Affected       TBD
======================= ============================================

zfs_scan_legacy
~~~~~~~~~~~~~~~

Setting ``zfs_scan_legacy = 1`` enables the legacy scan and scrub
behavior instead of the newer sequential behavior.

+-------------------+-------------------------------------------------+
| zfs_scan_legacy   | Notes                                           |
+===================+=================================================+
| Tags              | `resilver <#resilver>`__, `scrub <#scrub>`__    |
+-------------------+-------------------------------------------------+
| When to change    | In some cases, the new scan mode can consumer   |
|                   | more memory as it collects and sorts I/Os;      |
|                   | using the legacy algorithm can be more memory   |
|                   | efficient at the expense of HDD read efficiency |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=use new method: scrubs and resilvers will     |
|                   | gather metadata in memory before issuing        |
|                   | sequential I/O, 1=use legacy algorithm will be  |
|                   | used where I/O is initiated as soon as it is    |
|                   | discovered                                      |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic, however changing to 0 does not affect  |
|                   | in-progress scrubs or resilvers                 |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.8.0 and later                                |
+-------------------+-------------------------------------------------+

zfs_scan_max_ext_gap
~~~~~~~~~~~~~~~~~~~~

``zfs_scan_max_ext_gap`` limits the largest gap in bytes between scrub
and resilver I/Os that will still be considered sequential for sorting
purposes.

+----------------------+----------------------------------------------+
| zfs_scan_max_ext_gap | Notes                                        |
+======================+==============================================+
| Tags                 | `resilver <#resilver>`__, `scrub <#scrub>`__ |
+----------------------+----------------------------------------------+
| When to change       | TBD                                          |
+----------------------+----------------------------------------------+
| Data Type            | ulong                                        |
+----------------------+----------------------------------------------+
| Units                | bytes                                        |
+----------------------+----------------------------------------------+
| Range                | 512 to ULONG_MAX                             |
+----------------------+----------------------------------------------+
| Default              | 2,097,152 (2 MiB)                            |
+----------------------+----------------------------------------------+
| Change               | Dynamic, however changing to 0 does not      |
|                      | affect in-progress scrubs or resilvers       |
+----------------------+----------------------------------------------+
| Versions Affected    | v0.8.0 and later                             |
+----------------------+----------------------------------------------+

zfs_scan_mem_lim_fact
~~~~~~~~~~~~~~~~~~~~~

``zfs_scan_mem_lim_fact`` limits the maximum fraction of RAM used for
I/O sorting by sequential scan algorithm. When the limit is reached
scanning metadata is stopped and data verification I/O is started. Data
verification I/O continues until the memory used by the sorting
algorithm drops below below
`zfs_scan_mem_lim_soft_fact <#zfs-scan-mem-lim-soft-fact>`__

Memory used by the sequential scan algorithm can be observed as the kmem
sio_cache. This is visible from procfs as
``grep sio_cache /proc/slabinfo`` and can be monitored using
slab-monitoring tools such as ``slabtop``

+-----------------------+---------------------------------------------+
| zfs_scan_mem_lim_fact | Notes                                       |
+=======================+=============================================+
| Tags                  | `memory <#memory>`__,                       |
|                       | `resilver <#resilver>`__,                   |
|                       | `scrub <#scrub>`__                          |
+-----------------------+---------------------------------------------+
| When to change        | TBD                                         |
+-----------------------+---------------------------------------------+
| Data Type             | int                                         |
+-----------------------+---------------------------------------------+
| Units                 | divisor of physical RAM                     |
+-----------------------+---------------------------------------------+
| Range                 | TBD                                         |
+-----------------------+---------------------------------------------+
| Default               | 20 (physical RAM / 20 or 5%)                |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.8.0 and later                            |
+-----------------------+---------------------------------------------+

zfs_scan_mem_lim_soft_fact
~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_scan_mem_lim_soft_fact`` sets the fraction of the hard limit,
`zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__, used to determined
the RAM soft limit for I/O sorting by the sequential scan algorithm.
After `zfs_scan_mem_lim_fact <#zfs-scan-mem-lim-fact>`__ has been
reached, metadata scanning is stopped until the RAM usage drops below
``zfs_scan_mem_lim_soft_fact``

+----------------------------+----------------------------------------+
| zfs_scan_mem_lim_soft_fact | Notes                                  |
+============================+========================================+
| Tags                       | `resilver <#resilver>`__,              |
|                            | `scrub <#scrub>`__                     |
+----------------------------+----------------------------------------+
| When to change             | TBD                                    |
+----------------------------+----------------------------------------+
| Data Type                  | int                                    |
+----------------------------+----------------------------------------+
| Units                      | divisor of (physical RAM /             |
|                            | `zfs_scan_mem                          |
|                            | _lim_fact <#zfs-scan-mem-lim-fact>`__) |
+----------------------------+----------------------------------------+
| Range                      | 1 to INT_MAX                           |
+----------------------------+----------------------------------------+
| Default                    | 20 (for default                        |
|                            | `zfs_scan_mem                          |
|                            | _lim_fact <#zfs-scan-mem-lim-fact>`__, |
|                            | 0.25% of physical RAM)                 |
+----------------------------+----------------------------------------+
| Change                     | Dynamic                                |
+----------------------------+----------------------------------------+
| Versions Affected          | v0.8.0 and later                       |
+----------------------------+----------------------------------------+

zfs_scan_vdev_limit
~~~~~~~~~~~~~~~~~~~

``zfs_scan_vdev_limit`` is the maximum amount of data that can be
concurrently issued at once for scrubs and resilvers per leaf vdev.
``zfs_scan_vdev_limit`` attempts to strike a balance between keeping the
leaf vdev queues full of I/Os while not overflowing the queues causing
high latency resulting in long txg sync times. While
``zfs_scan_vdev_limit`` represents a bandwidth limit, the existing I/O
limit of `zfs_vdev_scrub_max_active <#zfs-vdev-scrub-max-active>`__
remains in effect, too.

+---------------------+-----------------------------------------------+
| zfs_scan_vdev_limit | Notes                                         |
+=====================+===============================================+
| Tags                | `resilver <#resilver>`__, `scrub <#scrub>`__, |
|                     | `vdev <#vdev>`__                              |
+---------------------+-----------------------------------------------+
| When to change      | TBD                                           |
+---------------------+-----------------------------------------------+
| Data Type           | ulong                                         |
+---------------------+-----------------------------------------------+
| Units               | bytes                                         |
+---------------------+-----------------------------------------------+
| Range               | 512 to ULONG_MAX                              |
+---------------------+-----------------------------------------------+
| Default             | 4,194,304 (4 MiB)                             |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.8.0 and later                              |
+---------------------+-----------------------------------------------+

zfs_send_corrupt_data
~~~~~~~~~~~~~~~~~~~~~

``zfs_send_corrupt_data`` enables ``zfs send`` to send of corrupt data
by ignoring read and checksum errors. The corrupted or unreadable blocks
are replaced with the value ``0x2f5baddb10c`` (ZFS bad block)

+-----------------------+---------------------------------------------+
| zfs_send_corrupt_data | Notes                                       |
+=======================+=============================================+
| Tags                  | `send <#send>`__                            |
+-----------------------+---------------------------------------------+
| When to change        | When data corruption exists and an attempt  |
|                       | to recover at least some data via           |
|                       | ``zfs send`` is needed                      |
+-----------------------+---------------------------------------------+
| Data Type             | boolean                                     |
+-----------------------+---------------------------------------------+
| Range                 | 0=do not send corrupt data, 1=replace       |
|                       | corrupt data with cookie                    |
+-----------------------+---------------------------------------------+
| Default               | 0                                           |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.6.0 and later                            |
+-----------------------+---------------------------------------------+

zfs_sync_pass_deferred_free
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SPA sync process is performed in multiple passes. Once the pass
number reaches ``zfs_sync_pass_deferred_free``, frees are no long
processed and must wait for the next SPA sync.

The ``zfs_sync_pass_deferred_free`` value is expected to be removed as a
tunable once the optimal value is determined during field testing.

The ``zfs_sync_pass_deferred_free`` pass must be greater than 1 to
ensure that regular blocks are not deferred.

=========================== ========================
zfs_sync_pass_deferred_free Notes
=========================== ========================
Tags                        `SPA <#spa>`__
When to change              Testing SPA sync process
Data Type                   int
Units                       SPA sync passes
Range                       1 to INT_MAX
Default                     2
Change                      Dynamic
Versions Affected           all
=========================== ========================

zfs_sync_pass_dont_compress
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SPA sync process is performed in multiple passes. Once the pass
number reaches ``zfs_sync_pass_dont_compress``, data block compression
is no longer processed and must wait for the next SPA sync.

The ``zfs_sync_pass_dont_compress`` value is expected to be removed as a
tunable once the optimal value is determined during field testing.

=========================== ========================
zfs_sync_pass_dont_compress Notes
=========================== ========================
Tags                        `SPA <#spa>`__
When to change              Testing SPA sync process
Data Type                   int
Units                       SPA sync passes
Range                       1 to INT_MAX
Default                     5
Change                      Dynamic
Versions Affected           all
=========================== ========================

zfs_sync_pass_rewrite
~~~~~~~~~~~~~~~~~~~~~

The SPA sync process is performed in multiple passes. Once the pass
number reaches ``zfs_sync_pass_rewrite``, blocks can be split into gang
blocks.

The ``zfs_sync_pass_rewrite`` value is expected to be removed as a
tunable once the optimal value is determined during field testing.

===================== ========================
zfs_sync_pass_rewrite Notes
===================== ========================
Tags                  `SPA <#spa>`__
When to change        Testing SPA sync process
Data Type             int
Units                 SPA sync passes
Range                 1 to INT_MAX
Default               2
Change                Dynamic
Versions Affected     all
===================== ========================

zfs_sync_taskq_batch_pct
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_sync_taskq_batch_pct`` controls the number of threads used by the
DSL pool sync taskq, ``dp_sync_taskq``

+--------------------------+------------------------------------------+
| zfs_sync_taskq_batch_pct | Notes                                    |
+==========================+==========================================+
| Tags                     | `SPA <#spa>`__                           |
+--------------------------+------------------------------------------+
| When to change           | to adjust the number of                  |
|                          | ``dp_sync_taskq`` threads                |
+--------------------------+------------------------------------------+
| Data Type                | int                                      |
+--------------------------+------------------------------------------+
| Units                    | percent of number of online CPUs         |
+--------------------------+------------------------------------------+
| Range                    | 1 to 100                                 |
+--------------------------+------------------------------------------+
| Default                  | 75                                       |
+--------------------------+------------------------------------------+
| Change                   | Prior to zfs module load                 |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.0 and later                         |
+--------------------------+------------------------------------------+

zfs_txg_history
~~~~~~~~~~~~~~~

Historical statistics for the last ``zfs_txg_history`` txg commits are
available in ``/proc/spl/kstat/zfs/POOL_NAME/txgs``

The work required to measure the txg commit (SPA statistics) is low.
However, for debugging purposes, it can be useful to observe the SPA
statistics.

================= ======================================================
zfs_txg_history   Notes
================= ======================================================
Tags              `debug <#debug>`__
When to change    To observe details of SPA sync behavior.
Data Type         int
Units             lines
Range             0 to INT_MAX
Default           0 for version v0.6.0 to v0.7.6, 100 for version v0.8.0
Change            Dynamic
Versions Affected all
================= ======================================================

zfs_txg_timeout
~~~~~~~~~~~~~~~

The open txg is committed to the pool periodically (SPA sync) and
``zfs_txg_timeout`` represents the default target upper limit.

txg commits can occur more frequently and a rapid rate of txg commits
often indicates a busy write workload, quota limits reached, or the free
space is critically low.

Many variables contribute to changing the actual txg times. txg commits
can also take longer than ``zfs_txg_timeout`` if the ZFS write throttle
is not properly tuned or the time to sync is otherwise delayed (eg slow
device). Shorter txg commit intervals can occur due to
`zfs_dirty_data_sync <#zfs-dirty-data-sync>`__ for write-intensive
workloads. The measured txg interval is observed as the ``otime`` column
(in nanoseconds) in the ``/proc/spl/kstat/zfs/POOL_NAME/txgs`` file.

See also `zfs_dirty_data_sync <#zfs-dirty-data-sync>`__ and
`zfs_txg_history <#zfs-txg-history>`__

+-------------------+-------------------------------------------------+
| zfs_txg_timeout   | Notes                                           |
+===================+=================================================+
| Tags              | `SPA <#spa>`__,                                 |
|                   | `ZIO_scheduler <#zio-scheduler>`__              |
+-------------------+-------------------------------------------------+
| When to change    | To optimize the work done by txg commit         |
|                   | relative to the pool requirements. See also     |
|                   | section `ZFS I/O                                |
|                   | Scheduler <https://g                            |
|                   | ithub.com/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Units             | seconds                                         |
+-------------------+-------------------------------------------------+
| Range             | 1 to INT_MAX                                    |
+-------------------+-------------------------------------------------+
| Default           | 5                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

zfs_vdev_aggregation_limit
~~~~~~~~~~~~~~~~~~~~~~~~~~

To reduce IOPs, small, adjacent I/Os can be aggregated (coalesced) into
a large I/O. For reads, aggregations occur across small adjacency gaps.
For writes, aggregation can occur at the ZFS or disk level.
``zfs_vdev_aggregation_limit`` is the upper bound on the size of the
larger, aggregated I/O.

Setting ``zfs_vdev_aggregation_limit = 0`` effectively disables
aggregation by ZFS. However, the block device scheduler can still merge
(aggregate) I/Os. Also, many devices, such as modern HDDs, contain
schedulers that can aggregate I/Os.

In general, I/O aggregation can improve performance for devices, such as
HDDs, where ordering I/O operations for contiguous LBAs is a benefit.
For random access devices, such as SSDs, aggregation might not improve
performance relative to the CPU cycles needed to aggregate. For devices
that represent themselves as having no rotation, the
`zfs_vdev_aggregation_limit_non_rotating <#zfs-vdev-aggregation-limit-non-rotating>`__
parameter is used instead of ``zfs_vdev_aggregation_limit``

+----------------------------+----------------------------------------+
| zfs_vdev_aggregation_limit | Notes                                  |
+============================+========================================+
| Tags                       | `vdev <#vdev>`__,                      |
|                            | `ZIO_scheduler <#zio-scheduler>`__     |
+----------------------------+----------------------------------------+
| When to change             | If the workload does not benefit from  |
|                            | aggregation, the                       |
|                            | ``zfs_vdev_aggregation_limit`` can be  |
|                            | reduced to avoid aggregation attempts  |
+----------------------------+----------------------------------------+
| Data Type                  | int                                    |
+----------------------------+----------------------------------------+
| Units                      | bytes                                  |
+----------------------------+----------------------------------------+
| Range                      | 0 to 1,048,576 (default) or 16,777,216 |
|                            | (if ``zpool`` ``large_blocks`` feature |
|                            | is enabled)                            |
+----------------------------+----------------------------------------+
| Default                    | 1,048,576, or 131,072 for <v0.8        |
+----------------------------+----------------------------------------+
| Change                     | Dynamic                                |
+----------------------------+----------------------------------------+
| Verification               | ZFS aggregation is observed with       |
|                            | ``zpool iostat -r`` and the block      |
|                            | scheduler merging is observed with     |
|                            | ``iostat -x``                          |
+----------------------------+----------------------------------------+
| Versions Affected          | all                                    |
+----------------------------+----------------------------------------+

zfs_vdev_cache_size
~~~~~~~~~~~~~~~~~~~

Note: with the current ZFS code, the vdev cache is not helpful and in
some cases actually harmful. Thusit is disabled by setting the
``zfs_vdev_cache_size = 0``

``zfs_vdev_cache_size`` is the size of the vdev cache.

+---------------------+-----------------------------------------------+
| zfs_vdev_cache_size | Notes                                         |
+=====================+===============================================+
| Tags                | `vdev <#vdev>`__,                             |
|                     | `vdev_cache <#vdev-cache>`__                  |
+---------------------+-----------------------------------------------+
| When to change      | Do not change                                 |
+---------------------+-----------------------------------------------+
| Data Type           | int                                           |
+---------------------+-----------------------------------------------+
| Units               | bytes                                         |
+---------------------+-----------------------------------------------+
| Range               | 0 to MAX_INT                                  |
+---------------------+-----------------------------------------------+
| Default             | 0 (vdev cache is disabled)                    |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Verification        | vdev cache statistics are available in the    |
|                     | ``/proc/spl/kstat/zfs/vdev_cache_stats`` file |
+---------------------+-----------------------------------------------+
| Versions Affected   | all                                           |
+---------------------+-----------------------------------------------+

zfs_vdev_cache_bshift
~~~~~~~~~~~~~~~~~~~~~

Note: with the current ZFS code, the vdev cache is not helpful and in
some cases actually harmful. Thus it is disabled by setting the
`zfs_vdev_cache_size <#zfs-vdev-cache-size>`__ to zero. This related
tunable is, by default, inoperative.

All read I/Os smaller than `zfs_vdev_cache_max <#zfs-vdev-cache-max>`__
are turned into (``1 << zfs_vdev_cache_bshift``) byte reads by the vdev
cache. At most `zfs_vdev_cache_size <#zfs-vdev-cache-size>`__ bytes will
be kept in each vdev's cache.

===================== ==============================================
zfs_vdev_cache_bshift Notes
===================== ==============================================
Tags                  `vdev <#vdev>`__, `vdev_cache <#vdev-cache>`__
When to change        Do not change
Data Type             int
Units                 shift
Range                 1 to INT_MAX
Default               16 (65,536 bytes)
Change                Dynamic
Versions Affected     all
===================== ==============================================

zfs_vdev_cache_max
~~~~~~~~~~~~~~~~~~

Note: with the current ZFS code, the vdev cache is not helpful and in
some cases actually harmful. Thus it is disabled by setting the
`zfs_vdev_cache_size <#zfs-vdev-cache-size>`__ to zero. This related
tunable is, by default, inoperative.

All read I/Os smaller than zfs_vdev_cache_max will be turned into
(``1 <<``\ `zfs_vdev_cache_bshift <#zfs-vdev-cache-bshift>`__ byte reads
by the vdev cache. At most ``zfs_vdev_cache_size`` bytes will be kept in
each vdev's cache.

================== ==============================================
zfs_vdev_cache_max Notes
================== ==============================================
Tags               `vdev <#vdev>`__, `vdev_cache <#vdev-cache>`__
When to change     Do not change
Data Type          int
Units              bytes
Range              512 to INT_MAX
Default            16,384 (16 KiB)
Change             Dynamic
Versions Affected  all
================== ==============================================

zfs_vdev_mirror_rotating_inc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The mirror read algorithm uses current load and an incremental weighting
value to determine the vdev to service a read operation. Lower values
determine the preferred vdev. The weighting value is
``zfs_vdev_mirror_rotating_inc`` for rotating media and
`zfs_vdev_mirror_non_rotating_inc <#zfs-vdev-mirror-non-rotating-inc>`__
for nonrotating media.

Verify the rotational setting described by a block device in sysfs by
observing ``/sys/block/DISK_NAME/queue/rotational``

+------------------------------+--------------------------------------+
| zfs_vdev_mirror_rotating_inc | Notes                                |
+==============================+======================================+
| Tags                         | `vdev <#vdev>`__,                    |
|                              | `mirror <#mirror>`__, `HDD <#hdd>`__ |
+------------------------------+--------------------------------------+
| When to change               | Increasing for mirrors with both     |
|                              | rotating and nonrotating media more  |
|                              | strongly favors the nonrotating      |
|                              | media                                |
+------------------------------+--------------------------------------+
| Data Type                    | int                                  |
+------------------------------+--------------------------------------+
| Units                        | scalar                               |
+------------------------------+--------------------------------------+
| Range                        | 0 to MAX_INT                         |
+------------------------------+--------------------------------------+
| Default                      | 0                                    |
+------------------------------+--------------------------------------+
| Change                       | Dynamic                              |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.7.0 and later                     |
+------------------------------+--------------------------------------+

zfs_vdev_mirror_non_rotating_inc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The mirror read algorithm uses current load and an incremental weighting
value to determine the vdev to service a read operation. Lower values
determine the preferred vdev. The weighting value is
`zfs_vdev_mirror_rotating_inc <#zfs-vdev-mirror-rotating-inc>`__ for
rotating media and ``zfs_vdev_mirror_non_rotating_inc`` for nonrotating
media.

Verify the rotational setting described by a block device in sysfs by
observing ``/sys/block/DISK_NAME/queue/rotational``

+----------------------------------+----------------------------------+
| zfs_vdev_mirror_non_rotating_inc | Notes                            |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `mirror <#mirror>`__,            |
|                                  | `SSD <#ssd>`__                   |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | scalar                           |
+----------------------------------+----------------------------------+
| Range                            | 0 to INT_MAX                     |
+----------------------------------+----------------------------------+
| Default                          | 0                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.7.0 and later                 |
+----------------------------------+----------------------------------+

zfs_vdev_mirror_rotating_seek_inc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For rotating media in a mirror, if the next I/O offset is within
`zfs_vdev_mirror_rotating_seek_offset <#zfs-vdev-mirror-rotating-seek-offset>`__
then the weighting factor is incremented by
(``zfs_vdev_mirror_rotating_seek_inc / 2``). Otherwise the weighting
factor is increased by ``zfs_vdev_mirror_rotating_seek_inc``. This
algorithm prefers rotating media with lower seek distance.

Verify the rotational setting described by a block device in sysfs by
observing ``/sys/block/DISK_NAME/queue/rotational``

+----------------------------------+----------------------------------+
| z                                | Notes                            |
| fs_vdev_mirror_rotating_seek_inc |                                  |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `mirror <#mirror>`__,            |
|                                  | `HDD <#hdd>`__                   |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | scalar                           |
+----------------------------------+----------------------------------+
| Range                            | 0 to INT_MAX                     |
+----------------------------------+----------------------------------+
| Default                          | 5                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.7.0 and later                 |
+----------------------------------+----------------------------------+

zfs_vdev_mirror_rotating_seek_offset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For rotating media in a mirror, if the next I/O offset is within
``zfs_vdev_mirror_rotating_seek_offset`` then the weighting factor is
incremented by
(`zfs_vdev_mirror_rotating_seek_inc <#zfs-vdev-mirror-rotating-seek-inc>`__\ ``/ 2``).
Otherwise the weighting factor is increased by
``zfs_vdev_mirror_rotating_seek_inc``. This algorithm prefers rotating
media with lower seek distance.

Verify the rotational setting described by a block device in sysfs by
observing ``/sys/block/DISK_NAME/queue/rotational``

+----------------------------------+----------------------------------+
| zfs_vdev_mirror_rotating_seek_off| Notes                            |
| set                              |                                  |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `mirror <#mirror>`__,            |
|                                  | `HDD <#hdd>`__                   |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | bytes                            |
+----------------------------------+----------------------------------+
| Range                            | 0 to INT_MAX                     |
+----------------------------------+----------------------------------+
| Default                          | 1,048,576 (1 MiB)                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.7.0 and later                 |
+----------------------------------+----------------------------------+

zfs_vdev_mirror_non_rotating_seek_inc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For nonrotating media in a mirror, a seek penalty is applied as
sequential I/O's can be aggregated into fewer operations, avoiding
unnecessary per-command overhead, often boosting performance.

Verify the rotational setting described by a block device in SysFS by
observing ``/sys/block/DISK_NAME/queue/rotational``

+----------------------------------+----------------------------------+
| zfs_v                            | Notes                            |
| dev_mirror_non_rotating_seek_inc |                                  |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `mirror <#mirror>`__,            |
|                                  | `SSD <#ssd>`__                   |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | scalar                           |
+----------------------------------+----------------------------------+
| Range                            | 0 to INT_MAX                     |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | v0.7.0 and later                 |
+----------------------------------+----------------------------------+

zfs_vdev_read_gap_limit
~~~~~~~~~~~~~~~~~~~~~~~

To reduce IOPs, small, adjacent I/Os are aggregated (coalesced) into
into a large I/O. For reads, aggregations occur across small adjacency
gaps where the gap is less than ``zfs_vdev_read_gap_limit``

+-------------------------+-------------------------------------------+
| zfs_vdev_read_gap_limit | Notes                                     |
+=========================+===========================================+
| Tags                    | `vdev <#vdev>`__,                         |
|                         | `ZIO_scheduler <#zio-scheduler>`__        |
+-------------------------+-------------------------------------------+
| When to change          | TBD                                       |
+-------------------------+-------------------------------------------+
| Data Type               | int                                       |
+-------------------------+-------------------------------------------+
| Units                   | bytes                                     |
+-------------------------+-------------------------------------------+
| Range                   | 0 to INT_MAX                              |
+-------------------------+-------------------------------------------+
| Default                 | 32,768 (32 KiB)                           |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic                                   |
+-------------------------+-------------------------------------------+
| Versions Affected       | all                                       |
+-------------------------+-------------------------------------------+

zfs_vdev_write_gap_limit
~~~~~~~~~~~~~~~~~~~~~~~~

To reduce IOPs, small, adjacent I/Os are aggregated (coalesced) into
into a large I/O. For writes, aggregations occur across small adjacency
gaps where the gap is less than ``zfs_vdev_write_gap_limit``

+--------------------------+------------------------------------------+
| zfs_vdev_write_gap_limit | Notes                                    |
+==========================+==========================================+
| Tags                     | `vdev <#vdev>`__,                        |
|                          | `ZIO_scheduler <#zio-scheduler>`__       |
+--------------------------+------------------------------------------+
| When to change           | TBD                                      |
+--------------------------+------------------------------------------+
| Data Type                | int                                      |
+--------------------------+------------------------------------------+
| Units                    | bytes                                    |
+--------------------------+------------------------------------------+
| Range                    | 0 to INT_MAX                             |
+--------------------------+------------------------------------------+
| Default                  | 4,096 (4 KiB)                            |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | all                                      |
+--------------------------+------------------------------------------+

zfs_vdev_scheduler
~~~~~~~~~~~~~~~~~~

When the pool is imported, for whole disk vdevs, the block device I/O
scheduler is set to ``zfs_vdev_scheduler``. The most common schedulers
are: *noop*, *cfq*, *bfq*, and *deadline*.

In some cases, the scheduler is not changeable using this method. Known
schedulers that cannot be changed are: *scsi_mq* and *none*. In these
cases, the scheduler is unchanged and an error message can be reported
to logs.

+--------------------+------------------------------------------------+
| zfs_vdev_scheduler | Notes                                          |
+====================+================================================+
| Tags               | `vdev <#vdev>`__,                              |
|                    | `ZIO_scheduler <#zio-scheduler>`__             |
+--------------------+------------------------------------------------+
| When to change     | since ZFS has its own I/O scheduler, using a   |
|                    | simple scheduler can result in more consistent |
|                    | performance                                    |
+--------------------+------------------------------------------------+
| Data Type          | string                                         |
+--------------------+------------------------------------------------+
| Range              | expected: *noop*, *cfq*, *bfq*, and *deadline* |
+--------------------+------------------------------------------------+
| Default            | *noop*                                         |
+--------------------+------------------------------------------------+
| Change             | Dynamic, but takes effect upon pool creation   |
|                    | or import                                      |
+--------------------+------------------------------------------------+
| Versions Affected  | all                                            |
+--------------------+------------------------------------------------+

zfs_vdev_raidz_impl
~~~~~~~~~~~~~~~~~~~

``zfs_vdev_raidz_impl`` overrides the raidz parity algorithm. By
default, the algorithm is selected at zfs module load time by the
results of a microbenchmark of algorithms based on the current hardware.

Once the module is loaded, the content of
``/sys/module/zfs/parameters/zfs_vdev_raidz_impl`` shows available
options with the currently selected enclosed in ``[]``. Details of the
results of the microbenchmark are observable in the
``/proc/spl/kstat/zfs/vdev_raidz_bench`` file.

+----------------+----------------------+-------------------------+
| algorithm      | architecture         | description             |
+================+======================+=========================+
| fastest        | all                  | fastest implementation  |
|                |                      | selected by             |
|                |                      | microbenchmark          |
+----------------+----------------------+-------------------------+
| original       | all                  | original raidz          |
|                |                      | implementation          |
+----------------+----------------------+-------------------------+
| scalar         | all                  | scalar raidz            |
|                |                      | implementation          |
+----------------+----------------------+-------------------------+
| sse2           | 64-bit x86           | uses SSE2 instruction   |
|                |                      | set                     |
+----------------+----------------------+-------------------------+
| ssse3          | 64-bit x86           | uses SSSE3 instruction  |
|                |                      | set                     |
+----------------+----------------------+-------------------------+
| avx2           | 64-bit x86           | uses AVX2 instruction   |
|                |                      | set                     |
+----------------+----------------------+-------------------------+
| avx512f        | 64-bit x86           | uses AVX512F            |
|                |                      | instruction set         |
+----------------+----------------------+-------------------------+
| avx512bw       | 64-bit x86           | uses AVX512F & AVX512BW |
|                |                      | instruction sets        |
+----------------+----------------------+-------------------------+
| aarch64_neon   | aarch64/64 bit ARMv8 | uses NEON               |
+----------------+----------------------+-------------------------+
| aarch64_neonx2 | aarch64/64 bit ARMv8 | uses NEON with more     |
|                |                      | unrolling               |
+----------------+----------------------+-------------------------+

=================== ====================================================
zfs_vdev_raidz_impl Notes
=================== ====================================================
Tags                `CPU <#cpu>`__, `raidz <#raidz>`__, `vdev <#vdev>`__
When to change      testing raidz algorithms
Data Type           string
Range               see table above
Default             *fastest*
Change              Dynamic
Versions Affected   v0.7.0 and later
=================== ====================================================

zfs_zevent_cols
~~~~~~~~~~~~~~~

``zfs_zevent_cols`` is a soft wrap limit in columns (characters) for ZFS
events logged to the console.

================= ==========================
zfs_zevent_cols   Notes
================= ==========================
Tags              `debug <#debug>`__
When to change    if 80 columns isn't enough
Data Type         int
Units             characters
Range             1 to INT_MAX
Default           80
Change            Dynamic
Versions Affected all
================= ==========================

zfs_zevent_console
~~~~~~~~~~~~~~~~~~

If ``zfs_zevent_console`` is true (1), then ZFS events are logged to the
console.

More logging and log filtering capabilities are provided by ``zed``

================== =========================================
zfs_zevent_console Notes
================== =========================================
Tags               `debug <#debug>`__
When to change     to log ZFS events to the console
Data Type          boolean
Range              0=do not log to console, 1=log to console
Default            0
Change             Dynamic
Versions Affected  all
================== =========================================

zfs_zevent_len_max
~~~~~~~~~~~~~~~~~~

``zfs_zevent_len_max`` is the maximum ZFS event queue length. A value of
0 results in a calculated value (16 \* number of CPUs) with a minimum of
64. Events in the queue can be viewed with the ``zpool events`` command.

================== ================================
zfs_zevent_len_max Notes
================== ================================
Tags               `debug <#debug>`__
When to change     increase to see more ZFS events
Data Type          int
Units              events
Range              0 to INT_MAX
Default            0 (calculate as described above)
Change             Dynamic
Versions Affected  all
================== ================================

zfs_zil_clean_taskq_maxalloc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During a SPA sync, intent log transaction groups (itxg) are cleaned. The
cleaning work is dispatched to the DSL pool ZIL clean taskq
(``dp_zil_clean_taskq``).
`zfs_zil_clean_taskq_minalloc <#zfs-zil-clean-taskq-minalloc>`__ is the
minimum and ``zfs_zil_clean_taskq_maxalloc`` is the maximum number of
cached taskq entries for ``dp_zil_clean_taskq``. The actual number of
taskq entries dynamically varies between these values.

When ``zfs_zil_clean_taskq_maxalloc`` is exceeded transaction records
(itxs) are cleaned synchronously with possible negative impact to the
performance of SPA sync.

Ideally taskq entries are pre-allocated prior to being needed by
``zil_clean()``, thus avoiding dynamic allocation of new taskq entries.

+------------------------------+--------------------------------------+
| zfs_zil_clean_taskq_maxalloc | Notes                                |
+==============================+======================================+
| Tags                         | `ZIL <#zil>`__                       |
+------------------------------+--------------------------------------+
| When to change               | If more ``dp_zil_clean_taskq``       |
|                              | entries are needed to prevent the    |
|                              | itxs from being synchronously        |
|                              | cleaned                              |
+------------------------------+--------------------------------------+
| Data Type                    | int                                  |
+------------------------------+--------------------------------------+
| Units                        | ``dp_zil_clean_taskq`` taskq entries |
+------------------------------+--------------------------------------+
| Range                        | `zfs_zil_clean_taskq_minallo         |
|                              | c <#zfs-zil-clean-taskq-minalloc>`__ |
|                              | to ``INT_MAX``                       |
+------------------------------+--------------------------------------+
| Default                      | 1,048,576                            |
+------------------------------+--------------------------------------+
| Change                       | Dynamic, takes effect per-pool when  |
|                              | the pool is imported                 |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.8.0                               |
+------------------------------+--------------------------------------+

zfs_zil_clean_taskq_minalloc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During a SPA sync, intent log transaction groups (itxg) are cleaned. The
cleaning work is dispatched to the DSL pool ZIL clean taskq
(``dp_zil_clean_taskq``). ``zfs_zil_clean_taskq_minalloc`` is the
minimum and
`zfs_zil_clean_taskq_maxalloc <#zfs-zil-clean-taskq-maxalloc>`__ is the
maximum number of cached taskq entries for ``dp_zil_clean_taskq``. The
actual number of taskq entries dynamically varies between these values.

``zfs_zil_clean_taskq_minalloc`` is the minimum number of ZIL
transaction records (itxs).

Ideally taskq entries are pre-allocated prior to being needed by
``zil_clean()``, thus avoiding dynamic allocation of new taskq entries.

+------------------------------+--------------------------------------+
| zfs_zil_clean_taskq_minalloc | Notes                                |
+==============================+======================================+
| Tags                         | `ZIL <#zil>`__                       |
+------------------------------+--------------------------------------+
| When to change               | TBD                                  |
+------------------------------+--------------------------------------+
| Data Type                    | int                                  |
+------------------------------+--------------------------------------+
| Units                        | dp_zil_clean_taskq taskq entries     |
+------------------------------+--------------------------------------+
| Range                        | 1 to                                 |
|                              | `zfs_zil_clean_taskq_maxallo         |
|                              | c <#zfs-zil-clean-taskq-maxalloc>`__ |
+------------------------------+--------------------------------------+
| Default                      | 1,024                                |
+------------------------------+--------------------------------------+
| Change                       | Dynamic, takes effect per-pool when  |
|                              | the pool is imported                 |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.8.0                               |
+------------------------------+--------------------------------------+

zfs_zil_clean_taskq_nthr_pct
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_zil_clean_taskq_nthr_pct`` controls the number of threads used by
the DSL pool ZIL clean taskq (``dp_zil_clean_taskq``). The default value
of 100% will create a maximum of one thread per cpu.

+------------------------------+--------------------------------------+
| zfs_zil_clean_taskq_nthr_pct | Notes                                |
+==============================+======================================+
| Tags                         | `taskq <#taskq>`__, `ZIL <#zil>`__   |
+------------------------------+--------------------------------------+
| When to change               | Testing ZIL clean and SPA sync       |
|                              | performance                          |
+------------------------------+--------------------------------------+
| Data Type                    | int                                  |
+------------------------------+--------------------------------------+
| Units                        | percent of number of CPUs            |
+------------------------------+--------------------------------------+
| Range                        | 1 to 100                             |
+------------------------------+--------------------------------------+
| Default                      | 100                                  |
+------------------------------+--------------------------------------+
| Change                       | Dynamic, takes effect per-pool when  |
|                              | the pool is imported                 |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.8.0                               |
+------------------------------+--------------------------------------+

zil_replay_disable
~~~~~~~~~~~~~~~~~~

If ``zil_replay_disable = 1``, then when a volume or filesystem is
brought online, no attempt to replay the ZIL is made and any existing
ZIL is destroyed. This can result in loss of data without notice.

================== ==================================
zil_replay_disable Notes
================== ==================================
Tags               `debug <#debug>`__, `ZIL <#zil>`__
When to change     Do not change
Data Type          boolean
Range              0=replay ZIL, 1=destroy ZIL
Default            0
Change             Dynamic
Versions Affected  v0.6.5
================== ==================================

zil_slog_bulk
~~~~~~~~~~~~~

``zil_slog_bulk`` is the log device write size limit per commit executed
with synchronous priority. Writes below ``zil_slog_bulk`` are executed
with synchronous priority. Writes above ``zil_slog_bulk`` are executed
with lower (asynchronous) priority to reduct potential log device abuse
by a single active ZIL writer.

+-------------------+-------------------------------------------------+
| zil_slog_bulk     | Notes                                           |
+===================+=================================================+
| Tags              | `ZIL <#zil>`__                                  |
+-------------------+-------------------------------------------------+
| When to change    | See `ZFS I/O                                    |
|                   | Scheduler <https://g                            |
|                   | ithub.com/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+-------------------+-------------------------------------------------+
| Data Type         | ulong                                           |
+-------------------+-------------------------------------------------+
| Units             | bytes                                           |
+-------------------+-------------------------------------------------+
| Range             | 0 to ULONG_MAX                                  |
+-------------------+-------------------------------------------------+
| Default           | 786,432                                         |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.8.0                                          |
+-------------------+-------------------------------------------------+

zio_delay_max
~~~~~~~~~~~~~

If a ZFS I/O operation takes more than ``zio_delay_max`` milliseconds to
complete, then an event is logged. Note that this is only a logging
facility, not a timeout on operations. See also ``zpool events``

================= =======================
zio_delay_max     Notes
================= =======================
Tags              `debug <#debug>`__
When to change    when debugging slow I/O
Data Type         int
Units             milliseconds
Range             1 to INT_MAX
Default           30,000 (30 seconds)
Change            Dynamic
Versions Affected all
================= =======================

zio_dva_throttle_enabled
~~~~~~~~~~~~~~~~~~~~~~~~

``zio_dva_throttle_enabled`` controls throttling of block allocations in
the ZFS I/O (ZIO) pipeline. When enabled, the maximum number of pending
allocations per top-level vdev is limited by
`zfs_vdev_queue_depth_pct <#zfs-vdev-queue-depth-pct>`__

+--------------------------+------------------------------------------+
| zio_dva_throttle_enabled | Notes                                    |
+==========================+==========================================+
| Tags                     | `vdev <#vdev>`__,                        |
|                          | `ZIO_scheduler <#zio-scheduler>`__       |
+--------------------------+------------------------------------------+
| When to change           | Testing ZIO block allocation algorithms  |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=do not throttle ZIO block allocations, |
|                          | 1=throttle ZIO block allocations         |
+--------------------------+------------------------------------------+
| Default                  | 1                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.0 and later                         |
+--------------------------+------------------------------------------+

zio_requeue_io_start_cut_in_line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zio_requeue_io_start_cut_in_line`` controls prioritization of a
re-queued ZFS I/O (ZIO) in the ZIO pipeline by the ZIO taskq.

+----------------------------------+----------------------------------+
| zio_requeue_io_start_cut_in_line | Notes                            |
+==================================+==================================+
| Tags                             | `Z                               |
|                                  | IO_scheduler <#zio-scheduler>`__ |
+----------------------------------+----------------------------------+
| When to change                   | Do not change                    |
+----------------------------------+----------------------------------+
| Data Type                        | boolean                          |
+----------------------------------+----------------------------------+
| Range                            | 0=don't prioritize re-queued     |
|                                  | I/Os, 1=prioritize re-queued     |
|                                  | I/Os                             |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | all                              |
+----------------------------------+----------------------------------+

zio_taskq_batch_pct
~~~~~~~~~~~~~~~~~~~

``zio_taskq_batch_pct`` sets the number of I/O worker threads as a
percentage of online CPUs. These workers threads are responsible for IO
work such as compression and checksum calculations.

Each block is handled by one worker thread, so maximum overall worker
thread throughput is function of the number of concurrent blocks being
processed, the number of worker threads, and the algorithms used. The
default value of 75% is chosen to avoid using all CPUs which can result
in latency issues and inconsistent application performance, especially
when high compression is enabled.

The taskq batch processes are:

+-------------+--------------+---------------------------------------+
| taskq       | process name | Notes                                 |
+=============+==============+=======================================+
| Write issue | z_wr_iss[_#] | Can be CPU intensive, runs at lower   |
|             |              | priority than other taskqs            |
+-------------+--------------+---------------------------------------+

Other taskqs exist, but most have fixed numbers of instances and
therefore require recompiling the kernel module to adjust.

+---------------------+-----------------------------------------------+
| zio_taskq_batch_pct | Notes                                         |
+=====================+===============================================+
| Tags                | `taskq <#taskq>`__,                           |
|                     | `ZIO_scheduler <#zio-scheduler>`__            |
+---------------------+-----------------------------------------------+
| When to change      | To tune parallelism in multiprocessor systems |
+---------------------+-----------------------------------------------+
| Data Type           | int                                           |
+---------------------+-----------------------------------------------+
| Units               | percent of number of CPUs                     |
+---------------------+-----------------------------------------------+
| Range               | 1 to 100, fractional number of CPUs are       |
|                     | rounded down                                  |
+---------------------+-----------------------------------------------+
| Default             | 75                                            |
+---------------------+-----------------------------------------------+
| Change              | Prior to zfs module load                      |
+---------------------+-----------------------------------------------+
| Verification        | The number of taskqs for each batch group can |
|                     | be observed using ``ps`` and counting the     |
|                     | threads                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | TBD                                           |
+---------------------+-----------------------------------------------+

zvol_inhibit_dev
~~~~~~~~~~~~~~~~

``zvol_inhibit_dev`` controls the creation of volume device nodes upon
pool import.

+-------------------+-------------------------------------------------+
| zvol_inhibit_dev  | Notes                                           |
+===================+=================================================+
| Tags              | `import <#import>`__, `volume <#volume>`__      |
+-------------------+-------------------------------------------------+
| When to change    | Inhibiting can slightly improve startup time on |
|                   | systems with a very large number of volumes     |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=create volume device nodes, 1=do not create   |
|                   | volume device nodes                             |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic, takes effect per-pool when the pool is |
|                   | imported                                        |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.0 and later                                |
+-------------------+-------------------------------------------------+

zvol_major
~~~~~~~~~~

``zvol_major`` is the default major number for volume devices.

+-------------------+-------------------------------------------------+
| zvol_major        | Notes                                           |
+===================+=================================================+
| Tags              | `volume <#volume>`__                            |
+-------------------+-------------------------------------------------+
| When to change    | Do not change                                   |
+-------------------+-------------------------------------------------+
| Data Type         | uint                                            |
+-------------------+-------------------------------------------------+
| Default           | 230                                             |
+-------------------+-------------------------------------------------+
| Change            | Dynamic, takes effect per-pool when the pool is |
|                   | imported or volumes are created                 |
+-------------------+-------------------------------------------------+
| Versions Affected | all                                             |
+-------------------+-------------------------------------------------+

zvol_max_discard_blocks
~~~~~~~~~~~~~~~~~~~~~~~

Discard (aka ATA TRIM or SCSI UNMAP) operations done on volumes are done
in batches ``zvol_max_discard_blocks`` blocks. The block size is
determined by the ``volblocksize`` property of a volume.

Some applications, such as ``mkfs``, discard the whole volume at once
using the maximum possible discard size. As a result, many gigabytes of
discard requests are not uncommon. Unfortunately, if a large amount of
data is already allocated in the volume, ZFS can be quite slow to
process discard requests. This is especially true if the volblocksize is
small (eg default=8KB). As a result, very large discard requests can
take a very long time (perhaps minutes under heavy load) to complete.
This can cause a number of problems, most notably if the volume is
accessed remotely (eg via iSCSI), in which case the client has a high
probability of timing out on the request.

Limiting the ``zvol_max_discard_blocks`` can decrease the amount of
discard workload request by setting the ``discard_max_bytes`` and
``discard_max_hw_bytes`` for the volume's block device in SysFS. This
value is readable by volume device consumers.

+-------------------------+-------------------------------------------+
| zvol_max_discard_blocks | Notes                                     |
+=========================+===========================================+
| Tags                    | `discard <#discard>`__,                   |
|                         | `volume <#volume>`__                      |
+-------------------------+-------------------------------------------+
| When to change          | if volume discard activity severely       |
|                         | impacts other workloads                   |
+-------------------------+-------------------------------------------+
| Data Type               | ulong                                     |
+-------------------------+-------------------------------------------+
| Units                   | number of blocks of size volblocksize     |
+-------------------------+-------------------------------------------+
| Range                   | 0 to ULONG_MAX                            |
+-------------------------+-------------------------------------------+
| Default                 | 16,384                                    |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic, takes effect per-pool when the   |
|                         | pool is imported or volumes are created   |
+-------------------------+-------------------------------------------+
| Verification            | Observe value of                          |
|                         | ``/sys/block/                             |
|                         | VOLUME_INSTANCE/queue/discard_max_bytes`` |
+-------------------------+-------------------------------------------+
| Versions Affected       | v0.6.0 and later                          |
+-------------------------+-------------------------------------------+

zvol_prefetch_bytes
~~~~~~~~~~~~~~~~~~~

When importing a pool with volumes or adding a volume to a pool,
``zvol_prefetch_bytes`` are prefetch from the start and end of the
volume. Prefetching these regions of the volume is desirable because
they are likely to be accessed immediately by ``blkid(8)`` or by the
kernel scanning for a partition table.

=================== ==============================================
zvol_prefetch_bytes Notes
=================== ==============================================
Tags                `prefetch <#prefetch>`__, `volume <#volume>`__
When to change      TBD
Data Type           uint
Units               bytes
Range               0 to UINT_MAX
Default             131,072
Change              Dynamic
Versions Affected   v0.6.5 and later
=================== ==============================================

zvol_request_sync
~~~~~~~~~~~~~~~~~

When processing I/O requests for a volume submit them synchronously.
This effectively limits the queue depth to 1 for each I/O submitter.
When set to 0 requests are handled asynchronously by the "zvol" thread
pool.

See also `zvol_threads <#zvol-threads>`__

+-------------------+-------------------------------------------------+
| zvol_request_sync | Notes                                           |
+===================+=================================================+
| Tags              | `volume <#volume>`__                            |
+-------------------+-------------------------------------------------+
| When to change    | Testing concurrent volume requests              |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=do concurrent (async) volume requests, 1=do   |
|                   | sync volume requests                            |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.7.2 and later                                |
+-------------------+-------------------------------------------------+

zvol_threads
~~~~~~~~~~~~

zvol_threads controls the maximum number of threads handling concurrent
volume I/O requests.

The default of 32 threads behaves similarly to a disk with a 32-entry
command queue. The actual number of threads required can vary widely by
workload and available CPUs. If lock analysis shows high contention in
the zvol taskq threads, then reducing the number of zvol_threads or
workload queue depth can improve overall throughput.

See also `zvol_request_sync <#zvol-request-sync>`__

+-------------------+-------------------------------------------------+
| zvol_threads      | Notes                                           |
+===================+=================================================+
| Tags              | `volume <#volume>`__                            |
+-------------------+-------------------------------------------------+
| When to change    | Matching the number of concurrent volume        |
|                   | requests with workload requirements can improve |
|                   | concurrency                                     |
+-------------------+-------------------------------------------------+
| Data Type         | uint                                            |
+-------------------+-------------------------------------------------+
| Units             | threads                                         |
+-------------------+-------------------------------------------------+
| Range             | 1 to UINT_MAX                                   |
+-------------------+-------------------------------------------------+
| Default           | 32                                              |
+-------------------+-------------------------------------------------+
| Change            | Dynamic, takes effect per-volume when the pool  |
|                   | is imported or volumes are created              |
+-------------------+-------------------------------------------------+
| Verification      | ``iostat`` using ``avgqu-sz`` or ``aqu-sz``     |
|                   | results                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.7.0 and later                                |
+-------------------+-------------------------------------------------+

zvol_volmode
~~~~~~~~~~~~

``zvol_volmode`` defines volume block devices behaviour when the
``volmode`` property is set to ``default``

Note: to maintain compatibility with ZFS on BSD, "geom" is synonymous
with "full"

===== ======= ===========================================
value volmode Description
===== ======= ===========================================
1     full    legacy fully functional behaviour (default)
2     dev     hide partitions on volume block devices
3     none    not exposing volumes outside ZFS
===== ======= ===========================================

================= ====================
zvol_volmode      Notes
================= ====================
Tags              `volume <#volume>`__
When to change    TBD
Data Type         enum
Range             1, 2, or 3
Default           1
Change            Dynamic
Versions Affected v0.7.0 and later
================= ====================

zfs_qat_disable
~~~~~~~~~~~~~~~

``zfs_qat_disable`` controls the Intel QuickAssist Technology (QAT)
driver providing hardware acceleration for gzip compression. When the
QAT hardware is present and qat driver available, the default behaviour
is to enable QAT.

+-------------------+-------------------------------------------------+
| zfs_qat_disable   | Notes                                           |
+===================+=================================================+
| Tags              | `compression <#compression>`__, `QAT <#qat>`__  |
+-------------------+-------------------------------------------------+
| When to change    | Testing QAT functionality                       |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=use QAT acceleration if available, 1=do not   |
|                   | use QAT acceleration                            |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.7, renamed to                                |
|                   | `zfs_qat_                                       |
|                   | compress_disable <#zfs-qat-compress-disable>`__ |
|                   | in v0.8                                         |
+-------------------+-------------------------------------------------+

zfs_qat_checksum_disable
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_qat_checksum_disable`` controls the Intel QuickAssist Technology
(QAT) driver providing hardware acceleration for checksums. When the QAT
hardware is present and qat driver available, the default behaviour is
to enable QAT.

+--------------------------+------------------------------------------+
| zfs_qat_checksum_disable | Notes                                    |
+==========================+==========================================+
| Tags                     | `checksum <#checksum>`__, `QAT <#qat>`__ |
+--------------------------+------------------------------------------+
| When to change           | Testing QAT functionality                |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=use QAT acceleration if available,     |
|                          | 1=do not use QAT acceleration            |
+--------------------------+------------------------------------------+
| Default                  | 0                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.8.0                                   |
+--------------------------+------------------------------------------+

zfs_qat_compress_disable
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_qat_compress_disable`` controls the Intel QuickAssist Technology
(QAT) driver providing hardware acceleration for gzip compression. When
the QAT hardware is present and qat driver available, the default
behaviour is to enable QAT.

+--------------------------+------------------------------------------+
| zfs_qat_compress_disable | Notes                                    |
+==========================+==========================================+
| Tags                     | `compression <#compression>`__,          |
|                          | `QAT <#qat>`__                           |
+--------------------------+------------------------------------------+
| When to change           | Testing QAT functionality                |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=use QAT acceleration if available,     |
|                          | 1=do not use QAT acceleration            |
+--------------------------+------------------------------------------+
| Default                  | 0                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.8.0                                   |
+--------------------------+------------------------------------------+

zfs_qat_encrypt_disable
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_qat_encrypt_disable`` controls the Intel QuickAssist Technology
(QAT) driver providing hardware acceleration for encryption. When the
QAT hardware is present and qat driver available, the default behaviour
is to enable QAT.

+-------------------------+-------------------------------------------+
| zfs_qat_encrypt_disable | Notes                                     |
+=========================+===========================================+
| Tags                    | `encryption <#encryption>`__,             |
|                         | `QAT <#qat>`__                            |
+-------------------------+-------------------------------------------+
| When to change          | Testing QAT functionality                 |
+-------------------------+-------------------------------------------+
| Data Type               | boolean                                   |
+-------------------------+-------------------------------------------+
| Range                   | 0=use QAT acceleration if available, 1=do |
|                         | not use QAT acceleration                  |
+-------------------------+-------------------------------------------+
| Default                 | 0                                         |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic                                   |
+-------------------------+-------------------------------------------+
| Versions Affected       | v0.8.0                                    |
+-------------------------+-------------------------------------------+

dbuf_cache_hiwater_pct
~~~~~~~~~~~~~~~~~~~~~~

The ``dbuf_cache_hiwater_pct`` and
`dbuf_cache_lowater_pct <#dbuf-cache-lowater-pct>`__ define the
operating range for dbuf cache evict thread. The hiwater and lowater are
percentages of the `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__
value. When the dbuf cache grows above ((100% +
``dbuf_cache_hiwater_pct``) \*
`dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__) then the dbuf cache
thread begins evicting. When the dbug cache falls below ((100% -
`dbuf_cache_lowater_pct <#dbuf-cache-lowater-pct>`__) \*
`dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__) then the dbuf cache
thread stops evicting.

====================== =============================
dbuf_cache_hiwater_pct Notes
====================== =============================
Tags                   `dbuf_cache <#dbuf-cache>`__
When to change         Testing dbuf cache algorithms
Data Type              uint
Units                  percent
Range                  0 to UINT_MAX
Default                10
Change                 Dynamic
Versions Affected      v0.7.0 and later
====================== =============================

dbuf_cache_lowater_pct
~~~~~~~~~~~~~~~~~~~~~~

The dbuf_cache_hiwater_pct and dbuf_cache_lowater_pct define the
operating range for dbuf cache evict thread. The hiwater and lowater are
percentages of the `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__
value. When the dbuf cache grows above ((100% +
`dbuf_cache_hiwater_pct <#dbuf-cache-hiwater-pct>`__) \*
`dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__) then the dbuf cache
thread begins evicting. When the dbug cache falls below ((100% -
``dbuf_cache_lowater_pct``) \*
`dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__) then the dbuf cache
thread stops evicting.

====================== =============================
dbuf_cache_lowater_pct Notes
====================== =============================
Tags                   `dbuf_cache <#dbuf-cache>`__
When to change         Testing dbuf cache algorithms
Data Type              uint
Units                  percent
Range                  0 to UINT_MAX
Default                10
Change                 Dynamic
Versions Affected      v0.7.0 and later
====================== =============================

dbuf_cache_max_bytes
~~~~~~~~~~~~~~~~~~~~

The dbuf cache maintains a list of dbufs that are not currently held but
have been recently released. These dbufs are not eligible for ARC
eviction until they are aged out of the dbuf cache. Dbufs are added to
the dbuf cache once the last hold is released. If a dbuf is later
accessed and still exists in the dbuf cache, then it will be removed
from the cache and later re-added to the head of the cache. Dbufs that
are aged out of the cache will be immediately destroyed and become
eligible for ARC eviction.

The size of the dbuf cache is set by ``dbuf_cache_max_bytes``. The
actual size is dynamically adjusted to the minimum of current ARC target
size (``c``) >> `dbuf_cache_max_shift <#dbuf-cache-max-shift>`__ and the
default ``dbuf_cache_max_bytes``

==================== =============================
dbuf_cache_max_bytes Notes
==================== =============================
Tags                 `dbuf_cache <#dbuf-cache>`__
When to change       Testing dbuf cache algorithms
Data Type            ulong
Units                bytes
Range                16,777,216 to ULONG_MAX
Default              104,857,600 (100 MiB)
Change               Dynamic
Versions Affected    v0.7.0 and later
==================== =============================

dbuf_cache_max_shift
~~~~~~~~~~~~~~~~~~~~

The `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__ minimum is the
lesser of `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__ and the
current ARC target size (``c``) >> ``dbuf_cache_max_shift``

==================== =============================
dbuf_cache_max_shift Notes
==================== =============================
Tags                 `dbuf_cache <#dbuf-cache>`__
When to change       Testing dbuf cache algorithms
Data Type            int
Units                shift
Range                1 to 63
Default              5
Change               Dynamic
Versions Affected    v0.7.0 and later
==================== =============================

dmu_object_alloc_chunk_shift
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each of the concurrent object allocators grabs
``2^dmu_object_alloc_chunk_shift`` dnode slots at a time. The default is
to grab 128 slots, or 4 blocks worth. This default value was
experimentally determined to be the lowest value that eliminates the
measurable effect of lock contention in the DMU object allocation code
path.

+------------------------------+--------------------------------------+
| dmu_object_alloc_chunk_shift | Notes                                |
+==============================+======================================+
| Tags                         | `allocation <#allocation>`__,        |
|                              | `DMU <#dmu>`__                       |
+------------------------------+--------------------------------------+
| When to change               | If the workload creates many files   |
|                              | concurrently on a system with many   |
|                              | CPUs, then increasing                |
|                              | ``dmu_object_alloc_chunk_shift`` can |
|                              | decrease lock contention             |
+------------------------------+--------------------------------------+
| Data Type                    | int                                  |
+------------------------------+--------------------------------------+
| Units                        | shift                                |
+------------------------------+--------------------------------------+
| Range                        | 7 to 9                               |
+------------------------------+--------------------------------------+
| Default                      | 7                                    |
+------------------------------+--------------------------------------+
| Change                       | Dynamic                              |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.7.0 and later                     |
+------------------------------+--------------------------------------+

send_holes_without_birth_time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alias for `ignore_hole_birth <#ignore-hole-birth>`__

zfs_abd_scatter_enabled
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_abd_scatter_enabled`` controls the ARC Buffer Data (ABD)
scatter/gather feature.

When disabled, the legacy behaviour is selected using linear buffers.
For linear buffers, all the data in the ABD is stored in one contiguous
buffer in memory (from a ``zio_[data_]buf_*`` kmem cache).

When enabled (default), the data in the ABD is split into equal-sized
chunks (from the ``abd_chunk_cache`` kmem_cache), with pointers to the
chunks recorded in an array at the end of the ABD structure. This allows
more efficient memory allocation for buffers, especially when large
recordsizes are used.

+-------------------------+-------------------------------------------+
| zfs_abd_scatter_enabled | Notes                                     |
+=========================+===========================================+
| Tags                    | `ABD <#abd>`__, `memory <#memory>`__      |
+-------------------------+-------------------------------------------+
| When to change          | Testing ABD                               |
+-------------------------+-------------------------------------------+
| Data Type               | boolean                                   |
+-------------------------+-------------------------------------------+
| Range                   | 0=use linear allocation only, 1=allow     |
|                         | scatter/gather                            |
+-------------------------+-------------------------------------------+
| Default                 | 1                                         |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic                                   |
+-------------------------+-------------------------------------------+
| Verification            | ABD statistics are observable in          |
|                         | ``/proc/spl/kstat/zfs/abdstats``. Slab    |
|                         | allocations are observable in             |
|                         | ``/proc/slabinfo``                        |
+-------------------------+-------------------------------------------+
| Versions Affected       | v0.7.0 and later                          |
+-------------------------+-------------------------------------------+

zfs_abd_scatter_max_order
~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_abd_scatter_max_order`` sets the maximum order for physical page
allocation when ABD is enabled (see
`zfs_abd_scatter_enabled <#zfs-abd-scatter-enabled>`__)

See also Buddy Memory Allocation in the Linux kernel documentation.

+---------------------------+-----------------------------------------+
| zfs_abd_scatter_max_order | Notes                                   |
+===========================+=========================================+
| Tags                      | `ABD <#abd>`__, `memory <#memory>`__    |
+---------------------------+-----------------------------------------+
| When to change            | Testing ABD features                    |
+---------------------------+-----------------------------------------+
| Data Type                 | int                                     |
+---------------------------+-----------------------------------------+
| Units                     | orders                                  |
+---------------------------+-----------------------------------------+
| Range                     | 1 to 10 (upper limit is                 |
|                           | hardware-dependent)                     |
+---------------------------+-----------------------------------------+
| Default                   | 10                                      |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Verification              | ABD statistics are observable in        |
|                           | ``/proc/spl/kstat/zfs/abdstats``        |
+---------------------------+-----------------------------------------+
| Versions Affected         | v0.7.0 and later                        |
+---------------------------+-----------------------------------------+

zfs_compressed_arc_enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~

When compression is enabled for a dataset, later reads of the data can
store the blocks in ARC in their on-disk, compressed state. This can
increse the effective size of the ARC, as counted in blocks, and thus
improve the ARC hit ratio.

+----------------------------+----------------------------------------+
| zfs_compressed_arc_enabled | Notes                                  |
+============================+========================================+
| Tags                       | `ABD <#abd>`__,                        |
|                            | `compression <#compression>`__         |
+----------------------------+----------------------------------------+
| When to change             | Testing ARC compression feature        |
+----------------------------+----------------------------------------+
| Data Type                  | boolean                                |
+----------------------------+----------------------------------------+
| Range                      | 0=compressed ARC disabled (legacy      |
|                            | behaviour), 1=compress ARC data        |
+----------------------------+----------------------------------------+
| Default                    | 1                                      |
+----------------------------+----------------------------------------+
| Change                     | Dynamic                                |
+----------------------------+----------------------------------------+
| Verification               | raw ARC statistics are observable in   |
|                            | ``/proc/spl/kstat/zfs/arcstats`` and   |
|                            | ARC hit ratios can be observed using   |
|                            | ``arcstat``                            |
+----------------------------+----------------------------------------+
| Versions Affected          | v0.7.0 and later                       |
+----------------------------+----------------------------------------+

zfs_key_max_salt_uses
~~~~~~~~~~~~~~~~~~~~~

For encrypted datasets, the salt is regenerated every
``zfs_key_max_salt_uses`` blocks. This automatic regeneration reduces
the probability of collisions due to the Birthday problem. When set to
the default (400,000,000) the probability of collision is approximately
1 in 1 trillion.

===================== ============================
zfs_key_max_salt_uses Notes
===================== ============================
Tags                  `encryption <#encryption>`__
When to change        Testing encryption features
Data Type             ulong
Units                 blocks encrypted
Range                 1 to ULONG_MAX
Default               400,000,000
Change                Dynamic
Versions Affected     v0.8.0 and later
===================== ============================

zfs_object_mutex_size
~~~~~~~~~~~~~~~~~~~~~

``zfs_object_mutex_size`` facilitates resizing the the per-dataset znode
mutex array for testing deadlocks therein.

===================== ===================================
zfs_object_mutex_size Notes
===================== ===================================
Tags                  `debug <#debug>`__
When to change        Testing znode mutex array deadlocks
Data Type             uint
Units                 orders
Range                 1 to UINT_MAX
Default               64
Change                Dynamic
Versions Affected     v0.7.0 and later
===================== ===================================

zfs_scan_strict_mem_lim
~~~~~~~~~~~~~~~~~~~~~~~

When scrubbing or resilvering, by default, ZFS checks to ensure it is
not over the hard memory limit before each txg commit. If finer-grained
control of this is needed ``zfs_scan_strict_mem_lim`` can be set to 1 to
enable checking before scanning each block.

+-------------------------+-------------------------------------------+
| zfs_scan_strict_mem_lim | Notes                                     |
+=========================+===========================================+
| Tags                    | `memory <#memory>`__,                     |
|                         | `resilver <#resilver>`__,                 |
|                         | `scrub <#scrub>`__                        |
+-------------------------+-------------------------------------------+
| When to change          | Do not change                             |
+-------------------------+-------------------------------------------+
| Data Type               | boolean                                   |
+-------------------------+-------------------------------------------+
| Range                   | 0=normal scan behaviour, 1=check hard     |
|                         | memory limit strictly during scan         |
+-------------------------+-------------------------------------------+
| Default                 | 0                                         |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic                                   |
+-------------------------+-------------------------------------------+
| Versions Affected       | v0.8.0                                    |
+-------------------------+-------------------------------------------+

zfs_send_queue_length
~~~~~~~~~~~~~~~~~~~~~

``zfs_send_queue_length`` is the maximum number of bytes allowed in the
zfs send queue.

+-----------------------+---------------------------------------------+
| zfs_send_queue_length | Notes                                       |
+=======================+=============================================+
| Tags                  | `send <#send>`__                            |
+-----------------------+---------------------------------------------+
| When to change        | When using the largest recordsize or        |
|                       | volblocksize (16 MiB), increasing can       |
|                       | improve send efficiency                     |
+-----------------------+---------------------------------------------+
| Data Type             | int                                         |
+-----------------------+---------------------------------------------+
| Units                 | bytes                                       |
+-----------------------+---------------------------------------------+
| Range                 | Must be at least twice the maximum          |
|                       | recordsize or volblocksize in use           |
+-----------------------+---------------------------------------------+
| Default               | 16,777,216 bytes (16 MiB)                   |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.8.1                                      |
+-----------------------+---------------------------------------------+

zfs_recv_queue_length
~~~~~~~~~~~~~~~~~~~~~

``zfs_recv_queue_length`` is the maximum number of bytes allowed in the
zfs receive queue.

+-----------------------+---------------------------------------------+
| zfs_recv_queue_length | Notes                                       |
+=======================+=============================================+
| Tags                  | `receive <#receive>`__                      |
+-----------------------+---------------------------------------------+
| When to change        | When using the largest recordsize or        |
|                       | volblocksize (16 MiB), increasing can       |
|                       | improve receive efficiency                  |
+-----------------------+---------------------------------------------+
| Data Type             | int                                         |
+-----------------------+---------------------------------------------+
| Units                 | bytes                                       |
+-----------------------+---------------------------------------------+
| Range                 | Must be at least twice the maximum          |
|                       | recordsize or volblocksize in use           |
+-----------------------+---------------------------------------------+
| Default               | 16,777,216 bytes (16 MiB)                   |
+-----------------------+---------------------------------------------+
| Change                | Dynamic                                     |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.8.1                                      |
+-----------------------+---------------------------------------------+

zfs_arc_min_prefetch_lifespan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``arc_min_prefetch_lifespan`` is the minimum time for a prefetched block
to remain in ARC before it is eligible for eviction.

============================= ======================================
zfs_arc_min_prefetch_lifespan Notes
============================= ======================================
Tags                          `ARC <#ARC>`__
When to change                TBD
Data Type                     int
Units                         clock ticks
Range                         0 = use default value
Default                       1 second (as expressed in clock ticks)
Change                        Dynamic
Versions Affected             v0.7.0
============================= ======================================

zfs_scan_ignore_errors
~~~~~~~~~~~~~~~~~~~~~~

``zfs_scan_ignore_errors`` allows errors discovered during scrub or
resilver to be ignored. This can be tuned as a workaround to remove the
dirty time list (DTL) when completing a pool scan. It is intended to be
used during pool repair or recovery to prevent resilvering when the pool
is imported.

+------------------------+--------------------------------------------+
| zfs_scan_ignore_errors | Notes                                      |
+========================+============================================+
| Tags                   | `resilver <#resilver>`__                   |
+------------------------+--------------------------------------------+
| When to change         | See description above                      |
+------------------------+--------------------------------------------+
| Data Type              | boolean                                    |
+------------------------+--------------------------------------------+
| Range                  | 0 = do not ignore errors, 1 = ignore       |
|                        | errors during pool scrub or resilver       |
+------------------------+--------------------------------------------+
| Default                | 0                                          |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | v0.8.1                                     |
+------------------------+--------------------------------------------+

zfs_top_maxinflight
~~~~~~~~~~~~~~~~~~~

``zfs_top_maxinflight`` is used to limit the maximum number of I/Os
queued to top-level vdevs during scrub or resilver operations. The
actual top-level vdev limit is calculated by multiplying the number of
child vdevs by ``zfs_top_maxinflight`` This limit is an additional cap
over and above the scan limits

+---------------------+-----------------------------------------------+
| zfs_top_maxinflight | Notes                                         |
+=====================+===============================================+
| Tags                | `resilver <#resilver>`__, `scrub <#scrub>`__, |
|                     | `ZIO_scheduler <#zio-scheduler>`__            |
+---------------------+-----------------------------------------------+
| When to change      | for modern ZFS versions, the ZIO scheduler    |
|                     | limits usually take precedence                |
+---------------------+-----------------------------------------------+
| Data Type           | int                                           |
+---------------------+-----------------------------------------------+
| Units               | I/O operations                                |
+---------------------+-----------------------------------------------+
| Range               | 1 to MAX_INT                                  |
+---------------------+-----------------------------------------------+
| Default             | 32                                            |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.6.0                                        |
+---------------------+-----------------------------------------------+

zfs_resilver_delay
~~~~~~~~~~~~~~~~~~

``zfs_resilver_delay`` sets a time-based delay for resilver I/Os. This
delay is in addition to the ZIO scheduler's treatment of scrub
workloads. See also `zfs_scan_idle <#zfs-scan-idle>`__

+--------------------+------------------------------------------------+
| zfs_resilver_delay | Notes                                          |
+====================+================================================+
| Tags               | `resilver <#resilver>`__,                      |
|                    | `ZIO_scheduler <#zio-scheduler>`__             |
+--------------------+------------------------------------------------+
| When to change     | increasing can reduce impact of resilver       |
|                    | workload on dynamic workloads                  |
+--------------------+------------------------------------------------+
| Data Type          | int                                            |
+--------------------+------------------------------------------------+
| Units              | clock ticks                                    |
+--------------------+------------------------------------------------+
| Range              | 0 to MAX_INT                                   |
+--------------------+------------------------------------------------+
| Default            | 2                                              |
+--------------------+------------------------------------------------+
| Change             | Dynamic                                        |
+--------------------+------------------------------------------------+
| Versions Affected  | v0.6.0                                         |
+--------------------+------------------------------------------------+

zfs_scrub_delay
~~~~~~~~~~~~~~~

``zfs_scrub_delay`` sets a time-based delay for scrub I/Os. This delay
is in addition to the ZIO scheduler's treatment of scrub workloads. See
also `zfs_scan_idle <#zfs-scan-idle>`__

+-------------------+-------------------------------------------------+
| zfs_scrub_delay   | Notes                                           |
+===================+=================================================+
| Tags              | `scrub <#scrub>`__,                             |
|                   | `ZIO_scheduler <#zio-scheduler>`__              |
+-------------------+-------------------------------------------------+
| When to change    | increasing can reduce impact of scrub workload  |
|                   | on dynamic workloads                            |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Units             | clock ticks                                     |
+-------------------+-------------------------------------------------+
| Range             | 0 to MAX_INT                                    |
+-------------------+-------------------------------------------------+
| Default           | 4                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.0                                          |
+-------------------+-------------------------------------------------+

zfs_scan_idle
~~~~~~~~~~~~~

When a non-scan I/O has occurred in the past ``zfs_scan_idle`` clock
ticks, then `zfs_resilver_delay <#zfs-resilver-delay>`__ or
`zfs_scrub_delay <#zfs-scrub-delay>`__ are enabled.

+-------------------+-------------------------------------------------+
| zfs_scan_idle     | Notes                                           |
+===================+=================================================+
| Tags              | `resilver <#resilver>`__, `scrub <#scrub>`__,   |
|                   | `ZIO_scheduler <#zio-scheduler>`__              |
+-------------------+-------------------------------------------------+
| When to change    | as part of a resilver/scrub tuning effort       |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Units             | clock ticks                                     |
+-------------------+-------------------------------------------------+
| Range             | 0 to MAX_INT                                    |
+-------------------+-------------------------------------------------+
| Default           | 50                                              |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.0                                          |
+-------------------+-------------------------------------------------+

icp_aes_impl
~~~~~~~~~~~~

By default, ZFS will choose the highest performance, hardware-optimized
implementation of the AES encryption algorithm. The ``icp_aes_impl``
tunable overrides this automatic choice.

Note: ``icp_aes_impl`` is set in the ``icp`` kernel module, not the
``zfs`` kernel module.

To observe the available options
``cat /sys/module/icp/parameters/icp_aes_impl`` The default option is
shown in brackets '[]'

================= ====================================
icp_aes_impl      Notes
================= ====================================
Tags              `encryption <#encryption>`__
Kernel module     icp
When to change    debugging ZFS encryption on hardware
Data Type         string
Range             varies by hardware
Default           automatic, depends on the hardware
Change            dynamic
Versions Affected planned for v2
================= ====================================

icp_gcm_impl
~~~~~~~~~~~~

By default, ZFS will choose the highest performance, hardware-optimized
implementation of the GCM encryption algorithm. The ``icp_gcm_impl``
tunable overrides this automatic choice.

Note: ``icp_gcm_impl`` is set in the ``icp`` kernel module, not the
``zfs`` kernel module.

To observe the available options
``cat /sys/module/icp/parameters/icp_gcm_impl`` The default option is
shown in brackets '[]'

================= ====================================
icp_gcm_impl      Notes
================= ====================================
Tags              `encryption <#encryption>`__
Kernel module     icp
When to change    debugging ZFS encryption on hardware
Data Type         string
Range             varies by hardware
Default           automatic, depends on the hardware
Change            Dynamic
Versions Affected planned for v2
================= ====================================

zfs_abd_scatter_min_size
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_abd_scatter_min_size`` changes the ARC buffer data (ABD)
allocator's threshold for using linear or page-based scatter buffers.
Allocations smaller than ``zfs_abd_scatter_min_size`` use linear ABDs.

Scatter ABD's use at least one page each, so sub-page allocations waste
some space when allocated as scatter allocations. For example, 2KB
scatter allocation wastes half of each page. Using linear ABD's for
small allocations results in slabs containing many allocations. This can
improve memory efficiency, at the expense of more work for ARC evictions
attempting to free pages, because all the buffers on one slab need to be
freed in order to free the slab and its underlying pages.

Typically, 512B and 1KB kmem caches have 16 buffers per slab, so it's
possible for them to actually waste more memory than scatter
allocations:

-  one page per buf = wasting 3/4 or 7/8
-  one buf per slab = wasting 15/16

Spill blocks are typically 512B and are heavily used on systems running
*selinux* with the default dnode size and the ``xattr=sa`` property set.

By default, linear allocations for 512B and 1KB, and scatter allocations
for larger (>= 1.5KB) allocation requests.

+--------------------------+------------------------------------------+
| zfs_abd_scatter_min_size | Notes                                    |
+==========================+==========================================+
| Tags                     | `ARC <#ARC>`__                           |
+--------------------------+------------------------------------------+
| When to change           | debugging memory allocation, especially  |
|                          | for large pages                          |
+--------------------------+------------------------------------------+
| Data Type                | int                                      |
+--------------------------+------------------------------------------+
| Units                    | bytes                                    |
+--------------------------+------------------------------------------+
| Range                    | 0 to MAX_INT                             |
+--------------------------+------------------------------------------+
| Default                  | 1536 (512B and 1KB allocations will be   |
|                          | linear)                                  |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | planned for v2                           |
+--------------------------+------------------------------------------+

zfs_unlink_suspend_progress
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_unlink_suspend_progress`` changes the policy for removing pending
unlinks. When enabled, files will not be asynchronously removed from the
list of pending unlinks and the space they consume will be leaked. Once
this option has been disabled and the dataset is remounted, the pending
unlinks will be processed and the freed space returned to the pool.

+-----------------------------+---------------------------------------+
| zfs_unlink_suspend_progress | Notes                                 |
+=============================+=======================================+
| Tags                        |                                       |
+-----------------------------+---------------------------------------+
| When to change              | used by the ZFS test suite (ZTS) to   |
|                             | facilitate testing                    |
+-----------------------------+---------------------------------------+
| Data Type                   | boolean                               |
+-----------------------------+---------------------------------------+
| Range                       | 0 = use async unlink removal, 1 = do  |
|                             | not async unlink thus leaking space   |
+-----------------------------+---------------------------------------+
| Default                     | 0                                     |
+-----------------------------+---------------------------------------+
| Change                      | prior to dataset mount                |
+-----------------------------+---------------------------------------+
| Versions Affected           | planned for v2                        |
+-----------------------------+---------------------------------------+

spa_load_verify_shift
~~~~~~~~~~~~~~~~~~~~~

``spa_load_verify_shift`` sets the fraction of ARC that can be used by
inflight I/Os when verifying the pool during import. This value is a
"shift" representing the fraction of ARC target size
(``grep -w c /proc/spl/kstat/zfs/arcstats``). The ARC target size is
shifted to the right. Thus a value of '2' results in the fraction = 1/4,
while a value of '4' results in the fraction = 1/8.

For large memory machines, pool import can consume large amounts of ARC:
much larger than the value of maxinflight. This can result in
`spa_load_verify_maxinflight <#spa-load-verify-maxinflight>`__ having a
value of 0 causing the system to hang. Setting ``spa_load_verify_shift``
can reduce this limit and allow importing without hanging.

+-----------------------+---------------------------------------------+
| spa_load_verify_shift | Notes                                       |
+=======================+=============================================+
| Tags                  | `import <#import>`__, `ARC <#ARC>`__,       |
|                       | `SPA <#SPA>`__                              |
+-----------------------+---------------------------------------------+
| When to change        | troubleshooting pool import on large memory |
|                       | machines                                    |
+-----------------------+---------------------------------------------+
| Data Type             | int                                         |
+-----------------------+---------------------------------------------+
| Units                 | shift                                       |
+-----------------------+---------------------------------------------+
| Range                 | 1 to MAX_INT                                |
+-----------------------+---------------------------------------------+
| Default               | 4                                           |
+-----------------------+---------------------------------------------+
| Change                | prior to importing a pool                   |
+-----------------------+---------------------------------------------+
| Versions Affected     | planned for v2                              |
+-----------------------+---------------------------------------------+

spa_load_print_vdev_tree
~~~~~~~~~~~~~~~~~~~~~~~~

``spa_load_print_vdev_tree`` enables printing of the attempted pool
import's vdev tree to kernel message to the ZFS debug message log
``/proc/spl/kstat/zfs/dbgmsg`` Both the provided vdev tree and MOS vdev
tree are printed, which can be useful for debugging problems with the
zpool ``cachefile``

+--------------------------+------------------------------------------+
| spa_load_print_vdev_tree | Notes                                    |
+==========================+==========================================+
| Tags                     | `import <#import>`__, `SPA <#SPA>`__     |
+--------------------------+------------------------------------------+
| When to change           | troubleshooting pool import failures     |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0 = do not print pool configuration in   |
|                          | logs, 1 = print pool configuration in    |
|                          | logs                                     |
+--------------------------+------------------------------------------+
| Default                  | 0                                        |
+--------------------------+------------------------------------------+
| Change                   | prior to pool import                     |
+--------------------------+------------------------------------------+
| Versions Affected        | planned for v2                           |
+--------------------------+------------------------------------------+

zfs_max_missing_tvds
~~~~~~~~~~~~~~~~~~~~

When importing a pool in readonly mode
(``zpool import -o readonly=on ...``) then up to
``zfs_max_missing_tvds`` top-level vdevs can be missing, but the import
can attempt to progress.

Note: This is strictly intended for advanced pool recovery cases since
missing data is almost inevitable. Pools with missing devices can only
be imported read-only for safety reasons, and the pool's ``failmode``
property is automatically set to ``continue``

The expected use case is to recover pool data immediately after
accidentally adding a non-protected vdev to a protected pool.

-  With 1 missing top-level vdev, ZFS should be able to import the pool
   and mount all datasets. User data that was not modified after the
   missing device has been added should be recoverable. Thus snapshots
   created prior to the addition of that device should be completely
   intact.

-  With 2 missing top-level vdevs, some datasets may fail to mount since
   there are dataset statistics that are stored as regular metadata.
   Some data might be recoverable if those vdevs were added recently.

-  With 3 or more top-level missing vdevs, the pool is severely damaged
   and MOS entries may be missing entirely. Chances of data recovery are
   very low. Note that there are also risks of performing an inadvertent
   rewind as we might be missing all the vdevs with the latest
   uberblocks.

==================== ==========================================
zfs_max_missing_tvds Notes
==================== ==========================================
Tags                 `import <#import>`__
When to change       troubleshooting pools with missing devices
Data Type            int
Units                missing top-level vdevs
Range                0 to MAX_INT
Default              0
Change               prior to pool import
Versions Affected    planned for v2
==================== ==========================================

dbuf_metadata_cache_shift
~~~~~~~~~~~~~~~~~~~~~~~~~

``dbuf_metadata_cache_shift`` sets the size of the dbuf metadata cache
as a fraction of ARC target size. This is an alternate method for
setting dbuf metadata cache size than
`dbuf_metadata_cache_max_bytes <#dbuf-metadata-cache-max-bytes>`__.

`dbuf_metadata_cache_max_bytes <#dbuf-metadata-cache-max-bytes>`__
overrides ``dbuf_metadata_cache_shift``

This value is a "shift" representing the fraction of ARC target size
(``grep -w c /proc/spl/kstat/zfs/arcstats``). The ARC target size is
shifted to the right. Thus a value of '2' results in the fraction = 1/4,
while a value of '6' results in the fraction = 1/64.

+---------------------------+-----------------------------------------+
| dbuf_metadata_cache_shift | Notes                                   |
+===========================+=========================================+
| Tags                      | `ARC <#ARC>`__,                         |
|                           | `dbuf_cache <#dbuf-cache>`__            |
+---------------------------+-----------------------------------------+
| When to change            |                                         |
+---------------------------+-----------------------------------------+
| Data Type                 | int                                     |
+---------------------------+-----------------------------------------+
| Units                     | shift                                   |
+---------------------------+-----------------------------------------+
| Range                     | practical range is                      |
|                           | (`                                      |
|                           | dbuf_cache_shift <#dbuf-cache-shift>`__ |
|                           | + 1) to MAX_INT                         |
+---------------------------+-----------------------------------------+
| Default                   | 6                                       |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | planned for v2                          |
+---------------------------+-----------------------------------------+

dbuf_metadata_cache_max_bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``dbuf_metadata_cache_max_bytes`` sets the size of the dbuf metadata
cache as a number of bytes. This is an alternate method for setting dbuf
metadata cache size than
`dbuf_metadata_cache_shift <#dbuf-metadata-cache-shift>`__

`dbuf_metadata_cache_max_bytes <#dbuf-metadata-cache-max-bytes>`__
overrides ``dbuf_metadata_cache_shift``

+-------------------------------+-------------------------------------+
| dbuf_metadata_cache_max_bytes | Notes                               |
+===============================+=====================================+
| Tags                          | `dbuf_cache <#dbuf-cache>`__        |
+-------------------------------+-------------------------------------+
| When to change                |                                     |
+-------------------------------+-------------------------------------+
| Data Type                     | int                                 |
+-------------------------------+-------------------------------------+
| Units                         | bytes                               |
+-------------------------------+-------------------------------------+
| Range                         | 0 = use                             |
|                               | `dbuf_metadata_cache_sh             |
|                               | ift <#dbuf-metadata-cache-shift>`__ |
|                               | to ARC ``c_max``                    |
+-------------------------------+-------------------------------------+
| Default                       | 0                                   |
+-------------------------------+-------------------------------------+
| Change                        | Dynamic                             |
+-------------------------------+-------------------------------------+
| Versions Affected             | planned for v2                      |
+-------------------------------+-------------------------------------+

dbuf_cache_shift
~~~~~~~~~~~~~~~~

``dbuf_cache_shift`` sets the size of the dbuf cache as a fraction of
ARC target size. This is an alternate method for setting dbuf cache size
than `dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__.

`dbuf_cache_max_bytes <#dbuf-cache-max-bytes>`__ overrides
``dbuf_cache_shift``

This value is a "shift" representing the fraction of ARC target size
(``grep -w c /proc/spl/kstat/zfs/arcstats``). The ARC target size is
shifted to the right. Thus a value of '2' results in the fraction = 1/4,
while a value of '5' results in the fraction = 1/32.

Performance tuning of dbuf cache can be monitored using:

-  ``dbufstat`` command
-  `node_exporter <https://github.com/prometheus/node_exporter>`__ ZFS
   module for prometheus environments
-  `telegraf <https://github.com/influxdata/telegraf>`__ ZFS plugin for
   general-purpose metric collection
-  ``/proc/spl/kstat/zfs/dbufstats`` kstat

+-------------------+-------------------------------------------------+
| dbuf_cache_shift  | Notes                                           |
+===================+=================================================+
| Tags              | `ARC <#ARC>`__, `dbuf_cache <#dbuf-cache>`__    |
+-------------------+-------------------------------------------------+
| When to change    | to improve performance of read-intensive        |
|                   | channel programs                                |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Units             | shift                                           |
+-------------------+-------------------------------------------------+
| Range             | 5 to MAX_INT                                    |
+-------------------+-------------------------------------------------+
| Default           | 5                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | planned for v2                                  |
+-------------------+-------------------------------------------------+

.. _dbuf_cache_max_bytes-1:

dbuf_cache_max_bytes
~~~~~~~~~~~~~~~~~~~~

``dbuf_cache_max_bytes`` sets the size of the dbuf cache in bytes. This
is an alternate method for setting dbuf cache size than
`dbuf_cache_shift <#dbuf-cache-shift>`__

Performance tuning of dbuf cache can be monitored using:

-  ``dbufstat`` command
-  `node_exporter <https://github.com/prometheus/node_exporter>`__ ZFS
   module for prometheus environments
-  `telegraf <https://github.com/influxdata/telegraf>`__ ZFS plugin for
   general-purpose metric collection
-  ``/proc/spl/kstat/zfs/dbufstats`` kstat

+----------------------+----------------------------------------------+
| dbuf_cache_max_bytes | Notes                                        |
+======================+==============================================+
| Tags                 | `ARC <#ARC>`__, `dbuf_cache <#dbuf-cache>`__ |
+----------------------+----------------------------------------------+
| When to change       |                                              |
+----------------------+----------------------------------------------+
| Data Type            | int                                          |
+----------------------+----------------------------------------------+
| Units                | bytes                                        |
+----------------------+----------------------------------------------+
| Range                | 0 = use                                      |
|                      | `dbuf_cache_shift <#dbuf-cache-shift>`__ to  |
|                      | ARC ``c_max``                                |
+----------------------+----------------------------------------------+
| Default              | 0                                            |
+----------------------+----------------------------------------------+
| Change               | Dynamic                                      |
+----------------------+----------------------------------------------+
| Versions Affected    | planned for v2                               |
+----------------------+----------------------------------------------+

metaslab_force_ganging
~~~~~~~~~~~~~~~~~~~~~~

When testing allocation code, ``metaslab_force_ganging`` forces blocks
above the specified size to be ganged.

====================== ==========================================
metaslab_force_ganging Notes
====================== ==========================================
Tags                   `allocation <#allocation>`__
When to change         for development testing purposes only
Data Type              ulong
Units                  bytes
Range                  SPA_MINBLOCKSIZE to (SPA_MAXBLOCKSIZE + 1)
Default                SPA_MAXBLOCKSIZE + 1 (16,777,217 bytes)
Change                 Dynamic
Versions Affected      planned for v2
====================== ==========================================

zfs_vdev_default_ms_count
~~~~~~~~~~~~~~~~~~~~~~~~~

When adding a top-level vdev, ``zfs_vdev_default_ms_count`` is the
target number of metaslabs.

+---------------------------+-----------------------------------------+
| zfs_vdev_default_ms_count | Notes                                   |
+===========================+=========================================+
| Tags                      | `allocation <#allocation>`__            |
+---------------------------+-----------------------------------------+
| When to change            | for development testing purposes only   |
+---------------------------+-----------------------------------------+
| Data Type                 | int                                     |
+---------------------------+-----------------------------------------+
| Range                     | 16 to MAX_INT                           |
+---------------------------+-----------------------------------------+
| Default                   | 200                                     |
+---------------------------+-----------------------------------------+
| Change                    | prior to creating a pool or adding a    |
|                           | top-level vdev                          |
+---------------------------+-----------------------------------------+
| Versions Affected         | planned for v2                          |
+---------------------------+-----------------------------------------+

vdev_removal_max_span
~~~~~~~~~~~~~~~~~~~~~

During top-level vdev removal, chunks of data are copied from the vdev
which may include free space in order to trade bandwidth for IOPS.
``vdev_removal_max_span`` sets the maximum span of free space included
as unnecessary data in a chunk of copied data.

===================== ================================
vdev_removal_max_span Notes
===================== ================================
Tags                  `vdev_removal <#vdev-removal>`__
When to change        TBD
Data Type             int
Units                 bytes
Range                 0 to MAX_INT
Default               32,768 (32 MiB)
Change                Dynamic
Versions Affected     planned for v2
===================== ================================

zfs_removal_ignore_errors
~~~~~~~~~~~~~~~~~~~~~~~~~

When removing a device, ``zfs_removal_ignore_errors`` controls the
process for handling hard I/O errors. When set, if a device encounters a
hard IO error during the removal process the removal will not be
cancelled. This can result in a normally recoverable block becoming
permanently damaged and is not recommended. This should only be used as
a last resort when the pool cannot be returned to a healthy state prior
to removing the device.

+---------------------------+-----------------------------------------+
| zfs_removal_ignore_errors | Notes                                   |
+===========================+=========================================+
| Tags                      | `vdev_removal <#vdev-removal>`__        |
+---------------------------+-----------------------------------------+
| When to change            | See description for caveat              |
+---------------------------+-----------------------------------------+
| Data Type                 | boolean                                 |
+---------------------------+-----------------------------------------+
| Range                     | during device removal: 0 = hard errors  |
|                           | are not ignored, 1 = hard errors are    |
|                           | ignored                                 |
+---------------------------+-----------------------------------------+
| Default                   | 0                                       |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | planned for v2                          |
+---------------------------+-----------------------------------------+

zfs_removal_suspend_progress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_removal_suspend_progress`` is used during automated testing of the
ZFS code to incease test coverage.

============================ ======================================
zfs_removal_suspend_progress Notes
============================ ======================================
Tags                         `vdev_removal <#vdev-removal>`__
When to change               do not change
Data Type                    boolean
Range                        0 = do not suspend during vdev removal
Default                      0
Change                       Dynamic
Versions Affected            planned for v2
============================ ======================================

zfs_condense_indirect_commit_entry_delay_ms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During vdev removal, the vdev indirection layer sleeps for
``zfs_condense_indirect_commit_entry_delay_ms`` milliseconds during
mapping generation. This parameter is used during automated testing of
the ZFS code to improve test coverage.

+----------------------------------+----------------------------------+
| zfs_condens                      | Notes                            |
| e_indirect_commit_entry_delay_ms |                                  |
+==================================+==================================+
| Tags                             | `vdev_removal <#vdev-removal>`__ |
+----------------------------------+----------------------------------+
| When to change                   | do not change                    |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | milliseconds                     |
+----------------------------------+----------------------------------+
| Range                            | 0 to MAX_INT                     |
+----------------------------------+----------------------------------+
| Default                          | 0                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_condense_indirect_vdevs_enable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During vdev removal, condensing process is an attempt to save memory by
removing obsolete mappings. ``zfs_condense_indirect_vdevs_enable``
enables condensing indirect vdev mappings. When set, ZFS attempts to
condense indirect vdev mappings if the mapping uses more than
`zfs_condense_min_mapping_bytes <#zfs-condense-min-mapping-bytes>`__
bytes of memory and if the obsolete space map object uses more than
`zfs_condense_max_obsolete_bytes <#zfs-condense-max-obsolete-bytes>`__
bytes on disk.

+----------------------------------+----------------------------------+
| zf                               | Notes                            |
| s_condense_indirect_vdevs_enable |                                  |
+==================================+==================================+
| Tags                             | `vdev_removal <#vdev-removal>`__ |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | boolean                          |
+----------------------------------+----------------------------------+
| Range                            | 0 = do not save memory, 1 = save |
|                                  | memory by condensing obsolete    |
|                                  | mapping after vdev removal       |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_condense_max_obsolete_bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After vdev removal, ``zfs_condense_max_obsolete_bytes`` sets the limit
for beginning the condensing process. Condensing begins if the obsolete
space map takes up more than ``zfs_condense_max_obsolete_bytes`` of
space on disk (logically). The default of 1 GiB is small enough relative
to a typical pool that the space consumed by the obsolete space map is
minimal.

See also
`zfs_condense_indirect_vdevs_enable <#zfs-condense-indirect-vdevs-enable>`__

=============================== ================================
zfs_condense_max_obsolete_bytes Notes
=============================== ================================
Tags                            `vdev_removal <#vdev-removal>`__
When to change                  no not change
Data Type                       ulong
Units                           bytes
Range                           0 to MAX_ULONG
Default                         1,073,741,824 (1 GiB)
Change                          Dynamic
Versions Affected               planned for v2
=============================== ================================

zfs_condense_min_mapping_bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After vdev removal, ``zfs_condense_min_mapping_bytes`` is the lower
limit for determining when to condense the in-memory obsolete space map.
The condensing process will not continue unless a minimum of
``zfs_condense_min_mapping_bytes`` of memory can be freed.

See also
`zfs_condense_indirect_vdevs_enable <#zfs-condense-indirect-vdevs-enable>`__

============================== ================================
zfs_condense_min_mapping_bytes Notes
============================== ================================
Tags                           `vdev_removal <#vdev-removal>`__
When to change                 do not change
Data Type                      ulong
Units                          bytes
Range                          0 to MAX_ULONG
Default                        128 KiB
Change                         Dynamic
Versions Affected              planned for v2
============================== ================================

zfs_vdev_initializing_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_initializing_max_active`` sets the maximum initializing I/Os
active to each device.

+----------------------------------+----------------------------------+
| zfs_vdev_initializing_max_active | Notes                            |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `Z                               |
|                                  | IO_scheduler <#zio-scheduler>`__ |
+----------------------------------+----------------------------------+
| When to change                   | See `ZFS I/O                     |
|                                  | Sch                              |
|                                  | eduler <https://github.com/zfson |
|                                  | linux/zfs/wiki/ZIO-Scheduler>`__ |
+----------------------------------+----------------------------------+
| Data Type                        | uint32                           |
+----------------------------------+----------------------------------+
| Units                            | I/O operations                   |
+----------------------------------+----------------------------------+
| Range                            | 1 to                             |
|                                  | `zfs_vdev_max_                   |
|                                  | active <#zfs-vdev-max-active>`__ |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_vdev_initializing_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_initializing_min_active`` sets the minimum initializing I/Os
active to each device.

+----------------------------------+----------------------------------+
| zfs_vdev_initializing_min_active | Notes                            |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `Z                               |
|                                  | IO_scheduler <#zio-scheduler>`__ |
+----------------------------------+----------------------------------+
| When to change                   | See `ZFS I/O                     |
|                                  | Sch                              |
|                                  | eduler <https://github.com/zfson |
|                                  | linux/zfs/wiki/ZIO-Scheduler>`__ |
+----------------------------------+----------------------------------+
| Data Type                        | uint32                           |
+----------------------------------+----------------------------------+
| Units                            | I/O operations                   |
+----------------------------------+----------------------------------+
| Range                            | 1 to                             |
|                                  | `zfs_vde                         |
|                                  | v_initializing_max_active <#zfs_ |
|                                  | vdev_initializing_max_active>`__ |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_vdev_removal_max_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_removal_max_active`` sets the maximum top-level vdev removal
I/Os active to each device.

+-----------------------------+---------------------------------------+
| zfs_vdev_removal_max_active | Notes                                 |
+=============================+=======================================+
| Tags                        | `vdev <#vdev>`__,                     |
|                             | `ZIO_scheduler <#zio-scheduler>`__    |
+-----------------------------+---------------------------------------+
| When to change              | See `ZFS I/O                          |
|                             | Scheduler <https://github.com/        |
|                             | zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+-----------------------------+---------------------------------------+
| Data Type                   | uint32                                |
+-----------------------------+---------------------------------------+
| Units                       | I/O operations                        |
+-----------------------------+---------------------------------------+
| Range                       | 1 to                                  |
|                             | `zfs_vdev                             |
|                             | _max_active <#zfs-vdev-max-active>`__ |
+-----------------------------+---------------------------------------+
| Default                     | 2                                     |
+-----------------------------+---------------------------------------+
| Change                      | Dynamic                               |
+-----------------------------+---------------------------------------+
| Versions Affected           | planned for v2                        |
+-----------------------------+---------------------------------------+

zfs_vdev_removal_min_active
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_removal_min_active`` sets the minimum top-level vdev removal
I/Os active to each device.

+-----------------------------+---------------------------------------+
| zfs_vdev_removal_min_active | Notes                                 |
+=============================+=======================================+
| Tags                        | `vdev <#vdev>`__,                     |
|                             | `ZIO_scheduler <#zio-scheduler>`__    |
+-----------------------------+---------------------------------------+
| When to change              | See `ZFS I/O                          |
|                             | Scheduler <https://github.com/        |
|                             | zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+-----------------------------+---------------------------------------+
| Data Type                   | uint32                                |
+-----------------------------+---------------------------------------+
| Units                       | I/O operations                        |
+-----------------------------+---------------------------------------+
| Range                       | 1 to                                  |
|                             | `zfs_vdev_removal_max_act             |
|                             | ive <#zfs-vdev-removal-max-active>`__ |
+-----------------------------+---------------------------------------+
| Default                     | 1                                     |
+-----------------------------+---------------------------------------+
| Change                      | Dynamic                               |
+-----------------------------+---------------------------------------+
| Versions Affected           | planned for v2                        |
+-----------------------------+---------------------------------------+

zfs_vdev_trim_max_active
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_trim_max_active`` sets the maximum trim I/Os active to each
device.

+--------------------------+------------------------------------------+
| zfs_vdev_trim_max_active | Notes                                    |
+==========================+==========================================+
| Tags                     | `vdev <#vdev>`__,                        |
|                          | `ZIO_scheduler <#zio-scheduler>`__       |
+--------------------------+------------------------------------------+
| When to change           | See `ZFS I/O                             |
|                          | Scheduler <https://github.c              |
|                          | om/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------+------------------------------------------+
| Data Type                | uint32                                   |
+--------------------------+------------------------------------------+
| Units                    | I/O operations                           |
+--------------------------+------------------------------------------+
| Range                    | 1 to                                     |
|                          | `zfs_v                                   |
|                          | dev_max_active <#zfs-vdev-max-active>`__ |
+--------------------------+------------------------------------------+
| Default                  | 2                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | planned for v2                           |
+--------------------------+------------------------------------------+

zfs_vdev_trim_min_active
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_trim_min_active`` sets the minimum trim I/Os active to each
device.

+--------------------------+------------------------------------------+
| zfs_vdev_trim_min_active | Notes                                    |
+==========================+==========================================+
| Tags                     | `vdev <#vdev>`__,                        |
|                          | `ZIO_scheduler <#zio-scheduler>`__       |
+--------------------------+------------------------------------------+
| When to change           | See `ZFS I/O                             |
|                          | Scheduler <https://github.c              |
|                          | om/zfsonlinux/zfs/wiki/ZIO-Scheduler>`__ |
+--------------------------+------------------------------------------+
| Data Type                | uint32                                   |
+--------------------------+------------------------------------------+
| Units                    | I/O operations                           |
+--------------------------+------------------------------------------+
| Range                    | 1 to                                     |
|                          | `zfs_vdev_trim_m                         |
|                          | ax_active <#zfs-vdev-trim-max-active>`__ |
+--------------------------+------------------------------------------+
| Default                  | 1                                        |
+--------------------------+------------------------------------------+
| Change                   | Dynamic                                  |
+--------------------------+------------------------------------------+
| Versions Affected        | planned for v2                           |
+--------------------------+------------------------------------------+

zfs_initialize_value
~~~~~~~~~~~~~~~~~~~~

When initializing a vdev, ZFS writes patterns of
``zfs_initialize_value`` bytes to the device.

+----------------------+----------------------------------------------+
| zfs_initialize_value | Notes                                        |
+======================+==============================================+
| Tags                 | `vdev_initialize <#vdev-initialize>`__       |
+----------------------+----------------------------------------------+
| When to change       | when debugging initialization code           |
+----------------------+----------------------------------------------+
| Data Type            | uint32 or uint64                             |
+----------------------+----------------------------------------------+
| Default              | 0xdeadbeef for 32-bit systems,               |
|                      | 0xdeadbeefdeadbeee for 64-bit systems        |
+----------------------+----------------------------------------------+
| Change               | prior to running ``zpool initialize``        |
+----------------------+----------------------------------------------+
| Versions Affected    | planned for v2                               |
+----------------------+----------------------------------------------+

zfs_lua_max_instrlimit
~~~~~~~~~~~~~~~~~~~~~~

``zfs_lua_max_instrlimit`` limits the maximum time for a ZFS channel
program to run.

+------------------------+--------------------------------------------+
| zfs_lua_max_instrlimit | Notes                                      |
+========================+============================================+
| Tags                   | `channel_programs <#channel-programs>`__   |
+------------------------+--------------------------------------------+
| When to change         | to enforce a CPU usage limit on ZFS        |
|                        | channel programs                           |
+------------------------+--------------------------------------------+
| Data Type              | ulong                                      |
+------------------------+--------------------------------------------+
| Units                  | LUA instructions                           |
+------------------------+--------------------------------------------+
| Range                  | 0 to MAX_ULONG                             |
+------------------------+--------------------------------------------+
| Default                | 100,000,000                                |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | planned for v2                             |
+------------------------+--------------------------------------------+

zfs_lua_max_memlimit
~~~~~~~~~~~~~~~~~~~~

'zfs_lua_max_memlimit' is the maximum memory limit for a ZFS channel
program.

==================== ========================================
zfs_lua_max_memlimit Notes
==================== ========================================
Tags                 `channel_programs <#channel-programs>`__
When to change
Data Type            ulong
Units                bytes
Range                0 to MAX_ULONG
Default              104,857,600 (100 MiB)
Change               Dynamic
Versions Affected    planned for v2
==================== ========================================

zfs_max_dataset_nesting
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_max_dataset_nesting`` limits the depth of nested datasets. Deeply
nested datasets can overflow the stack. The maximum stack depth depends
on kernel compilation options, so it is impractical to predict the
possible limits. For kernels compiled with small stack sizes,
``zfs_max_dataset_nesting`` may require changes.

+-------------------------+-------------------------------------------+
| zfs_max_dataset_nesting | Notes                                     |
+=========================+===========================================+
| Tags                    | `dataset <#dataset>`__                    |
+-------------------------+-------------------------------------------+
| When to change          | can be tuned temporarily to fix existing  |
|                         | datasets that exceed the predefined limit |
+-------------------------+-------------------------------------------+
| Data Type               | int                                       |
+-------------------------+-------------------------------------------+
| Units                   | datasets                                  |
+-------------------------+-------------------------------------------+
| Range                   | 0 to MAX_INT                              |
+-------------------------+-------------------------------------------+
| Default                 | 50                                        |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic, though once on-disk the value    |
|                         | for the pool is set                       |
+-------------------------+-------------------------------------------+
| Versions Affected       | planned for v2                            |
+-------------------------+-------------------------------------------+

zfs_ddt_data_is_special
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_ddt_data_is_special`` enables the deduplication table (DDT) to
reside on a special top-level vdev.

+-------------------------+-------------------------------------------+
| zfs_ddt_data_is_special | Notes                                     |
+=========================+===========================================+
| Tags                    | `dedup <#dedup>`__,                       |
|                         | `special_vdev <#special-vdev>`__          |
+-------------------------+-------------------------------------------+
| When to change          | when using a special top-level vdev and   |
|                         | no dedup top-level vdev and it is desired |
|                         | to store the DDT in the main pool         |
|                         | top-level vdevs                           |
+-------------------------+-------------------------------------------+
| Data Type               | boolean                                   |
+-------------------------+-------------------------------------------+
| Range                   | 0=do not use special vdevs to store DDT,  |
|                         | 1=store DDT in special vdevs              |
+-------------------------+-------------------------------------------+
| Default                 | 1                                         |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic                                   |
+-------------------------+-------------------------------------------+
| Versions Affected       | planned for v2                            |
+-------------------------+-------------------------------------------+

zfs_user_indirect_is_special
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If special vdevs are in use, ``zfs_user_indirect_is_special`` enables
user data indirect blocks (a form of metadata) to be written to the
special vdevs.

+------------------------------+--------------------------------------+
| zfs_user_indirect_is_special | Notes                                |
+==============================+======================================+
| Tags                         | `special_vdev <#special-vdev>`__     |
+------------------------------+--------------------------------------+
| When to change               | to force user data indirect blocks   |
|                              | to remain in the main pool top-level |
|                              | vdevs                                |
+------------------------------+--------------------------------------+
| Data Type                    | boolean                              |
+------------------------------+--------------------------------------+
| Range                        | 0=do not write user indirect blocks  |
|                              | to a special vdev, 1=write user      |
|                              | indirect blocks to a special vdev    |
+------------------------------+--------------------------------------+
| Default                      | 1                                    |
+------------------------------+--------------------------------------+
| Change                       | Dynamic                              |
+------------------------------+--------------------------------------+
| Versions Affected            | planned for v2                       |
+------------------------------+--------------------------------------+

zfs_reconstruct_indirect_combinations_max
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After device removal, if an indirect split block contains more than
``zfs_reconstruct_indirect_combinations_max`` many possible unique
combinations when being reconstructed, it can be considered too
computationally expensive to check them all. Instead, at most
``zfs_reconstruct_indirect_combinations_max`` randomly-selected
combinations are attempted each time the block is accessed. This allows
all segment copies to participate fairly in the reconstruction when all
combinations cannot be checked and prevents repeated use of one bad
copy.

+----------------------------------+----------------------------------+
| zfs_recon                        | Notes                            |
| struct_indirect_combinations_max |                                  |
+==================================+==================================+
| Tags                             | `vdev_removal <#vdev-removal>`__ |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | attempts                         |
+----------------------------------+----------------------------------+
| Range                            | 0=do not limit attempts, 1 to    |
|                                  | MAX_INT = limit for attempts     |
+----------------------------------+----------------------------------+
| Default                          | 4096                             |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_send_unmodified_spill_blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_send_unmodified_spill_blocks`` enables sending of unmodified spill
blocks in the send stream. Under certain circumstances, previous
versions of ZFS could incorrectly remove the spill block from an
existing object. Including unmodified copies of the spill blocks creates
a backwards compatible stream which will recreate a spill block if it
was incorrectly removed.

+----------------------------------+----------------------------------+
| zfs_send_unmodified_spill_blocks | Notes                            |
+==================================+==================================+
| Tags                             | `send <#send>`__                 |
+----------------------------------+----------------------------------+
| When to change                   | TBD                              |
+----------------------------------+----------------------------------+
| Data Type                        | boolean                          |
+----------------------------------+----------------------------------+
| Range                            | 0=do not send unmodified spill   |
|                                  | blocks, 1=send unmodified spill  |
|                                  | blocks                           |
+----------------------------------+----------------------------------+
| Default                          | 1                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_spa_discard_memory_limit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_spa_discard_memory_limit`` sets the limit for maximum memory used
for prefetching a pool's checkpoint space map on each vdev while
discarding a pool checkpoint.

============================ ============================
zfs_spa_discard_memory_limit Notes
============================ ============================
Tags                         `checkpoint <#checkpoint>`__
When to change               TBD
Data Type                    int
Units                        bytes
Range                        0 to MAX_INT
Default                      16,777,216 (16 MiB)
Change                       Dynamic
Versions Affected            planned for v2
============================ ============================

zfs_special_class_metadata_reserve_pct
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_special_class_metadata_reserve_pct`` sets a threshold for space in
special vdevs to be reserved exclusively for metadata. This prevents
small blocks or dedup table from completely consuming a special vdev.

====================================== ================================
zfs_special_class_metadata_reserve_pct Notes
====================================== ================================
Tags                                   `special_vdev <#special-vdev>`__
When to change                         TBD
Data Type                              int
Units                                  percent
Range                                  0 to 100
Default                                25
Change                                 Dynamic
Versions Affected                      planned for v2
====================================== ================================

zfs_trim_extent_bytes_max
~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_trim_extent_bytes_max`` sets the maximum size of a trim (aka
discard, scsi unmap) command. Ranges larger than
``zfs_trim_extent_bytes_max`` are split in to chunks no larger than
``zfs_trim_extent_bytes_max`` bytes prior to being issued to the device.
Use ``zpool iostat -w`` to observe the latency of trim commands.

+---------------------------+-----------------------------------------+
| zfs_trim_extent_bytes_max | Notes                                   |
+===========================+=========================================+
| Tags                      | `trim <#trim>`__                        |
+---------------------------+-----------------------------------------+
| When to change            | if the device can efficiently handle    |
|                           | larger trim requests                    |
+---------------------------+-----------------------------------------+
| Data Type                 | uint                                    |
+---------------------------+-----------------------------------------+
| Units                     | bytes                                   |
+---------------------------+-----------------------------------------+
| Range                     | `zfs_trim_extent_by                     |
|                           | tes_min <#zfs-trim-extent-bytes-min>`__ |
|                           | to MAX_UINT                             |
+---------------------------+-----------------------------------------+
| Default                   | 134,217,728 (128 MiB)                   |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | planned for v2                          |
+---------------------------+-----------------------------------------+

zfs_trim_extent_bytes_min
~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_trim_extent_bytes_min`` sets the minimum size of trim (aka
discard, scsi unmap) commands. Trim ranges smaller than
``zfs_trim_extent_bytes_min`` are skipped unless they're part of a
larger range which was broken in to chunks. Some devices have
performance degradation during trim operations, so using a larger
``zfs_trim_extent_bytes_min`` can reduce the total amount of space
trimmed. Use ``zpool iostat -w`` to observe the latency of trim
commands.

+---------------------------+-----------------------------------------+
| zfs_trim_extent_bytes_min | Notes                                   |
+===========================+=========================================+
| Tags                      | `trim <#trim>`__                        |
+---------------------------+-----------------------------------------+
| When to change            | when trim is in use and device          |
|                           | performance suffers from trimming small |
|                           | allocations                             |
+---------------------------+-----------------------------------------+
| Data Type                 | uint                                    |
+---------------------------+-----------------------------------------+
| Units                     | bytes                                   |
+---------------------------+-----------------------------------------+
| Range                     | 0=trim all unallocated space, otherwise |
|                           | minimum physical block size to MAX\_    |
+---------------------------+-----------------------------------------+
| Default                   | 32,768 (32 KiB)                         |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | planned for v2                          |
+---------------------------+-----------------------------------------+

zfs_trim_metaslab_skip
~~~~~~~~~~~~~~~~~~~~~~

| ``zfs_trim_metaslab_skip`` enables uninitialized metaslabs to be
  skipped during the trim (aka discard, scsi unmap) process.
  ``zfs_trim_metaslab_skip`` can be useful for pools constructed from
  large thinly-provisioned devices where trim operations perform slowly.
| As a pool ages an increasing fraction of the pool's metaslabs are
  initialized, progressively degrading the usefulness of this option.
  This setting is stored when starting a manual trim and persists for
  the duration of the requested trim. Use ``zpool iostat -w`` to observe
  the latency of trim commands.

+------------------------+--------------------------------------------+
| zfs_trim_metaslab_skip | Notes                                      |
+========================+============================================+
| Tags                   | `trim <#trim>`__                           |
+------------------------+--------------------------------------------+
| When to change         |                                            |
+------------------------+--------------------------------------------+
| Data Type              | boolean                                    |
+------------------------+--------------------------------------------+
| Range                  | 0=do not skip uninitialized metaslabs      |
|                        | during trim, 1=skip uninitialized          |
|                        | metaslabs during trim                      |
+------------------------+--------------------------------------------+
| Default                | 0                                          |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | planned for v2                             |
+------------------------+--------------------------------------------+

zfs_trim_queue_limit
~~~~~~~~~~~~~~~~~~~~

``zfs_trim_queue_limit`` sets the maximum queue depth for leaf vdevs.
See also `zfs_vdev_trim_max_active <#zfs-vdev-trim-max-active>`__ and
`zfs_trim_extent_bytes_max <#zfs-trim-extent-bytes-max>`__ Use
``zpool iostat -q`` to observe trim queue depth.

+----------------------+------------------------------------------------------+
| zfs_trim_queue_limit | Notes                                                |
+======================+======================================================+
| Tags                 | `trim <#trim>`__                                     |
+----------------------+------------------------------------------------------+
| When to change       | to restrict the number of trim commands in the queue |
+----------------------+------------------------------------------------------+
| Data Type            | uint                                                 |
+----------------------+------------------------------------------------------+
| Units                | I/O operations                                       |
+----------------------+------------------------------------------------------+
| Range                | 1 to MAX_UINT                                        |
+----------------------+------------------------------------------------------+
| Default              | 10                                                   |
+----------------------+------------------------------------------------------+
| Change               | Dynamic                                              |
+----------------------+------------------------------------------------------+
| Versions Affected    | planned for v2                                       |
+----------------------+------------------------------------------------------+

zfs_trim_txg_batch
~~~~~~~~~~~~~~~~~~

``zfs_trim_txg_batch`` sets the number of transaction groups worth of
frees which should be aggregated before trim (aka discard, scsi unmap)
commands are issued to a device. This setting represents a trade-off
between issuing larger, more efficient trim commands and the delay
before the recently trimmed space is available for use by the device.

Increasing this value will allow frees to be aggregated for a longer
time. This will result is larger trim operations and potentially
increased memory usage. Decreasing this value will have the opposite
effect. The default value of 32 was empirically determined to be a
reasonable compromise.

================== ===================
zfs_trim_txg_batch Notes
================== ===================
Tags               `trim <#trim>`__
When to change     TBD
Data Type          uint
Units              metaslabs to stride
Range              1 to MAX_UINT
Default            32
Change             Dynamic
Versions Affected  planned for v2
================== ===================

zfs_vdev_aggregate_trim
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_aggregate_trim`` allows trim I/Os to be aggregated. This is
normally not helpful because the extents to be trimmed will have been
already been aggregated by the metaslab.

+-------------------------+-------------------------------------------+
| zfs_vdev_aggregate_trim | Notes                                     |
+=========================+===========================================+
| Tags                    | `trim <#trim>`__, `vdev <#vdev>`__,       |
|                         | `ZIO_scheduler <#zio-scheduler>`__        |
+-------------------------+-------------------------------------------+
| When to change          | when debugging trim code or trim          |
|                         | performance issues                        |
+-------------------------+-------------------------------------------+
| Data Type               | boolean                                   |
+-------------------------+-------------------------------------------+
| Range                   | 0=do not attempt to aggregate trim        |
|                         | commands, 1=attempt to aggregate trim     |
|                         | commands                                  |
+-------------------------+-------------------------------------------+
| Default                 | 0                                         |
+-------------------------+-------------------------------------------+
| Change                  | Dynamic                                   |
+-------------------------+-------------------------------------------+
| Versions Affected       | planned for v2                            |
+-------------------------+-------------------------------------------+

zfs_vdev_aggregation_limit_non_rotating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_aggregation_limit_non_rotating`` is the equivalent of
`zfs_vdev_aggregation_limit <#zfs-vdev-aggregation-limit>`__ for devices
which represent themselves as non-rotating to the Linux blkdev
interfaces. Such devices have a value of 0 in
``/sys/block/DEVICE/queue/rotational`` and are expected to be SSDs.

+----------------------------------+----------------------------------+
| zfs_vde                          | Notes                            |
| v_aggregation_limit_non_rotating |                                  |
+==================================+==================================+
| Tags                             | `vdev <#vdev>`__,                |
|                                  | `Z                               |
|                                  | IO_scheduler <#zio-scheduler>`__ |
+----------------------------------+----------------------------------+
| When to change                   | see                              |
|                                  | `zfs_vdev_aggregation_limit      |
|                                  | <#zfs-vdev-aggregation-limit>`__ |
+----------------------------------+----------------------------------+
| Data Type                        | int                              |
+----------------------------------+----------------------------------+
| Units                            | bytes                            |
+----------------------------------+----------------------------------+
| Range                            | 0 to MAX_INT                     |
+----------------------------------+----------------------------------+
| Default                          | 131,072 bytes (128 KiB)          |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zil_nocacheflush
~~~~~~~~~~~~~~~~

ZFS uses barriers (volatile cache flush commands) to ensure data is
committed to permanent media by devices. This ensures consistent
on-media state for devices where caches are volatile (eg HDDs).

``zil_nocacheflush`` disables the cache flush commands that are normally
sent to devices by the ZIL after a log write has completed.

The difference between ``zil_nocacheflush`` and
`zfs_nocacheflush <#zfs-nocacheflush>`__ is ``zil_nocacheflush`` applies
to ZIL writes while `zfs_nocacheflush <#zfs-nocacheflush>`__ disables
barrier writes to the pool devices at the end of transaction group syncs.

WARNING: setting this can cause ZIL corruption on power loss if the
device has a volatile write cache.

+-------------------+-------------------------------------------------+
| zil_nocacheflush  | Notes                                           |
+===================+=================================================+
| Tags              | `disks <#disks>`__, `ZIL <#ZIL>`__              |
+-------------------+-------------------------------------------------+
| When to change    | If the storage device has nonvolatile cache,    |
|                   | then disabling cache flush can save the cost of |
|                   | occasional cache flush commands                 |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=send cache flush commands, 1=do not send      |
|                   | cache flush commands                            |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | planned for v2                                  |
+-------------------+-------------------------------------------------+

zio_deadman_log_all
~~~~~~~~~~~~~~~~~~~

``zio_deadman_log_all`` enables debugging messages for all ZFS I/Os,
rather than only for leaf ZFS I/Os for a vdev. This is meant to be used
by developers to gain diagnostic information for hang conditions which
don't involve a mutex or other locking primitive. Typically these are
conditions where a thread in the zio pipeline is looping indefinitely.

See also `zfs_dbgmsg_enable <#zfs-dbgmsg-enable>`__

+---------------------+-----------------------------------------------+
| zio_deadman_log_all | Notes                                         |
+=====================+===============================================+
| Tags                | `debug <#debug>`__                            |
+---------------------+-----------------------------------------------+
| When to change      | when debugging ZFS I/O pipeline               |
+---------------------+-----------------------------------------------+
| Data Type           | boolean                                       |
+---------------------+-----------------------------------------------+
| Range               | 0=do not log all deadman events, 1=log all    |
|                     | deadman events                                |
+---------------------+-----------------------------------------------+
| Default             | 0                                             |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | planned for v2                                |
+---------------------+-----------------------------------------------+

zio_decompress_fail_fraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If non-zero, ``zio_decompress_fail_fraction`` represents the denominator
of the probability that ZFS should induce a decompression failure. For
instance, for a 5% decompression failure rate, this value should be set
to 20.

+------------------------------+--------------------------------------+
| zio_decompress_fail_fraction | Notes                                |
+==============================+======================================+
| Tags                         | `debug <#debug>`__                   |
+------------------------------+--------------------------------------+
| When to change               | when debugging ZFS internal          |
|                              | compressed buffer code               |
+------------------------------+--------------------------------------+
| Data Type                    | ulong                                |
+------------------------------+--------------------------------------+
| Units                        | probability of induced decompression |
|                              | failure is                           |
|                              | 1/``zio_decompress_fail_fraction``   |
+------------------------------+--------------------------------------+
| Range                        | 0 = do not induce failures, or 1 to  |
|                              | MAX_ULONG                            |
+------------------------------+--------------------------------------+
| Default                      | 0                                    |
+------------------------------+--------------------------------------+
| Change                       | Dynamic                              |
+------------------------------+--------------------------------------+
| Versions Affected            | planned for v2                       |
+------------------------------+--------------------------------------+

zio_slow_io_ms
~~~~~~~~~~~~~~

An I/O operation taking more than ``zio_slow_io_ms`` milliseconds to
complete is marked as a slow I/O. Slow I/O counters can be observed with
``zpool status -s``. Each slow I/O causes a delay zevent, observable
using ``zpool events``. See also ``zfs-events(5)``.

+-------------------+-------------------------------------------------+
| zio_slow_io_ms    | Notes                                           |
+===================+=================================================+
| Tags              | `vdev <#vdev>`__, `zed <#zed>`__                |
+-------------------+-------------------------------------------------+
| When to change    | when debugging slow devices and the default     |
|                   | value is inappropriate                          |
+-------------------+-------------------------------------------------+
| Data Type         | int                                             |
+-------------------+-------------------------------------------------+
| Units             | milliseconds                                    |
+-------------------+-------------------------------------------------+
| Range             | 0 to MAX_INT                                    |
+-------------------+-------------------------------------------------+
| Default           | 30,000 (30 seconds)                             |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | planned for v2                                  |
+-------------------+-------------------------------------------------+

vdev_validate_skip
~~~~~~~~~~~~~~~~~~

``vdev_validate_skip`` disables label validation steps during pool
import. Changing is not recommended unless you know what you are doing
and are recovering a damaged label.

+--------------------+------------------------------------------------+
| vdev_validate_skip | Notes                                          |
+====================+================================================+
| Tags               | `vdev <#vdev>`__                               |
+--------------------+------------------------------------------------+
| When to change     | do not change                                  |
+--------------------+------------------------------------------------+
| Data Type          | boolean                                        |
+--------------------+------------------------------------------------+
| Range              | 0=validate labels during pool import, 1=do not |
|                    | validate vdev labels during pool import        |
+--------------------+------------------------------------------------+
| Default            | 0                                              |
+--------------------+------------------------------------------------+
| Change             | prior to pool import                           |
+--------------------+------------------------------------------------+
| Versions Affected  | planned for v2                                 |
+--------------------+------------------------------------------------+

zfs_async_block_max_blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_async_block_max_blocks`` limits the number of blocks freed in a
single transaction group commit. During deletes of large objects, such
as snapshots, the number of freed blocks can cause the DMU to extend txg
sync times well beyond `zfs_txg_timeout <#zfs-txg-timeout>`__.
``zfs_async_block_max_blocks`` is used to limit these effects.

========================== ====================================
zfs_async_block_max_blocks Notes
========================== ====================================
Tags                       `delete <#delete>`__, `DMU <#DMU>`__
When to change             TBD
Data Type                  ulong
Units                      blocks
Range                      1 to MAX_ULONG
Default                    MAX_ULONG (do not limit)
Change                     Dynamic
Versions Affected          planned for v2
========================== ====================================

zfs_checksum_events_per_second
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_checksum_events_per_second`` is a rate limit for checksum events.
Note that this should not be set below the ``zed`` thresholds (currently
10 checksums over 10 sec) or else ``zed`` may not trigger any action.

============================== =============================
zfs_checksum_events_per_second Notes
============================== =============================
Tags                           `vdev <#vdev>`__
When to change                 TBD
Data Type                      uint
Units                          checksum events
Range                          ``zed`` threshold to MAX_UINT
Default                        20
Change                         Dynamic
Versions Affected              planned for v2
============================== =============================

zfs_disable_ivset_guid_check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_disable_ivset_guid_check`` disables requirement for IVset guids to
be present and match when doing a raw receive of encrypted datasets.
Intended for users whose pools were created with ZFS on Linux
pre-release versions and now have compatibility issues.

For a ZFS raw receive, from a send stream created by ``zfs send --raw``,
the crypt_keydata nvlist includes a to_ivset_guid to be set on the new
snapshot. This value will override the value generated by the snapshot
code. However, this value may not be present, because older
implementations of the raw send code did not include this value. When
``zfs_disable_ivset_guid_check`` is enabled, the receive proceeds and a
newly-generated value is used.

+------------------------------+--------------------------------------+
| zfs_disable_ivset_guid_check | Notes                                |
+==============================+======================================+
| Tags                         | `receive <#receive>`__               |
+------------------------------+--------------------------------------+
| When to change               | debugging pre-release ZFS raw sends  |
+------------------------------+--------------------------------------+
| Data Type                    | boolean                              |
+------------------------------+--------------------------------------+
| Range                        | 0=check IVset guid, 1=do not check   |
|                              | IVset guid                           |
+------------------------------+--------------------------------------+
| Default                      | 0                                    |
+------------------------------+--------------------------------------+
| Change                       | Dynamic                              |
+------------------------------+--------------------------------------+
| Versions Affected            | planned for v2                       |
+------------------------------+--------------------------------------+

zfs_obsolete_min_time_ms
~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_obsolete_min_time_ms`` is similar to
`zfs_free_min_time_ms <#zfs-free-min-time-ms>`__ and used for cleanup of
old indirection records for vdevs removed using the ``zpool remove``
command.

======================== ==========================================
zfs_obsolete_min_time_ms Notes
======================== ==========================================
Tags                     `delete <#delete>`__, `remove <#remove>`__
When to change           TBD
Data Type                int
Units                    milliseconds
Range                    0 to MAX_INT
Default                  500
Change                   Dynamic
Versions Affected        planned for v2
======================== ==========================================

zfs_override_estimate_recordsize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_override_estimate_recordsize`` overrides the default logic for
estimating block sizes when doing a zfs send. The default heuristic is
that the average block size will be the current recordsize.

+----------------------------------+----------------------------------+
| zfs_override_estimate_recordsize | Notes                            |
+==================================+==================================+
| Tags                             | `send <#send>`__                 |
+----------------------------------+----------------------------------+
| When to change                   | if most data in your dataset is  |
|                                  | not of the current recordsize    |
|                                  | and you require accurate zfs     |
|                                  | send size estimates              |
+----------------------------------+----------------------------------+
| Data Type                        | ulong                            |
+----------------------------------+----------------------------------+
| Units                            | bytes                            |
+----------------------------------+----------------------------------+
| Range                            | 0=do not override, 1 to          |
|                                  | MAX_ULONG                        |
+----------------------------------+----------------------------------+
| Default                          | 0                                |
+----------------------------------+----------------------------------+
| Change                           | Dynamic                          |
+----------------------------------+----------------------------------+
| Versions Affected                | planned for v2                   |
+----------------------------------+----------------------------------+

zfs_remove_max_segment
~~~~~~~~~~~~~~~~~~~~~~

``zfs_remove_max_segment`` sets the largest contiguous segment that ZFS
attempts to allocate when removing a vdev. This can be no larger than
16MB. If there is a performance problem with attempting to allocate
large blocks, consider decreasing this. The value is rounded up to a
power-of-2.

+------------------------+--------------------------------------------+
| zfs_remove_max_segment | Notes                                      |
+========================+============================================+
| Tags                   | `remove <#remove>`__                       |
+------------------------+--------------------------------------------+
| When to change         | after removing a top-level vdev, consider  |
|                        | decreasing if there is a performance       |
|                        | degradation when attempting to allocate    |
|                        | large blocks                               |
+------------------------+--------------------------------------------+
| Data Type              | int                                        |
+------------------------+--------------------------------------------+
| Units                  | bytes                                      |
+------------------------+--------------------------------------------+
| Range                  | maximum of the physical block size of all  |
|                        | vdevs in the pool to 16,777,216 bytes (16  |
|                        | MiB)                                       |
+------------------------+--------------------------------------------+
| Default                | 16,777,216 bytes (16 MiB)                  |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | planned for v2                             |
+------------------------+--------------------------------------------+

zfs_resilver_disable_defer
~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_resilver_disable_defer`` disables the ``resilver_defer`` pool
feature. The ``resilver_defer`` feature allows ZFS to postpone new
resilvers if an existing resilver is in progress.

+----------------------------+----------------------------------------+
| zfs_resilver_disable_defer | Notes                                  |
+============================+========================================+
| Tags                       | `resilver <#resilver>`__               |
+----------------------------+----------------------------------------+
| When to change             | if resilver postponement is not        |
|                            | desired due to overall resilver time   |
|                            | constraints                            |
+----------------------------+----------------------------------------+
| Data Type                  | boolean                                |
+----------------------------+----------------------------------------+
| Range                      | 0=allow ``resilver_defer`` to postpone |
|                            | new resilver operations, 1=immediately |
|                            | restart resilver when needed           |
+----------------------------+----------------------------------------+
| Default                    | 0                                      |
+----------------------------+----------------------------------------+
| Change                     | Dynamic                                |
+----------------------------+----------------------------------------+
| Versions Affected          | planned for v2                         |
+----------------------------+----------------------------------------+

zfs_scan_suspend_progress
~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_scan_suspend_progress`` causes a scrub or resilver scan to freeze
without actually pausing.

========================= ============================================
zfs_scan_suspend_progress Notes
========================= ============================================
Tags                      `resilver <#resilver>`__, `scrub <#scrub>`__
When to change            testing or debugging scan code
Data Type                 boolean
Range                     0=do not freeze scans, 1=freeze scans
Default                   0
Change                    Dynamic
Versions Affected         planned for v2
========================= ============================================

zfs_scrub_min_time_ms
~~~~~~~~~~~~~~~~~~~~~

Scrubs are processed by the sync thread. While scrubbing at least
``zfs_scrub_min_time_ms`` time is spent working on a scrub between txg
syncs.

===================== =================================================
zfs_scrub_min_time_ms Notes
===================== =================================================
Tags                  `scrub <#scrub>`__
When to change
Data Type             int
Units                 milliseconds
Range                 1 to (`zfs_txg_timeout <#zfs-txg-timeout>`__ - 1)
Default               1,000
Change                Dynamic
Versions Affected     planned for v2
===================== =================================================

zfs_slow_io_events_per_second
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``zfs_slow_io_events_per_second`` is a rate limit for slow I/O events.
Note that this should not be set below the ``zed`` thresholds (currently
10 checksums over 10 sec) or else ``zed`` may not trigger any action.

============================= =============================
zfs_slow_io_events_per_second Notes
============================= =============================
Tags                          `vdev <#vdev>`__
When to change                TBD
Data Type                     uint
Units                         slow I/O events
Range                         ``zed`` threshold to MAX_UINT
Default                       20
Change                        Dynamic
Versions Affected             planned for v2
============================= =============================

zfs_vdev_min_ms_count
~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_min_ms_count`` is the minimum number of metaslabs to create
in a top-level vdev.

+-----------------------+---------------------------------------------+
| zfs_vdev_min_ms_count | Notes                                       |
+=======================+=============================================+
| Tags                  | `metaslab <#metaslab>`__, `vdev <#vdev>`__  |
+-----------------------+---------------------------------------------+
| When to change        | TBD                                         |
+-----------------------+---------------------------------------------+
| Data Type             | int                                         |
+-----------------------+---------------------------------------------+
| Units                 | metaslabs                                   |
+-----------------------+---------------------------------------------+
| Range                 | 16 to                                       |
|                       | `zfs_vdev_m                                 |
|                       | s_count_limit <#zfs-vdev-ms-count-limit>`__ |
+-----------------------+---------------------------------------------+
| Default               | 16                                          |
+-----------------------+---------------------------------------------+
| Change                | prior to creating a pool or adding a        |
|                       | top-level vdev                              |
+-----------------------+---------------------------------------------+
| Versions Affected     | planned for v2                              |
+-----------------------+---------------------------------------------+

zfs_vdev_ms_count_limit
~~~~~~~~~~~~~~~~~~~~~~~

``zfs_vdev_ms_count_limit`` is the practical upper limit for the number
of metaslabs per top-level vdev.

+-------------------------+-------------------------------------------+
| zfs_vdev_ms_count_limit | Notes                                     |
+=========================+===========================================+
| Tags                    | `metaslab <#metaslab>`__,                 |
|                         | `vdev <#vdev>`__                          |
+-------------------------+-------------------------------------------+
| When to change          | TBD                                       |
+-------------------------+-------------------------------------------+
| Data Type               | int                                       |
+-------------------------+-------------------------------------------+
| Units                   | metaslabs                                 |
+-------------------------+-------------------------------------------+
| Range                   | `zfs_vdev                                 |
|                         | _min_ms_count <#zfs-vdev-min-ms-count>`__ |
|                         | to 131,072                                |
+-------------------------+-------------------------------------------+
| Default                 | 131,072                                   |
+-------------------------+-------------------------------------------+
| Change                  | prior to creating a pool or adding a      |
|                         | top-level vdev                            |
+-------------------------+-------------------------------------------+
| Versions Affected       | planned for v2                            |
+-------------------------+-------------------------------------------+

spl_hostid
~~~~~~~~~~

| ``spl_hostid`` is a unique system id number. It originated in Sun's
  products where most systems had a unique id assigned at the factory.
  This assignment does not exist in modern hardware.
| In ZFS, the hostid is stored in the vdev label and can be used to
  determine if another system had imported the pool. When set
  ``spl_hostid`` can be used to uniquely identify a system. By default
  this value is set to zero which indicates the hostid is disabled. It
  can be explicitly enabled by placing a unique non-zero value in the
  file shown in `spl_hostid_path <#spl-hostid-path>`__

+-------------------+-------------------------------------------------+
| spl_hostid        | Notes                                           |
+===================+=================================================+
| Tags              | `hostid <#hostid>`__, `MMP <#MMP>`__            |
+-------------------+-------------------------------------------------+
| Kernel module     | spl                                             |
+-------------------+-------------------------------------------------+
| When to change    | to uniquely identify a system when vdevs can be |
|                   | shared across multiple systems                  |
+-------------------+-------------------------------------------------+
| Data Type         | ulong                                           |
+-------------------+-------------------------------------------------+
| Range             | 0=ignore hostid, 1 to 4,294,967,295 (32-bits or |
|                   | 0xffffffff)                                     |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | prior to importing pool                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.1                                          |
+-------------------+-------------------------------------------------+

spl_hostid_path
~~~~~~~~~~~~~~~

``spl_hostid_path`` is the path name for a file that can contain a
unique hostid. For testing purposes, ``spl_hostid_path`` can be
overridden by the ZFS_HOSTID environment variable.

+-------------------+-------------------------------------------------+
| spl_hostid_path   | Notes                                           |
+===================+=================================================+
| Tags              | `hostid <#hostid>`__, `MMP <#MMP>`__            |
+-------------------+-------------------------------------------------+
| Kernel module     | spl                                             |
+-------------------+-------------------------------------------------+
| When to change    | when creating a new ZFS distribution where the  |
|                   | default value is inappropriate                  |
+-------------------+-------------------------------------------------+
| Data Type         | string                                          |
+-------------------+-------------------------------------------------+
| Default           | "/etc/hostid"                                   |
+-------------------+-------------------------------------------------+
| Change            | read-only, can only be changed prior to spl     |
|                   | module load                                     |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.6.1                                          |
+-------------------+-------------------------------------------------+

spl_kmem_alloc_max
~~~~~~~~~~~~~~~~~~

Large ``kmem_alloc()`` allocations fail if they exceed KMALLOC_MAX_SIZE,
as determined by the kernel source. Allocations which are marginally
smaller than this limit may succeed but should still be avoided due to
the expense of locating a contiguous range of free pages. Therefore, a
maximum kmem size with reasonable safely margin of 4x is set.
``kmem_alloc()`` allocations larger than this maximum will quickly fail.
``vmem_alloc()`` allocations less than or equal to this value will use
``kmalloc()``, but shift to ``vmalloc()`` when exceeding this value.

================== ====================
spl_kmem_alloc_max Notes
================== ====================
Tags               `memory <#memory>`__
Kernel module      spl
When to change     TBD
Data Type          uint
Units              bytes
Range              TBD
Default            KMALLOC_MAX_SIZE / 4
Change             Dynamic
Versions Affected  v0.7.0
================== ====================

spl_kmem_alloc_warn
~~~~~~~~~~~~~~~~~~~

As a general rule ``kmem_alloc()`` allocations should be small,
preferably just a few pages since they must by physically contiguous.
Therefore, a rate limited warning is printed to the console for any
``kmem_alloc()`` which exceeds the threshold ``spl_kmem_alloc_warn``

The default warning threshold is set to eight pages but capped at 32K to
accommodate systems using large pages. This value was selected to be
small enough to ensure the largest allocations are quickly noticed and
fixed. But large enough to avoid logging any warnings when a allocation
size is larger than optimal but not a serious concern. Since this value
is tunable, developers are encouraged to set it lower when testing so
any new largish allocations are quickly caught. These warnings may be
disabled by setting the threshold to zero.

+---------------------+-----------------------------------------------+
| spl_kmem_alloc_warn | Notes                                         |
+=====================+===============================================+
| Tags                | `memory <#memory>`__                          |
+---------------------+-----------------------------------------------+
| Kernel module       | spl                                           |
+---------------------+-----------------------------------------------+
| When to change      | developers are encouraged lower when testing  |
|                     | so any new, large allocations are quickly     |
|                     | caught                                        |
+---------------------+-----------------------------------------------+
| Data Type           | uint                                          |
+---------------------+-----------------------------------------------+
| Units               | bytes                                         |
+---------------------+-----------------------------------------------+
| Range               | 0=disable the warnings,                       |
+---------------------+-----------------------------------------------+
| Default             | 32,768 (32 KiB)                               |
+---------------------+-----------------------------------------------+
| Change              | Dynamic                                       |
+---------------------+-----------------------------------------------+
| Versions Affected   | v0.7.0                                        |
+---------------------+-----------------------------------------------+

spl_kmem_cache_expire
~~~~~~~~~~~~~~~~~~~~~

Cache expiration is part of default illumos cache behavior. The idea is
that objects in magazines which have not been recently accessed should
be returned to the slabs periodically. This is known as cache aging and
when enabled objects will be typically returned after 15 seconds.

On the other hand Linux slabs are designed to never move objects back to
the slabs unless there is memory pressure. This is possible because
under Linux the cache will be notified when memory is low and objects
can be released.

By default only the Linux method is enabled. It has been shown to
improve responsiveness on low memory systems and not negatively impact
the performance of systems with more memory. This policy may be changed
by setting the ``spl_kmem_cache_expire`` bit mask as follows, both
policies may be enabled concurrently.

===================== =================================================
spl_kmem_cache_expire Notes
===================== =================================================
Tags                  `memory <#memory>`__
Kernel module         spl
When to change        TBD
Data Type             bitmask
Range                 0x01 - Aging (illumos), 0x02 - Low memory (Linux)
Default               0x02
Change                Dynamic
Versions Affected     v0.6.1 to v0.8.x
===================== =================================================

spl_kmem_cache_kmem_limit
~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the size of a memory cache object it may be backed by
``kmalloc()`` or ``vmalloc()`` memory. This is because the size of the
required allocation greatly impacts the best way to allocate the memory.

When objects are small and only a small number of memory pages need to
be allocated, ideally just one, then ``kmalloc()`` is very efficient.
However, allocating multiple pages with ``kmalloc()`` gets increasingly
expensive because the pages must be physically contiguous.

For this reason we shift to ``vmalloc()`` for slabs of large objects
which which removes the need for contiguous pages. ``vmalloc()`` cannot
be used in all cases because there is significant locking overhead
involved. This function takes a single global lock over the entire
virtual address range which serializes all allocations. Using slightly
different allocation functions for small and large objects allows us to
handle a wide range of object sizes.

The ``spl_kmem_cache_kmem_limit`` value is used to determine this cutoff
size. One quarter of the kernel's compiled PAGE_SIZE is used as the
default value because
`spl_kmem_cache_obj_per_slab <#spl-kmem-cache-obj-per-slab>`__ defaults
to 16. With these default values, at most four contiguous pages are
allocated.

========================= ====================
spl_kmem_cache_kmem_limit Notes
========================= ====================
Tags                      `memory <#memory>`__
Kernel module             spl
When to change            TBD
Data Type                 uint
Units                     pages
Range                     TBD
Default                   PAGE_SIZE / 4
Change                    Dynamic
Versions Affected         v0.7.0 to v0.8.x
========================= ====================

spl_kmem_cache_max_size
~~~~~~~~~~~~~~~~~~~~~~~

``spl_kmem_cache_max_size`` is the maximum size of a kmem cache slab in
MiB. This effectively limits the maximum cache object size to
``spl_kmem_cache_max_size`` /
`spl_kmem_cache_obj_per_slab <#spl-kmem-cache-obj-per-slab>`__ Kmem
caches may not be created with object sized larger than this limit.

======================= =========================================
spl_kmem_cache_max_size Notes
======================= =========================================
Tags                    `memory <#memory>`__
Kernel module           spl
When to change          TBD
Data Type               uint
Units                   MiB
Range                   TBD
Default                 4 for 32-bit kernel, 32 for 64-bit kernel
Change                  Dynamic
Versions Affected       v0.7.0
======================= =========================================

spl_kmem_cache_obj_per_slab
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``spl_kmem_cache_obj_per_slab`` is the preferred number of objects per
slab in the kmem cache. In general, a larger value will increase the
caches memory footprint while decreasing the time required to perform an
allocation. Conversely, a smaller value will minimize the footprint and
improve cache reclaim time but individual allocations may take longer.

=========================== ====================
spl_kmem_cache_obj_per_slab Notes
=========================== ====================
Tags                        `memory <#memory>`__
Kernel module               spl
When to change              TBD
Data Type                   uint
Units                       kmem cache objects
Range                       TBD
Default                     8
Change                      Dynamic
Versions Affected           v0.7.0 to v0.8.x
=========================== ====================

spl_kmem_cache_obj_per_slab_min
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``spl_kmem_cache_obj_per_slab_min`` is the minimum number of objects
allowed per slab. Normally slabs will contain
`spl_kmem_cache_obj_per_slab <#spl-kmem-cache-obj-per-slab>`__ objects
but for caches that contain very large objects it's desirable to only
have a few, or even just one, object per slab.

=============================== ===============================
spl_kmem_cache_obj_per_slab_min Notes
=============================== ===============================
Tags                            `memory <#memory>`__
Kernel module                   spl
When to change                  debugging kmem cache operations
Data Type                       uint
Units                           kmem cache objects
Range                           TBD
Default                         1
Change                          Dynamic
Versions Affected               v0.7.0
=============================== ===============================

spl_kmem_cache_reclaim
~~~~~~~~~~~~~~~~~~~~~~

``spl_kmem_cache_reclaim`` prevents Linux from being able to rapidly
reclaim all the memory held by the kmem caches. This may be useful in
circumstances where it's preferable that Linux reclaim memory from some
other subsystem first. Setting ``spl_kmem_cache_reclaim`` increases the
likelihood out of memory events on a memory constrained system.

+------------------------+--------------------------------------------+
| spl_kmem_cache_reclaim | Notes                                      |
+========================+============================================+
| Tags                   | `memory <#memory>`__                       |
+------------------------+--------------------------------------------+
| Kernel module          | spl                                        |
+------------------------+--------------------------------------------+
| When to change         | TBD                                        |
+------------------------+--------------------------------------------+
| Data Type              | boolean                                    |
+------------------------+--------------------------------------------+
| Range                  | 0=enable rapid memory reclaim from kmem    |
|                        | caches, 1=disable rapid memory reclaim     |
|                        | from kmem caches                           |
+------------------------+--------------------------------------------+
| Default                | 0                                          |
+------------------------+--------------------------------------------+
| Change                 | Dynamic                                    |
+------------------------+--------------------------------------------+
| Versions Affected      | v0.7.0                                     |
+------------------------+--------------------------------------------+

spl_kmem_cache_slab_limit
~~~~~~~~~~~~~~~~~~~~~~~~~

For small objects the Linux slab allocator should be used to make the
most efficient use of the memory. However, large objects are not
supported by the Linux slab allocator and therefore the SPL
implementation is preferred. ``spl_kmem_cache_slab_limit`` is used to
determine the cutoff between a small and large object.

Objects of ``spl_kmem_cache_slab_limit`` or smaller will be allocated
using the Linux slab allocator, large objects use the SPL allocator. A
cutoff of 16 KiB was determined to be optimal for architectures using 4
KiB pages.

+---------------------------+-----------------------------------------+
| spl_kmem_cache_slab_limit | Notes                                   |
+===========================+=========================================+
| Tags                      | `memory <#memory>`__                    |
+---------------------------+-----------------------------------------+
| Kernel module             | spl                                     |
+---------------------------+-----------------------------------------+
| When to change            | TBD                                     |
+---------------------------+-----------------------------------------+
| Data Type                 | uint                                    |
+---------------------------+-----------------------------------------+
| Units                     | bytes                                   |
+---------------------------+-----------------------------------------+
| Range                     | TBD                                     |
+---------------------------+-----------------------------------------+
| Default                   | 16,384 (16 KiB) when kernel PAGE_SIZE = |
|                           | 4KiB, 0 for other PAGE_SIZE values      |
+---------------------------+-----------------------------------------+
| Change                    | Dynamic                                 |
+---------------------------+-----------------------------------------+
| Versions Affected         | v0.7.0                                  |
+---------------------------+-----------------------------------------+

spl_max_show_tasks
~~~~~~~~~~~~~~~~~~

``spl_max_show_tasks`` is the limit of tasks per pending list in each
taskq shown in ``/proc/spl/taskq`` and ``/proc/spl/taskq-all``. Reading
the ProcFS files walks the lists with lock held and it could cause a
lock up if the list grow too large. If the list is larger than the
limit, the string \`"(truncated)" is printed.

================== ===================================
spl_max_show_tasks Notes
================== ===================================
Tags               `taskq <#taskq>`__
Kernel module      spl
When to change     TBD
Data Type          uint
Units              tasks reported
Range              0 disables the limit, 1 to MAX_UINT
Default            512
Change             Dynamic
Versions Affected  v0.7.0
================== ===================================

spl_panic_halt
~~~~~~~~~~~~~~

``spl_panic_halt`` enables kernel panic upon assertion failures. When
not enabled, the asserting thread is halted to facilitate further
debugging.

+-------------------+-------------------------------------------------+
| spl_panic_halt    | Notes                                           |
+===================+=================================================+
| Tags              | `debug <#debug>`__, `panic <#panic>`__          |
+-------------------+-------------------------------------------------+
| Kernel module     | spl                                             |
+-------------------+-------------------------------------------------+
| When to change    | when debugging assertions and kernel core dumps |
|                   | are desired                                     |
+-------------------+-------------------------------------------------+
| Data Type         | boolean                                         |
+-------------------+-------------------------------------------------+
| Range             | 0=halt thread upon assertion, 1=panic kernel    |
|                   | upon assertion                                  |
+-------------------+-------------------------------------------------+
| Default           | 0                                               |
+-------------------+-------------------------------------------------+
| Change            | Dynamic                                         |
+-------------------+-------------------------------------------------+
| Versions Affected | v0.7.0                                          |
+-------------------+-------------------------------------------------+

spl_taskq_kick
~~~~~~~~~~~~~~

Upon writing a non-zero value to ``spl_taskq_kick``, all taskqs are
scanned. If any taskq has a pending task more than 5 seconds old, the
taskq spawns more threads. This can be useful in rare deadlock
situations caused by one or more taskqs not spawning a thread when it
should.

================= =====================
spl_taskq_kick    Notes
================= =====================
Tags              `taskq <#taskq>`__
Kernel module     spl
When to change    See description above
Data Type         uint
Units             N/A
Default           0
Change            Dynamic
Versions Affected v0.7.0
================= =====================

spl_taskq_thread_bind
~~~~~~~~~~~~~~~~~~~~~

``spl_taskq_thread_bind`` enables binding taskq threads to specific
CPUs, distributed evenly over the available CPUs. By default, this
behavior is disabled to allow the Linux scheduler the maximum
flexibility to determine where a thread should run.

+-----------------------+---------------------------------------------+
| spl_taskq_thread_bind | Notes                                       |
+=======================+=============================================+
| Tags                  | `CPU <#CPU>`__, `taskq <#taskq>`__          |
+-----------------------+---------------------------------------------+
| Kernel module         | spl                                         |
+-----------------------+---------------------------------------------+
| When to change        | when debugging CPU scheduling options       |
+-----------------------+---------------------------------------------+
| Data Type             | boolean                                     |
+-----------------------+---------------------------------------------+
| Range                 | 0=taskqs are not bound to specific CPUs,    |
|                       | 1=taskqs are bound to CPUs                  |
+-----------------------+---------------------------------------------+
| Default               | 0                                           |
+-----------------------+---------------------------------------------+
| Change                | prior to loading spl kernel module          |
+-----------------------+---------------------------------------------+
| Versions Affected     | v0.7.0                                      |
+-----------------------+---------------------------------------------+

spl_taskq_thread_dynamic
~~~~~~~~~~~~~~~~~~~~~~~~

``spl_taskq_thread_dynamic`` enables taskqs to set the TASKQ_DYNAMIC
flag will by default create only a single thread. New threads will be
created on demand up to a maximum allowed number to facilitate the
completion of outstanding tasks. Threads which are no longer needed are
promptly destroyed. By default this behavior is enabled but it can be d.

See also
`zfs_zil_clean_taskq_nthr_pct <#zfs-zil-clean-taskq-nthr-pct>`__,
`zio_taskq_batch_pct <#zio-taskq-batch-pct>`__

+--------------------------+------------------------------------------+
| spl_taskq_thread_dynamic | Notes                                    |
+==========================+==========================================+
| Tags                     | `taskq <#taskq>`__                       |
+--------------------------+------------------------------------------+
| Kernel module            | spl                                      |
+--------------------------+------------------------------------------+
| When to change           | disable for performance analysis or      |
|                          | troubleshooting                          |
+--------------------------+------------------------------------------+
| Data Type                | boolean                                  |
+--------------------------+------------------------------------------+
| Range                    | 0=taskq threads are not dynamic, 1=taskq |
|                          | threads are dynamically created and      |
|                          | destroyed                                |
+--------------------------+------------------------------------------+
| Default                  | 1                                        |
+--------------------------+------------------------------------------+
| Change                   | prior to loading spl kernel module       |
+--------------------------+------------------------------------------+
| Versions Affected        | v0.7.0                                   |
+--------------------------+------------------------------------------+

spl_taskq_thread_priority
~~~~~~~~~~~~~~~~~~~~~~~~~

| ``spl_taskq_thread_priority`` allows newly created taskq threads to
  set a non-default scheduler priority. When enabled the priority
  specified when a taskq is created will be applied to all threads
  created by that taskq.
| When disabled all threads will use the default Linux kernel thread
  priority.

+---------------------------+-----------------------------------------+
| spl_taskq_thread_priority | Notes                                   |
+===========================+=========================================+
| Tags                      | `CPU <#CPU>`__, `taskq <#taskq>`__      |
+---------------------------+-----------------------------------------+
| Kernel module             | spl                                     |
+---------------------------+-----------------------------------------+
| When to change            | when troubleshooting CPU                |
|                           | scheduling-related performance issues   |
+---------------------------+-----------------------------------------+
| Data Type                 | boolean                                 |
+---------------------------+-----------------------------------------+
| Range                     | 0=taskq threads use the default Linux   |
|                           | kernel thread priority, 1=              |
+---------------------------+-----------------------------------------+
| Default                   | 1                                       |
+---------------------------+-----------------------------------------+
| Change                    | prior to loading spl kernel module      |
+---------------------------+-----------------------------------------+
| Versions Affected         | v0.7.0                                  |
+---------------------------+-----------------------------------------+

spl_taskq_thread_sequential
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``spl_taskq_thread_sequential`` is the number of items a taskq worker
thread must handle without interruption before requesting a new worker
thread be spawned. ``spl_taskq_thread_sequential`` controls how quickly
taskqs ramp up the number of threads processing the queue. Because Linux
thread creation and destruction are relatively inexpensive a small
default value has been selected. Thus threads are created aggressively,
which is typically desirable. Increasing this value results in a slower
thread creation rate which may be preferable for some configurations.

=========================== ==================================
spl_taskq_thread_sequential Notes
=========================== ==================================
Tags                        `CPU <#CPU>`__, `taskq <#taskq>`__
Kernel module               spl
When to change              TBD
Data Type                   int
Units                       taskq items
Range                       1 to MAX_INT
Default                     4
Change                      Dynamic
Versions Affected           v0.7.0
=========================== ==================================

spl_kmem_cache_kmem_threads
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``spl_kmem_cache_kmem_threads`` shows the current number of
``spl_kmem_cache`` threads. This task queue is responsible for
allocating new slabs for use by the kmem caches. For the majority of
systems and workloads only a small number of threads are required.

+-----------------------------+---------------------------------------+
| spl_kmem_cache_kmem_threads | Notes                                 |
+=============================+=======================================+
| Tags                        | `CPU <#CPU>`__, `memory <#memory>`__  |
+-----------------------------+---------------------------------------+
| Kernel module               | spl                                   |
+-----------------------------+---------------------------------------+
| When to change              | read-only                             |
+-----------------------------+---------------------------------------+
| Data Type                   | int                                   |
+-----------------------------+---------------------------------------+
| Range                       | 1 to MAX_INT                          |
+-----------------------------+---------------------------------------+
| Units                       | threads                               |
+-----------------------------+---------------------------------------+
| Default                     | 4                                     |
+-----------------------------+---------------------------------------+
| Change                      | read-only, can only be changed prior  |
|                             | to spl module load                    |
+-----------------------------+---------------------------------------+
| Versions Affected           | v0.7.0                                |
+-----------------------------+---------------------------------------+

spl_kmem_cache_magazine_size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``spl_kmem_cache_magazine_size`` shows the current . Cache magazines are
an optimization designed to minimize the cost of allocating memory. They
do this by keeping a per-cpu cache of recently freed objects, which can
then be reallocated without taking a lock. This can improve performance
on highly contended caches. However, because objects in magazines will
prevent otherwise empty slabs from being immediately released this may
not be ideal for low memory machines.

For this reason spl_kmem_cache_magazine_size can be used to set a
maximum magazine size. When this value is set to 0 the magazine size
will be automatically determined based on the object size. Otherwise
magazines will be limited to 2-256 objects per magazine (eg per CPU).
Magazines cannot be disabled entirely in this implementation.

+------------------------------+--------------------------------------+
| spl_kmem_cache_magazine_size | Notes                                |
+==============================+======================================+
| Tags                         | `CPU <#CPU>`__, `memory <#memory>`__ |
+------------------------------+--------------------------------------+
| Kernel module                | spl                                  |
+------------------------------+--------------------------------------+
| When to change               |                                      |
+------------------------------+--------------------------------------+
| Data Type                    | int                                  |
+------------------------------+--------------------------------------+
| Units                        | threads                              |
+------------------------------+--------------------------------------+
| Range                        | 0=automatically scale magazine size, |
|                              | otherwise 2 to 256                   |
+------------------------------+--------------------------------------+
| Default                      | 0                                    |
+------------------------------+--------------------------------------+
| Change                       | read-only, can only be changed prior |
|                              | to spl module load                   |
+------------------------------+--------------------------------------+
| Versions Affected            | v0.7.0                               |
+------------------------------+--------------------------------------+
