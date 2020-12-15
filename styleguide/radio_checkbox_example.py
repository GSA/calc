from django import forms
from django.shortcuts import render
from django.contrib import messages
from uswds_forms import UswdsRadioSelect, UswdsCheckboxSelectMultiple


class ExampleForm(forms.Form):
    radios = forms.ChoiceField(
        widget=UswdsRadioSelect,
        choices=(
            ('1', 'First'),
            ('2', 'Second'),
        )
    )

    checkboxes = forms.MultipleChoiceField(
        widget=UswdsCheckboxSelectMultiple,
        choices=(
            ('a', 'Choice A'),
            ('b', 'Choice B'),
        )
    )


def create_template_context(radio_checkbox_form=None):
    if radio_checkbox_form is None:
        radio_checkbox_form = ExampleForm()

    return {'radio_checkbox_form': radio_checkbox_form}


def view(request):
    form = None

    if request.method == 'POST':
        form = ExampleForm(request.POST)

        if form.is_valid():
            messages.add_message(
                request, messages.SUCCESS,
                "You chose radio option #{}!".format(
                    form.cleaned_data['radios'])
            )
        else:
            messages.add_message(
                request, messages.ERROR,
                'Uh oh. Please correct the error(s) below and try again.'
            )

    return render(
        request,
        'styleguide_radio.html',
        create_template_context(radio_checkbox_form=form),
    )
