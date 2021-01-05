from django.test import SimpleTestCase
from django.template import Template, Context

from ..crotchety import CrotchetyFileNotFoundError


class CrotchetyTests(SimpleTestCase):
    def test_exception_is_thrown_when_file_not_found(self):
        template = Template("""
            {% load staticfiles %}
            {% static 'i/am/nonexistent.js' %}
        """)

        with self.assertRaises(CrotchetyFileNotFoundError):
            template.render(Context({}))
