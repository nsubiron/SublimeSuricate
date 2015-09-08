# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import imp
import os

import sublime

from . import _variables


_THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


class _SuricateAPI(object):
    api_is_ready = False
    debug_log = False
    is_packaged = _THIS_FOLDER.endswith('.sublime-package')
    if is_packaged:
        package_path = _THIS_FOLDER
    else:
        package_path = os.path.abspath(os.path.join(_THIS_FOLDER, '..'))
    package_name = os.path.splitext(os.path.basename(package_path))[0]
    library_module_name = '.'.join([package_name, 'lib'])
    settings_file_base_name = 'Suricate.sublime-settings'
    profile_extension = '.suricate-profile'
    generated_files_path = None
    variables = {}

    @staticmethod
    def set_ready():
        if _SuricateAPI.api_is_ready:
            raise RuntimeError('suricate API already initialized')
        packages_path = sublime.packages_path()
        folder_path = os.path.join(packages_path, _SuricateAPI.package_name)
        _SuricateAPI.generated_files_path = os.path.abspath(folder_path)
        _SuricateAPI._init_variables()
        _SuricateAPI.api_is_ready = True

    @staticmethod
    def unload():
        _SuricateAPI.api_is_ready = False
        _SuricateAPI.variables.clear()

    @staticmethod
    def set_debug_log(active=None):
        if active is None:
            _SuricateAPI.debug_log = not _SuricateAPI.debug_log
        else:
            _SuricateAPI.debug_log = bool(active)

    @staticmethod
    def _init_variables():
        is_valid = lambda k, v: not k.startswith('_') and isinstance(v, str)
        prefix = 'suricate_'
        api_vars = vars(_SuricateAPI)
        variables = dict((prefix + k, v)
                         for k, v in api_vars.items() if is_valid(k, v))
        _SuricateAPI.variables.update(variables)


def api_is_ready():
    return _SuricateAPI.api_is_ready


def is_packaged():
    return _SuricateAPI.is_packaged


def log(message, *args):
    print('Suricate: ' + message % args)


def debuglog(message, *args):
    if _SuricateAPI.debug_log:
        log(message, *args)


def set_debuglog(active=None):
    _SuricateAPI.set_debug_log(active)


def reload_module(module):
    if get_setting('dev_mode', False):
        debuglog('reloading module %r', module.__name__)
        return imp.reload(module)
    return module


def extract_variables(window=None):
    if window is None:
        window = sublime.active_window()
    variables = _variables.extract_window_variables(window)
    variables.update(_SuricateAPI.variables)
    return variables


def expand_variables(value, variables=None, window=None):
    if variables is None:
        variables = extract_variables(window)
    return _variables.expand_variables(value, variables)


def get_variable(key, default=None):
    return extract_variables().get(key, default)


def load_settings():
    return sublime.load_settings(_SuricateAPI.settings_file_base_name)


def get_setting(key, default=None):
    return load_settings().get(key, default)
