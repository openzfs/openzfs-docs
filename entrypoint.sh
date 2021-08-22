#!/bin/sh
apk add git py3-pip mandoc make
pip install -r docs/requirements.txt
make man
make feature_matrix
make html
