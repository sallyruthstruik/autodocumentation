#coding: utf8
"""
Autodoc
-------------
Данный модуль позволяет в автоматическом режиме документировать методы Flask API.

Принцип работы:

* При прогоне тестов, если установлена переменная окружения AUTODOC_WRITE при вызове декорированной
  декоратором :func:`.autodoc_dec` функции, результат ее выполнения и параметры запроса сохраняются
  в файл .calls.

* В docstring функции нужно указать параметр <examples>. Он будет заменен на
  примеры запросов к функции.

Пример::

    @app.route(...)
    @autodoc_dec()
    def some_route():
        '''
        Примеры запросов:

        <examples>

        '''
        ...


.. note::

    Для сохранения вызовов нужно указать переменную окружения AUTODOC_WRITE.

"""
import io
import logging
from functools import wraps

from autodoc.doc_builder import DocBuilder
from autodoc.flask_writer import FlaskRequestWriter



def autodoc_dec(writer=FlaskRequestWriter(), doc_builder=DocBuilder()):

    doc_builder.writer = FlaskRequestWriter()

    def decorator(func):

        @wraps(func)
        def inner(*a, **k):
            output = func(*a, **k)

            if writer.allow_write():
                writer.write(
                    func, output, *a, **k
                )

            return output

        doc_builder.add_doc(inner)

        return inner

    return decorator