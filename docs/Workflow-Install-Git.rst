Install Git
===========

To work with the ZFS software on Github, it's necessary to install the
Git software on your computer and set it up. This page covers that
process for some common Linux operating systems. Other Linux operating
systems should be similar.

Install the Software Package
----------------------------

The first step is to actually install the Git software package. This
package can be found in the repositories used by most Linux
distributions. If your distribution isn't listed here, or you'd like to
install from source, please have a look in the `official Git
documentation <https://git-scm.com/download/linux>`__.

Red Hat and CentOS
~~~~~~~~~~~~~~~~~~

::

   # yum install git

Fedora
~~~~~~

::

   $ sudo dnf install git

Debian and Ubuntu
~~~~~~~~~~~~~~~~~

::

   $ sudo apt install git

Configuring Git
---------------

Your user name and email address must be set within Git before you can
make commits to the ZFS project. In addition, your preferred text editor
should be set to whatever you would like to use.

::

   $ git config --global user.name "John Doe"
   $ git config --global user.email johndoe@example.com
   $ git config --global core.editor emacs
