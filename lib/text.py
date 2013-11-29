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

import sublime_wrapper

def complete_line(line, char=None, n=80):
    """Returns a string of ``char`` that together with ``line`` sums ``n``
    characters. If ``char`` is ``None`` use ``line``'s last character."""
    if (line or char) and len(line) < n:
      return (line[-1] if char is None else char)*(n-len(line))
    return line

def fill_current_line(view, *args, **kwargs):
    """See text.fill_line.
    @todo It doesn't work as expected, rewrite."""
    getline = lambda region: view.substr(view.line(region.end()))
    func = lambda region: complete_line(getline(region), *args, **kwargs)
    sublime_wrapper.foreach_region(func, view, clear=True)
