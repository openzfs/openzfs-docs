Rebase the Update
=================

Updates to the ZFS on Linux project should always be based on the
current *master* branch. This makes them easier to merge into the
repository.

There are two steps in the rebase process. The first step is to update
the *local master* branch from the *upstream master* repository. This
can be done by entering the following commands:

::

   $ git fetch upstream master
   $ git checkout master
   $ git merge upstream/master

The second step is to perform the actual rebase of the updates. This is
done by entering the command ``git rebase upstream/master``. If there
are any conflicts between the updates in your *local* branch and the
updates in the *upstream master* branch, you will be informed of them,
and allowed to correct them (see the
`Conflicts <https://github.com/zfsonlinux/zfs/wiki/Workflow-Conflicts>`__
page).

This would also be a good time to
`squash <https://github.com/zfsonlinux/zfs/wiki/Workflow-Squash>`__ your
commits.
