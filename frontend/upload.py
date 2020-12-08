from typing import Dict

from django import forms
from django.forms.utils import flatatt
from django.utils.html import escape


DEFAULT_FILE_EXTENSIONS = (".xlsx", ".xls", ".csv")


class UploadWidget(forms.widgets.FileInput):
    '''
    This widget represents an upload widget that the user can
    easily drag-and-drop files into.

    It is tightly coupled to upload.js.
    '''

    def __init__(self, attrs=None, degraded=False, required=True,
                 accept=DEFAULT_FILE_EXTENSIONS,
                 extra_instructions='XLS, XLSX, or CSV format, please.',
                 existing_filename=None):
        super().__init__(attrs=attrs)
        self.required = required
        self.degraded = degraded
        self.accept = accept
        self.extra_instructions = extra_instructions
        self.existing_filename = existing_filename

    def render(self, name, value, attrs=None):
        final_attrs: Dict[str, str] = {}
        if attrs:
            final_attrs.update(attrs)

        final_attrs['accept'] = ",".join(self.accept)
        final_attrs['is'] = 'upload-input'

        id_for_label = final_attrs.get('id', '')
        widget_attrs = {}

        if self.degraded:
            widget_attrs['data-force-degradation'] = ''

        nojs_preamble = ''
        if self.existing_filename:
            if self.required:
                raise AssertionError(
                    'Using an existing filename is incompatible with '
                    'the "required" attribute'
                )
            widget_attrs['data-fake-initial-filename'] = self.existing_filename
            nojs_preamble = (
                'You\'ve already uploaded '
                '<code>{}</code>. '.format(
                    escape(self.existing_filename)
                ) +
                'You can keep using it or select a new file to replace it.'
            )

        label_txt = 'Choose file'
        final_attrs['aria-label'] = label_txt

        return "\n".join([
            '<upload-widget%s>' % flatatt(widget_attrs),
            '  <span class="nojs-preamble">%s</span>' % nojs_preamble,
            '  %s' % super().render(name, value, final_attrs),
            '  <div class="upload-chooser">',
            '    <label for="%s">%s</label>' % (id_for_label, label_txt),
            '    <span>%s</span>' % self.extra_instructions,
            '  </div>',
            '</upload-widget>'
        ])
