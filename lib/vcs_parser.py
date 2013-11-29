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

def parse(out, command, vcsname):
    """Returns a list of pairs ``[filepath, extra information]``."""
    mapper = globals()['_%s_mapper__%s' % (command, vcsname)]
    return [x for x in mapper(out)]

## Private #####################################################################

def _status_mapper__Surround(out):
    for line in out.split('\n'):
      if not line.startswith(' '):
        folder = '/'.join(line.strip().split('/')[1:])
      elif line.startswith(' ') and not line.startswith(' '*2):
        basename, state = line.split()[:2]
        path = '/'.join([folder, basename])
      elif line.startswith('   -'):
        text = '%s %s' % (state, line.strip())
        yield [path, text]

def _status_mapper__Git(out):
    modifiedkey = '#\tmodified:   '
    for line in out.split('\n'):
      if line.startswith(modifiedkey):
        path = line.replace(modifiedkey, '').strip()
        yield [path, 'modified']