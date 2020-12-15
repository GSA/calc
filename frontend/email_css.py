import pathlib
from django.utils.safestring import mark_safe


CSS_PATH = (pathlib.Path(__file__).resolve().parent /
            'static' / 'frontend' / 'built' / 'style' / 'email.min.css')


def get():
    return mark_safe(CSS_PATH.read_text(encoding='utf-8'))  # nosec
