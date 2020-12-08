from typing import Union
from textwrap import dedent, fill
import abc
from django.utils.safestring import SafeString
from django.urls import reverse
import markdown

from ..models import Contract, ContractsQuerySet


number = Union[int, float]


def format_text(text: str) -> str:
    return fill(dedent(text)).strip()


def format_html(markdown_text: str) -> SafeString:
    html = markdown.markdown(format_text(markdown_text))

    # Unwrap the <p></p> that markdown wraps it in.
    html = html[len('<p>'):-len('</p>')]

    return SafeString(html)


class BaseMetric(metaclass=abc.ABCMeta):
    '''
    An abstract base class that describes a contract-related
    metric that can be shown in a report, along with examples of
    labor rates behind the metric.
    '''

    MAX_EXAMPLES = 10

    def get_queryset(self) -> ContractsQuerySet:
        '''
        Return a ContractsQuerySet that represents the data
        behind the metric.
        '''

        return Contract.objects.none()

    def get_examples_queryset(self) -> ContractsQuerySet:
        '''
        Return a ContractsQuerySet containing examples
        of data behind the metric.
        '''

        return self.get_queryset()[:self.MAX_EXAMPLES]

    def count(self) -> number:
        '''
        Count the metric.
        '''

        return self.get_queryset().count()

    @abc.abstractproperty
    def desc(self) -> str:
        '''
        Return a markdown sentence that describes what the
        count means, assuming the count begins the sentence.

        For example, a value of "labor rates are weird" works
        because "53 labor rates are weird" makes sense, assuming
        that the count is 53.

        Note that this value may be converted to HTML and marked
        as safe, which means that it shouldn't contain any
        untrusted user data.
        '''

        raise NotImplementedError()

    @property
    def footnote(self) -> str:
        '''
        Return a markdown sentence that offers a footnote for
        the description. This can include further details
        that explain how the count is calculated, why the
        count might have the value it does, and so on.

        The value of this property defaults to the empty
        string, meaning that there is no footnote.
        '''

        return ''

    @property
    def desc_text(self) -> str:
        return format_text(self.desc)

    @property
    def desc_html(self) -> SafeString:
        return format_html(self.desc)

    @property
    def footnote_text(self) -> str:
        return format_text(self.footnote)

    @property
    def footnote_html(self) -> SafeString:
        return format_html(self.footnote)

    @property
    def slug(self) -> str:
        return self.__class__.__module__.split('.')[-1]

    @property
    def verbose_name(self) -> str:
        return self.slug

    def get_absolute_url(self) -> str:
        return reverse('data_quality_report_detail', kwargs={
            'slug': self.slug
        })
