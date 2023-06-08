# coding=utf-8
# from django.template.base import Library
from django import template
from __poll.utils.utils import snakeify
import os.path


register = template.Library()


@register.filter
def concat(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)

@register.filter
def count(dictionary):
    try:
        return dictionary.count()
    except Exception as e:
        pass
    finally:
        try:
            return len(dictionary)
        except Exception as e:
            return 0

@register.filter
def sum(dictionary, key):
    total = 0
    for d in dictionary:
        for k, v in d.__dict__.items():
            if key == k:
                total += v
    return total


@register.filter
def clean_url(dictionary):
    default_avatar = 'https://www.clker.com/cliparts/u/Q/E/2/c/d/grey-background-facebook-2-th.png'
    dictionary = dictionary.replace('%3A', ':')
    splitters = ['https:/', 'http:/']
    for splitter in splitters:
        if splitter in dictionary:
            parts = dictionary.split(splitter)
            file_path = parts[1]
            if len(file_path) > 0:
                start_str = 'https:/' if splitter.startswith('https:/') else 'http:/'
                if not file_path.startswith('/'):
                    start_str += '/'
                return f'{start_str}{file_path}'
            else: 
                return default_avatar
    print(dictionary)
    return dictionary

@register.filter
def list_get_item(dictionary, key):
    return dictionary[key]


@register.filter
def get_vars(dictionary):
    try:
        return [p for p, v in vars(dictionary).items()]
    except Exception as e:
        print(e)
        return ''

@register.filter
def get_keys(dictionary):
    try:
        return ','.join([v for k, v in dictionary.items()])
    except Exception as e:
        print(e)
        return ''

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return ''
    if key is None:
        return dictionary
    base = dictionary
    all_items = ''
    if type(key) is int:
        # TODO: exception handling
        all_items = dictionary.get(key, '')
    else:
        paths = key.split('&')
        for path in paths:
            keys = path.split('.')
            item = base
            for k in keys:
                # if type(item) is not 'object':
                #     return item
                if type(item) not in [str, int] and item is not None:
                    item = item.get(k, '')
            if '&' in k:
                if type(item) is str:
                    if len(all_items) > 0:
                        all_items += ' '
                    all_items = all_items + item
            else:
                return item
    return all_items


@register.filter
def add_quotes(dictionary):
    return f'{dictionary}'

@register.filter
def make_snake(dictionary):
    if type(dictionary) is str:
        return snakeify(dictionary)
    return ''

@register.filter
def ucwords(dictionary):
    item = dictionary
    items = item.lower() \
                .replace('_', ' ') \
                .replace('.', ' ') \
                .replace('&', ' & ') \
                .split(' ')
    result = ''
    for item in items:
        if len(result) > 0:
            result = result + ' '
        result = result + item.capitalize()
    return result

@register.filter
def capitalize(dictionary):
    return dictionary.capitalize()

@register.filter
def lower(dictionary):
    return dictionary.lower()

@register.filter
def upper(dictionary):
    return dictionary.upper()

@register.filter
def lead_cell(dictionary):
    return 'td-success' if int(dictionary) > 0 else ''
