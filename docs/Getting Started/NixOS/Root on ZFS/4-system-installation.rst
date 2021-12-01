.. highlight:: sh

System Installation
======================

.. contents:: Table of Contents
   :local:


Additional configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

As NixOS configuration is declarative, post-installation tasks,
such as user accounts and package selection, can all be done by
specifing them in configuration. See `NixOS manual <https://nixos.org/nixos/manual/>`__
for details.

For timezone, hostname, networking, keyboard layout, etc,
see ``/mnt/etc/nixos/configuration.nix``.

Set root password
-----------------

This optional step is an example
of declaratively configuring the system.

#. Generate password hash::

    INST_ROOT_PASSWD=$(mkpasswd -m SHA-512 -s)

#. Declare `initialHashedPassword
   <https://nixos.org/manual/nixos/stable/options.html#opt-users.users._name_.initialHashedPassword>`__
   for root user::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
      users.users.root.initialHashedPassword = "${INST_ROOT_PASSWD}";
    EOF

System installation
~~~~~~~~~~~~~~~~~~~

#. Finalize the config file::

    tee -a /mnt/etc/nixos/${INST_CONFIG_FILE} <<EOF
    }
    EOF

#. Take a snapshot of the clean installation, without state
   for future use::

    zfs snapshot -r rpool_$INST_UUID/$INST_ID@install_start
    zfs snapshot -r bpool_$INST_UUID/$INST_ID@install_start

#. Apply configuration

   If root password hash is not set::

    nixos-install -v --show-trace --root /mnt

   You will be prompted for a new root password.

   If password hash has been set::

    nixos-install -v --show-trace --no-root-passwd --root /mnt


Finish installation
~~~~~~~~~~~~~~~~~~~~

#. Take a snapshot of the clean installation for future use::

    zfs snapshot -r rpool_$INST_UUID/$INST_ID@install
    zfs snapshot -r bpool_$INST_UUID/$INST_ID@install

#. Unmount EFI system partition::

    umount /mnt/boot/efis/*
    umount /mnt/boot/efi

#. Export pools::

    zpool export bpool_$INST_UUID
    zpool export rpool_$INST_UUID

#. Reboot::

    reboot

Immutable root file system
~~~~~~~~~~~~~~~~~~~~~~~~~~

This section is optional.

Often, programs generate mutable files in paths such as
``/etc`` and ``/var/lib``. The generated files can be considered a
part of the system state.

This generated state is not declaratively managed
by NixOS and can not be reproduced from NixOS configuration.

To ensure that the system state is fully managed by NixOS and reproducible,
we need to periodically purge the system state and let NixOS 
regenerate root file system from scratch.

Also see: `Erase your darlings: 
immutable infrastructure for mutable systems <https://grahamc.com/blog/erase-your-darlings>`__.

Save mutable data to alternative path
-------------------------------------

Before enabling purging on root dataset, we need to back up
essential mutable data first, such as host SSH key and network connections.
Below are some tips.

- Some programs support specifying another
  location for mutable data, such as
  Wireguard::

   networking.wireguard.interfaces.wg0.privateKeyFile = "/state/etc/wireguard/wg0";

- For programs without a configurable data path,
  `environment.etc <https://nixos.org/manual/nixos/stable/options.html#opt-environment.etc>`__
  may be used::

   environment.etc = { 
     "ssh/ssh_host_rsa_key".source = "/state/etc/ssh/ssh_host_rsa_key";
   }

- systemd’s tmpfiles.d rules are also an option::

   systemd.tmpfiles.rules = [
     "L /var/lib/bluetooth - - - - /state/var/lib/bluetooth"
   ];

- Bind mount::

   for i in {/etc/nixos,/etc/cryptkey.d}; do
     mkdir -p /state/$i /$i
     mount -o bind /state/$i /$i
   done
   nixos-generate-config --show-hardware-config

Boot from empty root file system
--------------------------------

After backing up mutable data, you can try switching to
an empty dataset as root file system.

#. Check current root file system::

    ROOT_FS=$(df --output=source /|tail -n1)
    # rpool/ROOT/default

#. Set empty file system as root::

    sed -i "s,${ROOT_FS},${ROOT_FS%/*}/empty,g" /etc/nixos/hardware-configuration-zfs.nix

#. Apply changes and reboot::

    nixos-rebuild boot
    reboot

#. If everything went fine, add the output of the following command to configuration::

    ROOT_FS=$(df --output=source /|tail -n1)
    cat <<EOF
      boot.initrd.postDeviceCommands = ''
        zpool import -Nf ${ROOT_FS%%/*}
        zfs rollback -r ${ROOT_FS%/*}/empty@start
      '';
    EOF

#. Apply and reboot::

    nixos-rebuild boot
    reboot
