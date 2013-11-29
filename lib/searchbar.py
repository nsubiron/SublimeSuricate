# Sublime Suricate is licensed under the GPL license.
#
# Copyright (C) 2013 N. Subiron
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""Search online"""

import sublime

from suricate import Settings

Engines = {
  'DuckDuckGo': 'https://duckduckgo.com/?q='
}

def show(caption=None, engine=None, default='DuckDuckGo'):
    if engine is None:
      engine = Settings.get('default_search_engine', default)
    if engine not in Engines:
      print('Search engine "%s" not implemented.' % engine)
      engine = default
    prefix = Engines[engine]
    if not caption:
      caption = '%s:' % engine
    window=sublime.active_window()
    on_done = lambda string: _on_done(prefix, string, window)
    window.show_input_panel(caption, '', on_done, None, None)

def _on_done(prefix, string, window):
    url = prefix + '+'.join(string.split())
    window.run_command('open_url', {'url': url})
