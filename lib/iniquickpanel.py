# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import configparser

import sublime

import suricate

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


def insert(view, ini_file, section):
    string = sublime_wrapper.locate_and_load_resource(ini_file)
    config = configparser.ConfigParser()
    config.read_file(string.split('\n'))
    display_list = [[x, y] for x, y in config[section].items()]
    on_done = lambda picked: view.run_command(
        'insert', {
            'characters': picked[0]})
    sublime_wrapper.show_quick_panel(display_list, on_done)
