from django import template

register = template.Library()


@register.filter
def format_price(value):
    try:
        return f"${int(value):,}".replace(",", ".")
    except:
        return value
