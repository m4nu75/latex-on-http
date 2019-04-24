# -*- coding: utf-8 -*-
"""
    latexonhttp.api.builds
    ~~~~~~~~~~~~~~~~~~~~~
    Manage Latex builds / compilations.

    :copyright: (c) 2017-2019 Yoan Tournade.
    :license: AGPL, see LICENSE for more details.
"""
import logging
from flask import Blueprint, request, jsonify, Response
from latexonhttp.compiler import latexToPdf
from latexonhttp.resources.normalization import normalize_resources_input
from latexonhttp.resources.validation import check_resources_prefetch
from latexonhttp.resources.fetching import fetch_resources
from latexonhttp.resources.utils import process_resource_data_spec
from latexonhttp.workspaces.lifecycle import create_workspace, remove_workspace
from latexonhttp.workspaces.filesystem import (
    get_workspace_root_path,
    persist_resource_to_workspace,
)
from latexonhttp.caching.resources import (
    forward_resource_to_cache,
    get_resource_from_cache,
)

from pprint import pformat

logger = logging.getLogger(__name__)

builds_app = Blueprint("builds", __name__)


# TODO Extract the filesystem/workspace management in a module:
# - determine of fs/files actions to get to construct the filesystem;
# - support content/string, base64/file, url/file, url/git, url/tar, post-data/tar
# - hash and make a (deterministic) signature of files uploaded;
# - from the list of actions, prepare the file system (giving only a root directory);
# (- add a cache management on the file system preparation subpart).
#
# The compiler only uses:
# - the hash for an eventual output cache
# (if entire input signature match a cached output file, just return this file);
# - the prepared directory of files where the build happens.

# Persist cached files.
# Endpoint for checking if inputs (or output) are cached,
# for smart client use.

# TODO Only register request here, and allows to define an hook for when
# the work is done?
# Allows the two: (async, sync)
@builds_app.route("/sync", methods=["POST"])
def compiler_latex():
    # TODO Distribute documentation. (HTML)
    payload = request.get_json()
    if not payload:
        return jsonify("MISSING_PAYLOAD"), 400

    # TODO Pre-normalized data checks.
    # - resources (mandatory, must be an array).
    # TODO High-level normalizsation.
    # - compiler
    # Choose compiler: latex, pdflatex, xelatex or lualatex
    # We default to pdflatex.
    compilerName = "pdflatex"
    if "compiler" in payload:
        if payload["compiler"] not in ["latex", "lualatex", "xelatex", "pdflatex"]:
            return jsonify("INVALID_COMPILER"), 400
        compilerName = payload["compiler"]
    if not "resources" in payload:
        return jsonify("MISSING_RESOURCES"), 400

    # -------------
    # Pre-fetch normalization and checks.
    # -------------

    normalized_resources = normalize_resources_input(payload["resources"])
    # if logger.isEnabledFor(logging.DEBUG):
    #     logger.debug(pformat(normalized_resources))
    # - Prefetch checks (paths, main document, ...);
    errors = check_resources_prefetch(normalized_resources)
    if errors:
        return jsonify(errors[0]), 400

    # -------------
    # Fetching, post-fetch normalization and checks, filesystem creation.
    # -------------

    workspace_id = create_workspace(normalized_resources)

    def on_fetched(resource, data):
        logger.debug("Fetched %s: %s bytes", resource["build_path"], len(data))
        # Hash fetched inputs;
        resource["data_spec"] = process_resource_data_spec(data)
        error = persist_resource_to_workspace(workspace_id, resource, data)
        if error:
            return error
        # Input cache forwarding.
        error = forward_resource_to_cache(resource, data)
        if error:
            return error

    # Input cache provider.
    error = fetch_resources(
        normalized_resources, on_fetched, get_from_cache=get_resource_from_cache
    )
    if error:
        return jsonify(error), 400
    # TODO
    # - Process build global signature/hash (compiler, resource hashes, other options...)

    # -------------
    # Compilation.
    # -------------

    # TODO Do an util to get main resource.
    main_resource = next(
        resource for resource in normalized_resources if resource["is_main_document"]
    )
    # TODO Try catch.
    latexToPdfOutput = latexToPdf(
        compilerName, get_workspace_root_path(workspace_id), main_resource
    )

    # -------------
    # Response creation.
    # -------------

    if not latexToPdfOutput["pdf"]:
        return (
            jsonify({"code": "COMPILATION_ERROR", "logs": latexToPdfOutput["logs"]}),
            400,
        )
    # TODO Also return compilation logs here.
    # (So return a json. Include the PDF as base64 data?)
    # (In the long term it will be better to give a static URL to download
    # the generated PDF. We begin to talk about caching. This requires
    # lifecycle management. With something like a Redis.)
    # URL to get build result: PDF output, log, etc.
    # TODO In async / build status endpoint, returns:
    # - Normalized inputs;
    # - URLs for PDF output, log;

    # TODO Output cache management.

    # -------------
    # Cleanup.
    # -------------

    remove_workspace(workspace_id)

    return Response(
        latexToPdfOutput["pdf"],
        status="201",
        headers={"Content-Type": "application/pdf"},
    )
