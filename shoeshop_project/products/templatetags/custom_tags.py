from django import template


register = template.Library()


# для того, чтобы пагинация работала при сортировке/фильтрации
@register.simple_tag()
def relative_url(argument, value, urlencode=None):
    url = f'?{argument}={value}'
    if urlencode.count('=') == 1 and urlencode.startswith('page'):
        return url
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = querystring[1:] if querystring[0].startswith('page') else querystring
        encoded_querystring = '&'.join(filtered_querystring)
        url += f'&{encoded_querystring}'
    return url


# @register.simple_tag
# def call_get_absolute_url(product_id):
#     product = get_single_product(product_id)
#     return product.get_absolute_url()
#
#
# @register.simple_tag
# def call_get_remove_from_cart_url(product_id):
#     product = get_single_product(product_id)
#     return product.get_remove_from_cart_url()


@register.simple_tag
def breadcrumb_schema():
    return "http://schema.org/BreadcrumbList"


@register.inclusion_tag('includes/breadcrumb_item.html')
def breadcrumb_item(url, title):
    return {
        'url': url,
        'title': title
    }
