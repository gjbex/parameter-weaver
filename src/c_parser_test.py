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
'''Module to test the parameter definition parser for C'''

import unittest

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.base_validator import BaseValidator, ParameterDefinitionError
from vsc.parameter_weaver.c.validator import Validator
from vsc.parameter_weaver.c.types import Int, Double, CharPtr
from vsc.parameter_weaver.help_formatter import HelpFormatter

class ParserTest(unittest.TestCase):
    '''Tests for the parameter definition parser'''

    def setUp(self):
        '''Set up parameter list to be expected from valid viles'''
        self._parameters = [
            Parameter(Int(), 'a', '10'),
            Parameter(Double(), 'f', '0.19'),
            Parameter(CharPtr(), 'str', 'abcde')
        ]
        self._parameters_w_description = [
            Parameter(Int(), 'a', '10'),
            Parameter(Double(), 'f', '0.19', 'relative error'),
            Parameter(CharPtr(), 'str', 'a;bcde', 'string to print')
        ]
        self._parser = ParameterParser(Validator())

    def test_simple_tab_separated_valid(self):
        '''Parse a simple file that is well-formed and valid'''
        file_name = 'tests/good_c.txt'
        try:
            self.assertEqual(self._parameters, self._parser.parse(file_name))
        except ParameterDefinitionError as error:
            self.fail(str(error))

    def test_default_descriptions(self):
        '''Test for the default description'''
        target = ('  -a <integer>: number of items (default: 10)\n' +
                  '  -f <DP float>: fraction valid (default: 0.19)\n' +
                  '  -my_string <string>: name of run (default: \'abcde\')\n'
                  '  -?: print this message')
        file_name = 'tests/descr_c.txt'
        try:
            parameters = self._parser.parse(file_name)
            help_formatter = HelpFormatter(parameters)
            description = help_formatter.create_help()
            self.assertEqual(target, description)
        except ParameterDefinitionError as error:
            self.fail(str(error))

    def test_complete_description(self):
        '''Test for the complete description'''
        target = ('usage: my_appl <conf> -a <integer> -f <DP float> -my_string <string> -? <file>\n' +
                  '  Brilliant application\n' +
                  '  -a <integer>: number of items (default: 10)\n' +
                  '  -f <DP float>: fraction valid (default: 0.19)\n' +
                  '  -my_string <string>: name of run (default: \'abcde\')\n' +
                  '  -?: print this message\n' +
                  '(c) 2013, gjb')
        file_name = 'tests/descr_c.txt'
        try:
            parameters = self._parser.parse(file_name)
            help_formatter = HelpFormatter(parameters,
                                           pre_params='<conf>',
                                           post_params='<file>',
                                           application='my_appl',
                                           copyright='(c) 2013, gjb')
            help_formatter.description = 'Brilliant application'
            description = help_formatter.create_help()
            self.assertEqual(target, description)
        except ParameterDefinitionError as error:
            print error.msg
            self.fail(str(error))

    def test_simple_tab_separated_invalid(self):
        '''Parse a simple file that is well-formed but invalid'''
        file_name = 'tests/bad_c.txt'
        with self.assertRaises(ParameterDefinitionError):
            parameters = self._parser.parse(file_name)
    
    def test_commented_semicolon_separated_valid(self):
        '''Parse a file containing comments and blank lines, with ';' as
           field separator that is well-formed and valid, but where
           dialect can not be determined'''
        file_name = 'tests/ugly_c.txt'
        with self.assertRaises(WeaverError):
            parameters = self._parser.parse(file_name)

    def test__semicolon_separated_delimiter(self):
        '''Parse a file blank lines, with ';' as field separator that is
           well-formed and valid, but where dialect can not be determined;
           provide delimiter'''
        file_name = 'tests/ugly_c.txt'
        parser = ParameterParser(Validator(), delimiter=';')
        try:
            self.assertEqual(self._parameters, parser.parse(file_name))
        except ParameterDefinitionError as error:
            self.fail(str(error))

    def test_excel_csv(self):
        '''Parse an Excel generated CSV file with some descriptions
           missing'''
        file_name = 'tests/excel_c.csv'
        try:
            result = self._parser.parse(file_name)
            for i in range(0, 3):
                self.assertEqual(self._parameters_w_description[i].type,
                                 result[i].type)
                self.assertEqual(self._parameters_w_description[i].name,
                                 result[i].name)
                self.assertEqual(self._parameters_w_description[i].default,
                                 result[i].default)
                self.assertEqual(self._parameters_w_description[i].description,
                                 result[i].description)
        except ParameterDefinitionError as error:
            self.fail(str(error))


if __name__ == '__main__':
    unittest.main()

