import time
from django import forms
from django.http import HttpResponse
from django.contrib import messages
from uswds_forms import UswdsRadioSelect, UswdsCheckboxSelectMultiple

from frontend import ajaxform
from frontend.upload import UploadWidget

CHOICE_REDIRECT = 'redirect'
CHOICE_500 = '500'
CHOICE_WEIRD = 'weird'


class ExampleForm(forms.Form):
    question = forms.IntegerField(label='What is 2+2?')

    on_valid_submit = forms.ChoiceField(
        label='When submitted without validation errors, I should:',
        choices=[
            (CHOICE_REDIRECT, 'Redirect to the style guide after 3 seconds'),
            (CHOICE_500, 'Explode in a 500 Internal Server Error'),
            (CHOICE_WEIRD, 'Return an unexpected response')
        ]
    )

    some_radios = forms.ChoiceField(
        widget=UswdsRadioSelect,
        choices=((1, "one"), (2, "two"))
    )

    some_checkboxes = forms.MultipleChoiceField(
        required=False,
        widget=UswdsCheckboxSelectMultiple,
        choices=(('a', 'Option A'), ('b', 'Option B'), ('c', 'Option C')))

    file = forms.FileField(widget=UploadWidget(
        accept=('.csv',),
        extra_instructions="CSV only, please."
    ))

    def clean_question(self):
        data = self.cleaned_data['question']
        if data != 4:
            raise forms.ValidationError('2 + 2 is not %d!' % data)
        return data


def create_template_context(ajaxform_form=None):
    if ajaxform_form is None:
        ajaxform_form = ExampleForm()

    return {'ajaxform_form': ajaxform_form}


def view(request):
    form = None

    if request.method == 'POST':
        if 'cancel' in request.POST:
            messages.add_message(
                request, messages.INFO,
                'Form submission cancelled.'
            )
        else:
            form = ExampleForm(request.POST, request.FILES)

            if form.is_valid():
                choice = form.cleaned_data['on_valid_submit']
                if choice == CHOICE_REDIRECT:
                    time.sleep(3)
                    return ajaxform.redirect(request, 'styleguide:index')
                elif choice == CHOICE_500:
                    raise Exception('Here is the 500 you ordered.')
                else:
                    return HttpResponse('Here is an unexpected response.')

            messages.add_message(
                request, messages.ERROR,
                'Uh oh. Please correct the error(s) below and try again.'
            )

    return ajaxform.render(
        request,
        context=create_template_context(ajaxform_form=form),
        template_name='styleguide_ajaxform.html',
        ajax_template_name='styleguide_ajaxform_example.html'
    )
