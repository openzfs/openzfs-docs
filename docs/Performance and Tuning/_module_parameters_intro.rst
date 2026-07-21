.. This file is hand-written and included verbatim at the top of the
   generated "Module Parameters" page. Edit it, not the generated page.

Most OpenZFS kernel module parameters are accessible in the SysFS
``/sys/module/zfs/parameters`` directory. Current values can be observed
by

.. code:: shell

   cat /sys/module/zfs/parameters/PARAMETER

Many of these can be changed by writing new values. These are denoted by
``Change: Dynamic`` in the parameter details below.

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
parameters other than in the ``zfs`` kernel module. For example, the
``icp`` kernel module parameters are visible in the
``/sys/module/icp/parameters`` directory and can be set by default at
boot time by changing the ``/etc/modprobe.d/icp.conf`` file.

See the man page for *modprobe.d* for more information.

On FreeBSD the same tunables are exposed as sysctls under the ``vfs.zfs``
tree, for example ``sysctl vfs.zfs.arc.max``, and can be set at boot time
from ``/boot/loader.conf``.

To observe the list of parameters supported by the modules you actually
have installed, along with a short synopsis of each, use the ``modinfo``
command:

.. code:: shell

   modinfo zfs

Manual pages
------------

The `zfs(4) <../man/master/4/zfs.4.html>`__ and
`spl(4) <../man/master/4/spl.4.html>`__ man pages (previously
``zfs-`` and ``spl-module-parameters(5)``, respectively, prior to
OpenZFS 2.1) are the authoritative description of the module parameters
and are shipped with the version of OpenZFS you run.

This page is generated from the same sources for every supported release,
and adds the information that the man pages do not carry: which versions
a parameter exists in, how its default changed between them, and the
accumulated advice of ZFS developers and practitioners about when to
change it.

Use the selector above to restrict the page to the parameters that exist
in a particular OpenZFS release, and the box next to it to narrow the
list down by name. Leave the selector at *All versions* to search the
full history, including parameters that have since been removed.
