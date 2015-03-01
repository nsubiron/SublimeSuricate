# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import subprocess

import sublime

import suricate


def touch(paths, times=None):
    for path in paths:
        with open(path, 'a'):
            os.utime(path, times)


def spawn(cmd, working_dir=None, shell=None):
    """Spawn a new process"""
    popen(cmd, working_dir, shell, timeout=0)


def async(*args, **kwargs):
    """Launch a new process and wait for output asynchronously.
    Calls popen_print_output."""
    callback = lambda: popen_print_output(*args, **kwargs)
    sublime.set_timeout_async(callback, 10)


def popen_print_output(*args, **kwargs):
    """Launch a new process and wait for output; show status message when
    finished and print stdout to Sublime's console. Show an error dialogue if
    something printed to stderr. Calls popen."""
    out, err = popen(*args, **kwargs)
    status = 'Subprocess finished.'
    sublime.set_timeout(lambda: sublime.status_message(status), 10)
    if out:
        print(out)
    if err:
        sublime.error_message(err)


def popen(cmd, working_dir=None, shell=None, timeout=None):
    """Wrapper around subprocess.Popen. Launch a new process and wait timeout
    seconds for output. Return stdout, stderr."""
    # Prepare arguments.
    cmd = suricate.expand_variables(cmd)
    working_dir = suricate.expand_variables(working_dir)
    if shell is None:
        shell = sublime.platform().lower() == 'windows'
    kwargs = {'cwd': working_dir, 'shell': shell}
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.PIPE
    # Launch process.
    suricate.debuglog('popen: %s', ' '.join(cmd))
    process = subprocess.Popen(cmd, **kwargs)
    try:
        out, err = process.communicate(timeout=timeout)
        decode = lambda x: None if x is None else x.decode('utf-8')
        return decode(out), decode(err)
    except subprocess.TimeoutExpired:
        if timeout != 0:
            suricate.log('WARNING: Popen: time-out expired, ignoring output')
        return None, None


def startfile(path):
    """Try to emulate the behaviour of double-clicking the file."""
    path = suricate.expand_variables(path)
    platform = sublime.platform().lower()
    if not os.access(path, os.F_OK):
        sublime.error_message('Cannot open file "%s"' % path)
        return
    if platform == 'windows':
        os.startfile(path)
    else:
        launcher = 'xdg-open' if platform == 'linux' else 'open'
        popen_print_output([launcher, path], timeout=5)
