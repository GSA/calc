from django import template, forms
from uswds_forms import UswdsDateWidget


register = template.Library()


# These are widget classes that consist of multiple sub-widgets. We'd
# like to use a <legend> element with these, instead of a <label>, so
# that screen-readers contextualize them properly.
LEGEND_WIDGETS = (
    UswdsDateWidget,
    forms.CheckboxSelectMultiple,
    forms.RadioSelect
)


@register.simple_tag(takes_context=True)
def fieldset(context, field):
    '''
    This template tag makes it easy to render form fields as
    <fieldset> elements.
    '''

    t = context.template.engine.get_template('frontend/fieldset.html')

    return t.render(template.Context({
        'field': field,
        'use_legend': isinstance(field.field.widget, LEGEND_WIDGETS)
    }))
