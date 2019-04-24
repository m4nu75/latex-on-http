# -*- coding: utf-8 -*-
"""
    latexonhttp.caching.store
    ~~~~~~~~~~~~~~~~~~~~~
    Caching metadata store for Latex-On-HTTP.

    :copyright: (c) 2019 Yoan Tournade.
    :license: AGPL, see LICENSE for more details.
"""
import logging

logger = logging.getLogger(__name__)

# TODO Store to Redis?
# TODO Use init-cache-metadata from resources
CACHE_METADATA = {}


def get_cache_metadata():
    global CACHE_METADATA
    # Returns a copy?
    return CACHE_METADATA


def persist_cache_metadata(metadata):
    # TODO Only allows the API to send updates? (React-like)
    # logger.debug("Cache metadata update: %s", metadata)
    global CACHE_METADATA
    CACHE_METADATA = metadata
    return CACHE_METADATA