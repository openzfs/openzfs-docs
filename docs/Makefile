# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

html: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

zfs_root_test:
	../scripts/zfs_root_guide_preprocessor.sh $(SOURCEDIR) $(BUILDDIR)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Gen man pages
ZFS_GIT_REPO = https://github.com/openzfs/zfs.git
ZFS_GIT_DIR = ./_build/zfs

.PHONY: man
man:
	if [ ! -d $(ZFS_GIT_DIR) ]; then \
		git clone --depth=1 $(ZFS_GIT_REPO) ./_build/zfs ; \
	else \
		git -C $(ZFS_GIT_DIR) pull ; \
	fi
	../scripts/man_pages.py ./_build/zfs/man ./

.PHONY: feature_matrix
feature_matrix:
	../scripts/compatibility_matrix.py ./_build/
