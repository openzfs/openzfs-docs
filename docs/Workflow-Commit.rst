Commit the Changes
==================

In order for your changes to be merged into the ZFS on Linux project,
you must first send the changes made in your *topic* branch to your
*local* repository. This can be done with the ``git commit -sa``. If
there are any new files, they will be reported as *untracked*, and they
will not be created in the *local* repository. To add newly created
files to the *local* repository, use the ``git add (file-name) ...``
command.

The ``-s`` option adds a *signed off by* line to the commit. This
*signed off by* line is required for the ZFS on Linux project. It
performs the following functions:

-  It is an acceptance of the `License
   Terms <https://github.com/zfsonlinux/zfs/blob/master/COPYRIGHT>`__ of
   the project.
-  It is the developer's certification that they have the right to
   submit the patch for inclusion into the code base.
-  It indicates agreement to the `Developer's Certificate of
   Origin <https://www.kernel.org/doc/html/latest/process/submitting-patches.html#sign-your-work-the-developer-s-certificate-of-origin>`__.

The ``-a`` option causes all modified files in the current branch to be
*staged* prior to performing the commit. A list of the modified files in
the *local* branch can be created by the use of the ``git status``
command. If there are files that have been modified that shouldn't be
part of the commit, they can either be rolled back in the current
branch, or the files can be manually staged with the
``git add (file-name) ...`` command, and the ``git commit -s`` command
can be run without the ``-a`` option.

When you run the ``git commit`` command, an editor will appear to allow
you to enter the commit messages. The following requirements apply to a
commit message:

-  The first line is a title for the commit, and must be bo longer than
   50 characters.
-  The second line should be blank, separating the title of the commit
   message from the body of the commit message.
-  There may be one or more lines in the commit message describing the
   reason for the changes (the body of the commit message). These lines
   must be no longer than 72 characters, and may contain blank lines.

   -  If the commit closes an Issue, there should be a line in the body
      with the string ``Closes``, followed by the issue number. If
      multiple issues are closed, multiple lines should be used.

-  After the body of the commit message, there should be a blank line.
   This separates the body from the *signed off by* line.
-  The *signed off by* line should have been created by the
   ``git commit -s`` command. If not, the line has the following format:

   -  The string "Signed-off-by:"
   -  The name of the developer. Please do not use any no pseudonyms or
      make any anonymous contributions.
   -  The email address of the developer, enclosed by angle brackets
      ("<>").
   -  An example of this is
      ``Signed-off-by: Random Developer <random@developer.example.org>``

-  If the commit changes only documentation, the line
   ``Requires-builders: style`` may be included in the body. This will
   cause only the *style* testing to be run. This can save a significant
   amount of time when Github runs the automated testing. For
   information on other testing options, please see the `Buildbot
   options <https://github.com/zfsonlinux/zfs/wiki/Buildbot-Options>`__
   page.

For more information about writing commit messages, please visit `How to
Write a Git Commit
Message <https://chris.beams.io/posts/git-commit/>`__.

After the changes have been committed to your *local* repository, they
should be pushed to your *forked* repository. This is done with the
``git push`` command.
