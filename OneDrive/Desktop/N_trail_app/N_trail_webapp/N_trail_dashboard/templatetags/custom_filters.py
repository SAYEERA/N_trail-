import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    return os.path.basename(value)

@register.filter
def range_filter(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):
    {% for i in 5|range_filter %}
      {{ i }}
    {% endfor %}
    Results with the numbers 0, 1, 2, 3, 4
    Instead of 5, one may use a variable set in the views
    """
    return range(int(value))

@register.filter
def add(value, arg):
    """
    Adds the arg to the value.
    """
    return int(value) + int(arg)

@register.filter
def times(number):
    return range(int(number))
