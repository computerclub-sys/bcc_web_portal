import re

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def cl_thumb(url, size="160x160"):
    if not url:
        return url
    w, h = size.split('x')
    return re.sub(
        r'(/image/upload/)(v?\d+/)?',
        rf'\1c_fill,w_{w},h_{h},q_100/\2',
        url,
    )
