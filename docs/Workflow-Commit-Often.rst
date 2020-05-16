Commit Often
============

When writing complex code, it is strongly suggested that developers save
their changes, and commit those changes to their local repository, on a
frequent basis. In general, this means every hour or two, or when a
specific milestone is hit in the development. This allows you to easily
*checkpoint* your work.

Details of this process can be found in the `Commit the
changes <https://github.com/zfsonlinux/zfs/wiki/Workflow-Commit>`__
page.

In addition, it is suggested that the changes be pushed to your forked
Github repository with the ``git push`` command at least every day, as a
backup. Changes should also be pushed prior to running a test, in case
your system crashes. This project works with kernel software. A crash
while testing development software could easily cause loss of data.

For developers who want to keep their development branches clean, it
might be useful to
`squash <https://github.com/zfsonlinux/zfs/wiki/Workflow-Squash>`__
commits from time to time, even before you're ready to `create a
PR <https://github.com/zfsonlinux/zfs/wiki/Workflow-Create-PR>`__.
