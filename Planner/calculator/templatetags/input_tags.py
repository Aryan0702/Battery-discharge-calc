from django import template
register = template.Library()  
@register.simple_tag

def printer():
    print('rank')
    return 'rank'