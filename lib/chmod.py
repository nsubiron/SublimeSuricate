# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import stat

def _current_permisions(path):
    return os.stat(path).st_mode

def executable(path):
    os.chmod(path, _current_permisions(path)|stat.S_IEXEC)

def toggle_read_only(path):
    if os.access(path, os.W_OK):
      os.chmod(path, stat.S_IREAD)
    else:
      os.chmod(path, _current_permisions(path)|stat.S_IWRITE)
