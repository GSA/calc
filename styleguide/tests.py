from django.test import TestCase, SimpleTestCase
from django.template import engines

from styleguide import email_examples, fullpage_example
from styleguide.templatetags.styleguide import (
    template_tag_library,
    github_url_for_path,
)


GITHUB_TREE_URL = github_url_for_path('')[:-1]


class StyleguideTests(TestCase):

    def test_styleguide_returns_200(self):
        response = self.client.get('/styleguide/')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_docs_returns_200(self):
        response = self.client.get('/styleguide/docs/')
        self.assertContains(response, 'Style Guide Documentation')

    def test_styleguide_ajaxform_returns_200(self):
        response = self.client.get('/styleguide/ajaxform')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_date_returns_200(self):
        response = self.client.get('/styleguide/date')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_radio_checkbox_returns_200(self):
        response = self.client.get('/styleguide/radio-checkbox')
        self.assertEqual(response.status_code, 200)

    def test_styleguide_email_examples_return_200(self):
        for example in email_examples.examples:
            html_response = self.client.get(example.html_url)
            self.assertEqual(html_response.status_code, 200)

            plaintext_response = self.client.get(example.plaintext_url)
            self.assertEqual(plaintext_response.status_code, 200)


class FullpageExampleTests(TestCase):
    def test_returns_200_if_name_is_valid(self):
        response = self.client.get(
            '/styleguide/fullpage-example/card-skinny')
        self.assertEqual(response.status_code, 200)

    def test_returns_404_if_name_is_invalid(self):
        response = self.client.get('/styleguide/fullpage-example/lololol')
        self.assertEqual(response.status_code, 404)

    def test_get_snippet_works(self):
        self.assertEqual(fullpage_example._get_snippet(
            'foo\n{# BEGIN SNIPPET #}\nblarg\n{# END SNIPPET #}\nbar'
        ), 'blarg\n')
        self.assertEqual(fullpage_example._get_snippet('flarg'), None)


class TemplateTagsTests(SimpleTestCase):
    def render_string(self, string):
        t = engines['django'].from_string(r'{% load styleguide %}' + string)
        return t.render({})

    def test_template_raises_exception_if_library_not_found(self):
        with self.assertRaisesRegexp(ValueError,
                                     'library blarg not found'):
            template_tag_library('blarg')

    def test_template_raises_exception_if_library_not_in_project(self):
        with self.assertRaisesRegexp(ValueError,
                                     'library staticfiles is not in project'):
            template_tag_library('staticfiles')

    def test_template_tag_library_works(self):
        self.assertIn(
            f'{GITHUB_TREE_URL}/styleguide/templatetags/styleguide.py',
            template_tag_library('styleguide'),
        )

    def test_template_url_raises_error_if_template_not_found(self):
        with self.assertRaisesRegexp(ValueError, 'Template blah not found'):
            self.render_string('{% template_url "blah" %}')

    def test_template_url_works(self):
        self.assertEqual(
            self.render_string('{% template_url "styleguide.html" %}'),
            f'{GITHUB_TREE_URL}/styleguide/templates/styleguide.html'
        )

    def test_fullpage_example_raises_error_if_name_is_invalid(self):
        with self.assertRaisesRegexp(FileNotFoundError, r'blahh\.html'):
            self.render_string('{% fullpage_example "blahh" %}')
