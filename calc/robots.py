from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    # https://en.wikipedia.org/wiki/Robots_exclusion_standard#Examples
    if settings.ENABLE_SEO_INDEXING:
        content = "User-agent: *\nDisallow:"
    else:
        content = "User-agent: *\nDisallow: /"

    return HttpResponse(content)
