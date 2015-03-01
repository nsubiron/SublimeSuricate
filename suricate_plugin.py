# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import sys

import sublime_plugin

from . import suricate
from .suricate._suricate import _SuricateAPI as SuricateAPI
from .suricate.managers import command_manager


MANAGER = command_manager.CommandManager()


def plugin_loaded():
    SuricateAPI.set_ready()
    sys.modules['suricate'] = suricate
    settings = suricate.load_settings()
    MANAGER.load(settings)
    settings.clear_on_change('Suricate')
    settings.add_on_change('Suricate', MANAGER.reload_settings)
    suricate.debuglog('active')


def plugin_unloaded():
    SuricateAPI.unload()
    suricate.debuglog('unloaded')


class SuricateCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)
        self._update()

    def _update(self):
        suricate.debuglog('updating flags for view %s' % self.view.buffer_id())
        self.filename = self.view.file_name()
        self.flags = MANAGER.update(self.filename)

    def is_visible(self, key=None, **kwargs):
        if self.filename != self.view.file_name():
            self._update()
        return MANAGER.is_enabled(key, self.flags)

    def want_event(self):
        return True

    def run(self, edit, key, event=None):
        args = {
            'edit': edit,
            'view': self.view,
            'window': self.view.window(),
            'event': event,
            'active_flags': self.flags
        }
        MANAGER.run(key, args)
