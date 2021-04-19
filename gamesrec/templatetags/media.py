from django import template
from django.shortcuts import reverse
from django.conf import settings

register = template.Library()

@register.simple_tag
def media(value):
    if 'media' in value:
        value = value[value.index('media')+len('media'):]
        if value.startswith('/'):
            value = value[1:]
    return f'{settings.MEDIA_URL}{value}'
