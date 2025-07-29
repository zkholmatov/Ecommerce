from django import template

register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except:
        return ''
    
@register.filter
def times(number):
    return range(int(number))