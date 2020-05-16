Delete a Branch
===============

When a commit has been accepted and merged into the main ZFS repository,
the developer's topic branch should be deleted. This is also appropriate
if the developer abandons the change, and could be appropriate if they
change the direction of the change.

To delete a topic branch, navigate to the base directory of your local
Git repository and use the ``git branch -d (branch-name)`` command. The
name of the branch should be the same as the branch that was created.
