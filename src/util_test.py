#!/usr/bin/env python
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
'''Tests for the utilities'''

import unittest

from vsc.util import Indenter

class UtilTest(unittest.TestCase):

    def setUp(self):
        self._indenter = Indenter('\t', 1)

    def test_indent_empty(self):
        text = ''
        target_text = text
        result = self._indenter.indent(text)
        self.assertEqual(target_text, result)

    def test_indent_whitespace(self):
        text = '\t\t'
        target_text = text
        result = self._indenter.indent(text)
        self.assertEqual(target_text, result)

    def test_indent_single_line(self):
        text = 'abc def'
        target_text = '\t' + text
        result = self._indenter.indent(text)
        self.assertEqual(target_text, result)

    def test_multiple_indent_single_line(self):
        text = 'abc def'
        target_text = '\t\t\t' + text
        result = self._indenter.indent(text, count=3)
        self.assertEqual(target_text, result)

    def test_indent_multiple_lines(self):
        text = 'abc def\ndfg hij'
        target_text = '\tabc def\n\tdfg hij'
        result = self._indenter.indent(text)
        self.assertEqual(target_text, result)

    def test_levels(self):
        indenter = Indenter('\t')
        self.assertEqual(0, indenter.level)
        text = 'abc'
        self.assertEqual(text, indenter.indent(text))
        indenter.incr()
        self.assertEqual(1, indenter.level)
        self.assertEqual('\t' + text, indenter.indent(text))
        indenter.incr()
        self.assertEqual(2, indenter.level)
        self.assertEqual('\t\t' + text, indenter.indent(text))
        indenter.decr()
        self.assertEqual(1, indenter.level)
        self.assertEqual('\t' + text, indenter.indent(text))
        indenter.decr()
        self.assertEqual(0, indenter.level)
        self.assertEqual(text, indenter.indent(text))

    def test_text(self):
        indenter = Indenter('\t')
        self.assertEqual('', indenter.text())
        indenter.add('abc')
        self.assertEqual('abc', indenter.text())
        indenter.incr()
        indenter.add('def')
        self.assertEqual('abc\n\tdef', indenter.text())
        indenter.decr()
        indenter.add('hij')
        self.assertEqual('abc\n\tdef\nhij', indenter.text())
        indenter.add()
        indenter.incr()
        indenter.add('klm')
        indenter.add()
        indenter.add('nop')
        self.assertEqual('abc\n\tdef\nhij\n\n\tklm\n\n\tnop', indenter.text())

