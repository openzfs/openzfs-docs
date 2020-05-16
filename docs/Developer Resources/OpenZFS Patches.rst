OpenZFS Patches
===============

The ZFS on Linux project is an adaptation of the upstream `OpenZFS
repository <https://github.com/openzfs/openzfs/>`__ designed to work in
a Linux environment. This upstream repository acts as a location where
new features, bug fixes, and performance improvements from all the
OpenZFS platforms can be integrated. Each platform is responsible for
tracking the OpenZFS repository and merging the relevant improvements
back in to their release.

For the ZFS on Linux project this tracking is managed through an
`OpenZFS tracking <http://build.zfsonlinux.org/openzfs-tracking.html>`__
page. The page is updated regularly and shows a list of OpenZFS commits
and their status in regard to the ZFS on Linux master branch.

This page describes the process of applying outstanding OpenZFS commits
to ZFS on Linux and submitting those changes for inclusion. As a
developer this is a great way to familiarize yourself with ZFS on Linux
and to begin quickly making a valuable contribution to the project. The
following guide assumes you have a `github
account <https://help.github.com/articles/signing-up-for-a-new-github-account/>`__,
are familiar with git, and are used to developing in a Linux
environment.

Porting OpenZFS changes to ZFS on Linux
---------------------------------------

Setup the Environment
~~~~~~~~~~~~~~~~~~~~~

**Clone the source.** Start by making a local clone of the
`spl <https://github.com/zfsonlinux/spl>`__ and
`zfs <https://github.com/zfsonlinux/zfs>`__ repositories.

::

   $ git clone -o zfsonlinux https://github.com/zfsonlinux/spl.git
   $ git clone -o zfsonlinux https://github.com/zfsonlinux/zfs.git

**Add remote repositories.** Using the GitHub web interface
`fork <https://help.github.com/articles/fork-a-repo/>`__ the
`zfs <https://github.com/zfsonlinux/zfs>`__ repository in to your
personal GitHub account. Add your new zfs fork and the
`openzfs <https://github.com/openzfs/openzfs/>`__ repository as remotes
and then fetch both repositories. The OpenZFS repository is large and
the initial fetch may take some time over a slow connection.

::

   $ cd zfs 
   $ git remote add <your-github-account> git@github.com:<your-github-account>/zfs.git
   $ git remote add openzfs https://github.com/openzfs/openzfs.git
   $ git fetch --all

**Build the source.** Compile the spl and zfs master branches. These
branches are always kept stable and this is a useful verification that
you have a full build environment installed and all the required
dependencies are available. This may also speed up the compile time
latter for small patches where incremental builds are an option.

::

   $ cd ../spl
   $ sh autogen.sh && ./configure --enable-debug && make -s -j$(nproc)
   $
   $ cd ../zfs
   $ sh autogen.sh && ./configure --enable-debug && make -s -j$(nproc)

Pick a patch
~~~~~~~~~~~~

Consult the `OpenZFS
tracking <http://build.zfsonlinux.org/openzfs-tracking.html>`__ page and
select a patch which has not yet been applied. For your first patch you
will want to select a small patch to familiarize yourself with the
process.

Porting a Patch
~~~~~~~~~~~~~~~

There are 2 methods:

-  `cherry-pick (easier) <#cherry-pick>`__
-  `manual merge <#manual-merge>`__

Please read about `manual merge <#manual-merge>`__ first to learn the
whole process.

Cherry-pick
^^^^^^^^^^^

You can start to
`cherry-pick <https://git-scm.com/docs/git-cherry-pick>`__ by your own,
but we have made a special
`script <https://github.com/zfsonlinux/zfs-buildbot/blob/master/scripts/openzfs-merge.sh>`__,
which tries to
`cherry-pick <https://git-scm.com/docs/git-cherry-pick>`__ the patch
automatically and generates the description.

0) Prepare environment:

Mandatory git settings (add to ``~/.gitconfig``):

::

   [merge]
       renameLimit = 999999
   [user]
       email = mail@yourmail.com
       name = Your Name

Download the script:

::

   wget https://raw.githubusercontent.com/zfsonlinux/zfs-buildbot/master/scripts/openzfs-merge.sh

1) Run:

::

   ./openzfs-merge.sh -d path_to_zfs_folder -c openzfs_commit_hash

This command will fetch all repositories, create a new branch
``autoport-ozXXXX`` (XXXX - OpenZFS issue number), try to cherry-pick,
compile and check cstyle on success.

If it succeeds without any merge conflicts - go to ``autoport-ozXXXX``
branch, it will have ready to pull commit. Congratulations, you can go
to step 7!

Otherwise you should go to step 2.

2) Resolve all merge conflicts manually. Easy method - install
   `Meld <http://meldmerge.org/>`__ or any other diff tool and run
   ``git mergetool``.

3) Check all compile and cstyle errors (See `Testing a
   patch <#testing-a-patch>`__).

4) Commit your changes with any description.

5) Update commit description (last commit will be changed):

::

   ./openzfs-merge.sh -d path_to_zfs_folder -g openzfs_commit_hash

6) Add any porting notes (if you have modified something):
   ``git commit --amend``

7) Push your commit to github:
   ``git push <your-github-account> autoport-ozXXXX``

8) Create a pull request to ZoL master branch.

9) Go to `Testing a patch <#testing-a-patch>`__ section.

Manual merge
^^^^^^^^^^^^

**Create a new branch.** It is important to create a new branch for
every commit you port to ZFS on Linux. This will allow you to easily
submit your work as a GitHub pull request and it makes it possible to
work on multiple OpenZFS changes concurrently. All development branches
need to be based off of the ZFS master branch and it's helpful to name
the branches after the issue number you're working on.

::

   $ git checkout -b openzfs-<issue-nr> master

**Generate a patch.** One of the first things you'll notice about the
ZFS on Linux repository is that it is laid out differently than the
OpenZFS repository. Organizationally it is much flatter, this is
possible because it only contains the code for OpenZFS not an entire OS.
That means that in order to apply a patch from OpenZFS the path names in
the patch must be changed. A script called zfs2zol-patch.sed has been
provided to perform this translation. Use the ``git format-patch``
command and this script to generate a patch.

::

   $ git format-patch --stdout <commit-hash>^..<commit-hash> | \
       ./scripts/zfs2zol-patch.sed >openzfs-<issue-nr>.diff

**Apply the patch.** In many cases the generated patch will apply
cleanly to the repository. However, it's important to keep in mind the
zfs2zol-patch.sed script only translates the paths. There are often
additional reasons why a patch might not apply. In some cases hunks of
the patch may not be applicable to Linux and should be dropped. In other
cases a patch may depend on other changes which must be applied first.
The changes may also conflict with Linux specific modifications. In all
of these cases the patch will need to be manually modified to apply
cleanly while preserving the its original intent.

::

   $ git am ./openzfs-<commit-nr>.diff

**Update the commit message.** By using ``git format-patch`` to generate
the patch and then ``git am`` to apply it the original comment and
authorship will be preserved. However, due to the formatting of the
OpenZFS commit you will likely find that the entire commit comment has
been squashed in to the subject line. Use ``git commit --amend`` to
cleanup the comment and be careful to follow `these standard
guidelines <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`__.

The summary line of an OpenZFS commit is often very long and you should
truncate it to 50 characters. This is useful because it preserves the
correct formatting of ``git log --pretty=oneline`` command. Make sure to
leave a blank line between the summary and body of the commit. Then
include the full OpenZFS commit message wrapping any lines which exceed
72 characters. Finally, add a ``Ported-by`` tag with your contact
information and both a ``OpenZFS-issue`` and ``OpenZFS-commit`` tag with
appropriate links. You'll want to verify your commit contains all of the
following information:

-  The subject line from the original OpenZFS patch in the form:
   "OpenZFS <issue-nr> - short description".
-  The original patch authorship should be preserved.
-  The OpenZFS commit message.
-  The following tags:

   -  **Authored by:** Original patch author
   -  **Reviewed by:** All OpenZFS reviewers from the original patch.
   -  **Approved by:** All OpenZFS reviewers from the original patch.
   -  **Ported-by:** Your name and email address.
   -  **OpenZFS-issue:** https ://www.illumos.org/issues/issue
   -  **OpenZFS-commit:** https
      ://github.com/openzfs/openzfs/commit/hash

-  **Porting Notes:** An optional section describing any changes
   required when porting.

For example, OpenZFS issue 6873 was `applied to
Linux <https://github.com/zfsonlinux/zfs/commit/b3744ae>`__ from this
upstream `OpenZFS
commit <https://github.com/openzfs/openzfs/commit/ee06391>`__.

::

   OpenZFS 6873 - zfs_destroy_snaps_nvl leaks errlist
      
   Authored by: Chris Williamson <chris.williamson@delphix.com>
   Reviewed by: Matthew Ahrens <mahrens@delphix.com>
   Reviewed by: Paul Dagnelie <pcd@delphix.com>
   Ported-by: Denys Rtveliashvili <denys@rtveliashvili.name>
       
   lzc_destroy_snaps() returns an nvlist in errlist.
   zfs_destroy_snaps_nvl() should nvlist_free() it before returning.
       
   OpenZFS-issue: https://www.illumos.org/issues/6873
   OpenZFS-commit: https://github.com/openzfs/openzfs/commit/ee06391

Testing a Patch
~~~~~~~~~~~~~~~

**Build the source.** Verify the patched source compiles without errors
and all warnings are resolved.

::

   $ make -s -j$(nproc)

**Run the style checker.** Verify the patched source passes the style
checker, the command should return without printing any output.

::

   $ make cstyle

**Open a Pull Request.** When your patch builds cleanly and passes the
style checks `open a new pull
request <https://help.github.com/articles/creating-a-pull-request/>`__.
The pull request will be queued for `automated
testing <https://github.com/zfsonlinux/zfs-buildbot/>`__. As part of the
testing the change is built for a wide range of Linux distributions and
a battery of functional and stress tests are run to detect regressions.

::

   $ git push <your-github-account> openzfs-<issue-nr>

**Fix any issues.** Testing takes approximately 2 hours to fully
complete and the results are posted in the GitHub `pull
request <https://github.com/zfsonlinux/zfs/pull/4594>`__. All the tests
are expected to pass and you should investigate and resolve any test
failures. The `test
scripts <https://github.com/zfsonlinux/zfs-buildbot/tree/master/scripts>`__
are all available and designed to run locally in order reproduce an
issue. Once you've resolved the issue force update the pull request to
trigger a new round of testing. Iterate until all the tests are passing.

::

   # Fix issue, amend commit, force update branch.
   $ git commit --amend
   $ git push --force <your-github-account> openzfs-<issue-nr>

Merging the Patch
~~~~~~~~~~~~~~~~~

**Review.** Lastly one of the ZFS on Linux maintainers will make a final
review of the patch and may request additional changes. Once the
maintainer is happy with the final version of the patch they will add
their signed-off-by, merge it to the master branch, mark it complete on
the tracking page, and thank you for your contribution to the project!

Porting ZFS on Linux changes to OpenZFS
---------------------------------------

Often an issue will be first fixed in ZFS on Linux or a new feature
developed. Changes which are not Linux specific should be submitted
upstream to the OpenZFS GitHub repository for review. The process for
this is described in the `OpenZFS
README <https://github.com/openzfs/openzfs/>`__.
