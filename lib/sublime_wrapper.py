# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Handy wrappers around sublime API."""

import sublime

import suricate


def execute(window=None, **kwargs):
    """Runs an external process asynchronously. On Windows, GUIs are suppressed.
    ``exec`` is the default command used by build systems, thus it provides
    similar functionality. However, a few options in build systems are taken
    care of by Sublime Text internally so they list below only contains
    parameters accepted by this command.
      * cmd ``[String]``
      * file_regex ``String``
      * line_regex ``String``
      * working_dir ``String``
      * encoding ``String``
      * env ``{String: String}``
      * path ``String``
      * shell ``Bool``
      * kill ``Bool``: If True will simply terminate the current build process.
      This is invoked via Build: Cancel command from the Command Palette.
      * quiet ``Bool``: If True prints less information about running the
      command."""
    if window is None:
        window = sublime.active_window()
    kwargs = suricate.expand_variables(kwargs, window=window)
    window.run_command('exec', kwargs)


def flush_to_buffer(
        text,
        name=None,
        scratch=False,
        syntax=None,
        syntax_file=None):
    """Flush text to a new buffer."""
    view = sublime.active_window().new_file()
    view.set_scratch(scratch)
    if name is not None:
        view.set_name(name)
    if syntax is not None:
        syntax_files = sublime.find_resources(syntax + '.tmLanguage')
        syntax_files += sublime.find_resources(syntax + '.hidden-tmLanguage')
        if syntax_files:
            view.set_syntax_file(syntax_files[0])
    elif syntax_file is not None:
        view.set_syntax_file(syntax_file)
    auto_indent = view.settings().get("auto_indent")
    view.settings().set("auto_indent", False)
    view.run_command('insert', {'characters': text})
    view.settings().set("auto_indent", auto_indent)
    view.run_command("move_to", {"to": "bof"})


def show_quick_panel(display_list, on_done, window=None):
    """Show a quick panel fed with display_list on window. on_done must be a
    callable object that accepts one argument, the element picked (not the
    index!). It won't be called if the user cancels."""
    if not display_list:
        suricate.log('ERROR: Quick panel fed with an empty list!')
        return
    if window is None:
        window = sublime.active_window()

    def _on_done(index):
        if index != -1:
            on_done(display_list[index])
        sublime.status_message('Cancelled')
    # This allows nested quick panels on Sublime Text 3.

    def _on_show_quick_panel():
        window.run_command('hide_overlay')
        window.show_quick_panel(display_list, _on_done)
    sublime.set_timeout(_on_show_quick_panel, 0)


def copy_build_variable_to_clipboard(key=None, window=None):
    """If key is None, show a quick panel with the currently available build
    variables."""
    variables = suricate.extract_variables(window)
    on_done = lambda picked: sublime.set_clipboard(picked[1])
    if key is None:
        show_quick_panel(sorted([[k, i] for k, i in variables.items()]), on_done)
    else:
        on_done([None, variables[key]])


def paste_build_variable(edit, key=None, view=None, window=None):
    """If key is None, show a quick panel with the currently available build
    variables."""
    variables = suricate.extract_variables(window)
    on_done = lambda picked: insert(picked[1], edit, view, clear=True)
    if key is None:
        show_quick_panel(sorted([[k, i] for k, i in variables.items()]), on_done)
    else:
        on_done([None, variables[key]])


def get_selection(view=None):
    """Retrieve selected regions as a list of strings."""
    if view is None:
        view = sublime.active_window().active_view()
    return [view.substr(region) for region in view.sel()]


def insert(string, edit, view, clear=False):
    """Insert string replacing view's current selection. If clear, move the
    cursor to the end of each region."""
    for region in view.sel():
        if clear:
            view.replace(edit, region, '')
            view.insert(edit, region.begin(), string)
        else:
            view.replace(edit, region, string)


def foreach_region(func, edit, view, clear=False):
    """Replace each selected region by the result of applying func on that
    region. If clear, move the cursor to the end of each region."""
    for region in view.sel():
        string = func(region)
        if clear:
            view.replace(edit, region, '')
            view.insert(edit, region.begin(), string)
        else:
            view.replace(edit, region, string)


def locate_and_load_resource(hint):
    """Try to load the first match of hint"""
    try:
        return sublime.load_resource(hint)
    except OSError:
        pass
    resources = sublime.find_resources(hint)
    if not resources:
        sublime.error_message('Unable to locate %r' % hint)
        raise OSError('resource not found')
    first = resources[0]
    if len(resources) > 1:
        suricate.log('WARNING: more than one %r found, using %r', hint, first)
    return sublime.load_resource(first)
