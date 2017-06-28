#coding: utf8
import json
import os

from autodoc.util import add_prefix_to_lines
from flask import globals as g

class FlaskRequestWriter(object):
    """
    Класс, записывающий контекст выполнения для Flask роутов.

    Сохраняет контекст запроса:

    * Метод
    * URL
    * Headers
    * POST body

    Может использоваться только с методами, возвращающими JSONResponse.

    Пример::

        @autodoc_dec(writer=FlaskRequestWriter())
        def somemethod():
            ...

    """
    def __init__(self):
        self.file_path = os.path.join(
            os.path.split(__file__)[0],
            ".calls"
        )

    def serialize(self, func, output, *a, **k):
        jsonBody = None

        try:
            jsonBody = g.request.json
        except:
            pass

        output = self._serialize_output(output)

        prefix = "        "

        return """

.. note::

    Request::

        {method} {url}
{headers}
{body}

    Response::

{response}

        """.format(
            method=g.request.method,
            url=g.request.url,
            body=add_prefix_to_lines(prefix, json.dumps(jsonBody)),
            headers=add_prefix_to_lines(
                prefix,
                json.dumps(dict(g.request.headers), indent=4, sort_keys=True)
            ),
            response=add_prefix_to_lines(prefix, output)
        ).strip("\n\t ")

    def get_key(self, func):
        return "{}.{}".format(func.__module__, func.__name__)

    def allow_write(self):
        return os.environ.get("AUTODOC_WRITE")

    def write(self, func, output, *a, **k):
        calls = self._get_saved_calls()

        key = self.get_key(func)
        calls.setdefault(key, [])

        serialized = self.serialize(func, output, *a, **k)
        if serialized not in calls[key]:
            calls[key].append(serialized)

        self._save_calls(calls)

    def _get_saved_calls(self):
        try:
            with open(self.file_path, "r") as fd:
                calls = json.loads(fd.read())
        except:
            calls = {}
        return calls

    def _save_calls(self, calls):
        with open(self.file_path, "w") as fd:
            fd.write(json.dumps(calls, indent=4))

    def get_calls(self, func):
        calls = self._get_saved_calls()
        key = self.get_key(func)

        return calls.get(key, [])

    def _serialize_output(self, output):
        if hasattr(output, "json"):
            output = json.dumps(output.json, indent=4)
        if isinstance(output, (dict, list)):
            output = json.dumps(output, indent=4)
        return output

    def clean(self):
        try:
            os.remove(self.file_path)
        except:
            pass