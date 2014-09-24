# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import configparser
import sublime

from suricate import import_module

sublime_wrapper = import_module('lib.sublime_wrapper')

def insert(view, inifile, section):
    string = sublime.load_resource('Packages/User/' + inifile)
    config = configparser.ConfigParser()
    config.read_file(string.split('\n'))
    display_list =  [[x,y] for x,y in config[section].items()]
    on_done = lambda picked: view.run_command('insert', {'characters': picked[0]})
    sublime_wrapper.show_quick_panel(display_list, on_done)
