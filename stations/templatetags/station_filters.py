from django import template

register = template.Library()

@register.filter
def is_instance_of(obj, class_path):
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        return isinstance(obj, cls)
    except (ImportError, AttributeError):
        return False

@register.filter
def filter_by_rating(reviews, rating):
    return [review for review in reviews if review.note == int(rating)]

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    if arg == 0:
        return 0
    # Convert arg to int if it's a QuerySet
    if hasattr(arg, '__len__'):
        arg = len(arg)
    return value / arg