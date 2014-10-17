# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import sublime

from suricate import Settings
from suricate import Verbose
from suricate import build_variables
from suricate import flags
from suricate import import_module
from suricate import util

process = import_module('lib.process')
sublime_wrapper = import_module('lib.sublime_wrapper')
vcs_parser = import_module('lib.vcs_parser')

SourceControlFileBaseName = 'SourceControlCommands.json'

def _do(cmd, caption, path, out=None, ask=None, **kwargs):
    working_dir, base_name = os.path.split(path) if os.path.isfile(path) else (path, '.')
    cmd = util.replacekeys(cmd, {'path': base_name})
    if Verbose: print('vcs do: ' + ' '.join(cmd))
    if ask and not sublime.ok_cancel_dialog(util.replacekeys(ask, {'path': base_name}), caption):
      return
    if out == 'gui':
      process.new_thread(cmd, working_dir)
    elif out == 'buffer':
      text, err = process.popen(cmd, working_dir)
      name = ' '.join(cmd[:2])
      sublime_wrapper.flush_to_buffer(text, name=name, scratch=True, syntax='Diff')
    elif out is not None and out.endswith('_list'):
      cout, err = process.popen(cmd, working_dir)
      vcsname = flags.to_string(flags.get_vcs(path))
      lst = vcs_parser.parse(cout, out.replace('_list', ''), vcsname)
      window = sublime.active_window()
      getpath = lambda picked: os.path.abspath(os.path.join(path, picked[0]))
      on_done = lambda picked: window.open_file(getpath(picked))
      sublime_wrapper.show_quick_panel(lst, on_done, window)
    else:
      sublime_wrapper.execute(cmd=cmd, working_dir=working_dir)

def call(cmd, active_flags, view):
    settings = sublime.load_settings(SourceControlFileBaseName)
    scslist = settings.get('user_source_control')
    scslist += settings.get('source_control')
    for item in scslist:
      cmdi = item['commands'].get(cmd)
      if cmdi is not None and \
         flags.special_check(active_flags, flags.from_string(item['flags'])) and \
         all(util.which(exe) is not None for exe in item['exes']):
        if Verbose: print('%s: %s' % (item['name'], cmdi['caption']))
        cmdi['path'] = view.file_name()
        return _do(**cmdi)
    print('Source control command \'%s\' is not available.' % cmd)

def show_quick_panel(path=None):
    def _show_quick_panel(display_list):
        if display_list:
          on_done = lambda picked: _show_quick_panel(picked.do())
          sublime_wrapper.show_quick_panel(display_list, on_done)
    _show_quick_panel(_get_list(path))

class PathProxy(list):
    def __init__(self, name, vcs, path):
        self.path = path
        list.__init__(self, [name, '%s; %s' % (vcs, path)])

    def do(self):
        return _get_list(self.path)

class _CmdiProxy(list):
    def __init__(self, parent, cmdi):
        self.cmdi = cmdi
        list.__init__(self, ['%s: %s' % (parent, cmdi['caption']), ' '.join(cmdi['cmd'])])

    def do(self):
        return _do(**self.cmdi)

def _get_list(path):
    if path is None:
      repos = {'Current File': '${file}'}
      repos.update(Settings.get('vcs_working_dirs', {}))
      repos = build_variables.expand(repos)
      def parse_settings(repositories):
          for name, path in repositories.items():
            path = os.path.abspath(path)
            if os.path.exists(path):
              f = flags.get_vcs(path)
              if f != flags.Flags.EMPTY:
                yield PathProxy(name, flags.to_string(f), path)
      return sorted([x for x in parse_settings(repos)])
    elif os.path.isfile(path) or os.path.isdir(path):
      return get_commands(flags.parse(path), path)
    else:
      sublime.error_message('File path "%s" not found!' % path)

def get_commands(active_flags, path):
    settings = sublime.load_settings(SourceControlFileBaseName)
    scslist = settings.get('user_source_control')
    scslist += settings.get('source_control')
    commandlist = []
    for item in scslist:
      if flags.special_check(active_flags, flags.from_string(item['flags'])) and \
         all(util.which(exe) is not None for exe in item['exes']):
        for name, cmdi in item.get('commands', {}).items():
          cmdi['path'] = path
          commandlist.append(_CmdiProxy(item['name'], cmdi))
    return commandlist

