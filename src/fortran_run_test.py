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
'''Module to test the Fortran implementation'''

import os
import shutil
import subprocess
import unittest

from vsc.parameter_weaver.params import Parameter, ParameterCsvParser, WeaverError
from vsc.parameter_weaver.fortran.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.fortran.formatter import Formatter

from utils import parse_dump

class FortranRunTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        parser = ParameterCsvParser(Validator())
        parameters = parser.parse('tests/good_fortran.txt')
        formatter = Formatter(parameters)
        flag_parameters = parser.parse('tests/flag_fortran.txt')
        flag_formatter = Formatter(flag_parameters)
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/main_dump.f90', 'tmp/main_dump.f90')
        shutil.copy('tests/flag_main_dump.f90', 'tmp/flag_main_dump.f90')
        base_name = 'parser'
        flag_base_name = 'flag_parser'
        main_file = 'main_dump.f90'
        flag_main_file = 'flag_main_dump.f90'
        self._exec_file = './cl_test_F'
        self._flag_exec_file = './cl_flag_test_F'
        artifacts = formatter.get_artifacts(base_name)
        module_file = artifacts[0].name
        artifacts[0].action(os.path.join('tmp', module_file))
        flag_artifacts = flag_formatter.get_artifacts(flag_base_name)
        flag_module_file = flag_artifacts[0].name
        flag_artifacts[0].action(os.path.join('tmp', flag_module_file))
        os.chdir('tmp')
        exit_code = subprocess.call(['gfortran', '-o', self._exec_file,
                                      module_file, main_file,
                                      '-lm'])
        if exit_code != 0:
            self.fail('link failed')
        exit_code = subprocess.call(['gfortran', '-o', self._flag_exec_file,
                                     flag_module_file, flag_main_file,
                                     '-lm'])
        if exit_code != 0:
            self.fail('flag link failed')

    @classmethod
    def tearDownClass(self):
        os.chdir('..')

    def test_default_run(self):
        result = subprocess.check_output([self._exec_file])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(1, int(values['next']))
        self.assertEqual(4, len(values))

    def test_first_run(self):
        result = subprocess.check_output([self._exec_file, '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(4, len(values))

    def test_one_additional_run(self):
        result = subprocess.check_output([self._exec_file, 'abc'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(1, int(values['next']))
        self.assertEqual(4, len(values))

    def test_first_one_additional_run(self):
        result = subprocess.check_output([self._exec_file, '-a', '17', 'abc'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(3, int(values['next']))
        self.assertEqual(4, len(values))

    def test_second_run(self):
        result = subprocess.check_output([self._exec_file, '-f', '3.14'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(4, len(values))

    def test_first_second_option_run(self):
        result = subprocess.check_output([self._exec_file, '-f', '3.14', '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(4, len(values))

    def test_first_third_option_run(self):
        result = subprocess.check_output([self._exec_file, '-str', 'alpha', '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'alpha'", values['str'])
        self.assertEqual(4, len(values))

    def test_all_options_run(self):
        result = subprocess.check_output([self._exec_file, '-str', 'alpha', '-a', '17', '-f', '-3.14'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertAlmostEqual(-3.14, float(values['f']))
        self.assertEqual("'alpha'", values['str'])
        self.assertEqual(4, len(values))

    def test_first_no_value(self):
        result = subprocess.check_output('{0} -a; exit 0'.format(self._exec_file),
                                         stderr=subprocess.STDOUT, shell=True)
        self.assertEqual("### error: option '-a' expects a value\n", result)

    def test_flag_default_run(self):
        result = subprocess.check_output([self._flag_exec_file])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertEqual('F', values['flag'])
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(3, len(values))

    def test_flag_second_run(self):
        result = subprocess.check_output([self._flag_exec_file, '-flag'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertEqual('T', values['flag'])
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(3, len(values))

    def test_flag_second_third_run(self):
        result = subprocess.check_output([self._flag_exec_file, '-str', 'alpha', '-flag'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertEqual('T', values['flag'])
        self.assertEqual("'alpha'", values['str'])
        self.assertEqual(3, len(values))

    def test_flag_second_third_run(self):
        result = subprocess.check_output([self._flag_exec_file, '-str', 'alpha', '-flag', '-a', '17'])
        values = parse_dump(result)
        self.assertEqual(17, int(values['a']))
        self.assertEqual('T', values['flag'])
        self.assertEqual("'alpha'", values['str'])
        self.assertEqual(3, len(values))

    def test_value_error(self):
        result = subprocess.check_output([self._flag_exec_file, '-a', 'abc'],
                                         stderr=subprocess.STDOUT)
        self.assertEqual("### error: invalid value for option '-a' of type integer\n", result)

    def test_first_no_value(self):
        result = subprocess.check_output([self._flag_exec_file, '-a'],
                                         stderr=subprocess.STDOUT)
        self.assertEqual("### error: option '-a' expects a value\n", result)


if __name__ == '__main__':
    unittest.main()

