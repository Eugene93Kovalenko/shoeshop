from django import template
from urllib.parse import urlencode
from itertools import groupby

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
# def query_url(parameters, **kwargs):
#     """
#     Returns a URL query string with the given parameters and key-value pairs.
#     If parameters is not None, any key-value pairs whose keys are not in kwargs will be filtered out.
#     """
#     url = f'?{urlencode(kwargs)}'
#
#     if parameters:
#         querystring = parameters.split('&')
#         used_fields = kwargs.keys()
#         filtered_querystring = filter(lambda p: p.split('=')[0] not in used_fields, querystring)
#         encoded_querystring = '&'.join(filtered_querystring)
#
#         if encoded_querystring:
#             url += f'&{encoded_querystring}'
#     return url
#
#
# @register.simple_tag(takes_context=True)
# def query_transform(context):
#     """
#     Returns the URL-encoded querystring for the current page,
#     updating the params with the key/value pairs passed to the tag.
#
#     E.g: given the querystring ?foo=1&bar=2
#     {% query_transform bar=3 %} outputs ?foo=1&bar=3
#     {% query_transform foo='baz' %} outputs ?foo=baz&bar=2
#     {% query_transform foo='one' bar='two' baz=99 %} outputs ?foo=one&bar=two&baz=99
#
#     A RequestContext is required for access to the current querystring.
#     """
#     previous_url = context['request'].META.get('HTTP_REFERER')
#     previous_parameter = ''
#     if previous_url:
#         previous_parameter = previous_url[previous_url.rfind('/') + 1:]
#     current_parameters = context['request'].GET.urlencode()
#     url = f'?{current_parameters}'
#     if 'q' in previous_parameter:
#         return f'{previous_parameter}&{current_parameters}'
#     return url
#
#
# @register.filter
# def split_url_parameters(stdin: str, exclude: str) -> list[list[str, str]]:
#     parameters = sorted([parameters for parameters in stdin.split("&")])
#     no_repeat_parameters = [item for item, _ in groupby(parameters)]
#     splitted_parameters = list(map(lambda x: x.split("="), no_repeat_parameters))
#     filtered_parameters = list(filter(lambda params: params[0] != exclude, splitted_parameters))
#     unique_parameters = [list(param) for param in set(tuple(param_list) for param_list in filtered_parameters)]
#     without_empty_values = list(filter(lambda x: x[1], unique_parameters))
#     return without_empty_values
