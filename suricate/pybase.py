# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Python 2 and 3 compatibility."""

import sys

PY2 = sys.version_info[0] == 2

if not PY2:
  unichr = chr
  text_type = str
  string_types = (str,)
  numeric_types = (int, float, complex)
  sequence_types = (list, tuple, range)
  binary_sequence_types = (bytes, bytearray, memoryview)
  set_types = (set, frozenset)
  mapping_types = (dict,)
else:
  unichr = unichr
  text_type = unicode
  string_types = (str, unicode)
  numeric_types = (int, float, long, complex)
  sequence_types = (list, tuple, xrange)
  binary_sequence_types = (bytearray, buffer)
  set_types = (set, frozenset)
  mapping_types = (dict,)
