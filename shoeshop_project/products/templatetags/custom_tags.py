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
