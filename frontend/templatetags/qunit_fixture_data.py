import json
from django import template
from django import forms
from django.utils.safestring import mark_safe

from ..upload import UploadWidget


register = template.Library()


class UploadTestsForm(forms.Form):
    file = forms.FileField(widget=UploadWidget(
        accept=('.csv', 'application/test')
    ))


class AjaxformTestsForm(forms.Form):
    foo = forms.CharField()
    a_radio = forms.ChoiceField(choices=((1, "one"), (2, "two")),
                                widget=forms.RadioSelect)
    some_checkboxes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(('a', 'Option A'), ('b', 'Option B'), ('c', 'Option C')))

    file = forms.FileField(widget=UploadWidget(
        accept=''
    ))

    def render(self):
        return ''.join([
            '<form enctype="multipart/form-data" method="post"',
            ' is="ajax-form"',
            ' action="/post-stuff">',
            '  %s' % str(self.as_ul()),
            '  <button type="submit">submit</button>',
            '  <button type="submit" name="cancel">cancel</button>',
            '</form>'
        ])


@register.simple_tag
def qunit_fixture_data_json():
    data = {
        'UPLOAD_TESTS_HTML': str(UploadTestsForm()['file']),
        'AJAXFORM_TESTS_HTML': AjaxformTestsForm().render()
    }

    return mark_safe(json.dumps(data))  # nosec
