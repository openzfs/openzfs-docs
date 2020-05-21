.. image:: docs/_static/img/logo/480px-Open-ZFS-Secondary-Logo-Colour-halfsize.png

OpenZFS Documentation
=====================

Public link: https://openzfs.github.io/openzfs-docs/

Local build
-----------

::

  cd ./docs/
  # install dependencies:
  pip install -r requirements.txt
  # run `sphinx` to build pages
  make html
  # html files will be generated in:
  cd ./docs/_build/html/
