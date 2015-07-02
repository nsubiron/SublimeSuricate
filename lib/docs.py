# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Basic tools to parse python files and generate documentation."""

import inspect
import os

from collections import namedtuple

import suricate

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


ModuleInfo = namedtuple('ModuleInfo', ['name', 'doc', 'functions'])
RoutineInfo = namedtuple('RoutineInfo', ['signature', 'doc'])


def routine(funcobj):
    """Retrieve signature as string of funcobj."""
    argspec = inspect.getargspec(funcobj)
    sign = []
    dsize = 0 if not argspec.defaults else len(argspec.defaults)
    getd = lambda x: "'%s'" % x if isinstance(x,str) else x
    for i, arg in enumerate(argspec.args, dsize - len(argspec.args)):
        sign.append(arg + ('' if i < 0 else '=%s' % getd(argspec.defaults[i])))
    if argspec.varargs:
        sign.append('*%s' % argspec.varargs)
    if argspec.keywords:
        sign.append('**%s' % argspec.keywords)
    return RoutineInfo(
        '%s(%s)' %
        (funcobj.__name__,
         ', '.join(sign)),
        funcobj.__doc__)


def module(module_name, metaname=None):
    """Retrieve information of module's routines. Note: the module is
    reloaded."""
    if metaname is None:
        metaname = module_name
    try:
        module = import_module(module_name)
        info = ModuleInfo(metaname, module.__doc__, [])
        for obj_name in [x for x in dir(module) if not x.startswith('_')]:
            obj = getattr(module, obj_name)
            if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                info.functions.append(routine(obj))
        return info
    except Exception as e:
        info = '%s: %s' % (type(e).__name__, ', '.join(e.args))
        return ModuleInfo(metaname, info, [])


def folder(path, parents=[]):
    path = os.path.abspath(path)
    for item in [x for x in os.listdir(path) if not x.startswith('_')]:
        itempath = os.path.join(path, item)
        if os.path.isdir(itempath):
            for info in folder(item, parents + [item]):
                yield info
        elif item.endswith('.py'):
            basename = item[:-3]
            yield module(basename, path, '.'.join(parents + [basename]))


def markdown(items, level=1, indent=0, indentstr='  '):
    getdoc = lambda info: '' if info.doc is None else info.doc + '\n'
    for info in items:
        if isinstance(info, ModuleInfo):
            yield '%s%s %s' % (indentstr * indent, '#' * level, info.name)
            for line in getdoc(info).split('\n'):
                yield '%s%s' % (indentstr * indent, line.strip())
            for line in markdown(
                    lambda: info.functions,
                    level,
                    indent,
                    indentstr):
                yield line
        elif isinstance(info, RoutineInfo):
            yield '%s* ``%s``' % (indentstr * indent, info.signature)
            for line in getdoc(info).split('\n'):
                yield '%s%s' % (indentstr * (indent + 1), line.strip())
        else:
            raise Exception('Invalid info type!')


def to_buffer_(title, root):
    print('Docs for %s...' % root)
    items = module(root)
    for line in markdown([items]):
        print(line)
    return
    text = '%s\n%s\n\n' % (title, '=' * len(title))
    text += '## modules\n\n'
    text += '\n'.join(line for line in markdown(lambda: folder(root), 3))
    sublime_wrapper.flush_to_buffer(
        text,
        name=title,
        scratch=True,
        syntax='Markdown')


class MarkdownWriter(object):
    def __init__(self):
        self.lines = []

    def newline(self):
        self.lines.append('')

    def add_header(self, header, level):
        if level < 1:
            raise ValueError('invalid markdown header level')
        elif level == 1 or level == 2:
            self._write(header)
            underline = '=' if level == 1 else '-'
            self._write(len(header)*underline)
        else:
            self._write(level*'#' + ' ' + header)
        self.newline()

    def add_module(self, alias, module_info):
        # @todo alias might be None.
        self.add_header(alias, level=2)
        if module_info.doc:
            self._write(module_info.doc)
            self.newline()
        for function_info in module_info.functions:
            self.add_function(function_info)

    def add_function(self, function_info):
        self.add_header('`%s`' % function_info.signature, level=3)
        if function_info.doc:
            self._write(function_info.doc.replace('\n    ', '\n'))
            self.newline()

    def _write(self, line, indent=0):
        if line:
            self.lines.append(indent*'  ' + line)


import pkgutil

def to_buffer(title, modules):
    # @todo infinite recursion.
    assert not suricate.is_packaged()

    writer = MarkdownWriter()
    writer.add_header(title, level=1)

    for mymodule in modules:
        module_name = mymodule['module']
        module_alias = mymodule.get('alias')
        recursive = mymodule.get('recursive', False)

        suricate.log('generating documentation for %r...', module_name)

        root = import_module(module_name)

        if not recursive:
            writer.add_module(module_alias, module(module_name))
        else:
            for _, name, _ in pkgutil.walk_packages(root.__path__, root.__name__ + '.'):
                suricate.log('parsing module %r...', name)
                module_info = module(name)
                if module_alias and module_info.name.startswith(module_name):
                    alias = module_alias + module_info.name[len(module_name):]
                else:
                    alias = module_info.name
                writer.add_module(alias, module_info)



    sublime_wrapper.flush_to_buffer(
        '\n'.join(writer.lines),
        name=title,
        scratch=True,
        syntax='Markdown')


import importlib
import sys
def import_module(module_name):
    was_present = module_name in sys.modules
    suricate.debuglog('import module %r', module_name)
    module = importlib.import_module(module_name)
    # @todo do NOT reload the suricate module!
    # return suricate.reload_module(module) if was_present else module
    return module
