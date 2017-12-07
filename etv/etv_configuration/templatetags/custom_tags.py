from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def first_words(value, n):
    return mark_safe(' '.join(value.split(' ')[:n]))

@register.filter
def last_words(value, n):
    return mark_safe(' '.join(value.split(' ')[n:]))

@register.filter
def score_space(value):
    return mark_safe(' '.join(value.split('_')))

@register.filter
def thin_nb_spaced(value):
    return mark_safe('&#x202F;'.join(value.split(' ')))

@register.filter
def nb_spaced(value):
    return mark_safe('&nbsp;'.join(value.split(' ')))

@register.inclusion_tag('plugin_links.html', takes_context=True)
def plugin_links(context):
    return {'PLUGINS':settings.PLUGINS, 'api_url':context['simulation']['path']}
