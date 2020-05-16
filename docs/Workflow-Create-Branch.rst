Create a Branch
===============

With small projects, it's possible to develop code as commits directly
on the *master* branch. In the ZFS-on-Linux project, that sort of
development would create havoc and make it difficult to open a PR or
rebase the code. For this reason, development in the ZFS-on-Linux
project is done on *topic* branches.

The following commands will perform the required functions:

::

   $ cd zfs
   $ git fetch upstream master
   $ git checkout master
   $ git merge upstream/master
   $ git branch (topic-branch-name)
   $ git checkout (topic-branch-name)

1. Navigate to your *local* repository.
2. Fetch the updates from the *upstream* repository.
3. Set the current branch to *master*.
4. Merge the fetched updates into the *local* repository.
5. Create a new *topic* branch on the updated *master* branch. The name
   of the branch should be either the name of the feature (preferred for
   development of features) or an indication of the issue being worked
   on (preferred for bug fixes).
6. Set the current branch to the newly created *topic* branch.

**Pro Tip**: The ``git checkout -b (topic-branch-name)`` command can be
used to create and checkout a new branch with one command.
