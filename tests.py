#coding: utf-8
import json
import os

from autodocumentation.decorator import autodoc
from autodocumentation.function_writer import FunctionWriter

try:
    from unittest.mock import patch, Mock
except:
    from mock import patch, Mock

import pytest
from flask import jsonify
from flask.app import Flask

from autodocumentation.doc_builder import DocBuilder
from autodocumentation.flask_writer import FlaskRequestWriter

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
        assert calls["test.test"][0] == {'body': 'null',
                                         'headers': '{\n    "Content-Type": "application/json"\n}',
                                         'method': 'GET',
                                         'response': '{\n    "key": "value"\n}',
                                         'url': '/test?key=value'}

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
                func, {"key": "value"}, {}
            )

def test_write_context(app):
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

        with autodoc.context(comment="Test!"):
            assert writer.serialize(func, jsonify({"key": "value"}))["comment"] == "Test!"

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
        assert writer.serialize(func, jsonify({"key": "value"}))["response"] == '{\n    "key": "value"\n}'
        assert writer.serialize(func, {"key": "value"})["response"] == '{\n    "key": "value"\n}'
        assert writer.serialize(func, {"key": "value"})["headers"] == '{\n    "Content-Type": "application/json"\n}'


def test_function_rendering():
    writer = FunctionWriter()

    def test(a, b, c=1, d=2):
        pass

    serialized = writer.serialize(
        test, None, ["Привет", "Мир"], "Мир", d={"Привет": "Hello"}
    )

    assert serialized["name"] == "test"
    assert serialized["output"] == "None"
    assert serialized["arguments"] == [
        ["a", "['Привет', 'Мир']"],
        ['b', "'Мир'"],
        ['d', "{'Привет': 'Hello'}"]
    ]
def test_rendering(app):

    writer = FlaskRequestWriter()
    builder = DocBuilder()

    doc = """

    Some text before:

    <examples>
"""

    modified = builder._modify_docstring(
        doc, [{
            'body': 'null',
            'headers': '{\n    "Content-Type": "application/json"\n}',
            'method': 'GET',
            'response': '{\n    "key": "value"\n}',
            'url': '/test?key=value'}]
    )
    assert "Some text before" in modified
    assert """            GET /test?key=value
            {
                "Content-Type": "application/json"
            }""" in modified











