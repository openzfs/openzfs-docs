Git and GitHub for beginners (ZoL edition)
==========================================

This is a very basic rundown of how to use Git and GitHub to make
changes.

Recommended reading: `ZFS on Linux
CONTRIBUTING.md <https://github.com/zfsonlinux/zfs/blob/master/.github/CONTRIBUTING.md>`__

First time setup
----------------

If you've never used Git before, you'll need a little setup to start
things off.

::

   git config --global user.name "My Name"
   git config --global user.email myemail@noreply.non

Cloning the initial repository
------------------------------

The easiest way to get started is to click the fork icon at the top of
the main repository page. From there you need to download a copy of the
forked repository to your computer:

::

   git clone https://github.com/<your-account-name>/zfs.git

This sets the "origin" repository to your fork. This will come in handy
when creating pull requests. To make pulling from the "upstream"
repository as changes are made, it is very useful to establish the
upstream repository as another remote (man git-remote):

::

   cd zfs
   git remote add upstream https://github.com/zfsonlinux/zfs.git

Preparing and making changes
----------------------------

In order to make changes it is recommended to make a branch, this lets
you work on several unrelated changes at once. It is also not
recommended to make changes to the master branch unless you own the
repository.

::

   git checkout -b my-new-branch

From here you can make your changes and move on to the next step.

Recommended reading: `C Style and Coding Standards for
SunOS <https://www.cis.upenn.edu/~lee/06cse480/data/cstyle.ms.pdf>`__,
`ZFS on Linux Developer
Resources <https://github.com/zfsonlinux/zfs/wiki/Developer-Resources>`__,
`OpenZFS Developer
Resources <https://openzfs.org/wiki/Developer_resources>`__

Testing your patches before pushing
-----------------------------------

Before committing and pushing, you may want to test your patches. There
are several tests you can run against your branch such as style
checking, and functional tests. All pull requests go through these tests
before being pushed to the main repository, however testing locally
takes the load off the build/test servers. This step is optional but
highly recommended, however the test suite should be run on a virtual
machine or a host that currently does not use ZFS. You may need to
install ``shellcheck`` and ``flake8`` to run the ``checkstyle``
correctly.

::

   sh autogen.sh
   ./configure
   make checkstyle

Recommended reading: `Building
ZFS <https://github.com/zfsonlinux/zfs/wiki/Building-ZFS>`__, `ZFS Test
Suite
README <https://github.com/zfsonlinux/zfs/blob/master/tests/README.md>`__

Committing your changes to be pushed
------------------------------------

When you are done making changes to your branch there are a few more
steps before you can make a pull request.

::

   git commit --all --signoff

This command opens an editor and adds all unstaged files from your
branch. Here you need to describe your change and add a few things:

::


   # Please enter the commit message for your changes. Lines starting
   # with '#' will be ignored, and an empty message aborts the commit.
   # On branch my-new-branch
   # Changes to be committed:
   #   (use "git reset HEAD <file>..." to unstage)
   #
   #   modified:   hello.c
   #

The first thing we need to add is the commit message. This is what is
displayed on the git log, and should be a short description of the
change. By style guidelines, this has to be less than 72 characters in
length.

Underneath the commit message you can add a more descriptive text to
your commit. The lines in this section have to be less than 72
characters.

When you are done, the commit should look like this:

::

   Add hello command

   This is a test commit with a descriptive commit message.
   This message can be more than one line as shown here.

   Signed-off-by: My Name <myemail@noreply.non>
   Closes #9998
   Issue #9999
   # Please enter the commit message for your changes. Lines starting
   # with '#' will be ignored, and an empty message aborts the commit.
   # On branch my-new-branch
   # Changes to be committed:
   #   (use "git reset HEAD <file>..." to unstage)
   #
   #   modified:   hello.c
   #

You can also reference issues and pull requests if you are filing a pull
request for an existing issue as shown above. Save and exit the editor
when you are done.

Pushing and creating the pull request
-------------------------------------

Home stretch. You've made your change and made the commit. Now it's time
to push it.

::

   git push --set-upstream origin my-new-branch

This should ask you for your github credentials and upload your changes
to your repository.

The last step is to either go to your repository or the upstream
repository on GitHub and you should see a button for making a new pull
request for your recently committed branch.

Correcting issues with your pull request
----------------------------------------

Sometimes things don't always go as planned and you may need to update
your pull request with a correction to either your commit message, or
your changes. This can be accomplished by re-pushing your branch. If you
need to make code changes or ``git add`` a file, you can do those now,
along with the following:

::

   git commit --amend
   git push --force

This will return you to the commit editor screen, and push your changes
over top of the old ones. Do note that this will restart the process of
any build/test servers currently running and excessively pushing can
cause delays in processing of all pull requests.

Maintaining your repository
---------------------------

When you wish to make changes in the future you will want to have an
up-to-date copy of the upstream repository to make your changes on. Here
is how you keep updated:

::

   git checkout master
   git pull upstream master
   git push origin master

This will make sure you are on the master branch of the repository, grab
the changes from upstream, then push them back to your repository.

Final words
-----------

This is a very basic introduction to Git and GitHub, but should get you
on your way to contributing to many open source projects. Not all
projects have style requirements and some may have different processes
to getting changes committed so please refer to their documentation to
see if you need to do anything different. One topic we have not touched
on is the ``git rebase`` command which is a little more advanced for
this wiki article.

Additional resources: `Github Help <https://help.github.com/>`__,
`Atlassian Git Tutorials <https://www.atlassian.com/git/tutorials>`__
