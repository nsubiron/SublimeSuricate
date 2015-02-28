# Sublime Suricate Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Search on DuckDuckGo"""

import sublime

import logging
import re

import suricate

from .thirdparty import duckduckgo2html

def get_selection_and_point(view):
    selection = view.sel()
    # Single cursor only.
    if len(selection) == 1:
      if selection[0].empty():
        return view.substr(view.word(selection[0].a)), selection[0].a
      else:
        return view.substr(selection[0]), selection[0].a
    return None, None

def get_scope(view, point):
    scope = view.scope_name(point)
    matchobj = re.match(r'(source).([a-z+]+)', str(scope))
    if matchobj:
      return matchobj.group(2)

def _clean_headers(html):
    regex = re.compile(r'(<h[0-9]+>(Answer|Abstract)</h[0-9]+>)')
    if len(regex.findall(html)) == 1:
      return regex.sub('', html)
    return html

def get_answer(query, scope=None, *args, **kwargs):
    suricate.log('Searching %r (using scope %r)...', query, scope)
    useragent = 'sublime-suricate'

    try:
      results = duckduckgo2html.search(query, useragent)

      # import os
      # this_folder = os.path.dirname(os.path.abspath(__file__))
      # with open(os.path.join(this_folder, 'last_run.json'), 'w+') as fd:
      #     fd.write('// Query %r.\n' % query)
      #     fd.write(results.json if results else 'None')

      html = duckduckgo2html.results2html(results)

      # with open(os.path.join(this_folder, 'answer.html'), 'w+') as fd:
      #     fd.write(html)

      # return _clean_headers(html)
      return html
    except:
      message = 'Sorry, there was an error retrieving the answer.'
      logging.exception(message)
      return message

def show_popup(view, css_file=None, *args, **kwargs):
    query, point = get_selection_and_point(view)
    if not query:
      return
    scope = get_scope(view, point)
    if scope in ['plain']:
      scope = None
    answer = get_answer(query, scope=scope, *args, **kwargs)
    if css_file is not None:
      style = '<style>%s</style>' % sublime.load_resource(css_file).replace('\r', '')
      answer = style + answer
    on_navigate = lambda url: view.window().run_command('open_url', {'url': url})
    view.show_popup(answer, on_navigate=on_navigate, max_width=400)
