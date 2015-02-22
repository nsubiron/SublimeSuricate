# Sublime Suricate Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Search online"""

import sublime

import suricate

sublime_wrapper = suricate.import_module('lib.sublime_wrapper')

Engines = {
    'DuckDuckGo': 'https://duckduckgo.com/?q=',
    'Google': 'https://www.google.com/search?q='
}

def show(caption=None, engine=None):
    engine = _get_default_engine_if_not_valid(engine)
    prefix = Engines[engine]
    if not caption:
      caption = '%s:' % engine
    window = sublime.active_window()
    on_done = lambda string: _on_done(prefix, string, window)
    window.show_input_panel(caption, '', on_done, None, None)

def search_selection(view=None, engine=None):
    prefix = Engines[_get_default_engine_if_not_valid(engine)]
    window = sublime.active_window()
    for string in sublime_wrapper.get_selection(view):
      _on_done(prefix, string, window)

def _on_done(prefix, string, window):
    url = prefix + '+'.join(string.split())
    window.run_command('open_url', {'url': url})

def _get_default_engine_if_not_valid(engine, default='DuckDuckGo'):
    if engine is None:
      engine = suricate.Settings.get('default_search_engine', default)
    if engine not in Engines:
      suricate.log('ERROR: Search engine "%s" not implemented.', engine)
      engine = default
    return engine
