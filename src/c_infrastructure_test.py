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
'''Module to test the general infrastructure of the weaver'''

import unittest

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.base_validator import BaseValidator, ParameterDefinitionError
from vsc.parameter_weaver.c.validator import Validator

class LanguageFreaturesTest(unittest.TestCase):
    '''Tests the language features'''

    def setUp(self):
        self._validator = Validator()

    def test_c_name(self):
        self.assertEqual('C', self._validator.programming_language)

    def test_c_types(self):
        types = ['bool', 'char *', 'double', 'float',
                 'int', 'long']
        self.assertEqual(types, sorted(self._validator.types()))

    def test_type_name(self):
        type_name = 'Config'
        self.assertTrue(self._validator.is_valid_type_name(type_name))

    def test_invalid_type_name(self):
        type_name = '3Config'
        self.assertFalse(self._validator.is_valid_type_name(type_name))


if __name__ == '__main__':
    unittest.main()

