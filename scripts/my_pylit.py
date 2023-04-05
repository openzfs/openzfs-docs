#!/usr/bin/env python3
#
# Copyright 2023 Maurice Zhou <yuchen@apvc.uk>
#
# Released without warranty under the terms of the
# Apache License 2.0.

import pylit

pylit.defaults.code_block_markers['shell'] = '::'
pylit.defaults.text_extensions = [".rst"]

pylit.main()
