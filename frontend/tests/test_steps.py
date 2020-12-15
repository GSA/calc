from django.test import SimpleTestCase

from frontend.steps import StepsWidget


class StepsWidgetTests(SimpleTestCase):
    def test_exception_thrown_when_labels_are_falsy(self):
        with self.assertRaisesRegexp(ValueError, 'Step 2 has no label'):
            StepsWidget(('foo', '', 'baz'), 2)

    def test_attrs_work(self):
        steps = StepsWidget(
            labels=('foo', 'bar', 'baz'),
            current=2
        )
        self.assertEqual(steps.steps, [
            StepsWidget._Step('foo', 1, False),
            StepsWidget._Step('bar', 2, True),
            StepsWidget._Step('baz', 3, False),
        ])
        self.assertEqual(steps.current_step, steps.steps[1])

    def test_rendering_works(self):
        steps = StepsWidget(
            labels=('foo', 'bar', 'baz'),
            current=2
        )
        html = steps()
        self.assertRegexpMatches(html, 'bar')
        self.assertRegexpMatches(html, 'Step 2 of 3')
