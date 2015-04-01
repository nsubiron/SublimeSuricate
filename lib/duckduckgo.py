# Sublime Suricate Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Search on DuckDuckGo"""

import logging
import re

import sublime

import suricate

from . import popup_util
from . import sublime_wrapper
from .thirdparty import duckduckgo2html

suricate.reload_module(popup_util)
suricate.reload_module(sublime_wrapper)
suricate.reload_module(duckduckgo2html)


DDG_USERAGENT = 'sublime-suricate'


def get_answer(query, scope=None, **kwargs):
    suricate.debuglog('searching %r using scope %r...', query, scope)
    try:
        html = ''

        if scope and scope.lower() != query.lower():
            scoped_kwargs = dict(kwargs)
            scoped_kwargs['hide_headers'] = True
            scoped_kwargs['hide_signature'] = True
            scoped_kwargs['max_number_of_results'] = 1

            scoped_results = duckduckgo2html.search(
                scope + ' ' + query,
                DDG_USERAGENT)
            scoped_html = duckduckgo2html.results2html(
                scoped_results,
                **scoped_kwargs)

            if scoped_html and not kwargs.get('hide_headers', False):
                html += '<h1>Scope {0}</h1>'.format(scope)
            if scoped_html:
                html += scoped_html
                if 'max_number_of_results' in kwargs and kwargs['max_number_of_results']:
                    kwargs['max_number_of_results'] -= 1
                    if kwargs['max_number_of_results'] < 1:
                        return html

        results = duckduckgo2html.search(query, DDG_USERAGENT)
        html += duckduckgo2html.results2html(results, **kwargs)

        return html if html else 'Sorry, no results found'
    except Exception:
        message = 'Sorry, there was an error retrieving the answer.'
        logging.exception(message)
        return message


def _get_scope(view, regex, point):
    matchobj = re.match(regex, str(view.scope_name(point)))
    return matchobj.group('keyword') if matchobj else None


def show_popup(view, event=None, css_file=None, scope_regex=None, **kwargs):
    popup = popup_util.PopUp(view, event=event, css_file=css_file)
    if popup.selected_words and popup.selected_words.words:
        point = popup.selected_words.position
        scope = _get_scope(view, scope_regex, point) if scope_regex else None
        answer = get_answer(popup.selected_words.words, scope=scope, **kwargs)
        popup.show(answer, max_width=450)


def insert_answer(edit, view, event=None):
    selected_words = popup_util.SelectedWords.make(view, event)
    if selected_words and selected_words.words:
        results = duckduckgo2html.search(selected_words.words, DDG_USERAGENT)
        has_answer = results and hasattr(results, 'answer') and results.answer
        if has_answer and results.answer.text:
            sublime_wrapper.insert(results.answer.text, edit, view, clear=False)
        else:
            sublime.status_message('Sorry, no results found')
