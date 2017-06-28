#coding: utf8
import logging
import re

from jinja2.environment import Template

LOGGER = logging.getLogger("autodoc")

class DocBuilder(object):

    writer = None   #type: FlaskRequestWriter

    def __init__(self, limit=1):
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
        examplesPart = Template(
"""{% for call in calls %}{% for line in call %}{{space}}{{line}}
{% endfor %}{% endfor %}"""
        )

        space = re.findall(r"([\t ]+)\<examples\>", doc)[0]

        calls = [
            [line.strip("\n\r") for line in call.split("\n")]
            for call in calls
        ]

        examplesPart = examplesPart.render(
            space=space,
            calls=calls
        )

        return re.sub(r"[\t ]+\<examples\>", examplesPart, doc)