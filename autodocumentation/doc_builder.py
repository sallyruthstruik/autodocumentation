#coding: utf8
import logging
import re

from jinja2.environment import Template

from autodocumentation.compat import to_unicode
from autodocumentation.util import add_prefix_to_lines

LOGGER = logging.getLogger("autodoc")

TEMPLATE = """{% for call in calls %}* {{call.comment or "Пример запроса"}}
    Request::

        {{call.method}} {{call.url}}
{{add_prefix_to_lines("        ", call.headers)}}

{{add_prefix_to_lines("        ", call.body)}}

    Response::

{{add_prefix_to_lines("        ", call.response)}}
{% endfor %}"""

class DocBuilder(object):

    writer = None   #type: FlaskRequestWriter

    def __init__(self, limit=3):
        self.limit = limit

    def add_doc(self, func):
        calls = self.writer.get_calls(func)[:self.limit]

        try:
            func.__doc__ = self._modify_docstring(
                func.__doc__, calls
            )
        except:
            LOGGER.exception("Can't build autodoc for func %s", func)

    def _modify_docstring(self, doc, calls):
        examplesPart = Template(to_unicode(TEMPLATE))

        space = re.findall(r"([\t ]+)\<examples\>", doc)[0]

        return add_prefix_to_lines(space, examplesPart.render(
            calls=calls,
            add_prefix_to_lines=add_prefix_to_lines,
            space=space
        ))