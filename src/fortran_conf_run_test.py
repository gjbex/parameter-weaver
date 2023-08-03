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

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.fortran.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.fortran.formatter import Formatter

from utils import parse_dump

class FortranConfRunTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        parser = ParameterParser(Validator())
        parameters = parser.parse('tests/good_fortran.txt')
        formatter = Formatter(parameters)
        main_file = 'main_conf_dump.f90'
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/{0}'.format(main_file),
                    'tmp/{0}'.format(main_file))
        base_name = 'parser'
        cls._exec_file = './cl_test_F'
        artifacts = formatter.get_artifacts(base_name)
        module_file = artifacts[0].name
        artifacts[0].action(os.path.join('tmp', module_file))
        os.chdir('tmp')
        exit_code = subprocess.call(
            ['gfortran', '-o', cls._exec_file, module_file, main_file, '-lm']
        )
        if exit_code != 0:
            cls.fail('link failed')

    @classmethod
    def tearDownClass(cls):
        os.chdir('..')

    def test_default_run(self):
        result = subprocess.check_output([self._exec_file])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(3, len(values))

    def test_first_run(self):
        result = subprocess.check_output([self._exec_file, '../tests/fortran_conf_01.txt'])
        values = parse_dump(result)
        self.assertEqual(29, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['str'])
        self.assertEqual(3, len(values))

    def test_one_additional_run(self):
        result = subprocess.check_output([self._exec_file, '../tests/fortran_conf_02.txt'])
        values = parse_dump(result)
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'qed deq'", values['str'])
        self.assertEqual(3, len(values))


if __name__ == '__main__':
    unittest.main()

