# -*- coding: utf-8 -*-
"""
    latexonhttp.resources.misc
    ~~~~~~~~~~~~~~~~~~~~~
    Resources utils.

    :copyright: (c) 2019 Yoan Tournade.
    :license: AGPL, see LICENSE for more details.
"""
import hashlib
import sys


def process_resource_data_spec(data):
    return {
        "hash": hashlib.sha256(data).hexdigest(),
        # https://docs.python.org/3/library/sys.html#sys.getsizeof
        # What we would like it too have an accurate estimation of size
        # (when written) on disk of the data (not on memory).
        # "size": sys.getsizeof(data)
        "size": len(data),
    }
