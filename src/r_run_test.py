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
'''Module to test the R implementation'''

import os
import shutil
import subprocess
import unittest

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.r.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.r.formatter import Formatter

from utils import parse_dump

class RRunTest(unittest.TestCase):
    '''Tests for the parameter definition formatter'''

    @classmethod
    def setUpClass(cls):
        file_name = 'tests/good_r.txt'
        parser = ParameterParser(Validator())
        parameters = parser.parse(file_name)
        formatter = Formatter(parameters)
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/main_dump.r', 'tmp/main_dump.r')
        base_name = 'parser'
        cls._main_file = 'main_dump.r'
        artifacts = formatter.get_artifacts(base_name)
        parser_file = artifacts[0].name
        artifacts[0].action(os.path.join('tmp', parser_file))
        os.chdir('tmp')

    @classmethod
    def tearDownClass(cls):
        os.chdir('..')

    def test_default_run(self):
        result = subprocess.check_output(['Rscript', self._main_file])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(0, int(values['cl_remains']))
        self.assertEqual(4, len(values))

    def test_first_option_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(0, int(values['cl_remains']))
        self.assertEqual(4, len(values))

    def test_second_option_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-f', '3.14'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(4, len(values))

    def test_first_second_option_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-f', '3.14', '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(4, len(values))

    def test_first_third_option_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-str', 'alpha', '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'alpha'", values['str'])
        self.assertEqual(4, len(values))

    def test_all_options_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-str', 'alpha', '-a', '17', '-f', '-3.14'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(-3.14, float(values['f']))
        self.assertEqual("'alpha'", values['str'])
        self.assertEqual(4, len(values))

    def test_first_no_value(self):
        result = subprocess.check_output('Rscript {0} -a; exit 0'.format(self._main_file),
                                         stderr=subprocess.STDOUT, shell=True)
        self.assertEqual("### error: option '-a' expects a value\n", result)

    def test_second_option_one_additional_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-f', '3.14', 'bla'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(1, int(values['cl_remains']))
        self.assertEqual(4, len(values))

    def test_second_option_two_additional_run(self):
        result = subprocess.check_output(['Rscript', self._main_file, '-f', '3.14', 'bla', 'foo'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(2, int(values['cl_remains']))
        self.assertEqual(4, len(values))


if __name__ == '__main__':
    unittest.main()

