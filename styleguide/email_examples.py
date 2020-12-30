from typing import List
from django.utils.text import slugify
from django.http import HttpResponse
from django.conf.urls import url
from django.core.urlresolvers import reverse

from data_capture.email import render_mail, EXAMPLES


# Erg, we want to be able to give templates the full path to our
# URLs, but in order to do this, we need to know what namespaces
# we're mounted under. While this is annoying architecturally,
# at least it's accurate--if it ever becomes inaccurate, tests
# will fail.
PREFIX = 'styleguide:email_examples:'


class ExampleEmail:
    '''
    Encapsulates an example email that can be sent out, and associated
    views that will render it in various formats for development/debugging
    purposes.
    '''

    def __init__(self, subject, template, ctx):
        self.subject = subject
        self.template = template
        self.ctx = ctx
        self.slug = slugify(subject).replace('-', '_')
        self.urls = [
            url('^' + self.slug + r'\.txt$', self.plaintext,
                name=f"plaintext_{self.slug}"),
            url('^' + self.slug + r'\.html$', self.html,
                name=f"html_{self.slug}"),
        ]

    @property
    def html_url(self):
        return reverse(f"{PREFIX}html_{self.slug}")

    @property
    def plaintext_url(self):
        return reverse(f"{PREFIX}plaintext_{self.slug}")

    def plaintext(self, request):
        plaintext, _ = render_mail(self.template, self.ctx)
        return HttpResponse(plaintext, content_type='text/plain',
                            charset='utf-8')

    def html(self, request):
        _, html = render_mail(self.template, self.ctx)
        return HttpResponse(html)

    @staticmethod
    def get_urlpatterns(examples):
        urls: List[url] = []
        for example in examples:
            urls += example.urls
        return urls


examples = [ExampleEmail(**example) for example in EXAMPLES]

urls = ExampleEmail.get_urlpatterns(examples)
