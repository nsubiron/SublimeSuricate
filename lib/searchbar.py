# Sublime Suricate Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Search online"""

import suricate

from . import popup_util

suricate.reload_module(popup_util)


# @todo get more, add to settings?
ENGINES = {
    'DuckDuckGo': 'https://duckduckgo.com/?q=',
    'Google': 'https://www.google.com/search?q='
}


def show(view, window, caption=None, engine=None):
    engine = _get_default_engine_if_not_valid(engine)
    prefix = ENGINES[engine]
    if not caption:
        caption = '%s:' % engine
    selected_words = popup_util.SelectedWords.make(view, extend_to_words=False)
    initial_text = selected_words.words if selected_words else ''
    on_done = lambda string: _on_done(prefix, string, window)
    window.show_input_panel(caption, initial_text, on_done, None, None)


def search_selection(view, event=None, engine=None):
    prefix = ENGINES[_get_default_engine_if_not_valid(engine)]
    selected_words = popup_util.SelectedWords.make(view, event)
    query = selected_words.words if selected_words else ''
    _on_done(prefix, query, view.window())


def _on_done(prefix, string, window):
    url = prefix + '+'.join(string.split())
    window.run_command('open_url', {'url': url})


def _get_default_engine_if_not_valid(engine, default='DuckDuckGo'):
    if engine is None:
        engine = suricate.get_setting('default_search_engine', default)
    if engine not in ENGINES:
        suricate.log('ERROR: Search engine "%s" not implemented.', engine)
        engine = default
    return engine
