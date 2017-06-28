import json
import os

try:
    from unittest.mock import patch, Mock
except:
    from mock import patch, Mock

import pytest
from flask import jsonify
from flask.app import Flask

from autodoc.doc_builder import DocBuilder
from autodoc.flask_writer import FlaskRequestWriter

@pytest.fixture()
def app():
    return Flask(__name__)

@pytest.fixture()
def allow_write():
    os.environ["AUTODOC_WRITE"] = "1"
    yield
    del os.environ["AUTODOC_WRITE"]

@patch.object(FlaskRequestWriter, "_get_saved_calls", lambda *a: {})
def test_writing(app):

    def check_calls(s, calls):
        assert len(calls["test.test"]) == 1
        assert '"key": "value"' in calls["test.test"][0]

    func = Mock(__module__="test", __name__="test")

    with patch.object(FlaskRequestWriter, "_save_calls", check_calls):

        with patch("flask.globals.request", Mock(
            method="GET",
            url="/test?key=value",
            json=None,
            headers={
                "Content-Type": "application/json"
            }
        )):
            FlaskRequestWriter().write(
                func, {"key": "value"}
            )


    docBuilder = DocBuilder()
    docBuilder.writer = FlaskRequestWriter()

    assert docBuilder._modify_docstring("   <examples>", [
        "Test\nTest"
    ]) == "   Test\n   Test\n"

def test_different_response_types(app):

    writer = FlaskRequestWriter()

    func = Mock(__module__="test", __name__="test")

    with patch("flask.globals.request", Mock(
        method="GET",
        url="/olala?key=value",
        json=None,
        headers={
            "Content-Type": "application/json"
        }
    )):

        body = '"key": "value"'
        headers = '"Content-Type": "application/json"'
        assert body in writer.serialize(func, jsonify({"key": "value"}))
        assert body in writer.serialize(func, {"key": "value"})
        assert headers in writer.serialize(func, {})








