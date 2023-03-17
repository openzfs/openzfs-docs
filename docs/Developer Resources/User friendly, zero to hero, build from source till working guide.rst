User friendly, zero to hero, build from source till working guide (Ubuntu based)
================================================================================

GitHub Repositories
~~~~~~~~~~~~~~~~~~~

The official source for OpenZFS is maintained at GitHub by the `openzfs <https://github.com/openzfs/>`__ organization. The primary git repository for the project is the `zfs <https://github.com/openzfs/zfs>`__ repository.

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

The first thing you'll need to do is prepare your environment by installing a full development tool chain. In addition, development headers for both the kernel and the following packages must be available. It is important to note that if the development kernel headers for the currently running kernel aren't installed, the modules won't compile properly.

The following dependencies should be installed to build the latest ZFS release.

-  **Debian, Ubuntu**:

.. code:: sh

  sudo apt install -y \
    build-essential \
    autoconf \
    automake \
    libtool \
    gawk \
    alien \
    fakeroot \
    dkms \
    libblkid-dev \
    uuid-dev \
    libudev-dev \
    libssl-dev \
    zlib1g-dev \
    libaio-dev \
    libattr1-dev \
    libelf-dev \
    linux-headers-generic \
    python3 \
    python3-dev \
    python3-setuptools \
    python3-cffi \
    libffi-dev \
    python3-packaging \
    git \
    libcurl4-openssl-dev

-  **Ansible**:

.. code:: sh

  - ansible.builtin.package:
      name:
        - build-essential
        - autoconf
        - automake
        - libtool
        - gawk
        - alien
        - fakeroot
        - dkms
        - libblkid-dev
        - uuid-dev
        - libudev-dev
        - libssl-dev
        - zlib1g-dev
        - libaio-dev
        - libattr1-dev
        - libelf-dev
        - linux-headers-generic
        - python3
        - python3-dev
        - python3-setuptools
        - python3-cffi
        - libffi-dev
        - python3-packaging
        - git
        - libcurl4-openssl-dev
      state: latest
      update_cache: true
    become: true

Getting the sources
~~~~~~~~~~~~~~~~~~~

Clone from GitHub
^^^^^^^^^^^^^^^^^

Start by cloning the ZFS repository from GitHub. The repository has a **master** branch for development and a series of **\*-release** branches for tagged releases. After checking out the repository your clone will default to the master branch. Tagged releases may be built by checking out zfs-x.y.z tags with matching version numbers or matching release branches.

-  **Debian, Ubuntu**:

.. code:: sh

  sudo chmod 777 /opt
  git clone https://github.com/openzfs/zfs

-  **Ansible**:

.. code:: sh

  - ansible.builtin.file:
      path: /opt
      mode: '0777'
    become: true

  - ansible.builtin.git:
      repo: https://github.com/openzfs/zfs.git
      dest: /opt/zfs
      version: master

Preparing the rest of the system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now pay attention to how your distribution handles kernel modules. On Ubuntu, for example, the modules from this repository install in the ``extra`` kernel module path, which is not in the standard ``depmod`` search path. Therefore, for the duration of your testing, edit ``/etc/depmod.d/ubuntu.conf`` and add ``extra`` to the beginning of the search path.

-  **Debian, Ubuntu**:

.. code:: sh

  sudo vim /etc/depmod.d/ubuntu.conf

-  **Ansible**:

.. code:: sh

  - ansible.builtin.lineinfile:
      dest: /etc/depmod.d/ubuntu.conf
      regexp: '^(search updates ubuntu built-in)$'
      line: '\1 extra'
      backrefs: yes
    become: true

Building
~~~~~~~~

The ZFS build system is based on GNU Autoconf and GNU Automake. So the first step is to run the ``autogen.sh`` script to generate the ``configure`` script. This script is used to configure the build environment and generate the ``Makefile`` used to build the ZFS modules.

- **Debian, Ubuntu**:

.. code:: sh

  git clean -fx
  ./autogen.sh
  ./configure --enable-systemd
  make -s -j$(nproc) deb-utils deb-dkms

- **Ansible**:

.. code:: sh

  - ansible.builtin.shell: |
      git clean -fx
    args:
      executable: /bin/bash
      chdir: /opt/zfs

  - ansible.builtin.shell: |
      ./autogen.sh
    args:
      executable: /bin/bash
      chdir: /opt/zfs

  - ansible.builtin.shell: |
      ./configure --enable-systemd
    args:
      executable: /bin/bash
      chdir: /opt/zfs

  - ansible.builtin.shell: |
      make -j$(nproc) deb-utils deb-dkms
    args:
      executable: /bin/bash
      chdir: /opt/zfs

Installing
~~~~~~~~~~

The ZFS packages are built using the ``Debian Package`` format. The packages are built using the ``make deb-utils deb-dkms`` command. The ``deb-utils`` package contains the ``zfs`` and ``zpool`` user space utilities. The ``deb-dkms`` package contains the ZFS kernel modules and a DKMS configuration file. DKMS is used to automatically rebuild and install the kernel modules when a new kernel is installed.

- **Debian, Ubuntu**:

.. code:: sh

  sudo apt install ./*.deb

- **Ansible**:

.. code:: sh

  - ansible.builtin.shell: |
      shopt -s extglob
      apt install ./*.deb
    args:
      executable: /bin/bash
      chdir: /opt/zfs
    become: true

Post Install
~~~~~~~~~~~~

After installing the ZFS packages, the ZFS services must be enabled and started. The ``zfs-import-cache`` service is responsible for importing the ZFS pools during system boot. The ``zfs-mount`` service is responsible for mounting all filesystems in the system's root pool. The ``zfs-zed`` service is responsible for monitoring the system for events and taking appropriate actions. The ``zfs-share`` service is responsible for automatically sharing any ZFS filesystems marked as shareable. The ``zfs.target`` is a convenience target that will start all of the ZFS services. The ``zfs-import.target`` is a convenience target that will start the ``zfs-import-cache`` and ``zfs-import-scan`` services.

- **Debian, Ubuntu**:

.. code:: sh

  sudo service enable \
    zfs-import-cache \
    zfs-import.target \
    zfs-mount \
    zfs-zed \
    zfs-share \
    zfs-volume-wait \
    zfs.target
  sudo service start \
    zfs-import-cache \
    zfs-import.target \
    zfs-mount \
    zfs-zed \
    zfs-share \
    zfs-volume-wait \
    zfs.target

- **Ansible**:

.. code:: sh

  - ansible.builtin.service:
      name:
        - zfs-import-cache
        - zfs-import.target
        - zfs-mount
        - zfs-share
        - zfs-zed
        - zfs-volume-wait
        - zfs.target
      state: started
      enabled: yes
    become: true

Final step
~~~~~~~~~~

Now reboot, and you should be able to use ZFS.
