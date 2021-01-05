from datetime import date
from django.test import TestCase

from uswds_forms import UswdsDateWidget


class UswdsDateWidgetTests(TestCase):
    '''
    We have a custom template override for UswdsDateWidget, so this
    test suite just makes sure it works properly.
    '''

    def test_render_uses_uswds_date_custom_element(self):
        widget = UswdsDateWidget()
        content = widget.render('boop', None, {'id': 'blarg'})
        self.assertIn('<uswds-date', content)
        self.assertIn('</uswds-date>', content)

    def test_render_assigns_ids_and_labels(self):
        widget = UswdsDateWidget()
        content = widget.render('boop', None, {'id': 'blarg'})
        self.assertRegexpMatches(content, 'id="blarg_0"')
        self.assertRegexpMatches(content, 'id="blarg_1"')
        self.assertRegexpMatches(content, 'id="blarg_2"')
        self.assertRegexpMatches(content, 'for="blarg_0"')
        self.assertRegexpMatches(content, 'for="blarg_1"')
        self.assertRegexpMatches(content, 'for="blarg_2"')

    def test_render_assigns_names(self):
        widget = UswdsDateWidget()
        content = widget.render('boop', None, {'id': 'foo'})
        self.assertRegexpMatches(content, 'name="boop_0"')
        self.assertRegexpMatches(content, 'name="boop_1"')
        self.assertRegexpMatches(content, 'name="boop_2"')

    def test_render_assigns_hint_id_and_aria_describedby(self):
        widget = UswdsDateWidget()
        content = widget.render('boop', None, {'id': 'foo'})
        self.assertRegexpMatches(content, 'id="foo_hint"')
        self.assertRegexpMatches(content, 'aria-describedby="foo_hint"')

    def test_render_takes_value_as_list(self):
        widget = UswdsDateWidget()
        content = widget.render('boop', [2006, 7, 29], {'id': 'foo'})
        self.assertRegexpMatches(content, 'value="2006"')
        self.assertRegexpMatches(content, 'value="7"')
        self.assertRegexpMatches(content, 'value="29"')

    def test_render_takes_value_as_date(self):
        widget = UswdsDateWidget()
        content = widget.render('boop', date(2005, 6, 28), {'id': 'foo'})
        self.assertRegexpMatches(content, 'value="2005"')
        self.assertRegexpMatches(content, 'value="6"')
        self.assertRegexpMatches(content, 'value="28"')
