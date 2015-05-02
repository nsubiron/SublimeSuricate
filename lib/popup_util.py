# Sublime Suricate Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Handy wrappers around sublime pop-up API."""

import os
import re

import sublime

import suricate

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


def score(lhs, rhs):
    intersection = set(lhs.split()).intersection(set(rhs.split()))
    return sum(len(x) for x in intersection) / len(lhs + rhs)


def _find_best_css(view, folder, default=None):
    regex_remove = re.compile(r'[\(\)\{\}\[\]\\-]')
    get_basename = lambda x: os.path.splitext(os.path.basename(x))[0]
    clean = lambda x: regex_remove.sub(' ', get_basename(x).lower())
    css_files = [
        x for x in sublime.find_resources('*.css') if x.startswith(folder)]
    color_scheme = clean(view.settings().get('color_scheme'))
    scored_files = [(score(clean(x), color_scheme), x) for x in css_files]
    suricate.debuglog('color scheme: %r, css files: %s', color_scheme, scored_files)
    scored_files = [x for x in scored_files if x[0] > 0]
    if not scored_files:
        return default
    if len(scored_files) > 1:
        scored_files = sorted(scored_files, key=lambda x: x[0], reverse=True)
    return scored_files[0][1]


def get_css(view):
    style_file = suricate.get_setting('popup_style_file')
    if style_file is None or style_file == 'auto':
        css_path = 'Packages/${suricate_package_name}/css'
        css_path = suricate.expand_variables(css_path, window=view.window())
        default_css = css_path + '/default.css'
        default = suricate.get_setting('popup_style_file_fallback', default_css)
        default = suricate.expand_variables(default, window=view.window())
        return _find_best_css(view, css_path, default)
    return style_file


class SelectedWords(object):
    def __init__(self, words, position):
        self.words = words
        self.position = position

    @staticmethod
    def make(view, event=None, extend_to_words=True):
        if extend_to_words:
            make_word = lambda point: view.substr(view.word(point))
        else:
            make_word = lambda point: ''
        if event:
            point = view.window_to_text((event['x'], event['y']))
            for region in view.sel():
                if region.contains(point):
                    return SelectedWords(view.substr(region), point)
            return SelectedWords(make_word(point), point)
        else:
            selection = view.sel()
            # Single cursor only.
            if len(selection) == 1:
                point = selection[0].b
                if selection[0].empty():
                    return SelectedWords(make_word(point), point)
                else:
                    return SelectedWords(view.substr(selection[0]), point)
            return None


class PopUp(object):
    def __init__(self, view, event=None, css_file=None):
        self.view = view
        self.css_file = css_file if css_file else get_css(view)
        self.style = self._get_style(self.css_file)
        self.selected_words = SelectedWords.make(view, event)

    def show(self, content, on_navigate=None, location=None, **kwargs):
        if not on_navigate:
            on_navigate = self._on_navigate
        if location is None and self.selected_words:
            location = self.selected_words.position
        self.view.show_popup(
            self.style + content,
            location=location,
            on_navigate=on_navigate,
            **kwargs)

    def _on_navigate(self, url):
        self.view.window().run_command('open_url', {'url': url})

    @staticmethod
    def _get_style(css_file):
        if not css_file:
            return ''
        css = sublime_wrapper.locate_and_load_resource(css_file)
        return '<style>%s</style>' % css.replace('\r', '')
