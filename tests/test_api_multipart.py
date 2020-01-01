# -*- coding: utf-8 -*-
"""
    tests.test_api_multipart
    ~~~~~~~~~~~~~~~~~~~~~
    Check Latex multipart compiling API.

    :copyright: (c) 2019 Yoan Tournade.
    :license: AGPL, see LICENSE for more details.
"""
import pytest
import requests
from .utils.pdf import snapshot_pdf

LATEX_HELLO_WORLD = (
    "\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}"
)
SAMPLE_HELLO_WORLD = "hello_world"


def test_multipart_api_full_spec(latex_on_http_api_url):
    """
    Compile a Latex document with multipart API by passing a complete resources
    specification and specifying the compiler.
    """
    # Create a multipart request.
    files = {"file1": ("hello_world.tex", LATEX_HELLO_WORLD)}
    form = {
        "compiler": "lualatex",
        "resources": '[{"main": "true", "multipart": "file1"}]',
    }
    r = requests.post(latex_on_http_api_url + "/builds/sync", files=files, data=form)
    assert r.status_code == 201
    snapshot_pdf(r.content, SAMPLE_HELLO_WORLD)


def test_multipart_api_inferred_compiler(latex_on_http_api_url):
    """
    Compile a Latex document with multipart API by passing a resources
    specification but without specifying the compiler.
    """
    # Create a multipart request.
    files = {"file1": ("hello_world.tex", LATEX_HELLO_WORLD)}
    form = {
        "resources": '[{"main": "true", "multipart": "file1"}]',
    }
    r = requests.post(latex_on_http_api_url + "/builds/sync", files=files, data=form)
    assert r.status_code == 201


def test_multipart_api_only_one_latex_file(latex_on_http_api_url):
    """
    Compile a Latex document with multipart API by only a Latex file.
    """
    # Create a multipart request.
    files = {"file1": ("hello_world.tex", LATEX_HELLO_WORLD)}
    r = requests.post(latex_on_http_api_url + "/builds/sync", files=files)
    assert r.status_code == 201


def test_multipart_api_invalid_json_resources_spec(latex_on_http_api_url):
    """
    Handle invalid json resources spec error.
    """
    # Create a multipart request.
    files = {"file1": ("hello_world.tex", LATEX_HELLO_WORLD)}
    form = {
        "resources": '[}}{"main": "true", "multipart": "file1"}]',
    }
    r = requests.post(latex_on_http_api_url + "/builds/sync", files=files, data=form)
    assert r.status_code == 400
    response_payload = r.json()
    assert response_payload["error"] == "INVALID_RESOURCES_JSON"
