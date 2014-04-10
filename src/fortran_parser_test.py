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
'''Module to test the parameter definition parser for Fortran'''

import unittest

from vsc.parameter_weaver.params import Parameter, ParameterCsvParser, WeaverError
from vsc.parameter_weaver.base_validator import BaseValidator, ParameterDefinitionError
from vsc.parameter_weaver.fortran.types import Integer, DoublePrecision, CharacterArray
from vsc.parameter_weaver.fortran.validator import Validator

class FortranParserTest(unittest.TestCase):
    '''Tests for Fortran parameter definition parser'''

    def setUp(self):
        '''Set up parameter list to be expected from valid viles'''
        self._parameters = [
            Parameter(Integer(), 'a', '10'),
            Parameter(DoublePrecision(), 'f', '0.19D00'),
            Parameter(CharacterArray(), 'str', 'abcde')
        ]
        self._parameters_w_description = [
            Parameter(Integer(), 'a', '10'),
            Parameter(DoublePrecision(), 'f', '0.19D00', 'relative error'),
            Parameter(CharacterArray(), 'str', 'a;bcde', 'string to print')
        ]
        self._parser = ParameterCsvParser(Validator())

    def test_simple_tab_separated_valid(self):
        '''Parse a simple file that is well-formed and valid'''
        file_name = 'tests/good_fortran.txt'
        t = CharacterArray()
        try:
            self.assertEqual(self._parameters, self._parser.parse(file_name))
        except ParameterDefinitionError as error:
            self.fail(str(error))


if __name__ == '__main__':
    unittest.main()

