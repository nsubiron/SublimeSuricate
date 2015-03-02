#!/usr/bin/env python3

"""Retrieve results from the DuckDuckGo zero-click API in simple HTML format."""

import json as jsonlib
import logging
import re
import urllib.request, urllib.error, urllib.parse


__version__ = (1, 0, 0)


def results2html(results, results_priority=None, max_number_of_results=None,
                 ignore_incomplete=True, always_show_related=False,
                 header_start_level=1, hide_headers=False, hide_signature=False):
    if not results:
        return ''

    if not results_priority:
        results_priority = ['answer', 'abstract', 'definition', 'results',
                            'infobox', 'redirect', 'related']

    if not always_show_related:
        other = [x for x in results_priority if x != 'related']
        if any(results.get(x).is_complete() for x in other):
            results_priority = other

    html_header = '<h{level:d}>{title}</h{level:d}>'
    html_paragraph = '<p>{contents}</p>'

    html_contents = []
    children = [results.get(x) for x in results_priority]
    results_count = 0
    for level, child in _iterchildren(header_start_level, children):
        html = child.as_html()
        valid = html and (not ignore_incomplete or child.is_complete())
        if not hide_headers and child.name and (valid or child.children()):
            header = html_header.format(title=child.name, level=level)
            html_contents.append(header)
        if valid:
            html_contents.append(html_paragraph.format(contents=html))
            results_count += 1
            if max_number_of_results and results_count >= max_number_of_results:
                break

    html_contents[:] = [x for x in html_contents if x]
    if not html_contents:
        return ''

    if not hide_signature:
        html_contents.append('<footer><small>Results from DuckDuckGo</small></footer>')

    return ''.join(html_contents).strip()


def search(query, useragent='duckduckgo2html', **kwargs):
    params = {
        'q': query,
        'format': 'json',
        'pretty': '1',
        'no_redirect': '1',
        'no_html': '1',
        'skip_disambig': '0',
    }
    params.update(kwargs)
    enc_params = urllib.parse.urlencode(params)
    url = 'http://api.duckduckgo.com/?' + enc_params

    try:
        request = urllib.request.Request(url, headers={'User-Agent': useragent})
        response = urllib.request.urlopen(request)
        json = jsonlib.loads(response.read().decode('utf-8'))
        response.close()
        return Results(json)
    except urllib.error.HTTPError as err:
        logging.error('Query failed with HTTPError code %s', err.code)
    except urllib.error.URLError as err:
        logging.error('Query failed with URLError %s', err.reason)
    except Exception:
        logging.error('Unhandled exception')
        raise
    return None


def _iterchildren(start_level, children):
    for item in children:
        grandchildren = item.children()
        yield start_level, item
        if grandchildren:
            for subitem in _iterchildren(start_level+1, grandchildren):
                yield subitem


def _html_url(url, display=None):
    if not display:
        display = url
    return '<a href="{0}">{1}</a>'.format(url, display)


class Results(object):
    def __init__(self, json):
        self.json = jsonlib.dumps(json, indent=2)
        self.type = json.get('Type')
        self.answer = Answer(json)
        self.results = _ResultList('Results', json.get('Results', []))
        self.related = _ResultList('Related Topics', json.get('RelatedTopics', []))
        self.abstract = Abstract(json)
        self.definition = Definition(json)
        self.redirect = Redirect(json)
        self.infobox = Infobox(json)

    def get(self, name):
        if hasattr(self, name) and getattr(self, name):
            return getattr(self, name)
        return _ResultItemBase()


class _ResultItemBase(object):
    """Base class for results"""

    def __init__(self, name=None):
        self.name = name

    def is_complete(self):
        return False

    def children(self):
        return []

    def as_html(self):
        return ''


class _ResultList(_ResultItemBase):
    """A list of results"""

    def __init__(self, name, items):
        super().__init__(name)
        self.items = [Result(x) for x in items]

    def children(self):
        return self.items


class Result(_ResultItemBase):
    def __init__(self, json):
        super().__init__(json.get('Name', '') if json else '')
        self.topics = [Result(elem) for elem in json.get('Topics', [])]
        self.html = json.get('Result', '') if json else ''
        self.text = json.get('Text', '') if json else ''
        self.url = json.get('FirstURL', '') if json else ''

    def is_complete(self):
        return True if self.text else False

    def children(self):
        return self.topics

    def as_html(self):
        if self.html:
            return Result._rex_sub.sub('a> ', self.html)
        elif self.text:
            return self.text

    _rex_sub = re.compile(r'a>(?! )')


class Abstract(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Abstract')
        self.html = json['Abstract']
        self.text = json['AbstractText']
        self.url = json['AbstractURL']
        self.source = json['AbstractSource']
        self.heading = json['Heading']

    def is_complete(self):
        return True if self.html or self.text else False

    def as_html(self):
        html_list = []
        if self.heading:
            html_list.append('<b>{0}</b>'.format(self.heading))
        if self.html:
            html_list.append(self.html)
        elif self.text:
            html_list.append(self.text)
        if self.url:
            html_list.append(_html_url(self.url, self.source))
        return ' - '.join(html_list)


class Answer(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Answer')
        self.text = json['Answer']
        self.type = json['AnswerType']
        self.url = None

    def is_complete(self):
        return True if self.text else False

    def as_html(self):
        return self.text.replace('\n', '<br>').replace('\r', '')


class Definition(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Definition')
        self.text = json['Definition']
        self.url = json['DefinitionURL']
        self.source = json['DefinitionSource']

    def is_complete(self):
        return True if self.text else False

    def as_html(self):
        if self.text and self.url:
            return self.text + ' - ' + _html_url(self.url, self.source)
        elif self.text:
            return self.text
        elif self.url:
            return _html_url(self.url, self.source)


class Redirect(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Redirect')
        self.url = json['Redirect']

    def is_complete(self):
        return True if self.url else False

    def as_html(self):
        return _html_url(self.url) if self.url else None


class Infobox(_ResultItemBase):
    class Content(object):
        def __init__(self, json):
            self.data_type = json.get('data_type', '') if json else ''
            self.label = json.get('label', '') if json else ''
            self.value = json.get('value', '') if json else ''

        def as_html(self):
            if self.data_type == 'string' and self.label and self.value:
                return '<b>{0}</b> {1}'.format(self.label, self.value)

    def __init__(self, json):
        super().__init__('Infobox')
        infobox = json.get('Infobox') if json.get('Infobox') else {}
        self.meta = infobox.get('meta', [])
        self.content = [Infobox.Content(x) for x in infobox.get('content', [])]

    def is_complete(self):
        return True if self.content else False

    def as_html(self):
        contents = [x.as_html() for x in self.content]
        return '<br>'.join(x for x in contents if x)


if __name__ == '__main__':

    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'query',
        nargs='*',
        help='the search query')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s v{0}.{1}.{2}'.format(*__version__))
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(filename)s: %(message)s')

    if args.query:
        queries = [' '.join(args.query)]
    elif not sys.stdin.isatty():
        queries = sys.stdin.read().splitlines()
    else:
        parser.print_help()
        sys.exit(1)

    for query in queries:
        html = results2html(search(query))
        if html:
            print(html)
        else:
            logging.warning('No results found')
