illumos Patches
===============

OpenZFS tracks illumos ZFS patches at the
`illumos Tracking <http://build.zfsonlinux.org/openzfs-tracking.html>`__
page. The page shows a list of illumos commits and their status in regard to
the OpenZFS master branch.  This page is no longer regularly updated.

This page describes the process of applying outstanding illumos commits
to OpenZFS and submitting those changes for inclusion. As a
developer this is a great way to familiarize yourself with OpenZFS
and to begin quickly making a valuable contribution to the project. The
following guide assumes you have a `github
account <https://help.github.com/articles/signing-up-for-a-new-github-account/>`__,
are familiar with git, and are used to developing in a Linux
environment.

Porting illumos changes to OpenZFS
----------------------------------

Setup the Environment
~~~~~~~~~~~~~~~~~~~~~

**Clone the source.** Start by making a local clone of the
`zfs <https://github.com/zfsonlinux/zfs>`__ repository.

::

   $ git clone -o zfsonlinux https://github.com/zfsonlinux/zfs.git

**Add remote repositories.** Using the GitHub web interface
`fork <https://help.github.com/articles/fork-a-repo/>`__ the
`zfs <https://github.com/zfsonlinux/zfs>`__ repository in to your
personal GitHub account. Add your new zfs fork and the
`illumos-gate <https://github.com/illumos/illumos-gat/>`__ repository as
remotes and then fetch both repositories. The illumos-gate repository is large
and the initial fetch may take some time over a slow connection.

::

   $ cd zfs 
   $ git remote add <your-github-account> git@github.com:<your-github-account>/zfs.git
   $ git remote add illumos-gate https://github.com/illumos/illumos-gate.git
   $ git fetch --all

**Build the source.** Compile the zfs master branch. This branch
is always kept stable and this is a useful verification that
you have a full build environment installed and all the required
dependencies are available. This may also speed up the compile time
latter for small patches where incremental builds are an option.

::

   $ cd ../zfs
   $ sh autogen.sh && ./configure --enable-debug && make -s -j$(nproc)

Pick a patch
~~~~~~~~~~~~

Consult the `illumos
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
``autoport-ozXXXX`` (XXXX - illumos issue number), try to cherry-pick,
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
every commit you port to OpenZFS. This will allow you to easily
submit your work as a GitHub pull request and it makes it possible to
work on multiple OpenZFS changes concurrently. All development branches
need to be based off of the OpenZFS master branch and it's helpful to name
the branches after the issue number you're working on.

::

   $ git checkout -b illumos-<issue-nr> master

**Generate a patch.** One of the first things you'll notice about the
OpenZFS repository is that it is laid out differently than the
illumos-gate repository. Organizationally it is much flatter, this is
possible because it only contains the code for OpenZFS not an entire OS.
That means that in order to apply a patch from illumos the path names in
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

   $ git am ./illumos-<commit-nr>.diff

**Update the commit message.** By using ``git format-patch`` to generate
the patch and then ``git am`` to apply it the original comment and
authorship will be preserved. However, due to the formatting of the
illumos commit you will likely find that the entire commit comment has
been squashed in to the subject line. Use ``git commit --amend`` to
cleanup the comment and be careful to follow `these standard
guidelines <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`__.

The summary line of an illumos commit is often very long and you should
truncate it to 50 characters. This is useful because it preserves the
correct formatting of ``git log --pretty=oneline`` command. Make sure to
leave a blank line between the summary and body of the commit. Then
include the full illumos commit message wrapping any lines which exceed
72 characters. Finally, add a ``Ported-by`` tag with your contact
information and both a ``illumos-issue`` and ``illumos-commit`` tag with
appropriate links. You'll want to verify your commit contains all of the
following information:

-  The subject line from the original illumos patch in the form:
   "illumos <issue-nr> - short description".
-  The original patch authorship should be preserved.
-  The illumos commit message.
-  The following tags:

   -  **Authored by:** Original patch author
   -  **Reviewed by:** All illumos reviewers from the original patch.
   -  **Approved by:** All illumos reviewers from the original patch.
   -  **Ported-by:** Your name and email address.
   -  **illumos-issue:** https ://www.illumos.org/issues/issue
   -  **illumos-commit:** https
      ://github.com/illumos/illumos-gate/commit/hash

-  **Porting Notes:** An optional section describing any changes
   required when porting.

For example, illumos issue 6873 was `applied to
OpenZFS <https://github.com/openzfs/openzfs/commit/b3744ae>`__ from this
upstream `illumos
commit <https://github.com/illumos/illumos-gate/commit/ee06391>`__.  Note
that this example predates the OpenZFS renaming, so the real commit uses
"OpenZFS" instead of "illumos"; the example below show how it should look
if done today.

::

   illumos 6873 - zfs_destroy_snaps_nvl leaks errlist
      
   Authored by: Chris Williamson <chris.williamson@delphix.com>
   Reviewed by: Matthew Ahrens <mahrens@delphix.com>
   Reviewed by: Paul Dagnelie <pcd@delphix.com>
   Ported-by: Denys Rtveliashvili <denys@rtveliashvili.name>
       
   lzc_destroy_snaps() returns an nvlist in errlist.
   zfs_destroy_snaps_nvl() should nvlist_free() it before returning.
       
   illumos-issue: https://www.illumos.org/issues/6873
   illumos-commit: https://github.com/openzfs/openzfs/commit/ee06391

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
testing <https://github.com/openzfs/zfs-buildbot/>`__. As part of the
testing the change is built for a wide range of Linux distributions and
a battery of functional and stress tests are run to detect regressions.

::

   $ git push <your-github-account> openzfs-<issue-nr>

**Fix any issues.** Testing takes approximately 2 hours to fully
complete and the results are posted in the GitHub `pull
request <https://github.com/openzfs/zfs/pull/4594>`__. All the tests
are expected to pass and you should investigate and resolve any test
failures. The `test
scripts <https://github.com/openzfs/zfs-buildbot/tree/master/scripts>`__
are all available and designed to run locally in order reproduce an
issue. Once you've resolved the issue force update the pull request to
trigger a new round of testing. Iterate until all the tests are passing.

::

   # Fix issue, amend commit, force update branch.
   $ git commit --amend
   $ git push --force <your-github-account> openzfs-<issue-nr>

Merging the Patch
~~~~~~~~~~~~~~~~~

**Review.** Lastly one of the OpenZFS maintainers will make a final
review of the patch and may request additional changes. Once the
maintainer is happy with the final version of the patch they will add
their signed-off-by, merge it to the master branch, mark it complete on
the tracking page, and thank you for your contribution to the project!
