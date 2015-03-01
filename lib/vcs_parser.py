# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Parse output of different version control systems.
Usage example: git status | python {file} status git"""

import suricate

NOT_IMPLEMENTED_MESSAGE = """{command} parser for {vcsname} not implemented.
Please implement {parser} in {file}."""


def parse(out, command, vcsname):
    """Returns a list of pairs ``[filepath, extra information]``."""
    try:
        mapper = globals()['_%s_mapper__%s' % (command, vcsname)]
    except KeyError as error:
        kwargs = {
            'parser': error,
            'command': command,
            'vcsname': vcsname,
            "file": __file__}
        suricate.log(NOT_IMPLEMENTED_MESSAGE.format(**kwargs))
        return []
    return [x for x in mapper(out)]

## Parsers ###############################################################


def _status_mapper__Surround(out):
    for line in out.split('\n'):
        if not line.startswith(' '):
            folder = '/'.join(line.strip().split('/')[1:])
        elif line.startswith(' ') and not line.startswith(' ' * 2):
            basename, state = line.split()[:2]
            path = '/'.join([folder, basename])
        elif line.startswith('   -'):
            text = '%s %s' % (state, line.strip())
            yield [path, text]


def _modifiedfiles_mapper__Git(out):
    return [[x, 'modified'] for x in out.split('\n') if x and not x.isspace()]

## Main ##################################################################

if __name__ == '__main__':

    import sys
    import argparse

    def main():
        parser = argparse.ArgumentParser(
            description=__doc__.format(
                file=__file__))
        parser.add_argument('command')
        parser.add_argument('vcsname')
        args = parser.parse_args()

        for path, text in parse(
                sys.stdin.read(), args.command, args.vcsname.title()):
            print('%s: %s' % (path, text))

    main()
