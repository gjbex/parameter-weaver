#
# ParameterWeaver: a code generator to handle command line parameters
# and configuration files for C/C++/Fortran/R/Octave
# Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''Some utility functions for ParameterWeaver'''

class Indenter(object):
    '''Indenter adds indentation to strings that represent lines of text'''

    def __init__(self, indent, level=0, eol='\n'):
        self._indent = indent
        self._init_level = level
        self.clear()
        self._eol = eol

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    @property
    def eol(self):
        return self._eol

    @property
    def indent_str(self):
        return self._indent

    def incr(self, count=1):
        self._level += count
        return self

    def decr(self, count=1):
        self._level -= count
        return self

    def indent(self, text, count=None):
        if len(text.strip()) == 0:
            return text
        indent = (
            count * self.indent_str
            if count is not None
            else self.level * self.indent_str
        )
        lines = text.split(self.eol)
        lines = [indent + x for x in lines]
        return self.eol.join(lines)

    def add(self, line=''):
        self._buffer.append(self.indent(line))
        return self

    def text(self):
        return self.eol.join(self._buffer)

    def clear(self):
        self._buffer = []
        self._level = self._init_level

